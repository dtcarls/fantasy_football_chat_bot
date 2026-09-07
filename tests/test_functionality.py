from datetime import datetime
import sys
import os
sys.path.insert(1, os.path.abspath('.'))
import gamedaybot.espn.functionality as espn
import gamedaybot.utils.util as utils


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


class FakeItem:
    def __init__(self, type, playerId, player):
        self.type = type
        self.playerId = playerId
        self.player = player


class FakeTxn:
    """Stands in for an espn_api Transaction.

    date is a ms epoch, as ESPN sends it. bid_amount is always set as an
    attribute (espn_api does data.get('bidAmount')) but is None for a league
    that does not use FAAB -- which is the case the None handling is about.
    """

    def __init__(self, team_name, items, date_ms, status='EXECUTED', bid_amount=None):
        self.team = FakeTeam(team_name)
        self.items = items
        self.date = date_ms
        self.status = status
        self.bid_amount = bid_amount


class FakeLeague:
    """League stub exposing only what get_waiver_report touches."""

    def __init__(self, transactions, positions=None, raise_on_transactions=None):
        self.scoringPeriodId = 5
        self._transactions = transactions
        self._positions = positions or {}
        self._raise = raise_on_transactions
        self.player_info_calls = []

    def transactions(self, scoring_period, types=None):
        if self._raise is not None:
            raise self._raise
        return self._transactions

    def player_info(self, name=None, playerId=None):
        self.player_info_calls.append(playerId)
        found = []
        for pid in (playerId if isinstance(playerId, list) else [playerId]):
            if pid in self._positions:
                player = FakePlayer(position=self._positions[pid])
                player.playerId = pid
                found.append(player)
        if not found:
            return None
        return found if len(found) > 1 else found[0]


DAY_MS = int(datetime(2024, 9, 4, 12, 0).timestamp() * 1000)
DAY = '2024-09-04'
OTHER_DAY_MS = DAY_MS - 86400 * 1000
FAILED = 'FAILED_INVALIDPLAYERSOURCE'


