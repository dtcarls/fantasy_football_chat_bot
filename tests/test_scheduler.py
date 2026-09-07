import sys
import os
import pytest
sys.path.insert(1, os.path.abspath('.'))

from apscheduler.schedulers.blocking import BlockingScheduler
import gamedaybot.espn.scheduler as scheduler_module


@pytest.fixture
def jobs(monkeypatch):
    """Build the schedule without starting it, and return {job id: job}.

    scheduler() ends in sched.start(), which blocks forever, so start is
    stubbed out. get_env_vars() insists on a league and at least one chat
    destination, so both are supplied here rather than relying on the
    environment the tests happen to run in.
    """
    monkeypatch.setenv('LEAGUE_ID', '1234567')
    monkeypatch.setenv('BOT_ID', 'x' * 20)
    monkeypatch.setattr(BlockingScheduler, 'start', lambda self, *a, **kw: None)

    built = {}
    real_add_job = BlockingScheduler.add_job

    def capture(self, func, trigger=None, args=None, **kwargs):
        job = real_add_job(self, func, trigger, args, **kwargs)
        built[kwargs.get('id')] = job
        return job

    monkeypatch.setattr(BlockingScheduler, 'add_job', capture)

    def build():
        built.clear()
        scheduler_module.scheduler()
        return built

    return build


def day_of_week(job):
    """Pull the day_of_week field out of an APScheduler CronTrigger."""
    for field in job.trigger.fields:
        if field.name == 'day_of_week':
            return str(field)
    raise AssertionError('trigger has no day_of_week field')


class TestWaiverSchedule:
    ############ For the DAILY_WAIVER schedule
    # Default: Wednesday only
    def test_waiver_defaults_to_wednesday(self, jobs, monkeypatch):
        monkeypatch.delenv('DAILY_WAIVER', raising=False)
        assert day_of_week(jobs()['waiver_report']) == 'wed'

    # DAILY_WAIVER must ADD days, never trade Wednesday away. The two add_job
    # calls this replaced shared an id, so the daily one replaced the weekly
    # one and dropped Wednesday -- the day ESPN processes waivers.
    def test_daily_waiver_includes_wednesday(self, jobs, monkeypatch):
        monkeypatch.setenv('DAILY_WAIVER', 'True')
        assert 'wed' in day_of_week(jobs()['waiver_report']) or \
            day_of_week(jobs()['waiver_report']) == '*'

    def test_daily_waiver_runs_every_day(self, jobs, monkeypatch):
        monkeypatch.setenv('DAILY_WAIVER', 'True')
        job = jobs()['waiver_report']
        # A CronTrigger's day_of_week field enumerates the weekdays it matches.
        assert len(list(job.trigger.fields[4].expressions)) == 1
        assert day_of_week(job) == '*'

    # Only ever one waiver job, whichever way the flag is set
    def test_single_waiver_job_when_daily(self, jobs, monkeypatch):
        monkeypatch.setenv('DAILY_WAIVER', 'True')
        assert len([jid for jid in jobs() if 'waiver' in jid]) == 1

    def test_single_waiver_job_when_weekly(self, jobs, monkeypatch):
        monkeypatch.delenv('DAILY_WAIVER', raising=False)
        assert len([jid for jid in jobs() if 'waiver' in jid]) == 1


class TestScheduleShape:
    ############ The rest of the schedule, so a change here is deliberate
    def test_expected_jobs_are_registered(self, jobs, monkeypatch):
        monkeypatch.delenv('DAILY_WAIVER', raising=False)
        monkeypatch.delenv('MONITOR_REPORT', raising=False)
        assert set(jobs()) == {
            'close_scores', 'power_rankings', 'final', 'standings',
            'waiver_report', 'matchups', 'scoreboard1', 'monitor', 'scoreboard2',
        }

    def test_monitor_report_can_be_disabled(self, jobs, monkeypatch):
        monkeypatch.setenv('MONITOR_REPORT', 'False')
        assert 'monitor' not in jobs()

    @pytest.mark.parametrize('job_id,expected_day', [
        ('close_scores', 'mon'),
        ('power_rankings', 'tue'),
        ('final', 'tue'),
        ('standings', 'wed'),
        ('matchups', 'thu'),
        ('monitor', 'sun'),
        ('scoreboard2', 'sun'),
    ])
    def test_job_days(self, jobs, monkeypatch, job_id, expected_day):
        monkeypatch.delenv('DAILY_WAIVER', raising=False)
        assert day_of_week(jobs()[job_id]) == expected_day
