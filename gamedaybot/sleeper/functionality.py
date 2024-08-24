import sys
import os
sys.path.insert(1, os.path.abspath('.'))

from gamedaybot.chat.groupme import GroupMe
from gamedaybot.chat.slack import Slack
from gamedaybot.chat.discord import Discord
from sleeper.api import LeagueAPIClient
from sleeper.api import PlayerAPIClient
from sleeper.enum import Sport

matchups = {}
users = {}
rosters = {}
players = {}
user_id_to_name = {}
roster_id_to_user_id = {}


def get_results():
    # Create a dictionary to hold the matchup data
    matchup_results = {}

    # Collect data into a dictionary with matchup_id as the key
    for matchup in matchups:
        roster_id = matchup.roster_id
        points = matchup.points
        matchup_id = matchup.matchup_id

        user_id = roster_id_to_user_id.get(roster_id, 'Unknown')
        team_name = user_id_to_name.get(user_id, 'Unknown')

        if matchup_id not in matchup_results:
            matchup_results[matchup_id] = []

        matchup_results[matchup_id].append((team_name, points))

    return matchup_results


def get_scoreboard():
    matchup_results = get_results()

    # Print matchups with team names and scores
    score=[]
    for matchup_id, teams in matchup_results.items():
        if len(teams) == 2:
            team_1_name, team_1_points = teams[0]
            team_2_name, team_2_points = teams[1]
            # print('%9s %6.2f - %6.2f %s' % (team_1_name[:9], team_1_points, team_2_points, team_2_name[:9]))
            score += ['%9s %6.2f - %6.2f %s' % (team_1_name[:9], team_1_points, team_2_points, team_2_name[:9])]
    text = ['Score Update'] + score
    return '\n'.join(text)

# def get_projected_scoreboard(league_id, week):
## Difficult

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
        output.append(f"{index:2}. ({team['wins']}-{team['losses']}) {team['team_name'][:9].ljust(9)}")
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


def get_matchups():
    # Step 1: Get standings data
    standings = {}
    for roster in rosters:
        user_id = roster.owner_id
        team_name = user_id_to_name.get(user_id, 'Unknown')
        wins = roster.settings.wins
        losses = roster.settings.losses
        standings[team_name] = (wins, losses)

    # Step 2: Get scoreboard data (team names for matchups)
    matchup_results = get_results()

    # Step 3: Format the matchups with win-loss records
    matchups_output = ['Matchups:']
    for matchup_id, teams in matchup_results.items():
        if len(teams) == 2:
            team_1_name = teams[0][0]
            team_2_name = teams[1][0]

            team_1_record = standings.get(team_1_name, (0, 0))
            team_2_record = standings.get(team_2_name, (0, 0))

            team_1_wl = f"({team_1_record[0]}-{team_1_record[1]})"
            team_2_wl = f"({team_2_record[0]}-{team_2_record[1]})"

            matchup_line = f"{team_1_name[:9].rjust(9)} {team_1_wl} vs {team_2_wl} {team_2_name[:9].ljust(9)}"
            matchups_output.append(matchup_line)

    # Return the formatted matchups as a single string
    return '\n'.join(matchups_output)


# TODO: Need reliable way of getting projected points in order to calculate achievers
def get_achievers_trophy():
    matchup_results = get_results()
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
    matchup_results = get_results()
    weekly_scores = {}
    for matchup_id, teams in matchup_results.items():
        if len(teams) == 2:
            team_1_name, team_1_points = teams[0]
            team_2_name, team_2_points = teams[1]
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
    matchup_results = get_results()

    low_score = 9999
    high_score = -1
    closest_score = 9999
    biggest_blowout = -1

    for matchup_id, teams in matchup_results.items():
        if len(teams) == 2:
            team_1_name, team_1_points = teams[0]
            team_2_name, team_2_points = teams[1]

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


if __name__ == "__main__":
    league_id = 992179861063786496
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
    print(get_matchups() + '\n')
    print(get_trophies() + '\n')