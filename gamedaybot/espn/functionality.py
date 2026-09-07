import logging
import os
from datetime import date

if os.environ.get("AWS_EXECUTION_ENV") is not None:
    # For use in lambda function
    import utils.util as util
else:
    # For local use
    import sys
    sys.path.insert(1, os.path.abspath('.'))
    import gamedaybot.utils.util as util

logger = logging.getLogger(__name__)


def season_started(league):
    """
    Check whether the league has reached a scoring period yet.

    ESPN reports scoringPeriodId == 0 for a league whose season has not begun:
    one that has not drafted, one abandoned mid-season, and every league before
    week 1 is scored. In that state league.box_scores() raises
    KeyError('rosterForCurrentScoringPeriod'), because the team payload has no
    roster for a period that does not exist.

    Only an explicit 0 counts. A scoring period we cannot read is not evidence
    of anything, so it proceeds exactly as before.

    Parameters
    ----------
    league : espn_api.football.League
        The league to check.

    Returns
    -------
    bool
        True when box scores can safely be fetched.
    """
    period = getattr(league, 'scoringPeriodId', None)
    return not (isinstance(period, int) and period == 0)


def fetch_box_scores(league, week=None):
    """
    Fetch box scores, or return an empty list when the season has not started.

    Every box-score read goes through here so the guard cannot be forgotten at
    one call site. Callers must treat an empty list as "nothing to report"
    rather than rendering an empty report.

    Parameters
    ----------
    league : espn_api.football.League
        The league to fetch for.
    week : int, optional
        The week to fetch. Defaults to the league's current week.

    Returns
    -------
    list
        The box scores, or an empty list when the season has not started.
    """
    if not season_started(league):
        logger.info('Season has not started (scoringPeriodId=0); skipping box scores')
        return []
    return league.box_scores(week=week)


def get_scoreboard_short(league, week=None, box_scores=None):
    """
    Retrieve the scoreboard for a given week of the fantasy football season.

    Parameters
    ----------
    league: espn_api.football.League
        The league for which to retrieve the scoreboard.
    week: int
        The week of the season for which to retrieve the scoreboard.
    box_scores: list, optional
        Pre-fetched box scores for the same week, to avoid a duplicate API call.

    Returns
    -------
    list of dict
        A list of dictionaries representing the games on the scoreboard for the given week. Each dictionary contains
        information about a single game, including the teams and their scores.
    """

    # Gets current week's scoreboard
    if box_scores is None:
        box_scores = fetch_box_scores(league, week=week)
    score = ['%4s %6.2f - %6.2f %s' % (i.home_team.team_abbrev, i.home_score,
                                       i.away_score, i.away_team.team_abbrev) for i in box_scores
             if i.away_team]
    if not score:
        # A bare 'Score Update' header with nothing under it is not worth
        # sending; espn_bot drops this sentinel instead.
        return util.NO_MATCHUP_DATA
    text = ['Score Update'] + score
    return '\n'.join(text)


def get_projected_scoreboard(league, week=None, box_scores=None):
    """
    Retrieve the projected scoreboard for a given week of the fantasy football season.

    Parameters
    ----------
    league: espn_api.football.League
        The league for which to retrieve the projected scoreboard.
    week: int
        The week of the season for which to retrieve the projected scoreboard.
    box_scores: list, optional
        Pre-fetched box scores for the same week, to avoid a duplicate API call.

    Returns
    -------
    list of dict
        A list of dictionaries representing the projected games on the scoreboard for the given week. Each dictionary
        contains information about a single game, including the teams and their projected scores.
    """

    # Gets current week's scoreboard projections
    if box_scores is None:
        box_scores = fetch_box_scores(league, week=week)
    score = ['%4s %6.2f - %6.2f %s' % (i.home_team.team_abbrev, get_projected_total(i.home_lineup),
                                       get_projected_total(i.away_lineup), i.away_team.team_abbrev) for i in box_scores
             if i.away_team]
    if not score:
        # Mirrors get_scoreboard_short: a bare header is not worth sending.
        return util.NO_MATCHUP_DATA
    text = ['Approximate Projected Scores'] + score
    return '\n'.join(text)


