import azure.functions as func
from ..ff_bot import ff_bot

"""
This file is a wrapper to allow Azure Functions to call bot_main
It appears you cannot pass a static variable to the function
method, so this shim is an easy solution
"""

def main(getFinal: func.TimerRequest) -> None:
    ff_bot.bot_main("getFinal")