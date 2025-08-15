# Message Schedule Documentation

This document provides a comprehensive overview of when the fantasy football bot sends messages throughout the week.

## Weekly Schedule Overview

| Day | Time | Timezone | Message Type | Description | Required Variables |
|-----|------|----------|--------------|-------------|-------------------|
| **Monday** | 6:30 PM | Eastern | Close Scores | Games within ~16 points for Monday Night Football | BOT_ID or WEBHOOK |
| **Monday** | 7:30 AM | Local | Scoreboard Update | Current week's scores (short format) | BOT_ID or WEBHOOK |
| **Tuesday** | 7:30 AM | Local | Final Scores & Trophies | Previous week final results and awards | BOT_ID or WEBHOOK |
| **Tuesday** | 6:30 PM | Local | Power Rankings | League power rankings based on performance | BOT_ID or WEBHOOK |
| **Wednesday** | 7:30 AM | Local | Standings | Current league standings | BOT_ID or WEBHOOK |
| **Wednesday** | 7:31 AM | Local | Waiver Report | Add/drop waiver wire activity | ESPN_S2, SWID |
| **Thursday** | 7:30 PM | Eastern | Matchups | Upcoming week's matchups and projections | BOT_ID or WEBHOOK |
| **Friday** | 7:30 AM | Local | Scoreboard Update | Current week's scores (short format) | BOT_ID or WEBHOOK |
| **Sunday** | 7:30 AM | Local | Player Monitor | Players with injury/performance concerns | MONITOR_REPORT=True |
| **Sunday** | 4:00 PM | Eastern | Live Scoreboard | Game day score updates | BOT_ID or WEBHOOK |
| **Sunday** | 8:00 PM | Eastern | Live Scoreboard | Game day score updates | BOT_ID or WEBHOOK |

## Optional/Conditional Messages

### Daily Waiver Reports
- **When**: Daily at 7:31 AM (Local Time)
- **Days**: Monday, Tuesday, Thursday, Friday, Saturday, Sunday
- **Condition**: `DAILY_WAIVER=True`
- **Requirements**: `ESPN_S2` and `SWID` environment variables

### Player Monitor Reports  
- **When**: Sunday at 7:30 AM (Local Time)
- **Condition**: `MONITOR_REPORT=True`
- **Content**: Players in starting lineup that are Questionable, Doubtful, Out, or projected < 4 points

## Time Zone Details

### Eastern Time (Game Times)
Used for NFL game-related messages:
- Monday Night Football close scores
- Thursday Night Football matchups  
- Sunday game day scoreboards

**Reasoning**: NFL games are scheduled in Eastern Time, so game-related messages use this timezone for consistency.

### Local Time (League Management)
Used for league management messages:
- Standings and power rankings
- Waiver reports and roster updates
- Weekly summaries and trophies

**Reasoning**: League management activities are more relevant to league members' local schedules.

## Message Content Details

### Close Scores (Monday 6:30 PM ET)
- **Purpose**: Highlight competitive games for Monday Night Football
- **Criteria**: Games with point differential ≤ 15.99 points
- **Format**: Team abbreviations with current scores
- **Example**: 
  ```
  Close Scores
  TEAM1  98.50 -  97.20 TEAM2
  TEAM3 104.75 - 103.10 TEAM4
  ```

### Scoreboard Updates (Multiple Times)
- **Purpose**: Regular score updates throughout the week
- **Format**: Short format with team abbreviations and scores
- **Timing**: Monday/Friday mornings, Sunday afternoon/evening
- **Example**:
  ```
  Score Update
  HOME  89.45 -  76.20 AWAY
  HOME 112.80 -  98.50 AWAY
  ```

### Final Scores & Trophies (Tuesday 7:30 AM)
- **Purpose**: Week wrap-up with final results and awards
- **Content**: 
  - Final scores from completed week
  - High score trophy
  - Low score trophy (if enabled)
  - Biggest blowout
  - Closest matchup
