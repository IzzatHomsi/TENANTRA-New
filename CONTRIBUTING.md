
# Contributing to Tenantra

First off, thank you for considering contributing to Tenantra! It's people like you that make Tenantra such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by the [Tenantra Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## How Can I Contribute?

### Reporting Bugs

If you find a bug, please open an issue on our [GitHub Issues](https://github.com/IzzatHomsi/TENANTRA-New/issues) page. Please include as much detail as possible, including:

- A clear and descriptive title.
- A step-by-step description of how to reproduce the bug.
- The expected behavior and what actually happened.
- Your environment details (OS, browser, etc.).

### Suggesting Enhancements

If you have an idea for a new feature or an enhancement to an existing one, please open an issue on our [GitHub Issues](https://github.com/IzzatHomsi/TENANTRA-New/issues) page. Please provide a clear and detailed explanation of the feature, why it would be beneficial, and any potential implementation ideas.

### Your First Code Contribution

Unsure where to begin contributing to Tenantra? You can start by looking through `good first issue` and `help wanted` issues:

- [Good first issues](https://github.com/IzzatHomsi/TENANTRA-New/labels/good%20first%20issue) - issues which should only require a few lines of code, and a test or two.
- [Help wanted issues](https://github.com/IzzatHomsi/TENANTRA-New/labels/help%20wanted) - issues which should be a bit more involved than `good first issue` issues.

### Pull Requests

1.  **Fork the repository** and create your branch from `main`.
2.  **Set up your development environment** as described in the [README.md](README.md) file.
3.  **Make your changes** and ensure that the code lints and all tests pass.
4.  **Create a pull request** to the `main` branch of the Tenantra repository.
5.  **Ensure your pull request has a clear title and description**, explaining the purpose of the changes and referencing any related issues.

## Coding Standards

### Backend (Python)

- We use [Black](https://github.com/psf/black) for code formatting. Please ensure your code is formatted with Black before submitting a pull request.
- We use [Flake8](https://flake8.pycqa.org/en/latest/) for linting. Please ensure your code passes all Flake8 checks.
- We use [mypy](http://mypy-lang.org/) for static type checking. Please ensure your code passes all mypy checks.

### Frontend (React/TypeScript)

- We use [Prettier](https://prettier.io/) for code formatting. Please ensure your code is formatted with Prettier before submitting a pull request.
- We use [ESLint](https://eslint.org/) for linting. Please ensure your code passes all ESLint checks.

## Commit Message Guidelines

We use the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification for our commit messages. This allows for easier automation of changelog generation and release versioning.

The commit message should be structured as follows:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Example:**

```
feat(auth): add password reset functionality

- Implement the password reset API endpoint.
- Add a password reset form to the frontend.

Fixes #123
```