def get_standings(league):
    """
    Retrieve the current standings for a fantasy football league.

    Parameters
    ----------
    league: object
        The league object for which to retrieve the standings.

    Returns
    -------
    str
        A string containing the current standings, formatted as a list of teams with their records and positions.
    """

    standings = league.standings()
    standings_txt = [f"{pos + 1:2}: ({team.wins}-{team.losses}) {team.team_name} " for
                     pos, team in enumerate(standings)]
    text = ["Current Standings"] + standings_txt

    return "\n".join(text)


def get_projected_total(lineup):
    """
    Retrieve the projected total points for a given lineup in a fantasy football league.

    Parameters
    ----------
    lineup : list
        A list of player objects that represents the lineup

    Returns
    -------
    float
        The projected total points for the given lineup.
    """

    total_projected = 0
    for i in lineup:
        # exclude player on bench and injured reserve
        if i.slot_position != 'BE' and i.slot_position != 'IR':
            # Check if the player has already played or not
            if i.points != 0 or i.game_played > 0:
                total_projected += i.points
            else:
                total_projected += i.projected_points
    return total_projected


def all_played(lineup):
    """
    Check if all the players in a given lineup have played their game.

    Parameters
    ----------
    lineup : list
        A list of player objects that represents the lineup

    Returns
    -------
    bool
        True if all the players in the lineup have played their game, False otherwise.
    """

    for i in lineup:
        # exclude player on bench and injured reserve
        if i.slot_position != 'BE' and i.slot_position != 'IR' and i.game_played < 100:
            return False
    return True


def get_monitor(league, box_scores=None):
    """
    Retrieve a list of players from a given fantasy football league that should be monitored during a game.

    Parameters
    ----------
    league: object
        The league object for which to retrieve the monitor players.
    box_scores: list, optional
        Pre-fetched box scores for the current week, to avoid a duplicate API call.

    Returns
    -------
    str
        A string containing the list of players to monitor, formatted as a list of player names and status.
    """

    if box_scores is None:
        box_scores = fetch_box_scores(league)
    monitor = []
    text = ''
    for i in box_scores:
        monitor += scan_roster(i.home_lineup, i.home_team)
        monitor += scan_roster(i.away_lineup, i.away_team)

    if monitor:
        text = ['Starting Players to Monitor'] + monitor
    else:
        text = ['No Players to Monitor this week. Good Luck!']
    return '\n'.join(text)


def scan_roster(lineup, team):
    """
    Retrieve a list of players from a given fantasy football league that have a status.

    Parameters
    ----------
    lineup : list
        A list of player objects that represents the lineup
    team : object
        The team object for which to retrieve the monitor players

    Returns
    -------
    list
        A list of strings containing the list of players to monitor, formatted as a list of player names and statuses.
    """

    count = 0
    players = []
    for i in lineup:
        # exclude bench and injured players and active or normal players
        if i.slot_position != 'BE' and i.slot_position != 'IR' and \
            i.injuryStatus != 'ACTIVE' and i.injuryStatus != 'NORMAL' \
                and i.game_played == 0:

            count += 1
            player = i.position + ' ' + i.name + ' - ' + i.injuryStatus.title().replace('_', ' ')
            players += [player]

        if i.slot_position == 'IR' and \
            i.injuryStatus != 'INJURY_RESERVE' and i.injuryStatus != 'OUT':

            count += 1
            player = i.position + ' ' + i.name + ' - Not IR eligible'
            players += [player]

    list = ""
    report = ""

    for p in players:
        list += p + "\n"

    if count > 0:
        s = '%s: \n%s \n' % (team.team_name, list[:-1])
        report = [s.lstrip()]

    return report


def get_matchups(league, week=None, box_scores=None):
    """
    Retrieve the matchups for a given week in a fantasy football league.

    Parameters
    ----------
    league: object
        The league object for which to retrieve the matchups.
    week : int, optional
        The week number for which to retrieve the matchups, by default None.
    box_scores: list, optional
        Pre-fetched box scores for the same week, to avoid a duplicate API call.

    Returns
    -------
    str
        A string containing the matchups for the given week, formatted as a list of team names and abbreviation.
    """

    # Gets current week's Matchups
    if box_scores is None:
        box_scores = fetch_box_scores(league, week=week)
    matchups = box_scores

    if not any(i.away_team for i in matchups):
        # Nothing to pair up: every slot is a bye, or the week has no data.
        return util.NO_MATCHUP_DATA

    full_names = ['%s vs %s' % (i.home_team.team_name, i.away_team.team_name) for i in matchups if i.away_team]

    abbrevs = ['%4s (%s-%s) vs (%s-%s) %s' % (i.home_team.team_abbrev, i.home_team.wins, i.home_team.losses,
                                              i.away_team.wins, i.away_team.losses, i.away_team.team_abbrev) for i in matchups
               if i.away_team]

    text = ['Matchups'] + full_names + [''] + abbrevs
    return '\n'.join(text)


