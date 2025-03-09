"""
Module for processing paper data to identify and filter authors with pharmaceutical affiliations.
"""

import logging
import re
from typing import Dict, List, Set, Any, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PaperProcessor:
    """
    Processes PubMed paper data to identify authors with pharmaceutical or biotech affiliations.
    """

    def __init__(self, debug: bool = False):
        """
        Initialize the paper processor.

        Args:
            debug: Enable debug logging
        """
        # Set logging level based on debug flag
        if debug:
            logger.setLevel(logging.DEBUG)

        # Common pharmaceutical/biotech company identifiers in affiliations
        self.pharma_indicators = [
            r'\b(?:pharma(?:ceutical)?s?|biotech|therapeutics|biosciences)\b',
            r'\binc\.?\b|\bllc\.?\b|\bltd\.?\b|\bcorp\.?\b|\bcorporation\b',
            r'\blaborator(?:y|ies)\b',
            r'\bmedical\s+research\b',
            r'\bbiopharm(?:a|aceutical)?\b',
            r'\bbiolog(?:y|ical)s?\b',
            r'\blife\s+sciences\b',
            r'\bhealth(?:care)?\b',
            r'\bmedicine[s]?\b',
            r'\bgenetics\b',
            r'\btherapeutics\b',
            r'\btechnology\b'
        ]

        # Common academic institution identifiers to exclude
        self.academic_indicators = [
            r'\buniversity\b|\bcollege\b|\bcampus\b',
            r'\bschool\s+of\b',
            r'\bacadem(?:y|ic)\b',
            r'\binstitut(?:e|ion)\b',
            r'\bdepartment\b|\bdept\.?\b',
            r'\bhospital\b',
            r'\bmedical\s+center\b|\bhealth\s+center\b',
            r'\bclinic(?:al)?\b',
            r'\bschool\b',
            r'\bfaculty\b',
            r'\bcampus\b',
            r'\bprofessor\b',
            r'\bedu\b'
        ]

        # Known major pharmaceutical companies
        self.pharma_companies = {
            'pfizer', 'merck', 'novartis', 'roche', 'sanofi', 'johnson & johnson', 'j&j',
            'glaxosmithkline', 'gsk', 'astrazeneca', 'abbvie', 'lilly', 'eli lilly',
            'bristol-myers squibb', 'bms', 'amgen', 'gilead', 'biogen',
            'bayer', 'boehringer', 'takeda', 'astellas', 'daiichi', 'eisai',
            'genentech', 'regeneron', 'moderna', 'biontech', 'curevac',
            'vertex', 'alexion', 'celgene', 'shire', 'incyte', 'seagen',
            'novavax', 'biomarin', 'alkermes', 'viatris', 'teva',
            'jazz', 'united therapeutics', 'ionis', 'allogene', 'bluebird bio'
        }

        logger.debug("Paper processor initialized")

    def process_papers(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process a list of papers to identify those with pharmaceutical company affiliations.

        Args:
            papers: List of paper detail dictionaries

        Returns:
            List of papers with pharmaceutical affiliations
        """
        logger.debug(f"Processing {len(papers)} papers to identify pharmaceutical affiliations")

        pharma_papers = []

        for paper in papers:
            non_academic_authors, company_affiliations, corresponding_emails = self._identify_pharma_authors(paper)

            if non_academic_authors:
                # Add processed information to the paper
                paper_with_pharma = {
                    "pubmed_id": paper["pubmed_id"],
                    "title": paper["title"],
                    "publication_date": paper["publication_date"],
                    "non_academic_authors": non_academic_authors,
                    "company_affiliations": list(company_affiliations),
                    "corresponding_author_email": "; ".join(corresponding_emails) if corresponding_emails else ""
                }

                pharma_papers.append(paper_with_pharma)

        logger.debug(f"Found {len(pharma_papers)} papers with pharmaceutical affiliations")
        return pharma_papers

    def _identify_pharma_authors(self, paper: Dict[str, Any]) -> Tuple[List[str], Set[str], List[str]]:
        """
        Identify authors affiliated with pharmaceutical or biotech companies in a paper.

        Args:
            paper: Paper details dictionary

        Returns:
            Tuple containing:
                - List of names of authors with pharmaceutical affiliations
                - Set of pharmaceutical company names
                - List of corresponding author emails
        """
        non_academic_authors = []
        company_affiliations = set()
        corresponding_emails = []

        for author in paper.get("authors", []):
            name = author.get("name", "")
            email = author.get("email")
            affiliations = author.get("affiliations", [])

            is_pharma_author = False
            author_companies = []

            for affiliation in affiliations:
                if not affiliation:
                    continue

                # Skip if clear academic affiliation
                if any(re.search(pattern, affiliation, re.IGNORECASE) for pattern in self.academic_indicators):
                    # Check if affiliation also contains a pharma company name
                    # (for cases of joint academic-industry affiliations)
                    if any(company in affiliation.lower() for company in self.pharma_companies):
                        is_pharma_author = True
                        for company in self.pharma_companies:
                            if company in affiliation.lower():
                                author_companies.append(company.title())
                    else:
                        # Skip clearly academic affiliations
                        continue

                # Check for pharma indicators
                if any(re.search(pattern, affiliation, re.IGNORECASE) for pattern in self.pharma_indicators):
                    is_pharma_author = True

                    # Try to extract company name
                    company_name = self._extract_company_name(affiliation)
                    if company_name:
                        author_companies.append(company_name)

            # Check email domain if available (as an additional signal)
            if email and "@" in email:
                domain = email.split("@")[1].lower()
                if not any(ac_indicator in domain for ac_indicator in ['edu', 'ac.', 'gov']):
                    # Corporate/commercial email domains
                    is_pharma_author = True

                    # Extract company name from email domain if possible
                    company_from_email = self._extract_company_from_email(domain)
                    if company_from_email:
                        author_companies.append(company_from_email)

            if is_pharma_author:
                non_academic_authors.append(name)
                company_affiliations.update(author_companies)
                if email:
                    corresponding_emails.append(email)

        return non_academic_authors, company_affiliations, corresponding_emails

    def _extract_company_name(self, affiliation: str) -> Optional[str]:
        """
        Attempt to extract company name from an affiliation string.

        Args:
            affiliation: Affiliation string

        Returns:
            Extracted company name or None if not found
        """
        # First check for known companies
        for company in self.pharma_companies:
            if company in affiliation.lower():
                return company.title()

        # Try to extract a company name based on common patterns
        # Pattern: [Name] Pharmaceuticals/Biotech/Therapeutics...
        company_matches = re.search(
            r'([A-Z][a-zA-Z0-9\s&\-]+)\s+(?:Pharma(?:ceutical)?s?|Biotech|Therapeutics|Biosciences|Labs?|Laboratories)',
            affiliation)
        if company_matches:
            return company_matches.group(0)

        # Pattern: [Name], Inc./LLC/Ltd./Corp./Corporation
        company_matches = re.search(
            r'([A-Z][a-zA-Z0-9\s&\-]+)(?:,\s+Inc\.?|,\s+LLC\.?|,\s+Ltd\.?|,\s+Corp\.?|,\s+Corporation)', affiliation)
        if company_matches:
            return company_matches.group(1)

        return None

    def _extract_company_from_email(self, domain: str) -> Optional[str]:
        """
        Attempt to extract company name from an email domain.

        Args:
            domain: Email domain (e.g., "company.com")

        Returns:
            Extracted company name or None if not extractable
        """
        # Remove common TLDs and extract the main domain
        parts = domain.split('.')
        if len(parts) >= 2:
            main_domain = parts[-2]

            # Check if the domain is a known pharma company
            for company in self.pharma_companies:
                normalized_company = company.replace(' ', '').replace('-', '').lower()
                if normalized_company in main_domain or main_domain in normalized_company:
                    return company.title()

            # If not a known company, return capitalized domain
            return main_domain.title()

        return None
