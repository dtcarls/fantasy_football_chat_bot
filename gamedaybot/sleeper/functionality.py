import sys
import os
sys.path.insert(1, os.path.abspath('.'))

from gamedaybot.chat.groupme import GroupMe
from gamedaybot.chat.slack import Slack
from gamedaybot.chat.discord import Discord
from sleeper.api import LeagueAPIClient
from sleeper.api import PlayerAPIClient
from sleeper.api.unofficial import UPlayerAPIClient
from sleeper.enum import Sport
from gamedaybot.utils.util import two_step_dominance

matchups = {}
users = {}
rosters = {}
players = {}
user_id_to_name = {}
roster_id_to_user_id = {}
all_matchup_data = {}
league_id = None
current_week = None
current_year = None

def get_current_week():
    if not current_week:
        week = 1
        nfl_state = LeagueAPIClient.get_sport_state(sport=Sport.NFL)

        if nfl_state.leg > 0 :
            week = nfl_state.leg #week of regular season
        return week
    else:
        return current_week

def get_current_year():
    if not current_year:
        year = 2024
        nfl_state = LeagueAPIClient.get_sport_state(sport=Sport.NFL)

        if nfl_state.league_season > '0':
            year = nfl_state.league_season
        return year
    else:
        return current_year


def get_matchup_results(_matchups=None):
    if not _matchups:
        _matchups = matchups

    matchup_results = {}

    # Collect data into a dictionary with matchup_id as the key
    for matchup in _matchups:
        roster_id = matchup.roster_id
        points = matchup.points
        matchup_id = matchup.matchup_id

        team_name = get_team_name_from_roster_id(roster_id)

        if matchup_id not in matchup_results:
            matchup_results[matchup_id] = []

        matchup_results[matchup_id].append((team_name, points, roster_id))

    return matchup_results


def get_projections(ppr=0, week=None, year=None):
    if not week:
        week = get_current_week()
    if not year:
        year = get_current_year()

    projections = {}
    for roster in rosters:
        user_id = roster.owner_id
        team_name = user_id_to_name.get(user_id, 'Unknown')
        projection = 0
        for player in roster.starters:
            try:
                stats = UPlayerAPIClient.get_player_projections(sport=Sport.NFL, player_id=str(player), season=year, week=1).stats
                match ppr:
                    case 1 | 'full' | '1' | '1.0':
                        pts = stats.pts_ppr
                    case 0.5 | 'half' | '0.5' | '.5':
                        pts = stats.pts_half_ppr
                    case _: #anything else
                        pts = stats.pts_std
            except ValueError:
                pts = 0
            projection += pts
        projections[team_name] = round(projection, 2)

    return projections


def get_matchup_data(_roster_id: int, _matchups=None):
    '''
    Retrieve the matchup details for a specific team in a specific week.
    '''
    # If matchups aren't provided, retrieve them for the given week
    if not _matchups:
        _matchups = matchups

    # Utilize the existing get_matchup_results function
    matchup_results = get_matchup_results(_matchups)

    # Find the specific matchup for the given team
    for matchup_id, teams in matchup_results.items():
        for team_name, points, roster_id in teams:
            if roster_id == _roster_id:
                # Find the opponent team in the same matchup
                for opponent_name, opponent_points, opponent_roster_id in teams:
                    if opponent_roster_id != _roster_id:
                        return {
                            'score': points,
                            'mov': points - opponent_points,  # Margin of Victory
                            'opponent_roster_id': opponent_roster_id
                        }

    return None  # If the team or matchup isn't found


def get_scoreboard():
    matchup_results = get_matchup_results()

    # Print matchups with team names and scores
    score=[]
    for matchup_id, teams in matchup_results.items():
        if len(teams) == 2:
            team_1_name, team_1_points, roster_id_1 = teams[0]
            team_2_name, team_2_points, roster_id_2 = teams[1]
            score += ['%9s %6.2f - %6.2f %s' % (team_1_name[:9], team_1_points, team_2_points, team_2_name[:9])]
    text = ['Score Update'] + score
    return '\n'.join(text)


def get_projected_scoreboard(ppr=0):
    projections = get_projections(ppr)
    matchup_results = get_matchup_results()

    score=[]
    for matchup_id, teams in matchup_results.items():
        if len(teams) == 2:
            team_1_name, team_1_points, roster_id_1 = teams[0]
            team_2_name, team_2_points, roster_id_2 = teams[1]
            score += ['%9s %6.2f - %6.2f %s' % (team_1_name[:9], projections[team_1_name], projections[team_2_name], team_2_name[:9])]
    text = ['Projected Scores'] + score
    return '\n'.join(text)