def get_close_scores(league, week=None, box_scores=None):
    """
    Retrieve the projected closest scores (15 points or closer) for a given week in a fantasy football league.

    Parameters
    ----------
    league: object
        The league object for which to retrieve the closest scores.
    week : int, optional
        The week number for which to retrieve the closest scores, by default None.
    box_scores: list, optional
        Pre-fetched box scores for the same week, to avoid a duplicate API call.

    Returns
    -------
    str
        A string containing the projected closest scores for the given week, formatted as a list of team names and abbreviation.
    """

    # Gets current projected closest scores (15 points or closer)
    if box_scores is None:
        box_scores = fetch_box_scores(league, week=week)
    score = []

    for i in box_scores:
        if i.away_team:
            away_projected = get_projected_total(i.away_lineup)
            home_projected = get_projected_total(i.home_lineup)
            diffScore = away_projected - home_projected

            if (abs(diffScore) <= 15 and (not all_played(i.away_lineup) or not all_played(i.home_lineup))):
                score += ['%4s %6.2f - %6.2f %s' % (i.home_team.team_abbrev, i.home_projected,
                                                    i.away_projected, i.away_team.team_abbrev)]

    if not score:
        return ('')
    text = ['Projected Close Scores'] + score
    return '\n'.join(text)


def get_waiver_report(league, faab=False, scoring_period=None, test_date=None):
    """
    Generate a waiver report for a given league and scoring period.

    The report lists all waiver transactions that occurred on the specified date (defaults to today),
    including the team that made the transaction, the player(s) added, and the player(s) dropped (if applicable).
    If faab is True, the report will include FAAB amount spent and will be sorted from largest to smallest FAAB bid.

    Parameters
    ----------
    league : object
        The league object for which the report is being generated.
    faab : bool, optional
        If True, include FAAB amount spent and sort report by FAAB descending. Defaults to False.
    scoring_period : int, optional
        The scoring period to query transactions for. Defaults to league.scoringPeriodId.
    test_date : str, optional
        Date string (YYYY-MM-DD) to simulate 'today' for testing historical transactions. Defaults to current date.

    Returns
    -------
    str
        A formatted string containing the waiver report.
    """


    # Allow testing with a specific scoring period and date
    if scoring_period is None:
        scoring_period = league.scoringPeriodId
    transactions = league.transactions(scoring_period, types={'WAIVER'})
    report = []
    report_items = []  # For sorting if faab
    today = test_date if test_date else date.today().strftime('%Y-%m-%d')
    text = ''

    for txn in transactions:
        # Only include transactions matching the test date and type WAIVER
        txn_date = None
        if txn.date:
            txn_date = date.fromtimestamp(txn.date / 1000).strftime('%Y-%m-%d')
        if txn_date == today and txn.status == 'EXECUTED':
            team_name = txn.team.team_name
            faab_amount = txn.bid_amount if hasattr(txn, 'bid_amount') else 0
            add_str = ''
            drop_str = ''
            for item in txn.items:
                if item.type == 'ADD':
                    if faab:
                        add_str += f"ADDED {league.player_info(item.player).position} - {item.player} (${faab_amount})\n"
                    else:
                        add_str += f"ADDED {league.player_info(item.player).position} - {item.player}\n"
                elif item.type == 'DROP':
                    drop_str += f"DROPPED {league.player_info(item.player).position} - {item.player}\n"
            s = f"{team_name} \n{add_str}{drop_str}"
            if faab:
                report_items.append((faab_amount, s.lstrip()))
            else:
                report.append(s.lstrip())

    if faab:
        # Sort by faab_amount descending
        report_items.sort(key=lambda x: x[0], reverse=True)
        report = [item[1] for item in report_items]

    # Only return a report if there are transactions
    if report:
        text = [f'Waiver Report {today}:'] + report

    return '\n'.join(text)


