"""
Tests for the PubMed client module.
"""

from unittest.mock import patch, MagicMock

import pytest

from pharma_papers.pubmed_client import PubMedClient


@pytest.fixture
def pubmed_client():
    """Create a PubMed client instance for testing."""
    return PubMedClient(email="test@example.com", debug=True)


@patch("pharma_papers.pubmed_client.Entrez")
def test_search(mock_entrez, pubmed_client):
    """Test the search method of the PubMed client."""
    # Setup mock
    mock_handle = MagicMock()
    mock_entrez.esearch.return_value = mock_handle
    mock_entrez.read.return_value = {"IdList": ["12345", "67890"]}

    # Execute the search
    result = pubmed_client.search("test query", max_results=10)

    # Verify the results
    assert len(result) == 2
    assert result == ["12345", "67890"]

    # Verify the mocks were called correctly
    mock_entrez.esearch.assert_called_once_with(
        db="pubmed",
        term="test query",
        retmax=10,
        sort="relevance"
    )
    mock_entrez.read.assert_called_once_with(mock_handle)
    mock_handle.close.assert_called_once()


@patch("pharma_papers.pubmed_client.Entrez")
def test_fetch_details(mock_entrez, pubmed_client):
    """Test the fetch_details method of the PubMed client."""
    # Setup mock
    mock_handle = MagicMock()
    mock_entrez.efetch.return_value = mock_handle

    # Sample PubMed record
    sample_record = {
        "PubmedArticle": [
            {
                "MedlineCitation": {
                    "PMID": "12345",
                    "Article": {
                        "ArticleTitle": "Test Title",
                        "Journal": {
                            "JournalIssue": {
                                "PubDate": {
                                    "Year": "2023"
                                }
                            }
                        },
                        "AuthorList": [
                            {
                                "LastName": "Smith",
                                "ForeName": "John",
                                "AffiliationInfo": [
                                    {"Affiliation": "Test University"}
                                ]
                            }
                        ],
                        "Abstract": {
                            "AbstractText": ["This is a test abstract."]
                        }
                    }
                }
            }
        ]
    }

    mock_entrez.read.return_value = sample_record

    # Execute the fetch_details
    result = pubmed_client.fetch_details(["12345"])

    # Verify the results
    assert len(result) == 1
    assert result[0]["pubmed_id"] == "12345"
    assert result[0]["title"] == "Test Title"
    assert result[0]["publication_date"] == "2023"
    assert len(result[0]["authors"]) == 1
    assert result[0]["authors"][0]["name"] == "Smith John"

    # Verify the mocks were called correctly
    mock_entrez.efetch.assert_called_once_with(
        db="pubmed",
        id="12345",
        retmode="xml"
    )
    mock_entrez.read.assert_called_once_with(mock_handle)
    mock_handle.close.assert_called_once()


@patch("pharma_papers.pubmed_client.Entrez")
def test_search_error_handling(mock_entrez, pubmed_client):
    """Test error handling in the search method."""
    # Setup mock to raise an exception on first call, then succeed on second
    mock_entrez.esearch.side_effect = [
        Exception("API error"),  # First call fails
        MagicMock()  # Second call succeeds
    ]

    mock_handle = MagicMock()
    mock_entrez.read.return_value = {"IdList": ["12345"]}
    mock_entrez.esearch.return_value = mock_handle

    # Execute the search with retries
    result = pubmed_client.search("test query", retries=2)

    # Verify the results
    assert result == ["12345"]

    # Verify the mock was called twice (due to retry)
    assert mock_entrez.esearch.call_count == 2
