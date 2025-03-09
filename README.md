# Pharma Papers

A Python tool to fetch research papers from PubMed and identify those with authors affiliated with pharmaceutical or biotech companies.

## Features

- Search PubMed for papers using PubMed's query syntax
- Identify papers with authors affiliated with pharmaceutical or biotech companies
- Export results to CSV with details on non-academic authors and their affiliations
- Command-line interface with options for customization

## Installation

This project uses Poetry for dependency management. To install:

```bash
# Clone the repository
git clone https://github.com/TanujaML/Backend_Takehome_problem_solution.git
cd pharma-papers

# Install dependencies using Poetry
poetry install
```

## Usage

After installation, you can use the `get-papers-list` command:

```bash
# Basic usage
poetry run get-papers-list "cancer immunotherapy"

# Save results to a file
poetry run get-papers-list "cancer immunotherapy" --file results.csv

# Enable debug mode
poetry run get-papers-list "cancer immunotherapy" --debug

# Set maximum results
poetry run get-papers-list "cancer immunotherapy" --max 200]

# Specify email for NCBI API (required by their terms of service)
poetry run get-papers-list "cancer immunotherapy" --email "your.email@example.com"

# Use an NCBI API key for higher rate limits
poetry run get-papers-list "cancer immunotherapy" --api-key "your-api-key"
```

## Advanced PubMed Queries

The tool supports PubMed's full query syntax, allowing for complex searches:

```bash
# Papers about cancer published in the last year
poetry run get-papers-list "cancer AND (\"last year\"[PDat])"

# Papers about COVID-19 vaccines in high-impact journals
poetry run get-papers-list "covid-19 vaccine AND (\"Nature\"[jour] OR \"Science\"[jour] OR \"Cell\"[jour])"
```

## Code Organization

The project is structured as follows:

- `pharma_papers/`
  - `__init__.py`: Package initialization
  - `cli.py`: Command-line interface implementation
  - `pubmed_client.py`: Client for interacting with the PubMed API
  - `paper_processor.py`: Processing and filtering of papers
  - `utils.py`: Utility functions for CSV export, etc.
- `tests/`: Unit tests for the package
- `pyproject.toml`: Poetry configuration and project metadata
- `README.md`: This documentation file

## PyPI Package

The package is available on Test PyPI. You can install it with:

```bash
pip install -i https://test.pypi.org/simple/ pharma-papers
```

## Development

To set up the development environment:

```bash
# Install development dependencies
poetry install --with dev

# Run tests
poetry run pytest

# Format code
poetry run black pharma_papers
poetry run isort pharma_papers

# Type checking
poetry run mypy pharma_papers
```

## Tools Used

This project was developed using:

- [Poetry](https://python-poetry.org/): Dependency management and packaging
- [Typer](https://typer.tiangolo.com/): Modern command-line interface
- [Biopython](https://biopython.org/): Interface to the NCBI Entrez API
- [pandas](https://pandas.pydata.org/): Data manipulation and CSV export
- [Rich](https://rich.readthedocs.io/): Rich text and beautiful formatting in the terminal
- [pytest](https://docs.pytest.org/): Testing framework
- [mypy](https://mypy.readthedocs.io/): Static type checking
- [black](https://black.readthedocs.io/): Code formatting
- [Claude 3.7 Sonnet](https://www.anthropic.com/): AI assistant used for code development
