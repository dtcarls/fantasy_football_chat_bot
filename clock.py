from apscheduler.schedulers.blocking import BlockingScheduler
import ff_bot

sched = BlockingScheduler()

@sched.scheduled_job(bot_main("get_scoreboard_short"),'interval', seconds=30)
print('hi')

sched.start()
