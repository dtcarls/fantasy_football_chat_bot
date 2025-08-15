# Developer Guide

This guide provides detailed information for developers working on the fantasy football chat bot.

## Table of Contents

- [Development Environment Setup](#development-environment-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Testing Strategy](#testing-strategy)
- [Debugging](#debugging)
- [Adding Features](#adding-features)
- [Deployment](#deployment)

## Development Environment Setup

### Prerequisites

- Python 3.7+ (Python 3.8+ recommended)
- Git
- A fantasy football league for testing (ESPN)
- Access to at least one messaging platform (GroupMe, Slack, or Discord)

### Local Development Setup

1. **Clone and Setup**
   ```bash
   git clone https://github.com/dtcarls/fantasy_football_chat_bot.git
   cd fantasy_football_chat_bot
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-test.txt
   ```

2. **Environment Configuration**
   Create a `.env` file or set environment variables:
   ```bash
   # Required
   export LEAGUE_ID="123456"
   export LEAGUE_YEAR="2024"
   export START_DATE="2024-09-05"
   export END_DATE="2025-01-05"
   
   # Messaging platform (choose one or more)
   export BOT_ID="your_groupme_bot_id"
   export SLACK_WEBHOOK_URL="https://hooks.slack.com/your/webhook"
   export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/your/webhook"
   
   # Optional
   export TIMEZONE="America/New_York"
   export TEST="True"
   export MONITOR_REPORT="True"
   export WAIVER_REPORT="True"
   ```

3. **Verify Setup**
   ```bash
   pytest
   python gamedaybot/espn/espn_bot.py get_standings
   ```

### IDE Configuration

#### VS Code
Recommended extensions:
- Python
- Pylance
- Python Docstring Generator

#### PyCharm
Configure:
- Project interpreter to your virtual environment
- Code style to PEP 8
- Run configurations for testing

## Project Structure

```
fantasy_football_chat_bot/
├── gamedaybot/                 # Main package
│   ├── chat/                   # Chat platform integrations
│   │   ├── discord.py         # Discord webhook client
│   │   ├── groupme.py         # GroupMe bot client
│   │   └── slack.py           # Slack webhook client
│   ├── espn/                   # ESPN integration
│   │   ├── env_vars.py        # Environment variable handling
│   │   ├── espn_bot.py        # Main bot orchestrator
│   │   ├── functionality.py   # ESPN data retrieval functions
│   │   ├── scheduler.py       # Job scheduling
│   │   └── season_recap.py    # End-of-season functionality
│   └── utils/                  # Utility functions
│       └── util.py            # Common utilities
├── tests/                      # Test suite
├── docs/                       # Documentation
├── requirements.txt           # Production dependencies
├── requirements-test.txt      # Testing dependencies
├── setup.py                   # Package configuration
├── Dockerfile                 # Docker configuration
├── Procfile                   # Heroku configuration
└── README.md                  # User documentation
```

### Key Files

- **`gamedaybot/espn/espn_bot.py`**: Main entry point and orchestrator
- **`gamedaybot/espn/scheduler.py`**: APScheduler job definitions
- **`gamedaybot/espn/functionality.py`**: ESPN data retrieval and formatting
- **`gamedaybot/espn/env_vars.py`**: Configuration management
- **`gamedaybot/chat/`**: Platform-specific message sending

## Development Workflow

### 1. Feature Development

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Develop and Test**
   ```bash
   # Write code
   # Add tests
   pytest tests/test_your_feature.py
   ```

3. **Test Integration**
   ```bash
   # Test specific function
   python gamedaybot/espn/espn_bot.py get_standings
   
   # Test scheduler (run briefly)
   python gamedaybot/espn/scheduler.py
   ```

### 2. Code Quality

```bash
# Style checking
flake8

# Run all tests
pytest

# Test coverage
pytest --cov=gamedaybot

# Type checking (if using mypy)
mypy gamedaybot/
```

### 3. Documentation

- Update docstrings for new functions
- Add to API reference if needed
- Update README.md for user-facing changes
- Add examples for complex features

## Testing Strategy

### Test Types

1. **Unit Tests**: Test individual functions in isolation
2. **Integration Tests**: Test ESPN API integration
3. **Platform Tests**: Test chat platform sending (mocked)
4. **End-to-End Tests**: Test complete workflows

### Writing Tests

```python
# tests/test_new_feature.py
import pytest
from gamedaybot.espn.functionality import your_new_function

def test_your_new_function_success():
    """Test successful execution of new function."""
    result = your_new_function("valid_input")
    assert result == expected_output

def test_your_new_function_error():
    """Test error handling in new function."""
    with pytest.raises(ValueError, match="Expected error message"):
        your_new_function("invalid_input")

@pytest.mark.integration
def test_espn_api_integration(mock_league):
    """Test integration with ESPN API."""
    # Test with mocked ESPN league object
    pass
```

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_functionality.py

# With coverage
pytest --cov=gamedaybot --cov-report=html

# Only unit tests (fast)
pytest -m "not integration"

# Integration tests (slower)
pytest -m integration
```

### Test Configuration

```python
# tests/conftest.py - shared test fixtures
@pytest.fixture
def mock_league():
    """Create a mock ESPN league for testing."""
    # Implementation
    pass

@pytest.fixture
def sample_env_vars():
    """Provide sample environment variables."""
    return {
        'league_id': '123456',
        'league_year': '2024',
        # ... other vars
    }
```

## Debugging

### Local Debugging

1. **Debug Individual Functions**
   ```python
   # In Python interpreter or script
   from gamedaybot.espn.espn_bot import espn_bot
   from gamedaybot.espn.env_vars import get_env_vars
   
   # Set breakpoint and run
   import pdb; pdb.set_trace()
   espn_bot('get_standings')
   ```

2. **Debug Scheduler**
   ```python
   # Temporarily modify scheduler.py for testing
   # Add immediate job instead of cron job
   sched.add_job(espn_bot, 'date', ['get_standings'], 
                 run_date=datetime.now() + timedelta(seconds=10))
   ```

### Logging

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Issues

1. **ESPN API Timeouts**
   - Check league ID and year
   - Verify league is public or provide ESPN_S2/SWID for private
   - Test with a different league

2. **Message Platform Errors**
   - Verify webhook URLs/bot IDs
   - Check character limits
   - Test with simple message first

3. **Scheduling Issues**
   - Check timezone settings
   - Verify date format (YYYY-MM-DD)
   - Ensure dates are within reasonable range

## Adding Features

### 1. New Message Type

1. **Add Function to functionality.py**
   ```python
   def get_new_message_type(league, week=None):
       """
       Get new type of fantasy football information.
       
       Parameters
       ----------
       league : espn_api.football.League
           The ESPN league object
       week : int, optional
           Week number, by default current week
           
       Returns
       -------
       str
           Formatted message text
       """
       # Implementation
       return formatted_message
   ```

2. **Add to espn_bot.py**
   ```python
   # In espn_bot function, add to function mapping
   elif function == "get_new_message_type":
       text = espn.get_new_message_type(league, ...)
   ```

3. **Add Scheduler Job (if needed)**
   ```python
   # In scheduler.py
   sched.add_job(espn_bot, 'cron', ['get_new_message_type'], 
                 id='new_message', day_of_week='mon', hour=8, ...)
   ```

4. **Add Tests**
   ```python
   def test_get_new_message_type():
       # Test implementation
       pass
   ```

### 2. New Chat Platform

1. **Create Platform Module**
   ```python
   # gamedaybot/chat/new_platform.py
   class NewPlatform:
       def __init__(self, webhook_url):
           self.webhook_url = webhook_url
       
       def send_message(self, text):
           # Platform-specific implementation
           pass
   ```

2. **Add Environment Variable**
   ```python
   # In env_vars.py
   try:
       new_platform_webhook = os.environ["NEW_PLATFORM_WEBHOOK"]
   except KeyError:
       new_platform_webhook = 1
   data['new_platform_webhook'] = new_platform_webhook
   ```

3. **Integrate with Bot**
   ```python
   # In espn_bot.py
   from gamedaybot.chat.new_platform import NewPlatform
   
   # Add platform creation logic
   if len(str(data['new_platform_webhook'])) > 1:
       new_platform = NewPlatform(data['new_platform_webhook'])
       # Add to platform list
   ```

### 3. Configuration Options

1. **Add Environment Variable**
   ```python
   # In env_vars.py
   try:
       new_option = utils.str_to_bool(os.environ["NEW_OPTION"])
   except KeyError:
       new_option = False
   data['new_option'] = new_option
   ```

2. **Use in Logic**
   ```python
   # In relevant module
   if data['new_option']:
       # Feature-specific logic
       pass
   ```

3. **Document in README**
   Add to environment variables table with description.

## Deployment

### Heroku Deployment

1. **Prepare for Deploy**
   ```bash
   # Ensure all changes are committed
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. **Deploy to Heroku**
   - Use the Deploy to Heroku button
   - Or manual deployment via Heroku CLI

3. **Configure Environment Variables**
   Set all required environment variables in Heroku dashboard.

### Docker Deployment

1. **Build Image**
   ```bash
   docker build -t fantasy-bot .
   ```

2. **Run Container**
   ```bash
   docker run -e LEAGUE_ID=123456 -e LEAGUE_YEAR=2024 ... fantasy-bot
   ```

### Local Production Testing

1. **Test with Real Data**
   ```bash
   # Set production environment variables
   # Run scheduler for a short time
   timeout 300 python gamedaybot/espn/scheduler.py
   ```

2. **Monitor Logs**
   Watch for errors, performance issues, or unexpected behavior.

## Performance Considerations

### Memory Usage
- Bot should use minimal memory
- No persistent data storage needed
- Clean up resources after use

### API Rate Limiting
- ESPN API has rate limits
- Space out requests appropriately
- Handle API errors gracefully

### Message Frequency
- Don't spam chat channels
- Respect platform rate limits
- Use appropriate scheduling intervals

## Best Practices

1. **Code Quality**
   - Follow PEP 8 style guidelines
   - Write descriptive variable names
   - Add type hints where helpful
   - Keep functions focused and small

2. **Error Handling**
   - Use specific exception types
   - Log errors with context
   - Fail gracefully when possible
   - Validate inputs

3. **Testing**
   - Test both success and failure cases
   - Mock external dependencies
   - Use descriptive test names
   - Maintain good test coverage

4. **Documentation**
   - Keep docstrings current
   - Document complex logic
   - Update README for user changes
   - Add examples for new features

This guide should help you get productive quickly with developing the fantasy football chat bot. For questions not covered here, check the other documentation files or reach out to the community!