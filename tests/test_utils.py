from datetime import datetime
import pytest
import sys
import os
sys.path.insert(1, os.path.abspath('.'))
import gamedaybot.utils.util as util


class TestStringToBool:
    ############ For `str_to_bool`
    # Test cases for valid True values
    def test_str_to_bool_yes(self):
        assert util.str_to_bool("yes") == True

    def test_str_to_bool_true(self):
        assert util.str_to_bool("true") == True

    def test_str_to_bool_t(self):
        assert util.str_to_bool("t") == True

    def test_str_to_bool_one(self):
        assert util.str_to_bool("1") == True

    # Test cases for case insensitivity
    def test_str_to_bool_yes_caps(self):
        assert util.str_to_bool("YES") == True

    def test_str_to_bool_true_mixed_case(self):
        assert util.str_to_bool("TrUe") == True

    # Test cases for valid False values
    def test_str_to_bool_no(self):
        assert util.str_to_bool("no") == False

    def test_str_to_bool_false(self):
        assert util.str_to_bool("false") == False

    def test_str_to_bool_f(self):
        assert util.str_to_bool("f") == False

    def test_str_to_bool_zero(self):
        assert util.str_to_bool("0") == False

    # Test cases for random string values
    def test_str_to_bool_random_string(self):
        assert util.str_to_bool("random") == False

    # Test cases for empty string
    def test_str_to_bool_empty_string(self):
        assert util.str_to_bool("") == False

    # Test cases for numbers other than '1' and '0'
    def test_str_to_bool_two(self):
        assert util.str_to_bool("2") == False

    # Test cases for special characters
    def test_str_to_bool_special_characters(self):
        assert util.str_to_bool("!@#$%^&*()") == False

    # Test cases for spaces
    def test_str_to_bool_spaces(self):
        assert util.str_to_bool("   ") == False

    # Test cases for None
    def test_str_to_bool_none(self):
        assert util.str_to_bool(None) == False

    # Test cases for number
    def test_str_to_bool_int(self):
        assert util.str_to_bool(123) == False

    # Test cases for leading/trailing whitespaces
    def test_str_to_bool_leading_whitespace(self):
        assert util.str_to_bool(" true ") == True

    def test_str_to_bool_trailing_whitespace(self):
        assert util.str_to_bool("true ") == True

    def test_str_to_bool_no_string(self):
        assert util.str_to_bool(True) == False

class TestStringLimitCheck:
    ############ For `str_limit_check`
    def test_str_limit_check_within_limit(self):
        assert util.str_limit_check("a" * 200, 250) == ["a" * 200]

    def test_str_limit_check_at_limit(self):
        assert util.str_limit_check("a" * 250, 250) == ["a" * 250]

    def test_str_limit_check_over_limit(self):
        long_str = (
            "Waiver Report 2022-12-14: \nPAIN TRAIN "
            "\nADDED QB Trevor Lawrence ($0)\nDROPPED QB Kyler Murray\n\n"
            "Mightnt i the Grissle \nADDED WR Curtis Samuel ($11)\nDROPPED WR Kadarius Toney\n\n"
            "PAIN TRAIN \nADDED QB Kirk Cousins ($0)\nDROPPED RB Travis Homer\n\n"
            "Adam's Injuried Meatsaber \nADDED TE Evan Engram ($20)\nDROPPED TE Foster Moreau\n\n"
            "PAIN TRAIN \nADDED D/ST Chiefs D/ST ($6)\nDROPPED D/ST Ravens D/ST"
        )
        expected_output = [
            'Waiver Report 2022-12-14: \nPAIN TRAIN \nADDED QB Trevor Lawrence ($0)\nDROPPED QB Kyler Murray\n\nMightnt i the Grissle \nADDED WR Curtis Samuel ($11)\nDROPPED WR Kadarius Toney\n\nPAIN TRAIN \nADDED QB Kirk Cousins ($0)\nDROPPED RB Travis Homer\n',
            "Adam's Injuried Meatsaber \nADDED TE Evan Engram ($20)\nDROPPED TE Foster Moreau\n\nPAIN TRAIN \nADDED D/ST Chiefs D/ST ($6)\nDROPPED D/ST Ravens D/ST"
        ]
        assert util.str_limit_check(long_str, 250) == expected_output

    def test_str_limit_check_empty_string(self):
        assert util.str_limit_check("", 5) == [""]

    def test_str_limit_check_zero_limit(self):
        with pytest.raises(ValueError):
            util.str_limit_check("hello", 0)

    def test_str_limit_check_negative_limit(self):
        with pytest.raises(ValueError):
            util.str_limit_check("hello", -5)

    def test_str_limit_check_split_on_newline(self):
        assert util.str_limit_check("hello\nworld", 8) == ["hello", "world"]

    def test_str_limit_check_string_with_only_newlines(self):
        assert util.str_limit_check("\n\n\n\n\n", 3) == [""]

    def test_str_limit_check_string_with_multiple_spaces(self):
        assert util.str_limit_check("     ", 3) == [""]

    def test_str_limit_check_string_with_multiple_spaces_and_newline(self):
        assert util.str_limit_check("   \n  ", 3) == [""]

    def test_str_limit_check_string_with_multiple_trailing_spaces(self):
        assert util.str_limit_check("hello world         ", 11) == ["hello world"]

    def test_str_limit_check_string_with_multiple_preceeding_spaces(self):
        assert util.str_limit_check("     hello world", 11) == ["hello world"]

    def test_str_limit_check_string_with_multiple_trailing_spaces_with_newline(self):
        assert util.str_limit_check("hello world \n      ", 11) == ["hello world"]

    def test_str_limit_check_string_with_multiple_preceeding_spaces_with_newline(self):
        assert util.str_limit_check(" \n    hello world", 11) == ["hello world"]

    def test_str_limit_check_non_string_input(self):
        with pytest.raises(TypeError):
            util.str_limit_check(12345, 5)

    def test_str_limit_check_non_integer_limit(self):
        with pytest.raises(TypeError):
            util.str_limit_check("hello", "five")

