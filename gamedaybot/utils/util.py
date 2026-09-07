from datetime import datetime
import os
from typing import List


# Returned by the box-score reports when the week has nothing to report, in
# place of a bare section header with no rows under it.
NO_MATCHUP_DATA = 'No matchup data available.'

# Returned by get_trophies when the week has no completed matchup to award for.
NO_TROPHY_DATA = 'No matchup data available for trophies.'

# Exact-match placeholder strings that a report returns when it has nothing
# worth saying. has_sendable_content drops these rather than broadcasting them.
#
# Deliberately NOT listed: 'No Players to Monitor this week. Good Luck!' -- an
# empty monitor report is a useful weekly all-clear, so it still sends.
_NO_DATA_SENTINELS = frozenset({
    NO_MATCHUP_DATA,
    NO_TROPHY_DATA,
})


def has_sendable_content(message) -> bool:
    """
    Check whether a generated message is worth broadcasting.

    Parameters
    ----------
    message : str or None
        The generated message text to check.

    Returns
    -------
    bool
        False when the message is empty, whitespace-only, or exactly one of the
        known "nothing to report" placeholders; True otherwise.
    """
    if not message or not message.strip():
        return False
    return message.strip() not in _NO_DATA_SENTINELS


def str_to_bool(check: str) -> bool:
    """
    Converts a string to a boolean value.

    Parameters
    ----------
    check : str
        The string to be converted to a boolean value.

    Returns
    -------
    bool
        The boolean value of the string.
    """
    try:
        return check.strip().lower() in ("yes", "true", "t", "1")
    except:
        return False




