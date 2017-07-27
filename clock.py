from apscheduler.schedulers.blocking import BlockingScheduler
#from ff_bot import bot_main
import ff_bot

sched = BlockingScheduler()

print('before')
sched.add_job(ff_bot.bot_main("get_scoreboard_short"),'interval', seconds=30)
print('after')

sched.start()
