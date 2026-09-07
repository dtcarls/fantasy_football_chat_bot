import sys
import os
sys.path.insert(1, os.path.abspath('.'))
import gamedaybot.espn.functionality as espn


class FakePlayer:
    """Stands in for an espn_api BoxPlayer.

    Defaults describe a healthy, playing starter, so each test only sets the
    one attribute it is about. Note game_played defaults to 0 (pre-game);
    espn_api leaves it at 100 for a player on a bye, which the bye tests set
    explicitly because that is what makes the bye branch necessary.
    """

    def __init__(self, position='WR', name='Player', slot_position='WR',
                 injuryStatus='ACTIVE', game_played=0, on_bye_week=False,
                 projected_points=10.0, points=0.0):
        self.position = position
        self.name = name
        self.slot_position = slot_position
        self.injuryStatus = injuryStatus
        self.game_played = game_played
        self.on_bye_week = on_bye_week
        self.projected_points = projected_points
        self.points = points


class FakeTeam:
    def __init__(self, team_name='Test Team'):
        self.team_name = team_name


def flagged(lineup, team_name='Test Team'):
    """Return scan_roster's player lines, without the team-name header.

    Lines are right-stripped: scan_roster's format string puts a trailing
    space on the last line, which is not what these tests are about.
    """
    report = espn.scan_roster(lineup, FakeTeam(team_name))
    if not report:
        return []
    return [line.rstrip() for line in report[0].splitlines()[1:] if line.strip()]


class TestScanRoster:
    ############ For `scan_roster`
    # A healthy, playing starter is never flagged
    def test_scan_roster_healthy_starter_not_flagged(self):
        assert flagged([FakePlayer(name='Healthy')]) == []

    def test_scan_roster_clean_lineup_returns_empty(self):
        assert espn.scan_roster([FakePlayer(name='Healthy')], FakeTeam()) == ''

    # Injury statuses
    def test_scan_roster_flags_questionable(self):
        assert flagged([FakePlayer(position='QB', name='Hurt', injuryStatus='QUESTIONABLE')]) == \
            ['QB Hurt - Questionable']

    def test_scan_roster_underscored_status_is_titled(self):
        assert flagged([FakePlayer(position='RB', name='Doubt', injuryStatus='INJURY_RESERVE')]) == \
            ['RB Doubt - Injury Reserve']

    def test_scan_roster_normal_status_not_flagged(self):
        assert flagged([FakePlayer(injuryStatus='NORMAL')]) == []

    # A player whose game has started is not flagged for injury any more
    def test_scan_roster_injury_ignored_once_game_started(self):
        assert flagged([FakePlayer(injuryStatus='QUESTIONABLE', game_played=100)]) == []

    # Bye weeks -- espn_api reports game_played 100 for these
    def test_scan_roster_flags_bye_starter(self):
        assert flagged([FakePlayer(position='TE', name='Bye Guy', on_bye_week=True, game_played=100)]) == \
            ['TE Bye Guy - BYE']

    def test_scan_roster_bye_flagged_even_though_game_played_is_100(self):
        # This is the whole reason the bye branch cannot be folded into the
        # other two, both of which require game_played == 0.
        player = FakePlayer(name='Bye Guy', on_bye_week=True, game_played=100)
        assert flagged([player]) == ['WR Bye Guy - BYE']

    # Zero projection
    def test_scan_roster_flags_zero_projection(self):
        assert flagged([FakePlayer(position='K', name='Zero', projected_points=0)]) == \
            ['K Zero - Projected 0']

    def test_scan_roster_zero_projection_ignored_once_game_started(self):
        assert flagged([FakePlayer(projected_points=0, game_played=100)]) == []

    # One line per player: the highest-priority reason wins
    def test_scan_roster_injury_beats_bye(self):
        assert flagged([FakePlayer(name='Both', injuryStatus='DOUBTFUL', on_bye_week=True)]) == \
            ['WR Both - Doubtful']

    def test_scan_roster_bye_beats_zero_projection(self):
        assert flagged([FakePlayer(name='Both', on_bye_week=True, game_played=100, projected_points=0)]) == \
            ['WR Both - BYE']

    # Bench players are excluded whatever their status
    def test_scan_roster_bench_player_ignored(self):
        assert flagged([FakePlayer(slot_position='BE', injuryStatus='OUT')]) == []

    def test_scan_roster_bench_bye_ignored(self):
        assert flagged([FakePlayer(slot_position='BE', on_bye_week=True, game_played=100)]) == []

    # IR slots: only an ineligible player is reported
    def test_scan_roster_valid_ir_not_flagged(self):
        assert flagged([FakePlayer(slot_position='IR', injuryStatus='INJURY_RESERVE')]) == []

    def test_scan_roster_out_player_in_ir_not_flagged(self):
        assert flagged([FakePlayer(slot_position='IR', injuryStatus='OUT')]) == []

    def test_scan_roster_ineligible_ir_flagged(self):
        assert flagged([FakePlayer(position='RB', name='Back', slot_position='IR')]) == \
            ['RB Back - Not IR eligible']

    # The report is headed with the team name
    def test_scan_roster_header_is_team_name(self):
        report = espn.scan_roster([FakePlayer(injuryStatus='OUT')], FakeTeam('Some Team'))
        assert report[0].splitlines()[0] == 'Some Team: '

    # Several flagged players come back in lineup order
    def test_scan_roster_multiple_players_in_order(self):
        lineup = [
            FakePlayer(position='QB', name='One', injuryStatus='OUT'),
            FakePlayer(position='TE', name='Two', on_bye_week=True, game_played=100),
            FakePlayer(position='K', name='Three', projected_points=0),
        ]
        assert flagged(lineup) == ['QB One - Out', 'TE Two - BYE', 'K Three - Projected 0']


