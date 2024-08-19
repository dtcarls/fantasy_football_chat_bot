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

def get_scoreboard():
    # Create a dictionary to hold the matchup data
    matchup_results = {}

    # Collect data into a dictionary with matchup_id as the key
    for matchup in matchups:
        roster_id = matchup.roster_id
        points = matchup.points
        # projected_points = matchup.starters_points
        matchup_id = matchup.matchup_id

        user_id = roster_id_to_user_id.get(roster_id, 'Unknown')
        team_name = user_id_to_name.get(user_id, 'Unknown')

        if matchup_id not in matchup_results:
            matchup_results[matchup_id] = []

        matchup_results[matchup_id].append((team_name, points))

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
    matchup_results = {}
    for matchup in matchups:
        roster_id = matchup.roster_id
        matchup_id = matchup.matchup_id

        user_id = roster_id_to_user_id.get(roster_id, 'Unknown')
        team_name = user_id_to_name.get(user_id, 'Unknown')

        if matchup_id not in matchup_results:
            matchup_results[matchup_id] = []

        matchup_results[matchup_id].append(team_name)

    # Step 3: Format the matchups with win-loss records
    matchups_output = ['Matchups:']
    for matchup_id, teams in matchup_results.items():
        if len(teams) == 2:
            team_1_name = teams[0][:9].rjust(9)
            team_2_name = teams[1][:9].ljust(9)

            team_1_record = standings.get(team_1_name, (0, 0))
            team_2_record = standings.get(team_2_name, (0, 0))

            team_1_wl = f"({team_1_record[0]}-{team_1_record[1]})"
            team_2_wl = f"({team_2_record[0]}-{team_2_record[1]})"

            matchup_line = f"{team_1_name} {team_1_wl} vs {team_2_wl} {team_2_name}"
            matchups_output.append(matchup_line)

    # Return the formatted matchups as a single string
    return '\n'.join(matchups_output)


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

    print(get_scoreboard())
    print(get_standings())
    print(get_monitor())
    print(get_matchups())