# Contributing to ZeroEye

Thank you for your interest in contributing to ZeroEye! This document provides guidelines and instructions for contributing.

## Getting Started

### Prerequisites

- Python 3.8+
- Git
- pip or conda

### Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/zeroeye.git
   cd zeroeye
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Development

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all function signatures
- Write docstrings for all public functions
- Keep functions focused and small

### Testing

Run tests before submitting:
```bash
python -m pytest tests/
```

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation changes

## Submitting Changes

1. Create a branch from `main`:
   ```bash
   git checkout -b feature/your-feature
   ```
2. Make your changes
3. Add tests if applicable
4. Commit with clear messages:
   ```bash
   git commit -m "feat: add new feature"
   ```
5. Push to your fork:
   ```bash
   git push origin feature/your-feature
   ```
6. Create a Pull Request

## Pull Request Guidelines

- Fill out the PR template completely
- Reference any related issues
- Include screenshots for UI changes
- Ensure all tests pass
- Keep PRs focused - one feature per PR

## Reporting Issues

When reporting issues, include:
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (OS, Python version)

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.
