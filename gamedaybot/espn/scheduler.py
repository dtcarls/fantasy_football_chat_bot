from apscheduler.schedulers.blocking import BlockingScheduler
from gamedaybot.espn.espn_bot import espn_bot
from gamedaybot.espn.env_vars import get_env_vars


def scheduler():
    """
    Initialize and start the fantasy football bot scheduler.
    
    This function sets up all scheduled jobs for sending fantasy football messages
    throughout the week. The scheduler runs continuously and sends messages to 
    configured chat platforms (GroupMe, Slack, Discord) at predetermined times.
    
    Scheduled Jobs
    --------------
    - Monday 6:30 PM ET: Close scores (games within 16 points)
    - Tuesday 7:30 AM Local: Final scores and trophies from previous week
    - Tuesday 6:30 PM Local: Power rankings
    - Wednesday 7:30 AM Local: Current standings
    - Wednesday 7:31 AM Local: Waiver report (if enabled)
    - Thursday 7:30 PM ET: Upcoming matchups
    - Friday/Monday 7:30 AM Local: Scoreboard updates
    - Sunday 7:30 AM Local: Player monitor report (if enabled)
    - Sunday 4:00 PM & 8:00 PM ET: Live scoreboard updates
    
    Optional Jobs
    -------------
    - Daily waiver reports: Runs daily at 7:31 AM Local (if DAILY_WAIVER=True)
    - Player monitor: Sunday mornings (if MONITOR_REPORT=True)
    
    Environment Variables
    --------------------
    The scheduler uses environment variables loaded via get_env_vars():
    - START_DATE/END_DATE: Season date range
    - TIMEZONE: Local timezone for scheduling
    - DAILY_WAIVER: Enable daily waiver reports
    - MONITOR_REPORT: Enable player monitoring
    
    Notes
    -----
    - Uses blocking scheduler - this function will run indefinitely
    - Misfire grace time is set to 15 minutes
    - Game times use America/New_York timezone
    - Local times use the configured TIMEZONE
    
    Returns
    -------
    None
        This function runs indefinitely until interrupted
    """
    data = get_env_vars()
    game_timezone = 'America/New_York'
    sched = BlockingScheduler(job_defaults={'misfire_grace_time': 15 * 60})
    ff_start_date = data['ff_start_date']
    ff_end_date = data['ff_end_date']
    my_timezone = data['my_timezone']

    # close scores (within 15.99 points): monday evening at 6:30pm east coast time.
    # power rankings:                     tuesday evening at 6:30pm local time.
    # trophies:                           tuesday morning at 7:30am local time.
    # standings:                          wednesday morning at 7:30am local time.
    # waiver report:                      wednesday morning at 7:31am local time. (optional)
    # matchups:                           thursday evening at 7:30pm east coast time.
    # score update:                       friday, monday, and tuesday morning at 7:30am local time.
    # player monitor report:              sunday morning at 7:30am local time.
    # score update:                       sunday at 4pm, 8pm east coast time.

    sched.add_job(espn_bot, 'cron', ['get_close_scores'], id='close_scores',
                  day_of_week='mon', hour=18, minute=30, start_date=ff_start_date, end_date=ff_end_date,
                  timezone=game_timezone, replace_existing=True)
    sched.add_job(espn_bot, 'cron', ['get_power_rankings'], id='power_rankings',
                  day_of_week='tue', hour=18, minute=30, start_date=ff_start_date, end_date=ff_end_date,
                  timezone=my_timezone, replace_existing=True)
    sched.add_job(espn_bot, 'cron', ['get_final'], id='final',
                  day_of_week='tue', hour=7, minute=30, start_date=ff_start_date, end_date=ff_end_date,
                  timezone=my_timezone, replace_existing=True)
    sched.add_job(espn_bot, 'cron', ['get_standings'], id='standings',
                  day_of_week='wed', hour=7, minute=30, start_date=ff_start_date, end_date=ff_end_date,
                  timezone=my_timezone, replace_existing=True)
    sched.add_job(espn_bot, 'cron', ['get_waiver_report'], id='waiver_report',
                  day_of_week='wed', hour=7, minute=31, start_date=ff_start_date, end_date=ff_end_date,
                  timezone=my_timezone, replace_existing=True)

    if data['daily_waiver']:
        sched.add_job(
            espn_bot, 'cron', ['get_waiver_report'],
            id='waiver_report', day_of_week='mon, tue, thu, fri, sat, sun', hour=7, minute=31, start_date=ff_start_date,
            end_date=ff_end_date, timezone=my_timezone, replace_existing=True)

    sched.add_job(espn_bot, 'cron', ['get_matchups'], id='matchups',
                  day_of_week='thu', hour=19, minute=30, start_date=ff_start_date, end_date=ff_end_date,
                  timezone=game_timezone, replace_existing=True)
    sched.add_job(espn_bot, 'cron', ['get_scoreboard_short'], id='scoreboard1',
                  day_of_week='fri,mon', hour=7, minute=30, start_date=ff_start_date, end_date=ff_end_date,
                  timezone=my_timezone, replace_existing=True)

    if data['monitor_report']:
        sched.add_job(espn_bot, 'cron', ['get_monitor'], id='monitor',
                      day_of_week='sun', hour=7, minute=30, start_date=ff_start_date, end_date=ff_end_date,
                      timezone=my_timezone, replace_existing=True)

    sched.add_job(espn_bot, 'cron', ['get_scoreboard_short'], id='scoreboard2',
                  day_of_week='sun', hour='16,20', start_date=ff_start_date, end_date=ff_end_date,
                  timezone=game_timezone, replace_existing=True)

    print("Ready!")
    sched.start()
