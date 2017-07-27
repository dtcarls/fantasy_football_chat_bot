from apscheduler.schedulers.blocking import BlockingScheduler
import ff_bot

sched = BlockingScheduler()

@sched.scheduled_job(bot_main("get_scoreboard_short"),'interval', seconds=30)


"""@sched.scheduled_job('cron', day_of_week='mon-fri', hour=17)
def scheduled_job():
    print('This job is run every weekday at 5pm.')"""
try:
    sched.start()
