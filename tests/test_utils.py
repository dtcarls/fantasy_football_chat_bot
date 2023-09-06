from datetime import datetime
import pytest
import sys
import os
sys.path.insert(1, os.path.abspath('.'))
import gamedaybot.utils as utils


class TestUtils:
    def test_str_to_bool_true(self):
        # Arrange
        s = "true"
        expected_output = True

        # Act
        actual_output = utils.str_to_bool(s)

        # Assert
        assert actual_output == expected_output

    def test_str_to_bool_false(self):
        # Arrange
        s = "false"
        expected_output = False

        # Act
        actual_output = utils.str_to_bool(s)

        # Assert
        assert actual_output == expected_output

    def test_str_to_bool_invalid(self):
        # Arrange
        s = "invalid"
        expected_output = False

        # Act
        actual_output = utils.str_to_bool(s)

        # Assert
        assert actual_output == expected_output

    def test_str_limit_check_within_limit(self):
        # Arrange
        s = "a" * 200
        limit = 250
        expected_output = [s]

        # Act
        actual_output = utils.str_limit_check(s, limit)

        # Assert
        assert actual_output == expected_output

    def test_str_limit_check_at_limit(self):
        # Arrange
        s = "a" * 250
        limit = 250
        expected_output = [s]

        # Act
        actual_output = utils.str_limit_check(s, limit)

        # Assert
        assert actual_output == expected_output

    def test_str_limit_check_over_limit(self):
        # Arrange
        s = (
            "Waiver Report 2022-12-14: \nPAIN TRAIN "
            "\nADDED QB Trevor Lawrence ($0)\nDROPPED QB Kyler Murray\n\n"
            "Mightnt i the Grissle \nADDED WR Curtis Samuel ($11)\nDROPPED WR Kadarius Toney\n\n"
            "PAIN TRAIN \nADDED QB Kirk Cousins ($0)\nDROPPED RB Travis Homer\n\n"
            "Adam's Injuried Meatsaber \nADDED TE Evan Engram ($20)\nDROPPED TE Foster Moreau\n\n"
            "PAIN TRAIN \nADDED D/ST Chiefs D/ST ($6)\nDROPPED D/ST Ravens D/ST"
        )

        limit = 250
        expected_output = [
            'Waiver Report 2022-12-14: \nPAIN TRAIN \nADDED QB Trevor Lawrence ($0)\nDROPPED QB Kyler Murray\n\nMightnt i the Grissle \nADDED WR Curtis Samuel ($11)\nDROPPED WR Kadarius Toney\n\nPAIN TRAIN \nADDED QB Kirk Cousins ($0)\nDROPPED RB Travis Homer\n',
            "Adam's Injuried Meatsaber \nADDED TE Evan Engram ($20)\nDROPPED TE Foster Moreau\n\nPAIN TRAIN \nADDED D/ST Chiefs D/ST ($6)\nDROPPED D/ST Ravens D/ST"]

        # Act
        actual_output = utils.str_limit_check(s, limit)

        # Assert
        assert actual_output == expected_output

    def test_str_to_datetime(self):
        # Arrange
        date_str = "2022-12-14"
        expected_output = datetime(2022, 12, 14)

        # Act
        actual_output = utils.str_to_datetime(date_str)

        # Assert
        assert actual_output == expected_output

    def test_str_to_datetime_invalid_date_format(self):
        # Arrange
        date_str = "12-14-2022"

        # Act and Assert
        with pytest.raises(ValueError):
            utils.str_to_datetime(date_str)

    def test_str_to_datetime_invalid_date(self):
        # Arrange
        date_str = "2022-13-14"

        # Act and Assert
        with pytest.raises(ValueError):
            utils.str_to_datetime(date_str)

    def test_str_to_datetime_invalid_month(self):
        # Arrange
        date_str = "2022-06-31"

        # Act and Assert
        with pytest.raises(ValueError):
            utils.str_to_datetime(date_str)

    def test_currently_in_season(self):
        # Arrange
        current_date = datetime(2022, 12, 1)
        start_date = "2022-09-08"
        end_date = "2023-01-09"
        expected_output = True

        # Act
        actual_output = utils.currently_in_season(start_date, end_date, current_date)

        # Assert
        assert actual_output == expected_output

    def test_currently_in_season_before_start_date(self):
        # Arrange
        current_date = datetime(2022, 6, 30)
        start_date = "2022-09-08"
        end_date = "2023-01-09"
        expected_output = False

        # Act
        actual_output = utils.currently_in_season(start_date, end_date, current_date)

        # Assert
        assert actual_output == expected_output

    def test_currently_in_season_after_end_date(self):
        # Arrange
        current_date = datetime(2023, 1, 10)
        start_date = "2022-09-08"
        end_date = "2023-01-09"
        expected_output = False

        # Act
        actual_output = utils.currently_in_season(start_date, end_date, current_date)

        # Assert
        assert actual_output == expected_output

    def test_currently_in_season_on_start_date(self):
        # Arrange
        current_date = datetime(2022, 9, 8)
        start_date = "2022-09-08"
        end_date = "2023-01-09"
        expected_output = True

        # Act
        actual_output = utils.currently_in_season(start_date, end_date, current_date)

        # Assert
        assert actual_output == expected_output

    def test_currently_in_season_on_end_date(self):
        # Arrange
        current_date = datetime(2023, 1, 9)
        start_date = "2022-09-08"
        end_date = "2023-01-09"
        expected_output = True

        # Act
        actual_output = utils.currently_in_season(start_date, end_date, current_date)

        # Assert
        assert actual_output == expected_output
