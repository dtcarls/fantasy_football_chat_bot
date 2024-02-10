from sleeper_ff_bot import bot
import pytest

def test_get_matchups_string():
    """
    Tests the get_matchups method
    :return:
    """
    matchups_string = bot.get_matchups_string(442724598706860032)
    print(matchups_string)
    assert isinstance(matchups_string, str)

def test_get_scores():
    scores_string = bot.get_scores_string(442724598706860032)
    print(scores_string)
    assert isinstance(scores_string, str)

def test_get_standings():
    """
    Tests the get_standings method
    :return:
    """
    standings_string = bot.get_standings_string(442724598706860032)
    print(standings_string)
    assert isinstance(standings_string, str)

@pytest.mark.skip(reason="no way of currently testing this. Should be easier next season")
def test_get_close_games():
    """
    Tests the get_close_games method
    :return:
    """
    close_game_string = bot.get_close_games_string(355526480094113792, 20)
    assert isinstance(close_game_string, str)

@pytest.mark.skip(reason="no way of currently testing this. Should be easier next season")
def test_get_highest_score():
    """
    Tests the get_highest_score method
    :return:
    """
    high_score_list = bot.get_highest_score(355526480094113792)
    assert isinstance(high_score_list, list)
    assert isinstance(high_score_list[0], float)
    assert isinstance(high_score_list[1], str)

def test_get_best_and_worst():
    best_and_worst = bot.get_best_and_worst_string(442724598706860032)
    print(best_and_worst)
def test_get_current_week():
    """
    Tests the get_current_week method
    :return:
    """
    current_week = bot.get_current_week()
    assert current_week > 0
    assert current_week < 16
