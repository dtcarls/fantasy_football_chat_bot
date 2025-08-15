# Architecture Documentation

This document explains the internal architecture and workflow of the fantasy football chat bot.

## Overview

The fantasy football chat bot is a Python application that automatically sends ESPN fantasy football league information to GroupMe, Slack, and Discord channels on a scheduled basis. The bot runs continuously and uses the APScheduler library to trigger messages at specific times throughout the week.

## System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Scheduler     │    │   ESPN Bot       │    │  Chat Platforms │
│  (scheduler.py) │───▶│ (espn_bot.py)    │───▶│   GroupMe       │
│                 │    │                  │    │   Slack         │
└─────────────────┘    └──────────────────┘    │   Discord       │
         │                       │              └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌──────────────────┐
│ Environment     │    │ ESPN API         │
│ Variables       │    │ (espn_api lib)   │
│ (env_vars.py)   │    │                  │
└─────────────────┘    └──────────────────┘
```

## Component Details

### 1. Scheduler (scheduler.py)

**Purpose:** Central job scheduling system that orchestrates all automated messages.

**Key Features:**
- Uses APScheduler with cron jobs
- Handles multiple time zones (ET for games, local for other messages)
- 15-minute misfire grace time for reliability
- Optional job activation based on environment variables

**Job Types:**
- **Fixed Schedule Jobs:** Always run if within season dates
- **Optional Jobs:** Only run if enabled via environment variables (daily waiver, monitor)

### 2. ESPN Bot (espn_bot.py)

**Purpose:** Main orchestrator that coordinates between ESPN data and chat platforms.

**Workflow:**
1. Load environment variables
2. Create ESPN League object using espn_api library
3. Determine which chat platforms are configured
4. Execute requested function to get fantasy data
5. Send formatted message to all configured platforms

**Design Patterns:**
- **Factory Pattern:** Creates appropriate chat platform objects
- **Strategy Pattern:** Different functions for different message types
- **Template Method:** Common flow with specific function implementations

### 3. Chat Platform Adapters

**Purpose:** Abstract away differences between messaging platforms.

**Common Interface:**
- `__init__(credentials)`: Initialize with platform-specific credentials
- `send_message(text)`: Send formatted message to platform

**Platform-Specific Handling:**
- **Character Limits:** Each platform has different limits
- **Message Formatting:** Code blocks for better readability
- **Error Handling:** Platform-specific exception types

### 4. Environment Configuration (env_vars.py)

**Purpose:** Centralized configuration management and validation.

**Responsibilities:**
- Load all environment variables with defaults
- Validate required variables are present
- Convert string values to appropriate types
- Ensure at least one messaging platform is configured

### 5. ESPN Data Layer (functionality.py)

**Purpose:** Interface with ESPN API to retrieve fantasy football data.

**Data Sources:**
- League standings and power rankings
- Weekly matchups and projections
- Live scoreboards and final scores
- Player status and waiver wire activity
- Historical data for trophies and analysis

### 6. Utility Functions (util.py)

**Purpose:** Common utility functions used throughout the application.

**Key Functions:**
- String manipulation (length limiting, boolean conversion)
- Date/time handling and validation
- Season date range checking

## Data Flow

### Typical Message Flow

1. **Trigger:** APScheduler triggers job at scheduled time
2. **Validation:** Check if current date is within fantasy season
3. **Data Retrieval:** ESPN Bot calls appropriate functionality function
4. **Data Processing:** Format data into human-readable text
5. **Platform Detection:** Determine which chat platforms are configured
6. **Message Delivery:** Send formatted message to each platform
7. **Error Handling:** Log errors and continue operation

### Environment Variable Flow

1. **Startup:** env_vars.py loads all configuration
2. **Validation:** Ensures required variables are present
3. **Storage:** Configuration stored in data dictionary
4. **Usage:** Other modules access configuration as needed

## Error Handling Strategy

### Graceful Degradation
- If one chat platform fails, others continue working
- Invalid environment variables use sensible defaults where possible
- ESPN API failures are logged but don't crash the scheduler

### Logging
- Structured logging throughout the application
- Error details captured for debugging
- Debug and info levels for different verbosity needs

## Deployment Architecture

### Heroku Deployment
- **Process Type:** Single worker process running scheduler
- **Persistence:** Stateless design, no local data storage
- **Configuration:** Environment variables for all settings
- **Scheduling:** APScheduler runs within application process

### Docker Support
- **Base Image:** Python runtime with required dependencies
- **Configuration:** Environment variables passed at runtime
- **Process:** Single container running the scheduler

## Security Considerations

### Credential Management
- All sensitive data stored as environment variables
- No hardcoded credentials in source code
- Platform-specific tokens and IDs properly isolated

### API Access
- ESPN API accessed through established Python library
- Rate limiting handled by underlying library
- Private league access requires user's own cookies

### Network Security
- HTTPS for all external API calls
- Webhook URLs validated before use
- No sensitive data logged

## Extensibility

### Adding New Chat Platforms
1. Create new class in `gamedaybot/chat/` directory
2. Implement `send_message(text)` method
3. Add platform detection logic in `espn_bot.py`
4. Update environment variable handling

### Adding New Message Types
1. Add function to `functionality.py`
2. Update `espn_bot.py` function mapping
3. Add scheduler job if needed
4. Update documentation

### Configuration Extensions
1. Add environment variable to `env_vars.py`
2. Update validation logic
3. Use in appropriate modules
4. Document in README.md

## Performance Considerations

### Memory Usage
- Minimal memory footprint
- No data persistence or caching
- Clean shutdown on process termination

### Network Efficiency
- Batch operations where possible
- Reuse HTTP connections
- Reasonable timeout values

### Scheduling Accuracy
- Cron-based scheduling for precision
- Misfire handling for reliability
- Time zone awareness for correctness

## Dependencies

### Core Dependencies
- **espn_api:** ESPN fantasy football data access
- **apscheduler:** Job scheduling and cron functionality
- **requests:** HTTP client for webhook calls
- **datetime:** Date and time manipulation

### Development Dependencies
- **pytest:** Testing framework
- **flake8:** Code style enforcement
- **requests_mock:** HTTP request mocking for tests

## Configuration Management

### Required Configuration
- **League Information:** LEAGUE_ID, LEAGUE_YEAR
- **Season Dates:** START_DATE, END_DATE
- **Messaging Platform:** At least one of BOT_ID, SLACK_WEBHOOK_URL, DISCORD_WEBHOOK_URL

### Optional Configuration
- **Features:** WAIVER_REPORT, MONITOR_REPORT, TOP_HALF_SCORING
- **Customization:** RANDOM_PHRASE, INIT_MSG
- **Private Leagues:** ESPN_S2, SWID

This architecture provides a robust, extensible foundation for automated fantasy football notifications while maintaining simplicity and reliability.