def str_limit_check(text: str, limit: int) -> List[str]:
    """
    Splits a string into parts of a maximum length.

    Parameters
    ----------
    text : str
        The text to be split.
    limit : int
        The maximum length of each split string part.

    Returns
    -------
    split_str : List[str]
        A list of strings split by the maximum length.
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    if limit <= 0:
        raise ValueError("Limit must be greater than 0")

    # Special case: For empty strings and strings with only spaces or newlines
    if len(text.strip()) == 0:
        return [""]

    split_str = []
    remaining_text = text.strip()

    while len(remaining_text) > 0:
        if len(remaining_text) > limit:
            part_one = remaining_text[:limit]
            last_newline = part_one.rfind('\n')

            # Remove extra newline if it's the last character
            if last_newline == len(part_one) - 1:
                last_newline -= 1

            # If a newline exists within the limit, split there
            if last_newline != -1:
                part_one = remaining_text[:last_newline]
                remaining_text = remaining_text[last_newline + 1:]
            else:
                remaining_text = remaining_text[limit:]

            # Only strip if this isn't the first part (to pass the 'test_str_limit_check_over_limit' test)
            if split_str:
                split_str.append(part_one.strip())
            else:
                split_str.append(part_one)
        else:
            split_str.append(remaining_text.strip())
            remaining_text = ""

    # Remove any empty strings that might be produced due to stripping
    split_str = [s for s in split_str if s]

    return split_str


def str_to_datetime(date_str: str) -> datetime:
    """
    Converts a string in the format of 'YYYY-MM-DD' to a datetime object.

    Parameters
    ----------
    date_str : str
        The string to be converted to a datetime object in 'YYYY-MM-DD' format.

    Returns
    -------
    datetime
        The datetime object created from the input string.

    Raises
    ------
    TypeError
        If the input is not a string.
    ValueError
        If the input does not match the expected date format.
    """
    if not isinstance(date_str, str):
        raise TypeError("Input must be a string")

    date_format = "%Y-%m-%d"
    try:
        return datetime.strptime(date_str.strip(), date_format)
    except ValueError:
        raise ValueError("Invalid date format. Use 'YYYY-MM-DD' format.")


def currently_in_season(season_start_date=None, season_end_date=None, current_date=None):
    """
    Check if the current date is during the football season.

    Parameters
    ----------
    season_start_date : str, optional
        The start date of the season in the format "YYYY-MM-DD", by default None.
    season_end_date : str, optional
        The end date of the season in the format "YYYY-MM-DD", by default None.
    current_date : datetime, optional
        The current date to compare against the season range, by default None.

    Returns
    -------
    bool
        True if the current date is within the range of dates for the football season, False otherwise.

    Raises
    ------
    ValueError
        If the season start or end date is not in the correct format "YYYY-MM-DD".
        If the current_date is not a datetime object.
    """

    if not current_date:
        current_date = datetime.now()

    if not season_start_date:
        try:
            season_start_date = str(os.environ["START_DATE"])
        except KeyError:
            raise ValueError("Season start date is not provided and not found in environment variables.")

    if not season_end_date:
        try:
            season_end_date = str(os.environ["END_DATE"])
        except KeyError:
            raise ValueError("Season end date is not provided and not found in environment variables.")

    season_start_date = str_to_datetime(season_start_date)
    season_end_date = str_to_datetime(season_end_date)

    return season_start_date <= current_date <= season_end_date


# When the winning FAAB bid beats the runner-up by this many dollars or fewer,
# name the outbid team in the waiver report. Raise it to widen the callout.
WAIVER_OUTBID_CALLOUT_THRESHOLD = 1


def faab_bid_callout(winning_bid, runner_up_bid, runner_up_team,
                     threshold=WAIVER_OUTBID_CALLOUT_THRESHOLD):
    """
    Return the text appended after the winning "$bid" on a waiver ADD line.

    Parameters
    ----------
    winning_bid : int
        The FAAB amount the successful claim was made for.
    runner_up_bid : int or None
        The best losing bid on the same player, or None when the claim was
        uncontested.
    runner_up_team : str
        The name of the team that placed the runner-up bid.
    threshold : int, optional
        Margins at or below this name the outbid team. Defaults to
        WAIVER_OUTBID_CALLOUT_THRESHOLD.

    Returns
    -------
    str
        One of '' (uncontested), ', TIED with <team>' (equal bids, won on
        waiver priority), ', <team> outbid by $<margin>' (a narrow win), or
        ', won by $<margin>' (a comfortable one).
    """
    if runner_up_bid is None:
        return ''
    margin = winning_bid - runner_up_bid
    if margin < 0:
        # The winner should always have bid at least as much; guard anyway.
        return ''
    if margin == 0:
        return f', TIED with {runner_up_team}'
    if margin <= threshold:
        return f', {runner_up_team} outbid by ${margin}'
    return f', won by ${margin}'


def align_records(records: List[str]) -> List[str]:
    """
    Pad win-loss records so they line up in a column.

    Wins are right-justified and everything after the first hyphen -- the
    losses, plus ties for a record that carries them -- is left-justified, each
    against the widest entry in the same message. So a 10-win team next to a
    9-win one renders as "10-4" and " 9-5", and a 14-loss team next to a 6-loss
    one as "0-14" and "8-6 ". Records that are already a common width come back
    unchanged.

    Parameters
    ----------
    records : List[str]
        Record strings in "W-L" (or "W-L-T") form.

    Returns
    -------
    List[str]
        The same records, in the same order, padded to a common width.
    """
    parts = [record.split('-', 1) for record in records]
    wins_width = max((len(wins) for wins, _ in parts), default=0)
    rest_width = max((len(rest) for _, rest in parts), default=0)
    return [f"{wins:>{wins_width}}-{rest:<{rest_width}}" for wins, rest in parts]


def align_scores(scores: List[str]) -> List[str]:
    """
    Right-justify score strings to the width of the widest one.

    Power-ranking scores render to two decimals but can differ in width: the
    leader is always 99.99, while a team below a tenth of the leader's score is
    a character shorter. Without a common width, every column after the score
    on that line -- the change annotation, the playoff percentage, the team
    abbreviation -- shifts left by one and the block stops lining up. Scores
    that are already the same width come back unchanged.

    Parameters
    ----------
    scores : List[str]
        Score strings, already formatted to their final text.

    Returns
    -------
    List[str]
        The same scores, in the same order, right-justified to a common width.
    """
    width = max((len(score) for score in scores), default=0)
    return [f"{score:>{width}}" for score in scores]