def get_standings():
    standings = []
    for roster in rosters:
        user_id = roster.owner_id
        team_name = user_id_to_name.get(user_id, 'Unknown')
        wins = roster.settings.wins
        losses = roster.settings.losses
        points_for = roster.settings.fpts + (roster.settings.fpts_decimal*.01)

        standings.append({
            'team_name': team_name,
            'wins': wins,
            'losses': losses,
            'points_for': points_for
        })

    # Sort the standings by wins, then by points_for as a tiebreaker
    standings.sort(key=lambda x: (-x['wins'], -x['points_for']))

    # Print the standings
    output = ["League Standings"]
    for index, team in enumerate(standings, 1):
        output.append(f"{index:2}. ({str(team['wins']).rjust(2)}-{str(team['losses']).ljust(2)}) {team['team_name'][:9].ljust(9)}")
        # output.append(f"{index:2}. ({team['wins']}-{team['losses']}) {team['team_name'][:9].ljust(9)} | Pts: {team['points_for']:.2f}")

    return '\n'.join(output)


def get_monitor():
    # Dictionary to hold the results
    flagged_players = {}

    # Iterate over each roster
    for roster in rosters:
        user_id = roster.owner_id
        team_name = user_id_to_name.get(user_id, 'Unknown')

        # Check each starting player
        for player_id in roster.starters:
            try:
                player = players[player_id]
                # projected_score = player.get('projected_points', 0)
                position = player.fantasy_positions[0].value
                status = player.injury_status.value

                # Flag players with 0 projected score or questionable/injured status
                if status != 'NA':
                    if team_name not in flagged_players:
                        flagged_players[team_name] = []
                    flagged_players[team_name].append({
                        'player_position': position,
                        'player_name': player.last_name ,
                        'status': status
                    })
            except KeyError:
                #do nothing
                pass

    # Output flagged players
    output = []
    for team_name, t_players in flagged_players.items():
        output.append(f"\n{team_name}:")
        for player in t_players:
            output.append(f" {player['player_position']} {player['player_name']} - {player['status'].capitalize()}")

    if output:
        output = ['Starting Players to Monitor:'] + output
    else:
        output = ['No Players to Monitor this week. Good Luck!']

    return '\n'.join(output)


def get_upcoming_matchups():
    # Step 1: Get standings data
    standings = {}
    for roster in rosters:
        user_id = roster.owner_id
        team_name = user_id_to_name.get(user_id, 'Unknown')
        wins = roster.settings.wins
        losses = roster.settings.losses
        standings[team_name] = (wins, losses)

    # Step 2: Get scoreboard data (team names for matchups)
    matchup_results = get_matchup_results()

    # Step 3: Format the matchups with win-loss records
    matchups_output = ['Matchups:']
    for matchup_id, teams in matchup_results.items():
        if len(teams) == 2:
            team_1_name = teams[0][0]
            team_2_name = teams[1][0]

            team_1_record = standings.get(team_1_name, (0, 0))
            team_2_record = standings.get(team_2_name, (0, 0))

            team_1_wl = f"{str(team_1_record[0]).rjust(2)}-{str(team_1_record[1]).ljust(2)}"
            team_2_wl = f"{str(team_2_record[0]).rjust(2)}-{str(team_2_record[1]).ljust(2)}"

            matchup_line = f"{team_1_name[:9].rjust(9)} ({team_1_wl}) vs ({team_2_wl}) {team_2_name[:9].ljust(9)}"
            matchups_output.append(matchup_line)

    # Return the formatted matchups as a single string
    return '\n'.join(matchups_output)


# TODO: Need reliable way of getting projected points in order to calculate achievers
def get_achievers_trophy():
    matchup_results = get_matchup_results()
    high_achiever_str = ['📈 Overachiever 📈']
    low_achiever_str = ['📉 Underachiever 📉']
    best_performance = -9999
    worst_performance = 9999
    for matchup_id, teams in matchup_results.items():
        if len(teams) == 2:
            team_1_name, team_1_points, team_1_proj = teams[0]
            team_2_name, team_2_points, team_2_proj = teams[1]
            home_performance = team_1_points - round(sum(team_1_proj), 2)
            away_performance = team_2_points - round(sum(team_2_proj), 2)

            if team_1_name != 0:
                if home_performance > best_performance:
                    best_performance = home_performance
                    over_achiever = team_1_name
                if home_performance < worst_performance:
                    worst_performance = home_performance
                    under_achiever = team_1_name
            if team_2_name != 0:
                if away_performance > best_performance:
                    best_performance = away_performance
                    over_achiever = team_2_name
                if away_performance < worst_performance:
                    worst_performance = away_performance
                    under_achiever = team_2_name

    if best_performance > 0:
        high_achiever_str += ['%s was %.2f points over their projection' % (over_achiever, best_performance)]
    else:
        high_achiever_str += ['No team out performed their projection']

    if worst_performance < 0:
        low_achiever_str += ['%s was %.2f points under their projection' % (under_achiever, abs(worst_performance))]
    else:
        low_achiever_str += ['No team was worse than their projection']

    return (high_achiever_str + low_achiever_str)


