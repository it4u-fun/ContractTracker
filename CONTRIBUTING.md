# Contributing to Contract Tracker

Thank you for your interest in contributing to Contract Tracker! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Process](#contributing-process)
- [Code Style](#code-style)
- [Testing](#testing)
- [Documentation](#documentation)
- [Issues and Bug Reports](#issues-and-bug-reports)
- [Feature Requests](#feature-requests)
- [Pull Requests](#pull-requests)

## Code of Conduct

This project adheres to a code of conduct that ensures a welcoming environment for all contributors. Please be respectful and constructive in all interactions.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Set up the development environment** (see below)
4. **Create a feature branch** for your changes
5. **Make your changes** following our coding standards
6. **Test your changes** thoroughly
7. **Submit a pull request**

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose (for containerized development)
- Git

### Local Development

```bash
# Clone your fork
git clone https://github.com/your-username/ContractTracker.git
cd ContractTracker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py
```

### Docker Development

```bash
# Build and run with Docker
./docker-scripts.sh build
./docker-scripts.sh run

# Or use docker-compose
docker-compose up -d
```

## Contributing Process

### 1. Choose an Issue

- Look for issues labeled `good first issue` for newcomers
- Check `help wanted` for areas needing assistance
- Create a new issue if you have a bug report or feature request

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-number-description
```

### 3. Make Changes

- Follow the code style guidelines below
- Write tests for new functionality
- Update documentation as needed
- Ensure all existing tests pass

### 4. Test Your Changes

```bash
# Run tests (when test suite is implemented)
pytest

# Run linting
flake8 app/ tests/
black app/ tests/
isort app/ tests/

# Test Docker build
./docker-scripts.sh build
```

### 5. Submit a Pull Request

- Push your branch to your fork
- Create a pull request with a clear description
- Link to any related issues
- Request review from maintainers

## Code Style

### Python

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for all public functions and classes
- Keep functions small and focused
- Use meaningful variable and function names

### JavaScript

- Use ES6+ features
- Follow consistent indentation (2 spaces)
- Use meaningful variable names
- Add comments for complex logic

### HTML/CSS

- Use semantic HTML
- Follow BEM methodology for CSS
- Keep templates modular and reusable
- Use Bootstrap classes consistently

### Example Code Style

```python
def calculate_contract_value(contract: Contract) -> int:
    """
    Calculate the total value of a contract.
    
    Args:
        contract: The contract to calculate value for
        
    Returns:
        Total contract value in pence
    """
    return contract.total_days * contract.daily_rate
```

## Testing

### Unit Tests

- Write tests for all new functionality
- Aim for high test coverage
- Use descriptive test names
- Test both success and failure cases

### Integration Tests

- Test API endpoints
- Test database operations
- Test Docker container functionality

### Manual Testing

- Test the web interface thoroughly
- Verify data persistence
- Test error handling
- Test on different browsers and devices

## Documentation

### Code Documentation

- Write clear docstrings for all functions
- Include type hints
- Add inline comments for complex logic
- Update README.md for user-facing changes

### API Documentation

- Document all API endpoints
- Include request/response examples
- Document error codes and messages

### User Documentation

- Update README.md for new features
- Add usage examples
- Update installation instructions if needed

## Issues and Bug Reports

### Reporting Bugs

When reporting bugs, please include:

1. **Clear description** of the bug
2. **Steps to reproduce** the issue
3. **Expected behavior** vs actual behavior
4. **Environment details** (OS, Python version, Docker version)
5. **Screenshots** or error messages if applicable
6. **Browser/device** information for UI issues

### Bug Report Template

```markdown
**Bug Description**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g. Ubuntu 22.04]
- Python: [e.g. 3.11.5]
- Docker: [e.g. 24.0.7]
- Browser: [e.g. Chrome 118]

**Additional Context**
Any other context about the problem.
```

## Feature Requests

### Suggesting Features

When suggesting features, please include:

1. **Clear description** of the feature
2. **Use case** and motivation
3. **Proposed implementation** (if you have ideas)
4. **Alternative solutions** you've considered
5. **Additional context** and examples

## Pull Requests

### PR Guidelines

1. **Clear title** describing the change
2. **Detailed description** of what was changed and why
3. **Link to related issues**
4. **Screenshots** for UI changes
5. **Testing notes** explaining how you tested
6. **Breaking changes** clearly documented

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

## Development Roadmap

### Current Priorities

1. **Testing Infrastructure**: Comprehensive test suite
2. **UK Bank Holiday Integration**: Real-time holiday data
3. **Invoice Generation**: PDF invoice creation
4. **Calendar Export**: ICS file generation
5. **Performance Optimization**: Database and caching improvements

### Future Enhancements

- Multi-user support
- Advanced reporting
- Mobile application
- API versioning
- Kubernetes deployment

## Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **Discussions**: For general questions and ideas
- **Documentation**: Check the README and inline docs first

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to Contract Tracker! 🎉