def get_power_rankings(league, week=None):
    """
    This function returns the power rankings of the teams in the league for a specific week,
    along with the change in power ranking number and playoff percentage from the previous week.
    If the week is not provided, it defaults to the current week.
    The power rankings are determined using a 2 step dominance algorithm,
    as well as a combination of points scored and margin of victory.
    It's weighted 80/15/5 respectively.

    Parameters
    ----------
    league: object
        The league object for which the power rankings are being generated
    week : int, optional
        The week for which the power rankings are to be returned (default is current week)

    Returns
    -------
    str
        A string representing the power rankings with changes from the previous week
    """

    # Check if the week is provided, if not use the previous week
    if not week:
        week = league.current_week - 1

    p_rank_up_emoji = "🟢"
    p_rank_down_emoji = "🔻"
    p_rank_same_emoji = "🟰"

    # Get the power rankings for the previous 2 weeks
    current_rankings = league.power_rankings(week=week)
    previous_rankings = league.power_rankings(week=week-1) if week > 1 else []

    # Normalize the scores
    def normalize_rankings(rankings):
        if not rankings:
            return []
        max_score = max(float(score) for score, _ in rankings)
        return [(f"{99.99 * float(score) / max_score:.2f}", team) for score, team in rankings]


    normalized_current_rankings = normalize_rankings(current_rankings)
    normalized_previous_rankings = normalize_rankings(previous_rankings)

    # Convert normalized previous rankings to a dictionary for easy lookup
    previous_rankings_dict = {team.team_abbrev: score for score, team in normalized_previous_rankings}

    # Prepare the output string
    rankings_text = ['Power Rankings (Playoff %)']
    for normalized_current_score, current_team in normalized_current_rankings:
        team_abbrev = current_team.team_abbrev
        rank_change_text = ''

        # Check if the team was present in the normalized previous rankings
        if team_abbrev in previous_rankings_dict:
            previous_score = previous_rankings_dict[team_abbrev]
            rank_change_percent = ((float(normalized_current_score) - float(previous_score)) / float(previous_score)) * 100
            rank_change_emoji = p_rank_up_emoji if rank_change_percent > 0 else p_rank_down_emoji if rank_change_percent < 0 else p_rank_same_emoji
            rank_change_text = f"[{rank_change_emoji}{abs(rank_change_percent):4.1f}%]"

        rankings_text.append(f"{normalized_current_score}{rank_change_text} ({current_team.playoff_pct:4.1f}) - {team_abbrev}")

    return '\n'.join(rankings_text)


def get_starter_counts(league):
    """
    Get the number of starters for each position

    Parameters
    ----------
    league : object
        The league object for which the starter counts are being generated

    Returns
    -------
    dict
        A dictionary containing the number of players at each position within the starting lineup.
    """

    return {pos: cnt for pos, cnt in league.settings.position_slot_counts.items() if pos not in ['BE', 'IR'] and cnt != 0}


def best_flex(flexes, player_pool, num):
    """
    Given a list of flex positions, a dictionary of player pool, and a number of players to return,
    this function returns the best flex players from the player pool.

    Parameters
    ----------
    flexes : list
        a list of strings representing the flex positions
    player_pool : dict
        a dictionary with keys as position and values as a dictionary with player name as key and value as score
    num : int
        number of players to return from the player pool

    Returns
    ----------
    best : dict
        a dictionary containing the best flex players from the player pool
    player_pool : dict
        the updated player pool after removing the best flex players
    """

    pool = {}
    # iterate through each flex position
    for flex_position in flexes:
        # add players from flex position to the pool
        try:
            pool = pool | player_pool[flex_position]
        except KeyError:
            pass
    # sort the pool by score in descending order
    pool = {k: v for k, v in sorted(pool.items(), key=lambda item: item[1], reverse=True)}
    # get the top num players from the pool
    best = dict(list(pool.items())[:num])
    # remove the best flex players from the player pool
    for pos in player_pool:
        for p in best:
            if p in player_pool[pos]:
                player_pool[pos].pop(p)
    return best, player_pool


