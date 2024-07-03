import time
import os
from gamedaybot.chat.groupme import GroupMe
from gamedaybot.chat.slack import Slack
from gamedaybot.chat.discord import Discord
from sleeper_wrapper import League, Stats, Players


def get_league_scoreboards(league_id, week):
    """
    Fetches scoreboards for a specific week from a Sleeper fantasy football league.

    This function retrieves the scoreboard information for a given week from a specified Sleeper fantasy football league.
    It returns a detailed breakdown of the matchups, including scores and other relevant game data, formatted as a dictionary.

    Parameters
    ----------
    league_id : int
        The unique identifier of the Sleeper fantasy football league.
    week : int
        The specific week of the fantasy football season for which to retrieve the scoreboard.

    Returns
    -------
    dict
        A dictionary containing detailed information about each matchup for the specified week. The structure and content
        of the returned data are documented in the Sleeper API Wrapper documentation.

    See Also
    --------
    https://github.com/SwapnikKatkoori/sleeper-api-wrapper#get_scoreboards
        Documentation for the `get_scoreboards` method in the Sleeper API Wrapper GitHub repository, which outlines the
        structure of the returned dictionary.
    """
    league = League(league_id)
    matchups = league.get_matchups(week)
    users = league.get_users()
    rosters = league.get_rosters()
    scoreboards = league.get_scoreboards(rosters, matchups, users, "pts_half_ppr", week)
    return scoreboards


def get_highest_score(league_id):
    """
    Retrieves the highest score and the corresponding team name for a specified week in a fantasy football league.

    This function analyzes the scores for all matchups in a given week within a specified fantasy football league. It then identifies the highest score achieved and returns both the score and the name of the team that achieved it.

    Parameters
    ----------
    league_id : int
        The unique identifier for the fantasy football league from which to retrieve the highest score.

    Returns
    -------
    list
        A list containing the highest score of the week and the name of the team that achieved it. The first element is the
        score (float or int) and the second element is the team name (str).

    Example
    -------
    >>> get_highest_score_of_the_week(123456)
    [142.76, "Team Awesome"]

    Note
    ----
    The implementation of this function would depend on the ability to interact with the specific fantasy football
    platform's API to retrieve matchup and scoring data.
    """
    week = get_current_week()
    scoreboards = get_league_scoreboards(league_id, week)
    max_score = [0, None]

    for matchup_id in scoreboards:
        matchup = scoreboards[matchup_id]
        # check both teams in the matchup to see if they have the highest score in the league
        if float(matchup[0][1]) > max_score[0]:
            score = matchup[0][1]
            team_name = matchup[0][0]
            max_score[0] = score
            max_score[1] = team_name
        if float(matchup[1][1]) > max_score[0]:
            score = matchup[1][1]
            team_name = matchup[1][0]
            max_score[0] = score
            max_score[1] = team_name
    return max_score


def get_lowest_score(league_id):
    """
    Retrieves the lowest score and the corresponding team name for a specified week in a fantasy football league.

    This function searches through all the matchups in a given week within the specified fantasy football league to identify
    the lowest score recorded. It returns the lowest score along with the name of the team that scored it.

    Parameters
    ----------
    league_id : int
        The identifier for the fantasy football league from which to retrieve the lowest score.

    Returns
    -------
    list
        A list containing two elements: the lowest score of the week (as a float or int) and the name of the team that
        achieved it (as a string).

    Example
    -------
    >>> get_lowest_score_of_the_week(7891011)
    [85.34, "Underperformers"]

    Note
    ----
    This function requires access to the fantasy football league's scoring data, typically available through the league's
    API or data interface. Implementation details will vary based on the specific platform and data access methods available.
    """
    week = get_current_week()
    scoreboards = get_league_scoreboards(league_id, week)
    min_score = [999, None]

    for matchup_id in scoreboards:
        matchup = scoreboards[matchup_id]
        # check both teams in the matchup to see if they have the lowest score in the league
        if float(matchup[0][1]) < min_score[0]:
            score = matchup[0][1]
            team_name = matchup[0][0]
            min_score[0] = score
            min_score[1] = team_name
        if float(matchup[1][1]) < min_score[0]:
            score = matchup[1][1]
            team_name = matchup[1][0]
            min_score[0] = score
            min_score[1] = team_name
    return min_score


