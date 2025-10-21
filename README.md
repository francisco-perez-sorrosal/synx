# Synx - Synapse Executor

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Synx** (Synapse Executor) provides an isolated environment to run Python code with enhanced security and monitoring capabilities.

## Features

- 🚀 **Isolated Execution**: Run Python code in secure, sandboxed environments
- 🎨 **Rich CLI**: Beautiful command-line interface with colorful output
- 📊 **Comprehensive Logging**: Structured logging with loguru and rich formatting
- ⚙️ **Pydantic Configuration**: Type-safe configuration management
- 🧪 **Testing Ready**: Built-in pytest configuration for quality assurance
- 🔧 **Development Tools**: Integrated black, ruff, and mypy for code quality

## Installation

This project uses [Pixi](https://pixi.sh/) for dependency management and environment handling.

### Prerequisites

- Python 3.11+
- [Pixi](https://pixi.sh/install)

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd synx
   ```

2. **Install dependencies**:
   ```bash
   pixi install
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

4. **Run the application**:
   ```bash
   pixi run start
   ```

## Usage

### Basic Usage

```bash
# Run the main application
pixi run start

# Show version information
pixi run start version

# Run with debug mode
pixi run start main --debug

# Set custom log level
pixi run start main --log-level DEBUG
```

### Development Commands

```bash
# Install development environment
pixi install --environment dev

# Run tests
pixi run test

# Format code
pixi run format

# Lint code
pixi run lint

# Type checking
pixi run type-check
```

## Project Structure

```
synx/
├── pyproject.toml          # Project configuration and pixi settings
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── README.md               # This file
├── src/
│   └── synx/
│       ├── __init__.py     # Package initialization
│       ├── main.py         # CLI application
│       └── logger.py       # Logging configuration
└── tests/
    ├── __init__.py
    └── test_main.py        # Test cases
```

## Configuration

The application can be configured through environment variables or command-line arguments:

### Environment Variables

- `APP_NAME`: Application name (default: "Synx")
- `DEBUG`: Enable debug mode (default: false)
- `LOG_LEVEL`: Logging level (default: INFO)

### Command Line Options

- `--debug, -d`: Enable debug mode
- `--log-level, -l`: Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

## Development

### Code Quality Tools

This project includes several tools to maintain code quality:

- **Black**: Code formatting
- **Ruff**: Fast Python linter and formatter
- **MyPy**: Static type checking
- **Pytest**: Testing framework

### Running Quality Checks

```bash
# Format code with black
pixi run format

# Lint with ruff
pixi run lint

# Type check with mypy
pixi run type-check

# Run all tests
pixi run test
```

### Adding Dependencies

```bash
# Add runtime dependency
pixi add package-name

# Add development dependency
pixi add --feature dev package-name

# Add PyPI-only package
pixi add --pypi package-name
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and ensure tests pass: `pixi run test`
4. Format and lint your code: `pixi run format && pixi run lint`
5. Commit your changes: `git commit -m "feat: add new feature"`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Francisco Perez-Sorrosal**
- Email: fperezsorrosal@gmail.com
- GitHub: [francisco-perez-sorrosal](https://github.com/francisco-perez-sorrosal)