def get_weekly_score_with_win_loss():
    matchup_results = get_matchup_results()
    weekly_scores = {}
    for matchup_id, teams in matchup_results.items():
        if len(teams) == 2:
            team_1_name, team_1_points, roster_id = teams[0]
            team_2_name, team_2_points, roster_id = teams[1]
            if team_1_name != 0 and team_2_name != 0:
                if team_1_points > team_2_points:
                    weekly_scores[team_1_name] = [team_1_points, 'W']
                    weekly_scores[team_2_name] = [team_2_points, 'L']
                else:
                    weekly_scores[team_1_name] = [team_1_points, 'L']
                    weekly_scores[team_2_name] = [team_2_points, 'W']
    return dict(sorted(weekly_scores.items(), key=lambda item: item[1], reverse=True))


def get_lucky_trophy():
    weekly_scores = get_weekly_score_with_win_loss()
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

    lucky_str = ['🍀 Lucky 🍀']+['%s was %s against the league, but still got the win' % (lucky_team, lucky_record)]
    unlucky_str = ['😡 Unlucky 😡']+['%s was %s against the league, but still took an L' % (unlucky_team, unlucky_record)]
    return (lucky_str + unlucky_str)


def get_trophies():
    matchup_results = get_matchup_results()

    low_score = 9999
    high_score = -1
    closest_score = 9999
    biggest_blowout = -1

    for matchup_id, teams in matchup_results.items():
        if len(teams) == 2:
            team_1_name, team_1_points, roster_id = teams[0]
            team_2_name, team_2_points, roster_id = teams[1]

            if team_1_name:
                if team_1_points > high_score:
                    high_score = team_1_points
                    high_team = team_1_name
                if team_1_points < low_score:
                    low_score = team_1_points
                    low_team = team_1_name
            if team_2_name:
                if team_2_points > high_score:
                    high_score = team_2_points
                    high_team = team_2_name
                if team_2_points < low_score:
                    low_score = team_2_points
                    low_team = team_2_name

            if team_2_name and team_1_name:
                if team_2_points - team_1_points != 0 and \
                        abs(team_2_points - team_1_points) < closest_score:
                    closest_score = abs(team_2_points - team_1_points)
                    if team_2_points - team_1_points < 0:
                        close_winner = team_1_name
                        close_loser = team_2_name
                    else:
                        close_winner = team_2_name
                        close_loser = team_1_name
                if abs(team_2_points - team_1_points) > biggest_blowout:
                    biggest_blowout = abs(team_2_points - team_1_points)
                    if team_2_points - team_1_points < 0:
                        ownerer = team_1_name
                        blown_out = team_2_name
                    else:
                        ownerer = team_2_name
                        blown_out = team_1_name

    high_score_str = ['👑 High score 👑']+['%s with %.2f points' % (high_team, high_score)]
    low_score_str = ['💩 Low score 💩']+['%s with %.2f points' % (low_team, low_score)]
    close_score_str = ['😅 Close win 😅']+['%s barely beat %s by %.2f points' % (close_winner, close_loser, closest_score)]
    blowout_str = ['😱 Blow out 😱']+['%s blew out %s by %.2f points' % (ownerer, blown_out, biggest_blowout)]


    text = ['Trophies of the week:'] + high_score_str + low_score_str + close_score_str + blowout_str + \
            get_lucky_trophy()
    return '\n'.join(text)


def get_all_matchups(week=None):
    if not week:
        week = get_current_week()

    # Fetch all matchup data for all weeks up to the specified week
    for w in range(1, week + 1):
        all_matchup_data[w] = LeagueAPIClient.get_matchups_for_week(league_id=league_id, week=w)


def power_points(dominance, teams, week):
    '''Returns list of power points'''
    power_points = []
    for i, team in zip(dominance, teams.values()):
        avg_score = sum(team['score'][:week]) / week
        avg_mov = sum(team['mov'][:week]) / week

        power = '{0:.2f}'.format((int(i)*0.8) + (int(avg_score)*0.15) +
                                 (int(avg_mov)*0.05))
        power_points.append(power)
    power_tup = [(i, j) for (i, j) in zip(power_points, teams)]
    return sorted(power_tup, key=lambda tup: float(tup[0]), reverse=True)