def make_roster_dict(starters_list, bench_list):
    """
    Organizes the players from a team's starters and bench into a dictionary categorized by their positions.

    This function takes two lists: one containing the starters of a fantasy football team and another containing the players
    on the bench. It organizes these players into a dictionary, where each player is categorized under their respective
    positions in either the starters or the bench sub-dictionary.

    Parameters
    ----------
    starters_list : list
        A list containing the starting players of a team. Each player is assumed to have identifiable position information.
    bench_list : list
        A list containing the bench players of a team. Similar to starters, each player should have position information.

    Returns
    -------
    dict
        A nested dictionary with two keys: 'starters' and 'bench'. Each of these keys maps to a dictionary where the keys
        are player positions and the values are lists of players occupying those positions in the starters or bench lists.

    Example
    -------
    >>> starters_list = [{"name": "Player A", "position": "QB"}, {"name": "Player B", "position": "RB"}]
    >>> bench_list = [{"name": "Player C", "position": "WR"}, {"name": "Player D", "position": "TE"}]
    >>> organize_team_by_position(starters_list, bench_list)
    {
        'starters': {'QB': ["Player A"], 'RB': ["Player B"]},
        'bench': {'WR': ["Player C"], 'TE': ["Player D"]}
    }

    Note
    ----
    The function assumes that each player in the starters and bench lists is represented as a dictionary with at least 'name'
    and 'position' keys. Adjustments may be needed based on the actual structure of player data.
    """
    week = get_current_week()
    players = Players().get_all_players()
    stats = Stats()
    week_stats = stats.get_week_stats("regular", STARTING_YEAR, week)

    roster_dict = {"starters": {}, "bench": {}}
    for player_id in starters_list:
        player = players[player_id]
        player_position = player["position"]
        player_name = player["first_name"] + " " + player["last_name"]
        try:
            player_std_score = week_stats[player_id]["pts_std"]
        except KeyError:
            player_std_score = None

        player_and_score_tup = (player_name, player_std_score)
        if player_position not in roster_dict["starters"]:
            roster_dict["starters"][player_position] = [player_and_score_tup]
        else:
            roster_dict["starters"][player_position].append(player_and_score_tup)

    for player_id in bench_list:
        player = players[player_id]
        player_position = player["position"]
        player_name = player["first_name"] + " " + player["last_name"]

        try:
            player_std_score = week_stats[player_id]["pts_std"]
        except KeyError:
            player_std_score = None

        player_and_score_tup = (player_name, player_std_score)
        if player_position not in roster_dict["bench"]:
            roster_dict["bench"][player_position] = [player_and_score_tup]
        else:
            roster_dict["bench"][player_position].append(player_and_score_tup)

    return roster_dict


def get_highest_bench_points(bench_points):
    """
    Finds the team with the highest scoring bench from a list of bench scores.

    This function processes a list of tuples, where each tuple contains a team's name and the standard points (std_points)
    scored by their bench players. It identifies the team with the highest scoring bench based on the standard points and
    returns the name of the team along with the points they scored.

    Parameters
    ----------
    bench_points : list
        A list of tuples, with each tuple containing a team's name and the standard points scored by their bench. The
        structure is [(team_name, std_points)].

    Returns
    -------
    tuple
        A tuple containing the name of the team with the highest scoring bench and the number of standard points they
        scored. The structure is (team_name, std_points).

    Example
    -------
    >>> bench_points = [("Team A", 150.5), ("Team B", 175.3), ("Team C", 140.2)]
    >>> find_highest_scoring_bench(bench_points)
    ("Team B", 175.3)

    Note
    ----
    This function assumes that all input points are valid and that there are no ties for the highest scoring bench.
    Adaptations may be needed for handling edge cases, such as multiple teams scoring equally high bench points.
    """

    max_tup = ("team_name", 0)
    for tup in bench_points:
        if tup[1] > max_tup[1]:
            max_tup = tup
    return max_tup


