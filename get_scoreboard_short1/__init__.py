import azure.functions as func
from ..fantasy_football_bot import fantasy_football_bot

"""
This file is a wrapper to allow Azure Functions to call bot_main
It appears you cannot pass a static variable to the function
method, so this shim is an easy solution
"""

def main(getScoreboardShort1: func.TimerRequest) -> None:
    fantasy_football_bot.bot_main("get_scoreboard_short")