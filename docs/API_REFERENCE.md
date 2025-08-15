# API Reference

This document provides comprehensive API documentation for all modules, classes, and functions in the fantasy football chat bot.

## Core Modules

### gamedaybot.espn.espn_bot

#### espn_bot(function)

Main entry point for the fantasy football bot functionality.

**Parameters:**
- `function` (str): The type of information to send. Available options:
  - `get_matchups`: Current week's matchups and projections
  - `get_monitor`: Player monitoring report
  - `get_scoreboard_short`: Current week's scores (short format)
  - `get_projected_scoreboard`: Projected scores for remaining games
  - `get_close_scores`: Games within ~16 points
  - `get_power_rankings`: League power rankings
  - `get_trophies`: Weekly trophies (high score, low score, etc.)
  - `get_standings`: Current league standings
  - `get_final`: Final scores and trophies from previous week
  - `get_waiver_report`: Add/drop waiver wire report

**Returns:** None

**Environment Variables Used:**
- `BOT_ID`: GroupMe bot ID
- `SLACK_WEBHOOK_URL`: Slack webhook URL
- `DISCORD_WEBHOOK_URL`: Discord webhook URL
- `LEAGUE_ID`: ESPN league ID
- `LEAGUE_YEAR`: Fantasy football season year
- `ESPN_S2`: ESPN S2 cookie (for private leagues)
- `SWID`: ESPN SWID (for private leagues)

### gamedaybot.espn.scheduler

#### scheduler()

Initializes and starts the fantasy football bot scheduler with all automated jobs.

**Scheduled Jobs:**
- **Monday 6:30 PM ET**: Close scores
- **Tuesday 7:30 AM Local**: Final scores and trophies
- **Tuesday 6:30 PM Local**: Power rankings
- **Wednesday 7:30 AM Local**: Standings
- **Wednesday 7:31 AM Local**: Waiver report
- **Thursday 7:30 PM ET**: Matchups
- **Friday/Monday 7:30 AM Local**: Scoreboard updates
- **Sunday 7:30 AM Local**: Player monitor (optional)
- **Sunday 4:00 PM & 8:00 PM ET**: Live scoreboards

**Returns:** None (runs indefinitely)

### gamedaybot.espn.env_vars

#### get_env_vars()

Collects and validates all environment variables needed for bot operation.

**Returns:** dict with keys:
- `ff_start_date`: Season start date
- `ff_end_date`: Season end date
- `my_timezone`: Timezone for scheduling
- `league_id`: ESPN league ID
- `league_year`: Fantasy season year
- `daily_waiver`: Enable daily waiver reports
- `monitor_report`: Enable player monitoring
- `test`: Test mode flag
- `top_half_scoring`: Include top half scoring
- `random_phrase`: Include random phrases
- `waiver_report`: Enable waiver reports
- `init_msg`: Bot startup message

## Chat Platform Classes

### gamedaybot.chat.groupme.GroupMe

GroupMe messaging platform integration.

#### __init__(bot_id)
**Parameters:**
- `bot_id` (str): GroupMe bot ID

#### send_message(text)
**Parameters:**
- `text` (str): Message text (max 1000 characters)

**Returns:** requests.Response object

### gamedaybot.chat.slack.Slack

Slack messaging platform integration.

#### __init__(webhook_url)
**Parameters:**
- `webhook_url` (str): Slack webhook URL

#### send_message(text)
**Parameters:**
- `text` (str): Message text (max 40000 characters)

**Returns:** requests.Response object

### gamedaybot.chat.discord.Discord

Discord messaging platform integration.

#### __init__(webhook_url)
**Parameters:**
- `webhook_url` (str): Discord webhook URL

#### send_message(text)
**Parameters:**
- `text` (str): Message text (max 3000 characters)

**Returns:** requests.Response object

## Utility Functions

### gamedaybot.utils.util

#### str_to_bool(check)
Converts string to boolean value.

**Parameters:**
- `check` (str): String to convert

**Returns:** bool

#### str_limit_check(text, limit)
Splits text into chunks respecting character limits.

**Parameters:**
- `text` (str): Text to split
- `limit` (int): Maximum length per chunk

**Returns:** List[str]

#### str_to_datetime(date_str)
Converts date string to datetime object.

**Parameters:**
- `date_str` (str): Date in 'YYYY-MM-DD' format

**Returns:** datetime object

#### currently_in_season(season_start_date, season_end_date, current_date)
Checks if current date is within fantasy season.

**Parameters:**
- `season_start_date` (str, optional): Season start date
- `season_end_date` (str, optional): Season end date  
- `current_date` (datetime, optional): Date to check

**Returns:** bool

## Fantasy Football Functions

### gamedaybot.espn.functionality

#### get_scoreboard_short(league, week)
Get current week's scoreboard in short format.

**Parameters:**
- `league` (espn_api.football.League): ESPN league object
- `week` (int, optional): Week number

**Returns:** str (formatted scoreboard text)

#### get_projected_scoreboard(league, week)
Get projected scores for remaining games.

**Parameters:**
- `league` (espn_api.football.League): ESPN league object
- `week` (int, optional): Week number

**Returns:** str (formatted projected scores)

## Exception Classes

- `GroupMeException`: Raised for GroupMe API errors
- `SlackException`: Raised for Slack API errors  
- `DiscordException`: Raised for Discord API errors

## Constants

- **Character Limits:**
  - GroupMe: 1000 characters
  - Slack: 40000 characters
  - Discord: 3000 characters
- **Default Timezone:** America/New_York
- **Misfire Grace Time:** 15 minutes