def optimal_lineup_score(lineup, starter_counts):
    """
    This function returns the optimal lineup score based on the provided lineup and starter counts.

    Parameters
    ----------
    lineup : list
        A list of player objects for which the optimal lineup score is being generated
    starter_counts : dict
        A dictionary containing the number of starters for each position

    Returns
    -------
    tuple
        A tuple containing the optimal lineup score, the provided lineup score, the difference between the two scores,
        and the percentage of the provided lineup's score compared to the optimal lineup's score.
    """

    best_lineup = {}
    position_players = {}

    # get all players and points
    score = 0
    score_pct = 0
    best_score = 0

    for player in lineup:
        try:
            position_players[player.position][player.name] = player.points
        except KeyError:
            position_players[player.position] = {}
            position_players[player.position][player.name] = player.points
        if player.slot_position not in ['BE', 'IR']:
            score += player.points

    # sort players by position for points
    for position in starter_counts:
        try:
            position_players[position] = {k: v for k, v in sorted(
                position_players[position].items(), key=lambda item: item[1], reverse=True)}
            best_lineup[position] = dict(list(position_players[position].items())[:starter_counts[position]])
            position_players[position] = dict(list(position_players[position].items())[starter_counts[position]:])
        except KeyError:
            best_lineup[position] = {}

    # flexes. need to figure out best in other single positions first
    for position in starter_counts:
        # flex
        if 'D/ST' not in position and '/' in position:
            flex = position.split('/')
            result = best_flex(flex, position_players, starter_counts[position])
            best_lineup[position] = result[0]
            position_players = result[1]

    # Offensive Player. need to figure out best in other positions first
    if 'OP' in starter_counts:
        flex = ['RB', 'WR', 'TE', 'QB']
        result = best_flex(flex, position_players, starter_counts['OP'])
        best_lineup['OP'] = result[0]
        position_players = result[1]

    # Defensive Player. need to figure out best in other positions first
    if 'DP' in starter_counts:
        flex = ['DT', 'DE', 'LB', 'CB', 'S']
        result = best_flex(flex, position_players, starter_counts['DP'])
        best_lineup['DP'] = result[0]
        position_players = result[1]

    for position in best_lineup:
        best_score += sum(best_lineup[position].values())

    if best_score != 0:
        score_pct = (score / best_score) * 100

    return (best_score, score, best_score - score, score_pct)


def optimal_team_scores(league, week=None, full_report=False, recap=False, box_scores=None):
    """
    This function returns the optimal team scores or managers.

    Parameters
    ----------
    league : object
        The league object for which the optimal team scores are being generated
    week : int, optional
        The week for which the optimal team scores are to be returned (default is the previous week)
    full_report : bool, optional
        A boolean indicating if a full report should be returned (default is False)
    box_scores : list, optional
        Pre-fetched box scores for the same week, to avoid a duplicate API call.

    Returns
    -------
    str or tuple
        If full_report is True, a string representing the full report of the optimal team scores.
        If full_report is False, a tuple containing the best and worst manager strings.
    """

    if not week:
        week = league.current_week - 1
    if box_scores is None:
        box_scores = fetch_box_scores(league, week=week)
    results = []
    best_scores = {}
    starter_counts = get_starter_counts(league)

    for i in box_scores:
        if i.home_team != 0:
            best_scores[i.home_team] = optimal_lineup_score(i.home_lineup, starter_counts)
        if i.away_team != 0:
            best_scores[i.away_team] = optimal_lineup_score(i.away_lineup, starter_counts)

    best_scores = {key: value for key, value in sorted(best_scores.items(), key=lambda item: item[1][3], reverse=True)}

    if full_report:
        i = 1
        for score in best_scores:
            s = ['%2d: %4s: %6.2f (%6.2f - %.2f%%)' %
                 (i, score.team_abbrev, best_scores[score][0],
                  best_scores[score][1], best_scores[score][3])]
            results += s
            i += 1

        text = ['Optimal Scores:  (Actual - % of optimal)'] + results
        return '\n'.join(text)
    else:
        num_teams = 0
        team_names = ''
        for score in best_scores:
            if best_scores[score][3] > 99.8:
                num_teams += 1
                team_names += score.team_name + ', '
            else:
                break

        if num_teams <= 1:
            best = next(iter(best_scores.items()))
            best_mgr_str = ['🤖 Best Manager 🤖'] + ['%s scored %.2f%% of their optimal score!' % (best[0].team_name, best[1][3])]
        else:
            team_names = team_names[:-2]
            best_mgr_str = ['🤖 Best Managers 🤖'] + [f'{team_names} scored their optimal score!']

        worst = best_scores.popitem()
        if recap:
            return worst[0].team_abbrev

        worst_mgr_str = ['🤡 Worst Manager 🤡'] + ['%s left %.2f points on their bench. Only scoring %.2f%% of their optimal score.' %
                                                 (worst[0].team_name, worst[1][0] - worst[1][1], worst[1][3])]

        return (best_mgr_str + worst_mgr_str)


