# Secure Lambda Scanner

## Overview

The `secure-lambda-scanner.py` script is designed to analyze Python Lambda functions in your AWS account for security vulnerabilities using Bandit. It dynamically discovers Python Lambda functions across all regions, downloads their code, extracts it, and runs Bandit against the extracted code. The results are stored in the specified destination directory in the desired format (default is 'txt').

## Prerequisites

Ensure the following prerequisites are met:

- Python 3
- [AWS CLI configured](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)
- [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) library installed
- [Bandit](https://bandit.readthedocs.io/en/latest/) installed and in your system's PATH
- [Pre-commit](https://pre-commit.com/) installed (optional but recommended)

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your/repo.git
    ```

2. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Set up pre-commit hooks:

    ```bash
    pre-commit install
    ```

## Usage

```bash
./secure-lambda-scanner.py --destination-directory /path/to/results --format txt
```

### Options:

- `--destination-directory` (`-d` or `--dest`): Set the destination path to store the Bandit results.
- `--format` (`-f` or `--fmt`): Specify the output format for Bandit results. Default is 'txt'.
- `--bucket-name` (`-b` or `--bucket`): Specify the destination bucket for uploading Bandit results.

## Configuration Files

### .pre-commit-config.yaml

The `.pre-commit-config.yaml` file specifies pre-commit hooks, including the Bandit hook, which is responsible for checking Python code for common security issues.

```yaml
repos:
-   repo: https://github.com/PyCQA/bandit
    rev: 1.7.6
    hooks:
    -   id: bandit
        args: ["-c", "pyproject.toml"]
        additional_dependencies: [".[toml]"]
```

### requirements.txt

The `requirements.txt` file lists the necessary Python dependencies for the script.

```plaintext
boto3
click
requests
```

### pyproject.toml

The `pyproject.toml` file configures Bandit by excluding the `./venv/*` directory from scanning.

```toml
[tool.bandit]
exclude_dirs = ["./venv/*"]
```

## Note

Make sure to run the script within a virtual environment with the specified requirements and pre-commit hooks to avoid potential errors, such as "bandit executable not found" or missing Python modules.