class TestStringToDatetime:
    ############ For `str_to_datetime`
    def test_str_to_datetime_valid_date(self):
        assert util.str_to_datetime("2022-12-14") == datetime(2022, 12, 14)

    def test_str_to_datetime_invalid_date_format(self):
        with pytest.raises(ValueError):
            util.str_to_datetime("12-14-2022")

    def test_str_to_datetime_invalid_date(self):
        with pytest.raises(ValueError):
            util.str_to_datetime("2022-13-14")

    def test_str_to_datetime_invalid_month(self):
        with pytest.raises(ValueError):
            util.str_to_datetime("2022-06-31")

    def test_str_to_datetime_invalid_leap_year(self):
        with pytest.raises(ValueError):
            util.str_to_datetime("2022-02-29")

    def test_str_to_datetime_incomplete_date(self):
        with pytest.raises(ValueError):
            util.str_to_datetime("2022-09")

    def test_str_to_datetime_non_string_input(self):
        with pytest.raises(TypeError):
            util.str_to_datetime(123)

    def test_str_to_datetime_whitespace_in_date_string(self):
        assert util.str_to_datetime("   2022-12-14   ") == datetime(2022, 12, 14)
        assert util.str_to_datetime("\n2022-12-14\n") == datetime(2022, 12, 14)

    def test_str_to_datetime_leap_year(self):
        assert util.str_to_datetime("2020-02-29") == datetime(2020, 2, 29)

    def test_str_to_datetime_empty_string(self):
        with pytest.raises(ValueError):
            util.str_to_datetime("")

    def test_str_to_datetime_date_with_time(self):
        with pytest.raises(ValueError):
            util.str_to_datetime("2023-09-08 12:34:56")

    def test_str_to_datetime_string_representation(self):
        with pytest.raises(ValueError):
            util.str_to_datetime("September 8, 2023")


class TestCurrentlyInSeason:
    ############ For `currently_in_season`
    def test_currently_in_season_within_season(self):
        assert util.currently_in_season("2022-09-08", "2023-01-09", datetime(2022, 12, 1)) == True

    def test_currently_in_season_before_start_date(self):
        assert util.currently_in_season("2022-09-08", "2023-01-09", datetime(2022, 6, 30)) == False

    def test_currently_in_season_after_end_date(self):
        assert util.currently_in_season("2022-09-08", "2023-01-09", datetime(2023, 1, 10)) == False

    def test_currently_in_season_on_start_date(self):
        assert util.currently_in_season("2022-09-08", "2023-01-09", datetime(2022, 9, 8)) == True

    def test_currently_in_season_on_end_date(self):
        assert util.currently_in_season("2022-09-08", "2023-01-09", datetime(2023, 1, 9)) == True

    def test_currently_in_season_valid(self):
        assert util.currently_in_season("2022-09-01", "2022-12-31", datetime(2022, 10, 15)) == True

    def test_currently_in_season_before_season(self):
        assert util.currently_in_season("2022-09-01", "2022-12-31", datetime(2022, 8, 15)) == False

    def test_currently_in_season_after_season(self):
        assert util.currently_in_season("2022-09-01", "2022-12-31", datetime(2023, 2, 15)) == False

    def test_currently_in_season_invalid_start_date_format(self):
        with pytest.raises(ValueError):
            util.currently_in_season("2022/09/01", "2022-12-31", datetime(2022, 10, 15))

    def test_currently_in_season_invalid_end_date_format(self):
        with pytest.raises(ValueError):
            util.currently_in_season("2022-09-01", "Dec 31, 2022", datetime(2022, 10, 15))

    def test_currently_in_season_non_string_start_date(self):
        with pytest.raises(TypeError):
            util.currently_in_season(123, "2022-12-31", datetime(2022, 10, 15))

    def test_currently_in_season_non_string_end_date(self):
        with pytest.raises(ValueError):
            util.currently_in_season("2022-09-01", None, datetime(2022, 10, 15))