def get_achievers_trophy(league, week=None, recap=False, box_scores=None):
    """
    This function returns the overachiever and underachiever of the league
    based on the difference between the projected score and the actual score.

    Parameters
    ----------
    league: object
        The league object for which the overachiever and underachiever are being determined
    week : int, optional
        The week for which the overachiever and underachiever are to be returned (default is current week)
    box_scores : list, optional
        Pre-fetched box scores for the same week, to avoid a duplicate API call.

    Returns
    -------
    str
        A string representing the overachiever and underachiever of the league
    """

    if box_scores is None:
        box_scores = fetch_box_scores(league, week=week)
    high_achiever_str = ['📈 Overachiever 📈']
    low_achiever_str = ['📉 Underachiever 📉']
    best_performance = -9999
    worst_performance = 9999
    for i in box_scores:
        home_performance = i.home_score - i.home_projected
        away_performance = i.away_score - i.away_projected

        if i.home_team != 0:
            if home_performance > best_performance:
                best_performance = home_performance
                over_achiever = i.home_team
            if home_performance < worst_performance:
                worst_performance = home_performance
                under_achiever = i.home_team
        if i.away_team != 0:
            if away_performance > best_performance:
                best_performance = away_performance
                over_achiever = i.away_team
            if away_performance < worst_performance:
                worst_performance = away_performance
                under_achiever = i.away_team

    if recap:
        return over_achiever.team_abbrev, under_achiever.team_abbrev

    if best_performance > 0:
        high_achiever_str += ['%s was %.2f points over their projection' % (over_achiever.team_name, best_performance)]
    else:
        high_achiever_str += ['No team out performed their projection']

    if worst_performance < 0:
        low_achiever_str += ['%s was %.2f points under their projection' % (under_achiever.team_name, abs(worst_performance))]
    else:
        low_achiever_str += ['No team was worse than their projection']

    return (high_achiever_str + low_achiever_str)


def get_weekly_score_with_win_loss(league, week=None, box_scores=None):
    if box_scores is None:
        box_scores = fetch_box_scores(league, week=week)
    weekly_scores = {}
    for i in box_scores:
        if i.home_team != 0 and i.away_team != 0:
            if i.home_score > i.away_score:
                weekly_scores[i.home_team] = [i.home_score, 'W']
                weekly_scores[i.away_team] = [i.away_score, 'L']
            else:
                weekly_scores[i.home_team] = [i.home_score, 'L']
                weekly_scores[i.away_team] = [i.away_score, 'W']
    return dict(sorted(weekly_scores.items(), key=lambda item: item[1], reverse=True))


def get_lucky_trophy(league, week=None, recap=False, box_scores=None):
    """
    This function takes in a league object and an optional week parameter. It retrieves the box scores for the specified league and week, and creates a dictionary with the weekly scores for each team. The teams are sorted in descending order by their scores, and the team with the lowest score and won is determined to be the lucky team for the week. The team with the highest score and lost is determined to be the unlucky team for the week. The function returns a list containing the lucky and unlucky teams, along with their records for the week.
    Parameters:
    league (object): A league object containing information about the league and its teams.
    week (int, optional): The week for which the box scores should be retrieved. If no week is specified, the current week will be used.
    box_scores (list, optional): Pre-fetched box scores for the same week, to avoid a duplicate API call.
    Returns:
    list: A list containing the lucky and unlucky teams, along with their records for the week.
    """
    weekly_scores = get_weekly_score_with_win_loss(league, week=week, box_scores=box_scores)
    losses = 0
    unlucky_record = ''
    lucky_record = ''
    num_teams = len(weekly_scores) - 1

    for t in weekly_scores:
        if weekly_scores[t][1] == 'L':
            unlucky_team = t
            unlucky_record = str(num_teams - losses) + '-' + str(losses)
            break
        losses += 1

    wins = 0
    weekly_scores = dict(sorted(weekly_scores.items(), key=lambda item: item[1]))
    for t in weekly_scores:
        if weekly_scores[t][1] == 'W':
            lucky_team = t
            lucky_record = str(wins) + '-' + str(num_teams - wins)
            break
        wins += 1

    if recap:
        return lucky_team.team_abbrev, unlucky_team.team_abbrev, weekly_scores

    lucky_str = ['🍀 Lucky 🍀']+['%s was %s against the league, but still got the win' % (lucky_team.team_name, lucky_record)]
    unlucky_str = ['😡 Unlucky 😡']+['%s was %s against the league, but still took an L' % (unlucky_team.team_name, unlucky_record)]
    return (lucky_str + unlucky_str)