def map_users_to_team_name(users):
    """
    Creates a mapping of user IDs to team names in a Sleeper fantasy football league.

    This function constructs a dictionary where the keys are user IDs and the values are the corresponding team names. This
    mapping is useful for associating various actions or statistics with the correct teams in a league, especially when
    interacting with the Sleeper API, which often references users by their IDs.

    Parameters
    ----------
    users : list
        A list of user dictionaries as returned by the Sleeper API when querying for league users. Each dictionary contains
        information about a user, including their user ID and associated team name.

    Returns
    -------
    dict
        A dictionary where each key is a user ID (as a string or integer) and each value is the corresponding team name
        (as a string). This enables quick lookup of team names based on user ID.

    Example
    -------
    Assuming `users` is a list of dictionaries, each containing at least 'user_id' and 'metadata' with a 'team_name' key:
    >>> users = [
            {"user_id": "123", "metadata": {"team_name": "The Rushers"}},
            {"user_id": "456", "metadata": {"team_name": "Field Warriors"}}
        ]
    >>> map_user_id_to_team_name(users)
    {"123": "The Rushers", "456": "Field Warriors"}

    Note
    ----
    The structure of the input `users` list should match the format returned by the Sleeper API endpoint for getting users
    in a league, as described in their documentation. Adjustments may be necessary if the data format changes.

    See Also
    --------
    https://docs.sleeper.app/#getting-users-in-a-league
        Sleeper API documentation for retrieving users in a league, detailing the expected structure of user information.
    """
    users_dict = {}

    # Maps the user_id to team name for easy lookup
    for user in users:
        try:
            users_dict[user["user_id"]] = user["metadata"]["team_name"]
        except:
            users_dict[user["user_id"]] = user["display_name"]
    return users_dict


def map_roster_id_to_owner_id(league_id):
    """
    Creates a mapping from roster IDs to owner IDs in a given fantasy football league.

    This function initializes a league object using the provided league ID, retrieves all rosters within the league,
    and then iterates through these rosters to map each roster's ID to its owner's ID. The result is a dictionary
    where keys are roster IDs and values are the corresponding owner IDs.

    Parameters
    ----------
    league_id : int
        The unique identifier of the fantasy football league.

    Returns
    -------
    dict
        A dictionary where each key is a roster ID (int) and each value is the corresponding owner ID (int). This
        mapping facilitates easy identification of roster ownership within the league.

    Example
    -------
    Assuming a league with the ID 1234567, where rosters and owners are predefined:

    >>> map_roster_id_to_owner_id(1234567)
    {1: 'owner_id_1', 2: 'owner_id_2', ...}

    Note
    ----
    This function depends on the `League` class and its `get_rosters` method from a fantasy football league module
    or API wrapper. The exact implementation details and the availability of these components may vary depending
    on the specific fantasy football platform and its API or SDK.
    """
    league = League(league_id)
    rosters = league.get_rosters()
    result_dict = {}
    for roster in rosters:
        roster_id = roster["roster_id"]
        owner_id = roster["owner_id"]
        result_dict[roster_id] = owner_id

    return result_dict



