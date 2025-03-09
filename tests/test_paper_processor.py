"""
Tests for the paper processor module.
"""

import pytest

from pharma_papers.paper_processor import PaperProcessor


@pytest.fixture
def paper_processor():
    """Create a PaperProcessor instance for testing."""
    return PaperProcessor(debug=True)


def test_process_papers_with_pharma_affiliations(paper_processor):
    """Test processing papers with pharmaceutical affiliations."""
    # Sample paper with pharma affiliation
    sample_papers = [
        {
            "pubmed_id": "12345",
            "title": "Test Pharmaceutical Paper",
            "publication_date": "2023/01/01",
            "authors": [
                {
                    "name": "Smith, John",
                    "affiliations": ["Pfizer Inc., New York, NY, USA"],
                    "email": "john.smith@pfizer.com"
                },
                {
                    "name": "Johnson, Emily",
                    "affiliations": ["Harvard University, Boston, MA, USA"],
                    "email": "emily.johnson@harvard.edu"
                }
            ]
        }
    ]

    # Process the papers
    result = paper_processor.process_papers(sample_papers)

    # Verify the results
    assert len(result) == 1
    assert result[0]["pubmed_id"] == "12345"
    assert "Smith, John" in result[0]["non_academic_authors"]
    assert "Johnson, Emily" not in result[0]["non_academic_authors"]
    assert "Pfizer" in result[0]["company_affiliations"]
    assert "john.smith@pfizer.com" in result[0]["corresponding_author_email"]


def test_process_papers_without_pharma_affiliations(paper_processor):
    """Test processing papers without pharmaceutical affiliations."""
    # Sample paper without pharma affiliation
    sample_papers = [
        {
            "pubmed_id": "67890",
            "title": "Test Academic Paper",
            "publication_date": "2023/02/01",
            "authors": [
                {
                    "name": "Brown, Robert",
                    "affiliations": ["Stanford University, Stanford, CA, USA"],
                    "email": "robert.brown@stanford.edu"
                },
                {
                    "name": "Lee, Sarah",
                    "affiliations": ["MIT, Cambridge, MA, USA"],
                    "email": "sarah.lee@mit.edu"
                }
            ]
        }
    ]

    # Process the papers
    result = paper_processor.process_papers(sample_papers)

    # Verify no papers were found with pharma affiliations
    assert len(result) == 0


def test_identify_pharma_authors_mixed_case(paper_processor):
    """Test identifying pharmaceutical authors with mixed affiliations."""
    # Sample paper with mixed academic and pharma affiliations
    sample_paper = {
        "pubmed_id": "24680",
        "title": "Test Mixed Affiliation Paper",
        "publication_date": "2023/03/01",
        "authors": [
            {
                "name": "White, Thomas",
                "affiliations": [
                    "Department of Biology, Yale University, New Haven, CT, USA",
                    "Moderna Therapeutics, Cambridge, MA, USA"
                ],
                "email": "thomas.white@moderna.com"
            },
            {
                "name": "Garcia, Maria",
                "affiliations": ["Novartis Institutes for BioMedical Research, Basel, Switzerland"],
                "email": "maria.garcia@novartis.com"
            },
            {
                "name": "Wilson, David",
                "affiliations": ["Johns Hopkins University School of Medicine, Baltimore, MD, USA"],
                "email": "david.wilson@jhu.edu"
            }
        ]
    }

    # Identify pharma authors
    non_academic_authors, company_affiliations, corresponding_emails = paper_processor._identify_pharma_authors(
        sample_paper)

    # Verify the results
    assert len(non_academic_authors) == 2
    assert "White, Thomas" in non_academic_authors
    assert "Garcia, Maria" in non_academic_authors
    assert "Wilson, David" not in non_academic_authors
    assert "Moderna" in company_affiliations
    assert "Novartis" in company_affiliations
    assert "thomas.white@moderna.com" in corresponding_emails
    assert "maria.garcia@novartis.com" in corresponding_emails


def test_extract_company_name(paper_processor):
    """Test extracting company names from affiliations."""
    # Test with direct company names
    assert "Pfizer" in paper_processor._extract_company_name("Pfizer Inc., New York, NY") or ""

    # Test with pattern matching
    company = paper_processor._extract_company_name("XYZ Pharmaceuticals, San Diego, CA")
    assert company and "XYZ Pharmaceuticals" in company

    # Test with no company
    assert paper_processor._extract_company_name("Department of Biology, University of California") is None


def test_extract_company_from_email(paper_processor):
    """Test extracting company names from email domains."""
    assert paper_processor._extract_company_from_email("pfizer.com") == "Pfizer"
    assert paper_processor._extract_company_from_email("research.novartis.com") == "Novartis"
    assert paper_processor._extract_company_from_email("biotech-company.io") == "Biotech-Company"
    assert paper_processor._extract_company_from_email("gmail.com") == "Gmail"  # Not ideal but expected behavior
