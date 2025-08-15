# Environment Variables Quick Reference

This document provides a comprehensive reference for all environment variables used by the fantasy football chat bot.

## Required Variables

### League Configuration
| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `LEAGUE_ID` | String | ESPN league ID (found in URL) | `123456` |
| `LEAGUE_YEAR` | String | Fantasy football season year | `2024` |
| `START_DATE` | String | Season start date (YYYY-MM-DD) | `2024-09-05` |
| `END_DATE` | String | Season end date (YYYY-MM-DD) | `2025-01-05` |

### Messaging Platform (At Least One Required)
| Variable | Type | Description | Where to Find |
|----------|------|-------------|---------------|
| `BOT_ID` | String | GroupMe bot ID | GroupMe developers page |
| `SLACK_WEBHOOK_URL` | String | Slack webhook URL | Slack app configuration |
| `DISCORD_WEBHOOK_URL` | String | Discord webhook URL | Discord server settings |

## Optional Variables

### Feature Flags
| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `WAIVER_REPORT` | Boolean | `False` | Enable weekly waiver reports |
| `DAILY_WAIVER` | Boolean | `False` | Enable daily waiver reports |
| `MONITOR_REPORT` | Boolean | `False` | Enable player status monitoring |
| `TOP_HALF_SCORING` | Boolean | `False` | Include top-half scoring in standings |
| `RANDOM_PHRASE` | Boolean | `False` | Add random phrases to matchups |

### Configuration
| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `TIMEZONE` | String | `America/New_York` | Local timezone for scheduling |
| `INIT_MSG` | String | None | Message sent when bot starts |
| `TEST` | Boolean | `False` | Enable test mode |

### Private League Access
| Variable | Type | Default | Description | Required For |
|----------|------|---------|-------------|--------------|
| `ESPN_S2` | String | None | ESPN authentication cookie | Private leagues, waiver reports |
| `SWID` | String | None | ESPN session ID (with or without {}) | Private leagues, waiver reports |

## Environment Variable Details

### Boolean Variables
Boolean values can be set using any of these formats:
- **True**: `true`, `True`, `1`, `yes`, `Yes`
- **False**: `false`, `False`, `0`, `no`, `No`, or omitted entirely

### Timezone Values
Use standard timezone identifiers from the [tz database](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones):
- `America/New_York` (Eastern Time)
- `America/Chicago` (Central Time)
- `America/Denver` (Mountain Time)
- `America/Los_Angeles` (Pacific Time)
- `Europe/London` (GMT/BST)
- `Europe/Paris` (CET/CEST)

### Date Format
Dates must be in ISO format: `YYYY-MM-DD`
- Valid: `2024-09-05`, `2025-01-05`
- Invalid: `09/05/2024`, `2024-9-5`, `September 5, 2024`

## Platform Setup Examples

### GroupMe Setup
```bash
export BOT_ID="your_groupme_bot_id_here"
```

### Slack Setup
```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

### Discord Setup
```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/YOUR/WEBHOOK/URL"
```

### Multiple Platforms
```bash
export BOT_ID="groupme_bot_id"
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
```

## Private League Configuration

For private ESPN leagues, you need to provide authentication:

1. **Log into ESPN Fantasy Football** in your browser
2. **Open Developer Tools** (F12 in most browsers)
3. **Go to Application tab** → Storage → Cookies → `https://fantasy.espn.com`
4. **Find and copy values** for:
   - `ESPN_S2`: Long string value
   - `SWID`: Usually in format `{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}`

```bash
export ESPN_S2="very_long_string_from_browser_cookie"
export SWID="{12345678-1234-1234-1234-123456789012}"
# Note: SWID can be with or without curly braces
```

## Complete Example Configuration

### Basic Public League
```bash
# Required
export LEAGUE_ID="123456"
export LEAGUE_YEAR="2024"
export START_DATE="2024-09-05"
export END_DATE="2025-01-05"
export BOT_ID="your_groupme_bot_id"

# Optional
export TIMEZONE="America/Chicago"
export TOP_HALF_SCORING="true"
export RANDOM_PHRASE="true"
export INIT_MSG="Fantasy Bot is online! 🏈"
```

### Advanced Private League
```bash
# Required
export LEAGUE_ID="123456"
export LEAGUE_YEAR="2024"
export START_DATE="2024-09-05"
export END_DATE="2025-01-05"
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."

# Private league access
export ESPN_S2="very_long_authentication_string"
export SWID="{12345678-1234-1234-1234-123456789012}"

# Features
export WAIVER_REPORT="true"
export DAILY_WAIVER="true"
export MONITOR_REPORT="true"
export TOP_HALF_SCORING="true"
export RANDOM_PHRASE="true"

# Configuration
export TIMEZONE="America/Los_Angeles"
export INIT_MSG="Welcome to the 2024 season!"
```

## Heroku Configuration

When deploying to Heroku, set variables in the dashboard or via CLI:

```bash
heroku config:set LEAGUE_ID=123456
heroku config:set LEAGUE_YEAR=2024
heroku config:set BOT_ID=your_bot_id
heroku config:set START_DATE=2024-09-05
heroku config:set END_DATE=2025-01-05
heroku config:set TIMEZONE=America/New_York
```

## Docker Configuration

For Docker deployment:

```bash
docker run -e LEAGUE_ID=123456 \
           -e LEAGUE_YEAR=2024 \
           -e BOT_ID=your_bot_id \
           -e START_DATE=2024-09-05 \
           -e END_DATE=2025-01-05 \
           fantasy_football_chat_bot
```

## Local Development

Create a `.env` file in the project root:

```bash
# .env file
LEAGUE_ID=123456
LEAGUE_YEAR=2024
BOT_ID=your_test_bot_id
START_DATE=2024-09-05
END_DATE=2025-01-05
TIMEZONE=America/New_York
TEST=true
```

Then load it in your shell:
```bash
source .env  # or use python-dotenv
```

## Validation and Troubleshooting

### Common Issues

1. **No messaging platform configured**
   - Error: "No messaging platform info provided"
   - Solution: Set at least one of `BOT_ID`, `SLACK_WEBHOOK_URL`, or `DISCORD_WEBHOOK_URL`

2. **Invalid date format**
   - Error: Date parsing errors
   - Solution: Use YYYY-MM-DD format for `START_DATE` and `END_DATE`

3. **Private league access denied**
   - Error: ESPN API authentication failures
   - Solution: Update `ESPN_S2` and `SWID` with fresh cookie values

4. **Waiver reports not working**
   - Error: Private league functions failing
   - Solution: Ensure `ESPN_S2` and `SWID` are set for private leagues

### Testing Configuration

Test your configuration before deployment:

```bash
# Test basic functionality
python gamedaybot/espn/espn_bot.py get_standings

# Test specific features
python gamedaybot/espn/espn_bot.py get_waiver_report
```

### Environment Variable Precedence

1. **Explicitly set environment variables** (highest priority)
2. **Default values in code** (fallback)
3. **Current year/date calculations** (for year/date defaults)

This reference should help you configure the bot properly for your specific needs and deployment environment!