def power_rankings(league_id: str=league_id, week: int=None):
    '''Return power rankings for any week in Sleeper'''

    # If week is not specified or invalid, use the current week
    if not week or week <= 0:
        week = get_current_week()

    # Fetch teams data from Sleeper API
    teams_data = rosters
    teams_sorted = sorted(teams_data, key=lambda x: x.roster_id, reverse=False)

    if not all_matchup_data:
        get_all_matchups(week)

    win_matrix = []
    teams_data = {}

    for team in teams_sorted:
        wins = [0] * len(teams_sorted)
        for w in range(1, week+1):
            matchup_data = get_matchup_data(team.roster_id, _matchups=all_matchup_data[w])
            if matchup_data:
                score = matchup_data['score']
                mov = matchup_data['mov']
                opponent_roster_id = matchup_data['opponent_roster_id']

                if team.roster_id not in teams_data:
                    teams_data[team.roster_id] = {'score': [], 'mov': []}

                teams_data[team.roster_id]['score'].append(score)
                teams_data[team.roster_id]['mov'].append(mov)

                if mov > 0:
                    opp_index = next(index for (index, d) in enumerate(teams_sorted) if d.roster_id == opponent_roster_id)
                    wins[opp_index] += 1
        win_matrix.append(wins)

    dominance_matrix = two_step_dominance(win_matrix)
    power_rank = power_points(dominance_matrix, teams_data, week)
    return power_rank


def print_power_rankings(week=None):
    """
    This function returns the power rankings of the teams in the league for a specific week,
    along with the change in power ranking number and playoff percentage from the previous week.
    If the week is not provided, it defaults to the current week.
    The power rankings are determined using a 2 step dominance algorithm,
    as well as a combination of points scored and margin of victory.
    It's weighted 80/15/5 respectively.

    Parameters
    ----------
    week : int, optional
        The week for which the power rankings are to be returned (default is current week)

    Returns
    -------
    str
        A string representing the power rankings with changes from the previous week
    """

    # Check if the week is provided, if not use the previous week
    # if not week:
    #     week = league.current_week - 1

    p_rank_up_emoji = "🟢"
    p_rank_down_emoji = "🔻"
    p_rank_same_emoji = "🟰"

    # Get the power rankings for the previous 2 weeks
    current_rankings = power_rankings(week=week)
    previous_rankings = power_rankings(week=week-1) if week > 1 else []

    # Normalize the scores
    def normalize_rankings(rankings):
        if not rankings:
            return []
        max_score = max(float(score) for score, _ in rankings)
        return [(f"{99.99 * float(score) / max_score:.2f}", team) for score, team in rankings]


    normalized_current_rankings = normalize_rankings(current_rankings)
    normalized_previous_rankings = normalize_rankings(previous_rankings)



    # Convert normalized previous rankings to a dictionary for easy lookup
    previous_rankings_dict = {get_team_name_from_roster_id(team): score for score, team in normalized_previous_rankings}

    # Prepare the output string
    rankings_text = ['Power Rankings [% change]']
    for normalized_current_score, current_team in normalized_current_rankings:
        team_abbrev = get_team_name_from_roster_id(current_team)
        rank_change_text = ''

        # Check if the team was present in the normalized previous rankings
        if team_abbrev in previous_rankings_dict:
            previous_score = previous_rankings_dict[team_abbrev]
            rank_change_percent = ((float(normalized_current_score) - float(previous_score)) / float(previous_score)) * 100
            rank_change_emoji = p_rank_up_emoji if rank_change_percent > 0 else p_rank_down_emoji if rank_change_percent < 0 else p_rank_same_emoji
            rank_change_text = f"[{rank_change_emoji}{abs(rank_change_percent):4.1f}%]"

        rankings_text.append(f"{normalized_current_score}{rank_change_text} - {team_abbrev}")

    return '\n'.join(rankings_text)


def get_team_name_from_roster_id(roster_id: int):
    user_id = roster_id_to_user_id.get(roster_id, 'Unknown')
    return user_id_to_name.get(user_id, 'Unknown') #team name


if __name__ == "__main__":
    # league_id = 992179861063786496 #4 man
    # league_id = 932291846812827648 # 10 man, no median
    league_id = 916114371233808384 # includes top half wins
    week = 1

    matchups = LeagueAPIClient.get_matchups_for_week(league_id=league_id, week=week)
    users = LeagueAPIClient.get_users_in_league(league_id=league_id)
    rosters = LeagueAPIClient.get_rosters(league_id=league_id)
    players = PlayerAPIClient.get_all_players(sport=Sport.NFL)

    # Create a mapping of user_id to display name
    user_id_to_name = {user.user_id: user.display_name for user in users}

    # Create a mapping of roster_id to user_id
    roster_id_to_user_id = {roster.roster_id: roster.owner_id for roster in rosters}

    print(get_scoreboard() + '\n')
    print(get_standings() + '\n')
    print(get_monitor() + '\n')
    print(get_upcoming_matchups() + '\n')
    print(get_trophies() + '\n')
    print(print_power_rankings(2) + '\n')
    print(get_projected_scoreboard() + '\n')