def get_bench_points(league_id):
    """
    Retrieves the scores for all teams in a given fantasy football league for the current week.

    This function connects to a fantasy football league using the provided league_id, collects the current week's
    scores for all teams, and returns a list of tuples. Each tuple contains a team's name and its score for the
    week.

    Parameters
    ----------
    league_id : int
        The unique identifier for the fantasy football league from which to retrieve the scores.

    Returns
    -------
    list
        A list of tuples, where each tuple contains a team's name (str) and its score (float or int) for the
        current week. The list represents all teams in the league.

    Example
    -------
    >>> get_team_scores(123456)
    [('Team A', 142.3), ('Team B', 130.5), ...]

    Note
    ----
    The implementation details of this function depend on the fantasy football platform being used and its API.
    You will need to adapt the function to fit the specific API calls and data structure used by your platform.
    """
    week = get_current_week()

    league = League(league_id)
    users = league.get_users()
    matchups = league.get_matchups(week)

    stats = Stats()
    # WEEK STATS NEED TO BE FIXED
    week_stats = stats.get_week_stats("regular", STARTING_YEAR, week)

    owner_id_to_team_dict = map_users_to_team_name(users)
    roster_id_to_owner_id_dict = map_roster_id_to_owner_id(league_id)
    result_list = []

    for matchup in matchups:
        starters = matchup["starters"]
        all_players = matchup["players"]
        bench = set(all_players) - set(starters)

        std_points = 0
        for player in bench:
            try:
                std_points += week_stats[str(player)]["pts_std"]
            except:
                continue
        owner_id = roster_id_to_owner_id_dict[matchup["roster_id"]]
        if owner_id is None:
            team_name = "Team name not available"
        else:
            team_name = owner_id_to_team_dict[owner_id]
        result_list.append((team_name, std_points))

    return result_list


def get_negative_starters(league_id):
    """
    Finds all of the players that scores negative points in standard and
    :param league_id: Int league_id
    :return: Dict {"owner_name":[("player_name", std_score), ...], "owner_name":...}
    """
    week = get_current_week()

    league = League(league_id)
    users = league.get_users()
    matchups = league.get_matchups(week)

    stats = Stats()
    # WEEK STATS NEED TO BE FIXED
    week_stats = stats.get_week_stats("regular", STARTING_YEAR, week)

    players = Players()
    players_dict = players.get_all_players()
    owner_id_to_team_dict = map_users_to_team_name(users)
    roster_id_to_owner_id_dict = map_roster_id_to_owner_id(league_id)

    result_dict = {}

    for i, matchup in enumerate(matchups):
        starters = matchup["starters"]
        negative_players = []
        for starter_id in starters:
            try:
                std_pts = week_stats[str(starter_id)]["pts_std"]
            except KeyError:
                std_pts = 0
            if std_pts < 0:
                player_info = players_dict[starter_id]
                player_name = "{} {}".format(player_info["first_name"], player_info["last_name"])
                negative_players.append((player_name, std_pts))

        if len(negative_players) > 0:
            owner_id = roster_id_to_owner_id_dict[matchup["roster_id"]]

            if owner_id is None:
                team_name = "Team name not available" + str(i)
            else:
                team_name = owner_id_to_team_dict[owner_id]
            result_dict[team_name] = negative_players
    return result_dict


def check_starters_and_bench(lineup_dict):
    """

    :param lineup_dict: A dict returned by make_roster_dict
    :return:
    """
    for key in lineup_dict:
        pass


def get_current_week():
    """
    Gets the current week.
    :return: Int current week
    """
    today = pendulum.today()
    starting_week = pendulum.datetime(STARTING_YEAR, STARTING_MONTH, STARTING_DAY)
    week = today.diff(starting_week).in_weeks()
    return week + 1


"""
These are all of the functions that create the final strings to send.
"""


def get_welcome_string():
    """
    Creates and returns the welcome message
    :return: String welcome message
    """
    welcome_message = "👋 Hello, I am Sleeper Bot! \n\nThe bot schedule for the {} ff season can be found here: ".format(
        STARTING_YEAR)
    welcome_message += "https://github.com/SwapnikKatkoori/sleeper-ff-bot#current-schedule \n\n"
    welcome_message += "Any feature requests, contributions, or issues for the bot can be added here: " \
                       "https://github.com/SwapnikKatkoori/sleeper-ff-bot \n\n"

    return welcome_message


def send_any_string(string_to_send):
    """
    Send any string to the bot.
    :param string_to_send: The string to send a bot
    :return: string to send
    """
    return string_to_send


