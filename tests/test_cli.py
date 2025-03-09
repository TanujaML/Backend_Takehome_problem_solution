"""
Tests for the CLI module.
"""

from unittest.mock import patch, MagicMock

from typer.testing import CliRunner

from pharma_papers.cli import app

runner = CliRunner()


@patch("pharma_papers.cli.PubMedClient")
@patch("pharma_papers.cli.PaperProcessor")
@patch("pharma_papers.cli.export_to_csv")
def test_cli_basic_query(mock_export, mock_processor, mock_client):
    """Test the CLI with a basic query."""
    # Setup mocks
    mock_client_instance = MagicMock()
    mock_client.return_value = mock_client_instance
    mock_client_instance.search.return_value = ["12345", "67890"]
    mock_client_instance.fetch_details.return_value = [{"pubmed_id": "12345"}, {"pubmed_id": "67890"}]

    mock_processor_instance = MagicMock()
    mock_processor.return_value = mock_processor_instance
    mock_processor_instance.process_papers.return_value = [{"pubmed_id": "12345"}]

    # Run the CLI
    result = runner.invoke(app, ["cancer"])

    # Verify the CLI runs successfully
    assert result.exit_code == 0

    # Verify the mocks were called correctly
    mock_client_instance.search.assert_called_once_with("cancer", max_results=100)
    mock_client_instance.fetch_details.assert_called_once_with(["12345", "67890"])
    mock_processor_instance.process_papers.assert_called_once()
    mock_export.assert_called_once_with([{"pubmed_id": "12345"}], None)


@patch("pharma_papers.cli.PubMedClient")
@patch("pharma_papers.cli.PaperProcessor")
@patch("pharma_papers.cli.export_to_csv")
def test_cli_with_file_output(mock_export, mock_processor, mock_client):
    """Test the CLI with file output specified."""
    # Setup mocks
    mock_client_instance = MagicMock()
    mock_client.return_value = mock_client_instance
    mock_client_instance.search.return_value = ["12345"]
    mock_client_instance.fetch_details.return_value = [{"pubmed_id": "12345"}]

    mock_processor_instance = MagicMock()
    mock_processor.return_value = mock_processor_instance
    mock_processor_instance.process_papers.return_value = [{"pubmed_id": "12345"}]

    # Run the CLI with file output
    result = runner.invoke(app, ["cancer", "--file", "output.csv"])

    # Verify the CLI runs successfully
    assert result.exit_code == 0

    # Verify the export was called with the correct filename
    mock_export.assert_called_once_with([{"pubmed_id": "12345"}], "output.csv")


@patch("pharma_papers.cli.PubMedClient")
def test_cli_no_results(mock_client):
    """Test the CLI behavior when no results are found."""
    # Setup mocks to return empty results
    mock_client_instance = MagicMock()
    mock_client.return_value = mock_client_instance
    mock_client_instance.search.return_value = []

    # Run the CLI
    result = runner.invoke(app, ["nonexistent_query"])

    # Verify the CLI exits cleanly with a message
    assert result.exit_code == 0
    assert "No papers found" in result.stdout


@patch("pharma_papers.cli.PubMedClient")
def test_cli_error_handling(mock_client):
    """Test the CLI error handling."""
    # Setup mocks to raise an exception
    mock_client_instance = MagicMock()
    mock_client.return_value = mock_client_instance
    mock_client_instance.search.side_effect = Exception("API error")

    # Run the CLI in normal mode (not debug)
    result = runner.invoke(app, ["cancer"])

    # Verify the CLI exits with an error message
    assert result.exit_code == 1
    assert "Error: API error" in result.stdout

    # Now run in debug mode which should raise the exception
    result = runner.invoke(app, ["cancer", "--debug"])
    assert result.exit_code == 1