class TestGetWaiverReport:
    ############ For `get_waiver_report`
    # A quiet waiver wire is normal, not an error. espn_api raises rather than
    # returning an empty list when a scoring period holds no transactions.
    def test_waiver_report_no_transactions_returns_empty(self):
        league = FakeLeague([], raise_on_transactions=Exception('No transactions found'))
        assert espn.get_waiver_report(league, test_date=DAY) == ''

    # Any other failure must still surface
    def test_waiver_report_other_exception_propagates(self):
        league = FakeLeague([], raise_on_transactions=Exception('401 Unauthorized'))
        try:
            espn.get_waiver_report(league, test_date=DAY)
        except Exception as exc:
            assert '401' in str(exc)
        else:
            raise AssertionError('expected the auth failure to propagate')

    # A non-FAAB league leaves bid_amount None; it must not render "$None"
    def test_waiver_report_none_bid_renders_zero(self):
        txn = FakeTxn('Team A', [FakeItem('ADD', 1, 'Player One')], DAY_MS, bid_amount=None)
        out = espn.get_waiver_report(FakeLeague([txn], {1: 'RB'}), faab=True, test_date=DAY)
        assert '$None' not in out
        assert '($0' in out

    # ... and must not crash the descending sort
    def test_waiver_report_none_bid_sorts(self):
        txns = [
            FakeTxn('Team A', [FakeItem('ADD', 1, 'One')], DAY_MS, bid_amount=None),
            FakeTxn('Team B', [FakeItem('ADD', 2, 'Two')], DAY_MS, bid_amount=12),
        ]
        out = espn.get_waiver_report(FakeLeague(txns, {1: 'RB', 2: 'WR'}), faab=True, test_date=DAY)
        assert out.index('Team B') < out.index('Team A')

    # An unresolvable player falls back to N/A rather than crashing
    def test_waiver_report_unresolved_position_is_na(self):
        txn = FakeTxn('Team A', [FakeItem('ADD', 99, 'Unknown')], DAY_MS, bid_amount=3)
        out = espn.get_waiver_report(FakeLeague([txn], {}), test_date=DAY)
        assert 'ADDED N/A - Unknown' in out

    # Positions are resolved in ONE batched call, not one per item
    def test_waiver_report_batches_player_lookups(self):
        items = [FakeItem('ADD', 1, 'One'), FakeItem('DROP', 2, 'Two'),
                 FakeItem('ADD', 3, 'Three'), FakeItem('DROP', 4, 'Four')]
        league = FakeLeague([FakeTxn('Team A', items, DAY_MS, bid_amount=5)],
                            {1: 'RB', 2: 'WR', 3: 'TE', 4: 'QB'})
        espn.get_waiver_report(league, test_date=DAY)
        assert len(league.player_info_calls) == 1
        assert sorted(league.player_info_calls[0]) == [1, 2, 3, 4]

    # Adds are listed before drops regardless of item order
    def test_waiver_report_adds_precede_drops(self):
        items = [FakeItem('DROP', 2, 'Dropped Guy'), FakeItem('ADD', 1, 'Added Guy')]
        league = FakeLeague([FakeTxn('Team A', items, DAY_MS, bid_amount=5)], {1: 'RB', 2: 'WR'})
        out = espn.get_waiver_report(league, test_date=DAY)
        assert out.index('ADDED') < out.index('DROPPED')

    # Only the report date's transactions are included
    def test_waiver_report_filters_by_date(self):
        txns = [FakeTxn('Today Team', [FakeItem('ADD', 1, 'One')], DAY_MS, bid_amount=1),
                FakeTxn('Yesterday Team', [FakeItem('ADD', 2, 'Two')], OTHER_DAY_MS, bid_amount=1)]
        out = espn.get_waiver_report(FakeLeague(txns, {1: 'RB', 2: 'WR'}), test_date=DAY)
        assert 'Today Team' in out and 'Yesterday Team' not in out

    # Only executed claims are reported as moves
    def test_waiver_report_skips_failed_claims(self):
        txns = [FakeTxn('Winner', [FakeItem('ADD', 1, 'One')], DAY_MS, bid_amount=10),
                FakeTxn('Loser', [FakeItem('ADD', 1, 'One')], DAY_MS, status=FAILED, bid_amount=9)]
        out = espn.get_waiver_report(FakeLeague(txns, {1: 'RB'}), test_date=DAY)
        assert 'Winner' in out
        assert 'Loser \n' not in out

    # The runner-up callout names a narrowly outbid rival
    def test_waiver_report_narrow_win_names_rival(self):
        txns = [FakeTxn('Winner', [FakeItem('ADD', 1, 'One')], DAY_MS, bid_amount=10),
                FakeTxn('Loser', [FakeItem('ADD', 1, 'One')], DAY_MS, status=FAILED, bid_amount=9)]
        out = espn.get_waiver_report(FakeLeague(txns, {1: 'RB'}), faab=True, test_date=DAY)
        assert 'Loser outbid by $1' in out

    def test_waiver_report_comfortable_win_reports_margin(self):
        txns = [FakeTxn('Winner', [FakeItem('ADD', 1, 'One')], DAY_MS, bid_amount=30),
                FakeTxn('Loser', [FakeItem('ADD', 1, 'One')], DAY_MS, status=FAILED, bid_amount=9)]
        out = espn.get_waiver_report(FakeLeague(txns, {1: 'RB'}), faab=True, test_date=DAY)
        assert 'won by $21' in out

    def test_waiver_report_tied_bid_reports_tie(self):
        txns = [FakeTxn('Winner', [FakeItem('ADD', 1, 'One')], DAY_MS, bid_amount=10),
                FakeTxn('Loser', [FakeItem('ADD', 1, 'One')], DAY_MS, status=FAILED, bid_amount=10)]
        out = espn.get_waiver_report(FakeLeague(txns, {1: 'RB'}), faab=True, test_date=DAY)
        assert 'TIED with Loser' in out

    # The best losing bid wins the callout, not merely the last one seen
    def test_waiver_report_uses_best_losing_bid(self):
        txns = [FakeTxn('Winner', [FakeItem('ADD', 1, 'One')], DAY_MS, bid_amount=20),
                FakeTxn('Low', [FakeItem('ADD', 1, 'One')], DAY_MS, status=FAILED, bid_amount=2),
                FakeTxn('High', [FakeItem('ADD', 1, 'One')], DAY_MS, status=FAILED, bid_amount=19)]
        out = espn.get_waiver_report(FakeLeague(txns, {1: 'RB'}), faab=True, test_date=DAY)
        assert 'High outbid by $1' in out

    # A team that outbid its OWN failed claim beat nobody
    def test_waiver_report_own_failed_claim_is_not_competition(self):
        txns = [FakeTxn('Same Team', [FakeItem('ADD', 1, 'One')], DAY_MS, bid_amount=10),
                FakeTxn('Same Team', [FakeItem('ADD', 1, 'One')], DAY_MS, status=FAILED, bid_amount=9)]
        out = espn.get_waiver_report(FakeLeague(txns, {1: 'RB'}), faab=True, test_date=DAY)
        assert 'outbid' not in out
        assert 'won by' not in out

    # An uncontested claim gets no callout
    def test_waiver_report_uncontested_has_no_callout(self):
        txn = FakeTxn('Team A', [FakeItem('ADD', 1, 'One')], DAY_MS, bid_amount=7)
        out = espn.get_waiver_report(FakeLeague([txn], {1: 'RB'}), faab=True, test_date=DAY)
        assert '($7)' in out

    # Without faab, no dollar amounts appear at all
    def test_waiver_report_non_faab_omits_bids(self):
        txn = FakeTxn('Team A', [FakeItem('ADD', 1, 'One')], DAY_MS, bid_amount=7)
        out = espn.get_waiver_report(FakeLeague([txn], {1: 'RB'}), faab=False, test_date=DAY)
        assert '$' not in out

    # Nothing on the report date at all
    def test_waiver_report_nothing_today_returns_empty(self):
        txn = FakeTxn('Team A', [FakeItem('ADD', 1, 'One')], OTHER_DAY_MS, bid_amount=1)
        assert espn.get_waiver_report(FakeLeague([txn], {1: 'RB'}), test_date=DAY) == ''

    # A transaction with no timestamp can never match the report date
    def test_waiver_report_undated_transaction_skipped(self):
        txn = FakeTxn('Team A', [FakeItem('ADD', 1, 'One')], None, bid_amount=1)
        assert espn.get_waiver_report(FakeLeague([txn], {1: 'RB'}), test_date=DAY) == ''

    # The header carries the report date
    def test_waiver_report_header(self):
        txn = FakeTxn('Team A', [FakeItem('ADD', 1, 'One')], DAY_MS, bid_amount=1)
        out = espn.get_waiver_report(FakeLeague([txn], {1: 'RB'}), test_date=DAY)
        assert out.splitlines()[0] == 'Waiver Report ' + DAY + ':'


class TestFaabBidCallout:
    ############ For `util.faab_bid_callout`
    def test_faab_callout_uncontested(self):
        assert utils.faab_bid_callout(10, None, None) == ''

    def test_faab_callout_tied(self):
        assert utils.faab_bid_callout(10, 10, 'Rival') == ', TIED with Rival'

    def test_faab_callout_narrow(self):
        assert utils.faab_bid_callout(10, 9, 'Rival') == ', Rival outbid by $1'

    def test_faab_callout_comfortable(self):
        assert utils.faab_bid_callout(30, 9, 'Rival') == ', won by $21'

    def test_faab_callout_threshold_is_configurable(self):
        assert utils.faab_bid_callout(10, 7, 'Rival', threshold=3) == ', Rival outbid by $3'

    def test_faab_callout_negative_margin_guarded(self):
        assert utils.faab_bid_callout(5, 9, 'Rival') == ''