def get_matchups_string(league_id):
    """
    Creates and returns a message of the current week's matchups.
    :param league_id: Int league_id
    :return: string message of the current week mathchups.
    """
    week = get_current_week()
    scoreboards = get_league_scoreboards(league_id, week)
    final_message_string = "________________________________\n"
    final_message_string += "Matchups for Week {}:\n".format(week)
    final_message_string += "________________________________\n\n"

    for i, matchup_id in enumerate(scoreboards):
        matchup = scoreboards[matchup_id]
        matchup_string = "Matchup {}:\n".format(i + 1)
        matchup_string += "{} VS. {} \n\n".format(matchup[0][0], matchup[1][0])
        final_message_string += matchup_string

    return final_message_string


def get_playoff_bracket_string(league_id):
    """
    Creates and returns a message of the league's playoff bracket.
    :param league_id: Int league_id
    :return: string message league's playoff bracket
    """
    league = League(league_id)
    bracket = league.get_playoff_winners_bracket()
    return bracket


def get_scores_string(league_id):
    """
    Creates and returns a message of the league's current scores for the current week.
    :param league_id: Int league_id
    :return: string message of the current week's scores
    """
    week = get_current_week()
    scoreboards = get_league_scoreboards(league_id, week)
    final_message_string = "Scores \n____________________\n\n"
    for i, matchup_id in enumerate(scoreboards):
        matchup = scoreboards[matchup_id]
        print(matchup)
        first_score = 0
        second_score = 0
        if matchup[0][1] is not None:
            first_score = matchup[0][1]
        if matchup[1][1] is not None:
            second_score = matchup[1][1]
        string_to_add = "Matchup {}\n{:<8} {:<8.2f}\n{:<8} {:<8.2f}\n\n".format(i + 1, matchup[0][0], first_score,
                                                                                matchup[1][0], second_score)
        final_message_string += string_to_add

    return final_message_string


def get_close_games_string(league_id, close_num):
    """
    Creates and returns a message of the league's close games.
    :param league_id: Int league_id
    :param close_num: Int what poInt difference is considered a close game.
    :return: string message of the current week's close games.
    """
    league = League(league_id)
    week = get_current_week()
    scoreboards = get_league_scoreboards(league_id, week)
    close_games = league.get_close_games(scoreboards, close_num)

    final_message_string = "___________________\n"
    final_message_string += "Close games😰😰\n"
    final_message_string += "___________________\n\n"

    for i, matchup_id in enumerate(close_games):
        matchup = close_games[matchup_id]
        print(matchup)
        string_to_add = "Matchup {}\n{:<8} {:<8.2f}\n{:<8} {:<8.2f}\n\n".format(i + 1, matchup[0][0], matchup[0][1],
                                                                                matchup[1][0], matchup[1][1])
        final_message_string += string_to_add
    return final_message_string


def get_standings_string(league_id):
    """
    Creates and returns a message of the league's standings.
    :param league_id: Int league_id
    :return: string message of the leagues standings.
    """
    league = League(league_id)
    rosters = league.get_rosters()
    users = league.get_users()
    standings = league.get_standings(rosters, users)
    final_message_string = "________________________________\n"
    final_message_string += "Standings \n|{0:^7}|{1:^7}|{2:^7}|{3:^7}\n".format("rank", "team", "wins", "points")
    final_message_string += "________________________________\n\n"
    try:
        playoff_line = os.environ["NUMBER_OF_PLAYOFF_TEAMS"] - 1
    except:
        playoff_line = 5
    for i, standing in enumerate(standings):
        team = standing[0]
        if team is None:
            team = "Team NA"
        if len(team) >= 7:
            team_name = team[:7]
        else:
            team_name = team
        string_to_add = "{0:^7} {1:^10} {2:>7} {3:>7}\n".format(i + 1, team_name, standing[1], standing[3])
        if i == playoff_line:
            string_to_add += "________________________________\n\n"
        final_message_string += string_to_add
    return final_message_string


