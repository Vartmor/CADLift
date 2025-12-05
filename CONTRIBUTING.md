# Contributing to CADLift

Thank you for your interest in contributing to CADLift! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Code Style](#code-style)
- [Testing](#testing)

## Code of Conduct

Please be respectful and constructive in all interactions. We're building something together!

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/cadlift.git
   cd cadlift
   ```
3. **Add the upstream remote**:
   ```bash
   git remote add upstream https://github.com/vartmor/cadlift.git
   ```

## Development Setup

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Copy environment file
cp .env.example .env

# Run database migrations
alembic upgrade head

# Start the development server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
# From the project root
npm install

# Copy environment file
cp .env.example .env.local

# Start the development server
npm run dev
```

## Making Changes

1. **Create a new branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. **Make your changes** and test them thoroughly

3. **Keep commits focused** - each commit should represent a single logical change

## Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, semicolons, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```
feat(api): add WebSocket support for real-time job updates
fix(geometry): correct wall thickness calculation for L-shaped rooms
docs(readme): update installation instructions
test(pipeline): add integration tests for image conversion
```

## Pull Request Process

1. **Update your fork**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Push your branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create a Pull Request** on GitHub with:
   - Clear title following commit guidelines
   - Description of changes
   - Screenshots/videos for UI changes
   - Related issue numbers

4. **Address review feedback** and keep your PR updated

## Code Style

### Python (Backend)

- Follow [PEP 8](https://pep8.org/)
- Use type hints for function signatures
- Maximum line length: 100 characters
- Use `black` for formatting: `black app tests`
- Use `ruff` for linting: `ruff check app`

### TypeScript (Frontend)

- Use TypeScript for all new code
- Prefer functional components with hooks
- Use descriptive variable and function names
- Keep components focused and small (<200 lines)

### General

- Write self-documenting code
- Add comments for complex logic
- Update documentation when changing APIs

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_geometry_validation.py

# Run with verbose output
pytest -v
```

### Frontend Tests

```bash
# Run E2E tests
npm run test:e2e

# Run in headed mode (see browser)
npm run test:e2e:headed

# Run with UI
npm run test:e2e:ui
```

### Writing Tests

- Write tests for all new features
- Maintain existing test coverage
- Use descriptive test names
- Test edge cases and error conditions

## Areas for Contribution

We especially welcome contributions in these areas:

- **Additional export formats** (FBX, DAE, etc.)
- **Door/window detection** improvements in DXF
- **Multi-story building support** enhancements
- **Material and texture support**
- **Frontend UI/UX improvements**
- **Documentation improvements**
- **Performance optimizations**
- **Internationalization** (new languages)

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions
- Check existing issues before creating new ones

---

Thank you for contributing to CADLift! 🏗️