- **Calculations**: Based on final player performances

### Power Rankings (Tuesday 6:30 PM)
- **Purpose**: League strength analysis
- **Algorithm**: 
  - 80% two-step dominance matrix
  - 15% points scored
  - 5% margin of victory
- **Format**: Ranked list with power scores
- **Note**: Focus on relative gaps rather than absolute numbers

### Standings (Wednesday 7:30 AM)
- **Purpose**: Current league standings
- **Content**:
  - Wins, losses, ties
  - Points for/against
  - Optional: Top half scoring wins (if `TOP_HALF_SCORING=True`)
- **Top Half Scoring**: Additional "wins" for being in top half of weekly scoring

### Waiver Report (Wednesday 7:31 AM)
- **Purpose**: Roster transaction summary
- **Requirements**: Private league access (ESPN_S2, SWID)
- **Content**: Recent add/drop activity
- **Daily Option**: Can run daily if `DAILY_WAIVER=True`

### Matchups (Thursday 7:30 PM ET)
- **Purpose**: Preview upcoming week's games
- **Content**:
  - Team matchups
  - Projected scores
  - Optional: Random phrases (if `RANDOM_PHRASE=True`)
- **Timing**: Before NFL Thursday Night Football

### Player Monitor (Sunday 7:30 AM)
- **Purpose**: Injury and performance alerts
- **Content**: Starting players who are:
  - Questionable (Q)
  - Doubtful (D)  
  - Out (O)
  - Projected < 4 points
- **Timing**: Before NFL games start

## Configuration Impact

### Required Environment Variables
All scheduled messages require:
- `LEAGUE_ID`: ESPN league identifier
- `LEAGUE_YEAR`: Fantasy season year
- `START_DATE` / `END_DATE`: Season date range
- At least one messaging platform:
  - `BOT_ID` (GroupMe)
  - `SLACK_WEBHOOK_URL` (Slack)  
  - `DISCORD_WEBHOOK_URL` (Discord)

### Optional Features
- `WAIVER_REPORT=True`: Enables Wednesday waiver reports
- `DAILY_WAIVER=True`: Enables daily waiver reports
- `MONITOR_REPORT=True`: Enables Sunday player monitoring
- `TOP_HALF_SCORING=True`: Adds top-half wins to standings
- `RANDOM_PHRASE=True`: Adds random phrases to matchups

### Private League Requirements
Waiver reports require ESPN authentication:
- `ESPN_S2`: Authentication cookie
- `SWID`: Session identifier

## Scheduling Technical Details

### APScheduler Configuration
- **Scheduler Type**: BlockingScheduler
- **Misfire Grace Time**: 15 minutes
- **Job Persistence**: Non-persistent (in-memory)
- **Time Zone Handling**: Explicit timezone specification per job

### Date Range Enforcement
- Jobs only run between `START_DATE` and `END_DATE`
- Date format: YYYY-MM-DD
- Automatic season boundary checking

### Error Handling
- Individual job failures don't affect other jobs
- API timeouts handled gracefully
- Platform-specific error recovery

## Customization Options

### Timing Modifications
To change message timing, modify `scheduler.py`:
```python
sched.add_job(espn_bot, 'cron', ['function_name'], 
              day_of_week='mon', hour=8, minute=0,  # Changed from 7:30
              start_date=ff_start_date, end_date=ff_end_date,
              timezone=my_timezone, replace_existing=True)
```

### Adding New Scheduled Messages
1. Create function in `functionality.py`
2. Add function call in `espn_bot.py`  
3. Add scheduler job in `scheduler.py`
4. Update this documentation

### Disabling Messages
Temporarily disable by commenting out scheduler jobs:
```python
# sched.add_job(espn_bot, 'cron', ['get_standings'], ...)
```

This schedule ensures your league stays informed throughout the fantasy football week with timely, relevant updates!