class TestIsByeBox:
    ############ For `is_bye_box`
    class Box:
        def __init__(self, home_team=None, away_team=None):
            self.home_team = home_team
            self.away_team = away_team

    def test_is_bye_box_both_present(self):
        assert espn.is_bye_box(self.Box(home_team=FakeTeam(), away_team=FakeTeam())) == False

    def test_is_bye_box_missing_away_none(self):
        assert espn.is_bye_box(self.Box(home_team=FakeTeam(), away_team=None)) == True

    def test_is_bye_box_missing_home_none(self):
        assert espn.is_bye_box(self.Box(home_team=None, away_team=FakeTeam())) == True

    def test_is_bye_box_legacy_zero(self):
        # Older espn_api used 0 rather than None for the missing side.
        assert espn.is_bye_box(self.Box(home_team=FakeTeam(), away_team=0)) == True

    def test_is_bye_box_attribute_absent(self):
        # scoreboard() Matchup objects never assign the attribute at all.
        class Bare:
            pass
        assert espn.is_bye_box(Bare()) == True


class FakeBox:
    """Stands in for an espn_api BoxScore for the close-scores tests."""

    def __init__(self, home_abbrev, home_proj, away_abbrev, away_proj, played=False):
        self.home_team = FakeTeam(home_abbrev)
        self.away_team = FakeTeam(away_abbrev)
        self.home_team.team_abbrev = home_abbrev
        self.away_team.team_abbrev = away_abbrev
        # game_played 100 means the games are over, which excludes the matchup
        # from the report regardless of how close it is. A finished player's
        # actual points stand in for their projection in get_projected_total,
        # so they are set equal here -- the projected totals come out the same
        # either way and `played` changes nothing but all_played().
        gp = 100 if played else 0
        self.home_lineup = [FakePlayer(projected_points=home_proj, game_played=gp,
                                       points=home_proj if played else 0.0)]
        self.away_lineup = [FakePlayer(projected_points=away_proj, game_played=gp,
                                       points=away_proj if played else 0.0)]


class TestGetCloseScores:
    ############ For `get_close_scores`
    # The default threshold is the module constant
    def test_close_scores_default_threshold_is_constant(self):
        assert espn.CLOSE_SCORES_DEFAULT_THRESHOLD == 15

    def test_close_scores_includes_matchup_inside_default(self):
        boxes = [FakeBox('AAA', 100.0, 'BBB', 110.0)]  # 10 apart
        assert 'AAA' in espn.get_close_scores(None, box_scores=boxes)

    def test_close_scores_excludes_matchup_outside_default(self):
        boxes = [FakeBox('AAA', 100.0, 'BBB', 130.0)]  # 30 apart
        assert espn.get_close_scores(None, box_scores=boxes) == ''

    # An explicit threshold overrides the default, both directions
    def test_close_scores_wider_threshold_includes_more(self):
        boxes = [FakeBox('AAA', 100.0, 'BBB', 130.0)]  # 30 apart
        assert 'AAA' in espn.get_close_scores(None, box_scores=boxes, threshold=40)

    def test_close_scores_tighter_threshold_excludes(self):
        boxes = [FakeBox('AAA', 100.0, 'BBB', 110.0)]  # 10 apart
        assert espn.get_close_scores(None, box_scores=boxes, threshold=5) == ''

    # The threshold is inclusive
    def test_close_scores_exactly_at_threshold_included(self):
        boxes = [FakeBox('AAA', 100.0, 'BBB', 115.0)]  # exactly 15
        assert 'AAA' in espn.get_close_scores(None, box_scores=boxes, threshold=15)

    def test_close_scores_one_over_threshold_excluded(self):
        boxes = [FakeBox('AAA', 100.0, 'BBB', 115.01)]
        assert espn.get_close_scores(None, box_scores=boxes, threshold=15) == ''

    # Direction does not matter -- the margin is absolute
    def test_close_scores_home_ahead_also_counts(self):
        boxes = [FakeBox('AAA', 120.0, 'BBB', 110.0)]
        assert 'AAA' in espn.get_close_scores(None, box_scores=boxes)

    # A finished matchup is never reported, however close
    def test_close_scores_skips_completed_games(self):
        boxes = [FakeBox('AAA', 100.0, 'BBB', 101.0, played=True)]
        assert espn.get_close_scores(None, box_scores=boxes) == ''

    # Only the qualifying matchups appear
    def test_close_scores_filters_mixed_slate(self):
        boxes = [
            FakeBox('CLS', 100.0, 'OPP', 105.0),   # 5 apart, in
            FakeBox('FAR', 100.0, 'AWY', 150.0),   # 50 apart, out
        ]
        out = espn.get_close_scores(None, box_scores=boxes)
        assert 'CLS' in out and 'FAR' not in out

    def test_close_scores_header_present_when_any_match(self):
        boxes = [FakeBox('AAA', 100.0, 'BBB', 105.0)]
        assert espn.get_close_scores(None, box_scores=boxes).splitlines()[0] == 'Projected Close Scores'
