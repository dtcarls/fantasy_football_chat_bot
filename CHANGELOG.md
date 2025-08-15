# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive API reference documentation
- Architecture documentation explaining internal design
- Contributing guidelines for developers
- Enhanced docstrings throughout the codebase
- Detailed documentation for scheduler functionality
- Environment variable validation documentation

### Changed
- Improved function documentation with detailed parameter descriptions
- Enhanced error handling documentation
- Better inline code comments for complex logic

### Documentation
- Created `/docs` directory with comprehensive documentation
- Added API_REFERENCE.md with detailed function documentation
- Added ARCHITECTURE.md explaining system design and data flow
- Added CONTRIBUTING.md with development guidelines and workflow
- Enhanced existing README.md references to new documentation

## [0.3.1] - 2024-08-15

### Fixed
- Various bug fixes and improvements (existing version in setup.py)

## Previous Versions

*Historical changelog information can be added here as more releases are tracked*

---

## Types of Changes

- **Added** for new features
- **Changed** for changes in existing functionality  
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes
- **Documentation** for documentation-only changes

## Release Guidelines

### Version Bumping

- **Patch version** (0.3.1 → 0.3.2): Bug fixes and documentation updates
- **Minor version** (0.3.1 → 0.4.0): New features that are backward compatible
- **Major version** (0.3.1 → 1.0.0): Breaking changes or significant architectural changes

### Release Checklist

- [ ] Update version in `setup.py`
- [ ] Update this CHANGELOG.md
- [ ] Test all functionality with real league data
- [ ] Update README.md if needed
- [ ] Create GitHub release with release notes
- [ ] Deploy to Heroku button (if infrastructure changes)

### Breaking Changes

When introducing breaking changes, clearly document:
- What changed and why
- Migration path for existing users
- Timeline for deprecation (if applicable)
- Example of new usage pattern

### Security Updates

Security-related changes should:
- Be clearly marked in changelog
- Include CVE numbers if applicable
- Provide upgrade instructions
- Be released as soon as possible