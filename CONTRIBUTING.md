# Contributing Guidelines

Thank you for your interest in contributing to the Fantasy Football Chat Bot! This document provides guidelines and information for contributors.

## Code of Conduct

This project follows the principle of being welcoming and inclusive. Please be respectful in all interactions and help maintain a positive community.

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Git for version control
- A text editor or IDE of your choice

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/fantasy_football_chat_bot.git
   cd fantasy_football_chat_bot
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-test.txt
   ```

3. **Run Tests**
   ```bash
   pytest
   ```

4. **Verify Code Style**
   ```bash
   flake8
   ```

### Environment Setup for Testing

Create a `.env` file or set environment variables:
```bash
export LEAGUE_ID="your_test_league_id"
export LEAGUE_YEAR="2024"
export START_DATE="2024-09-05"
export END_DATE="2025-01-05"
export TIMEZONE="America/New_York"
export TEST="True"
# Add one messaging platform for testing:
export BOT_ID="test_bot_id"  # or
export SLACK_WEBHOOK_URL="https://hooks.slack.com/test"  # or
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/test"
```

## How to Contribute

### Reporting Issues

Before creating a new issue:
1. **Search existing issues** to avoid duplicates
2. **Check the FAQ** in README.md
3. **Join the Discord** for community support first

When creating an issue:
- Use a clear, descriptive title
- Provide detailed steps to reproduce
- Include environment information (Python version, platform)
- Add relevant error messages or logs
- Specify your league settings if applicable

### Suggesting Features

Feature requests should:
- Clearly describe the proposed functionality
- Explain the use case and benefits
- Consider impact on existing users
- Be feasible within the project's scope

### Contributing Code

#### Types of Contributions Welcome

1. **Bug Fixes**
   - Fix existing functionality issues
   - Improve error handling
   - Resolve edge cases

2. **New Features**
   - Additional message types
   - New chat platform support
   - Enhanced formatting options
   - Configuration improvements

3. **Testing**
   - Add test coverage for existing code
   - Create integration tests
   - Improve test reliability

4. **Documentation**
   - API documentation improvements
   - Setup guide enhancements
   - Code comments and docstrings

#### Development Workflow

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

2. **Make Changes**
   - Follow existing code style and patterns
   - Add tests for new functionality
   - Update documentation if needed
   - Keep commits focused and atomic

3. **Test Your Changes**
   ```bash
   # Run all tests
   pytest
   
   # Run specific test file
   pytest tests/test_functionality.py
   
   # Check code style
   flake8
   
   # Test with a real league (optional)
   python gamedaybot/espn/espn_bot.py
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "Brief description of changes"
   ```

5. **Push and Create Pull Request**
   ```bash
   git push origin your-branch-name
   ```

#### Pull Request Guidelines

**Before Submitting:**
- [ ] All tests pass
- [ ] Code follows existing style conventions
- [ ] Documentation is updated if needed
- [ ] No unnecessary dependencies added
- [ ] Changes are backward compatible (unless major version)

**Pull Request Description Should Include:**
- Clear description of what changed
- Reference to related issue (if applicable)
- Testing steps performed
- Breaking changes (if any)
- Screenshots for UI changes (if applicable)

**Review Process:**
- PRs require review from maintainers
- Feedback should be addressed promptly
- All CI checks must pass
- Maintainers may request changes or provide suggestions

## Code Style Guidelines

### Python Style

Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with these specifics:

- **Line Length:** 120 characters maximum
- **Indentation:** 4 spaces (no tabs)
- **Imports:** Group standard library, third-party, and local imports
- **Naming:** Use descriptive variable and function names

### Documentation Style

- **Docstrings:** Use NumPy-style docstrings for functions and classes
- **Comments:** Explain why, not what
- **README:** Keep setup instructions current and clear

### Example Function Documentation

```python
def example_function(param1, param2=None):
    """
    Brief description of what the function does.
    
    Longer description if needed, explaining the purpose,
    behavior, and any important details.
    
    Parameters
    ----------
    param1 : str
        Description of the first parameter.
    param2 : int, optional
        Description of the optional parameter, by default None.
    
    Returns
    -------
    dict
        Description of the return value.
        
    Raises
    ------
    ValueError
        When invalid input is provided.
    """
```

## Testing Guidelines

### Test Structure

- Tests are located in the `tests/` directory
- Test files should be named `test_[module_name].py`
- Use descriptive test function names: `test_function_name_expected_behavior`

### Writing Tests

```python
def test_function_with_valid_input():
    """Test that function works correctly with valid input."""
    result = your_function("valid_input")
    assert result == expected_output

def test_function_with_invalid_input():
    """Test that function raises appropriate error with invalid input."""
    with pytest.raises(ValueError):
        your_function("invalid_input")
```

### Test Coverage

- Aim for high test coverage on new code
- Test both success and failure scenarios
- Mock external API calls in tests
- Test edge cases and boundary conditions

## Adding New Chat Platform Support

To add support for a new chat platform:

1. **Create Platform Module**
   ```python
   # gamedaybot/chat/new_platform.py
   class NewPlatform:
       def __init__(self, credentials):
           self.credentials = credentials
       
       def send_message(self, text):
           # Implementation here
           pass
   ```

2. **Add Environment Variable Support**
   ```python
   # In env_vars.py
   try:
       new_platform_url = os.environ["NEW_PLATFORM_URL"]
   except KeyError:
       new_platform_url = 1
   ```

3. **Integrate with ESPN Bot**
   ```python
   # In espn_bot.py
   from gamedaybot.chat.new_platform import NewPlatform
   
   # Add to platform creation logic
   if len(str(new_platform_url)) > 1:
       new_platform = NewPlatform(new_platform_url)
   ```

4. **Add Tests**
   ```python
   # tests/test_new_platform.py
   def test_new_platform_send_message():
       # Test implementation
       pass
   ```

5. **Update Documentation**
   - Add setup instructions to README.md
   - Update environment variables table
   - Add to API reference

## Release Process

### Version Numbering

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR.MINOR.PATCH**
- **MAJOR:** Breaking changes
- **MINOR:** New features (backward compatible)
- **PATCH:** Bug fixes (backward compatible)

### Preparing a Release

1. Update version in `setup.py`
2. Update CHANGELOG.md with changes
3. Test thoroughly with real leagues
4. Create release tag and notes
5. Deploy to package repositories if applicable

## Getting Help

### Resources

- **Documentation:** Check the `/docs` folder
- **Discord:** Join the community Discord server
- **Issues:** Search existing GitHub issues
- **README:** Review setup and FAQ sections

### Questions About Contributing

If you have questions about contributing:
1. Check this document first
2. Search existing issues for similar questions
3. Ask in the Discord community
4. Create a GitHub issue with the "question" label

## Recognition

Contributors are recognized in several ways:
- Listed in repository contributors
- Mentioned in release notes for significant contributions
- Invited to join the project as maintainers for ongoing contributions

Thank you for helping make this project better! 🏈