def get_best_and_worst_string(league_id):
    """
    :param league_id: Int league_id
    :return: String of the highest Scorer, lowest scorer, most points left on the bench, and Why bother section.
    """
    highest_scorer = get_highest_score(league_id)[1]
    highest_score = get_highest_score(league_id)[0]
    highest_score_emojis = "🏆🏆"
    lowest_scorer = get_lowest_score(league_id)[1]
    lowest_score = get_lowest_score(league_id)[0]
    lowest_score_emojis = "😢😢"
    final_string = "{} Highest Scorer:\n{}\n{:.2f}\n\n{} Lowest Scorer:\n {}\n{:.2f}\n\n".format(highest_score_emojis,
                                                                                                 highest_scorer,
                                                                                                 highest_score,
                                                                                                 lowest_score_emojis,
                                                                                                 lowest_scorer,
                                                                                                 lowest_score)
    highest_bench_score_emojis = " 😂😂"
    bench_points = get_bench_points(league_id)
    largest_scoring_bench = get_highest_bench_points(bench_points)
    final_string += "{} Most points left on the bench:\n{}\n{:.2f} in standard\n\n".format(highest_bench_score_emojis,
                                                                                           largest_scoring_bench[0],
                                                                                           largest_scoring_bench[1])
    negative_starters = get_negative_starters(league_id)
    if negative_starters:
        final_string += "🤔🤔Why bother?\n"

    for key in negative_starters:
        negative_starters_list = negative_starters[key]
        final_string += "{} Started:\n".format(key)
        for negative_starter_tup in negative_starters_list:
            final_string += "{} who had {} in standard\n".format(negative_starter_tup[0], negative_starter_tup[1])
        final_string += "\n"
    return final_string


def get_bench_beats_starters_string(league_id):
    """
    Gets all bench players that outscored starters at their position.
    :param league_id: Int league_id
    :return: String teams which had bench players outscore their starters in a position.
    """
    week = get_current_week()
    league = League(league_id)
    matchups = league.get_matchups(week)

    final_message_string = "________________________________\n"
    final_message_string += "Worst of the week💩💩\n"
    final_message_string += "________________________________\n\n"

    for matchup in matchups:
        starters = matchup["starters"]
        all_players = matchup["players"]
        bench = set(all_players) - set(starters)


if __name__ == "__main__":
    """
    Main script for the bot
    """
    bot = None

    bot_type = os.environ["BOT_TYPE"]
    league_id = os.environ["LEAGUE_ID"]

    # Check if the user specified the close game num. Default is 20.
    try:
        close_num = os.environ["CLOSE_NUM"]
    except:
        close_num = 20

    starting_date = pendulum.datetime(STARTING_YEAR, STARTING_MONTH, STARTING_DAY)

    if bot_type == "groupme":
        bot_id = os.environ["BOT_ID"]
        bot = GroupMe(bot_id)
    elif bot_type == "slack":
        webhook = os.environ["SLACK_WEBHOOK"]
        bot = Slack(webhook)
    elif bot_type == "discord":
        webhook = os.environ["DISCORD_WEBHOOK"]
        bot = Discord(webhook)

    bot.send(get_welcome_string)  # inital message to send
    schedule.every().thursday.at("19:00").do(bot.send, get_matchups_string,
                                             league_id)  # Matchups Thursday at 4:00 pm ET
    schedule.every().friday.at("12:00").do(bot.send, get_scores_string, league_id)  # Scores Friday at 12 pm ET
    schedule.every().sunday.at("23:00").do(bot.send, get_close_games_string, league_id,
                                           int(close_num))  # Close games Sunday on 7:00 pm ET
    schedule.every().monday.at("12:00").do(bot.send, get_scores_string, league_id)  # Scores Monday at 12 pm ET
    schedule.every().tuesday.at("15:00").do(bot.send, get_standings_string,
                                            league_id)  # Standings Tuesday at 11:00 am ET
    schedule.every().tuesday.at("15:01").do(bot.send, get_best_and_worst_string,
                                            league_id)  # Standings Tuesday at 11:01 am ET

    while True:
        if starting_date <= pendulum.today():
            schedule.run_pending()
        time.sleep(50)
