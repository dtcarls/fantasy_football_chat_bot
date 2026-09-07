import os
# import pandas as pd
# import dataframe_image as dfi
if os.environ.get("AWS_EXECUTION_ENV") is not None:
    import espn.functionality as espn
else:
    # For local use
    import sys
    sys.path.insert(1, os.path.abspath('.'))
    import gamedaybot.espn.functionality as espn


def trophy_recap(league):
    """
    This function takes in a league object and returns a string representing the trophies earned by each team in the league.

    Parameters
    ----------
    league : object
        A league object from the ESPN Fantasy API.

    Returns
    -------
    str
        A string that contains the team names and the number of trophies earned for each team
    """

    ICONS = ['👑', '💩', '😱', '😅', '🍀', '😡', '📈', '📉', '🤡']
    legend = ['*LEGEND*', '👑: Most Points', '💩: Least Points', '😱: Blown out', '😅: Close wins', '🍀: Lucky',
              '😡: Unlucky', '📈: Most over projection', '📉: Most under projection', '🤡: Most points left on bench']
    team_trophies = {}
    team_names = []

    for team in league.teams:
        # Initialize trophy count for each team
        team_trophies[team.team_abbrev] = [0 for i in range(len(ICONS))]
        team_names.append(team.team_abbrev)

    def award(team_abbrev, index):
        # A trophy can go unawarded for a week -- a playoff week where the
        # matchup was a bye, or a week with no completed games -- and that week
        # simply does not count toward anyone's total.
        if team_abbrev is not None:
            team_trophies[team_abbrev][index] += 1

    for week in range(1, league.current_week):
        # All four trophy lookups below read the same week, so fetch it once
        # and hand the same box scores to each of them.
        box_scores = espn.fetch_box_scores(league, week=week)

        # Get high score, low score, blown out, and close win trophies
        high_score_team, low_score_team, blown_out_team, close_win_team = espn.get_trophies(
            league=league, week=week, recap=True, box_scores=box_scores)
        award(high_score_team, 0)
        award(low_score_team, 1)
        award(blown_out_team, 2)
        award(close_win_team, 3)

        # Get lucky and unlucky trophies
        lucky_team, unlucky_team, scores = espn.get_lucky_trophy(
            league=league, week=week, recap=True, box_scores=box_scores)
        award(lucky_team, 4)
        award(unlucky_team, 5)

        # Get overachiever and underachiever trophies
        overachiever_team, underachiever_team = espn.get_achievers_trophy(
            league=league, week=week, recap=True, box_scores=box_scores)
        award(overachiever_team, 6)
        award(underachiever_team, 7)

        # Get most points left on bench trophy
        best_manager_team = espn.optimal_team_scores(
            league=league, week=week, recap=True, box_scores=box_scores)
        award(best_manager_team, 8)

    result = 'Season Recap!\n'
    result += "Team".ljust(7, ' ')
    for icon in ICONS:
        result += icon + ' '
    result += '\n'
    for team_name, trophies in team_trophies.items():
        result += f"{team_name.ljust(5, ' ')}: {trophies}\n"
    result += '\n'.join(legend)

    # Pretty picture
    ### Libraries make lambda size too big
    # df = pd.DataFrame.from_dict(team_trophies, orient='index', columns=ICONS)
    # df_styled = df.style.background_gradient(cmap='Greens')
    # dfi.export(df_styled, '/tmp/season_recap.png')
    return (result)


def win_matrix(league):
    """
    This function takes in a league and returns a string of the standings if every team played every other team every week.
    The standings are sorted by winning percentage, and the string includes the team abbreviation, wins, and losses.

    Parameters
    ----------
    league : object
        A league object from the ESPN Fantasy API.

    Returns
    -------
    str
        A string of the standings in the format of "position. team abbreviation (wins-losses)"
    """

    team_record = {team.team_abbrev: [0, 0] for team in league.teams}

    for week in range(1, league.current_week):
        scores = espn.get_weekly_score_with_win_loss(league=league, week=week)
        losses = 0
        for team in scores:
            team_record[team.team_abbrev][0] += len(scores) - 1 - losses
            team_record[team.team_abbrev][1] += losses
            losses += 1

    team_record = dict(sorted(team_record.items(), key=lambda item: item[1][0] / item[1][1], reverse=True))

    standings_txt = ["Standings if everyone played every team every week"]
    pos = 1
    for team in team_record:
        standings_txt += [f"{pos:2}. {team:4} ({team_record[team][0]}-{team_record[team][1]})"]
        pos += 1

    return '\n'.join(standings_txt)
