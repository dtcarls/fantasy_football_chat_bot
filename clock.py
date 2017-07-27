from apscheduler.schedulers.blocking import BlockingScheduler
import ff_bot

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=1)
bot_main("get_scoreboard_short")

'''@sched.scheduled_job('cron', day_of_week='mon-fri', hour=17)
def scheduled_job():
    print('This job is run every weekday at 5pm.')'''

sched.start()