def get_trophies(league, week=None, recap=False, box_scores=None):
    """
    Returns trophies for the highest score, lowest score, closest score, and biggest win.

    Parameters
    ----------
    league : object
        The league object for which the trophies are to be returned
    week : int, optional
        The week for which the trophies are to be returned (default is current week)
    box_scores : list, optional
        Pre-fetched box scores for the same week, to avoid a duplicate API call.
        Also passed on to the lucky, achiever and optimal-lineup trophies, so
        the whole trophy set costs a single box_scores call.

    Returns
    -------
    str
        A string representing the trophies
    """
    if not week:
        week = league.current_week - 1

    if box_scores is None:
        box_scores = fetch_box_scores(league, week=week)
    matchups = box_scores
    low_score = 99999999
    high_score = -1
    closest_score = 99999999
    biggest_blowout = -1

    for i in matchups:
        if i.home_team != 0:
            if i.home_score > high_score:
                high_score = i.home_score
                high_team = i.home_team
            if i.home_score < low_score:
                low_score = i.home_score
                low_team = i.home_team
        if i.away_team != 0:
            if i.away_score > high_score:
                high_score = i.away_score
                high_team = i.away_team
            if i.away_score < low_score:
                low_score = i.away_score
                low_team = i.away_team

        if i.away_team != 0 and i.home_team != 0:
            if i.away_score - i.home_score != 0 and \
                    abs(i.away_score - i.home_score) < closest_score:
                closest_score = abs(i.away_score - i.home_score)
                if i.away_score - i.home_score < 0:
                    close_winner = i.home_team
                    close_loser = i.away_team
                else:
                    close_winner = i.away_team
                    close_loser = i.home_team
            if abs(i.away_score - i.home_score) > biggest_blowout:
                biggest_blowout = abs(i.away_score - i.home_score)
                if i.away_score - i.home_score < 0:
                    ownerer = i.home_team
                    blown_out = i.away_team
                else:
                    ownerer = i.away_team
                    blown_out = i.home_team

    if (recap):
        return high_team.team_abbrev, low_team.team_abbrev, blown_out.team_abbrev, close_winner.team_abbrev

    high_score_str = ['👑 High score 👑']+['%s with %.2f points' % (high_team.team_name, high_score)]
    low_score_str = ['💩 Low score 💩']+['%s with %.2f points' % (low_team.team_name, low_score)]
    close_score_str = ['😅 Close win 😅']+['%s barely beat %s by %.2f points' %
                                         (close_winner.team_name, close_loser.team_name, closest_score)]
    blowout_str = ['😱 Blow out 😱']+['%s blew out %s by %.2f points' % (ownerer.team_name, blown_out.team_name, biggest_blowout)]

    text = ['Trophies of the week:'] + high_score_str + low_score_str + blowout_str + close_score_str + \
        get_lucky_trophy(league, week, box_scores=box_scores) + \
        get_achievers_trophy(league, week, box_scores=box_scores) + \
        optimal_team_scores(league, week, box_scores=box_scores)
    return '\n'.join(text)


def get_player_achievers(league, week=None, return_number=2):
    """
    Returns the top and bottom N players who exceeded or fell short of their projection the most in starting lineups for the given week.
    """
    if not week:
        week = league.current_week - 1
    box_scores = fetch_box_scores(league, week=week)
    player_diffs = []
    for matchup in box_scores:
        for team, team_lineup in zip([matchup.home_team, matchup.away_team], [matchup.home_lineup, matchup.away_lineup]):
            for player in team_lineup:
                if player.slot_position not in ['BE', 'IR'] and hasattr(player, 'projected_points') and player.projected_points is not None:
                    diff = round(player.points - player.projected_points, 2)
                    player_diffs.append({
                        'name': player.name,
                        'team': player.proTeam if hasattr(player, 'proTeam') else '',
                        'fantasy_team': team.team_abbrev if team else '',
                        'points': player.points,
                        'projected': player.projected_points,
                        'diff': diff
                    })
    sorted_diffs = sorted(player_diffs, key=lambda x: x['diff'], reverse=True)
    best = sorted_diffs[:return_number]
    worst = sorted_diffs[-return_number:]
    return best, worst
