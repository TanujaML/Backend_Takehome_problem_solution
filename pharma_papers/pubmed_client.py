"""
PubMed client module for fetching paper data from the PubMed API.
"""

import logging
import time
from typing import Dict, List, Optional, Any

from Bio import Entrez

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PubMedClient:
    """
    Client for interacting with the PubMed API via the Entrez Programming Utilities.
    """

    def __init__(self, email: str, tool: str = "PharmaFilters", api_key: Optional[str] = None, debug: bool = False):
        """
        Initialize PubMed client.

        Args:
            email: Email address to identify yourself to NCBI
            tool: Name of the tool/application
            api_key: NCBI API key (optional but recommended for higher rate limits)
            debug: Enable debug logging
        """
        self.email = email
        self.tool = tool
        self.api_key = api_key
        self.debug = debug

        # Configure Entrez
        Entrez.email = email
        Entrez.tool = tool
        if api_key:
            Entrez.api_key = api_key

        # Set logging level based on debug flag
        if debug:
            logger.setLevel(logging.DEBUG)

        logger.debug("PubMed client initialized")

    def search(self, query: str, max_results: int = 100, retries: int = 3) -> List[str]:
        """
        Search PubMed for papers matching the query.

        Args:
            query: PubMed query string
            max_results: Maximum number of results to return
            retries: Number of retry attempts for API calls

        Returns:
            List of PubMed IDs matching the query
        """
        logger.debug(f"Searching PubMed with query: {query}")

        attempt = 0
        while attempt < retries:
            try:
                # Search PubMed
                handle = Entrez.esearch(
                    db="pubmed",
                    term=query,
                    retmax=max_results,
                    sort="relevance"
                )
                record = Entrez.read(handle)
                handle.close()

                id_list = record["IdList"]
                logger.debug(f"Found {len(id_list)} papers matching the query")
                return id_list

            except Exception as e:
                attempt += 1
                logger.warning(f"Error searching PubMed (attempt {attempt}/{retries}): {e}")
                if attempt < retries:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error("Failed to search PubMed after maximum retries")
                    raise

        return []  # This should never be reached due to the raise above, but keeps mypy happy

    def fetch_details(self, id_list: List[str], batch_size: int = 50, retries: int = 3) -> List[Dict[str, Any]]:
        """
        Fetch detailed information for a list of PubMed IDs.

        Args:
            id_list: List of PubMed IDs
            batch_size: Number of records to fetch in each batch
            retries: Number of retry attempts for API calls

        Returns:
            List of paper details dictionaries
        """
        logger.debug(f"Fetching details for {len(id_list)} papers")

        papers = []
        for i in range(0, len(id_list), batch_size):
            batch_ids = id_list[i:i + batch_size]
            logger.debug(f"Fetching batch of {len(batch_ids)} papers (IDs {i} to {i + len(batch_ids) - 1})")

            attempt = 0
            while attempt < retries:
                try:
                    # Fetch paper details
                    handle = Entrez.efetch(
                        db="pubmed",
                        id=",".join(batch_ids),
                        retmode="xml"
                    )
                    records = Entrez.read(handle)
                    handle.close()

                    # Process paper details
                    for paper in records["PubmedArticle"]:
                        paper_details = self._extract_paper_details(paper)
                        papers.append(paper_details)

                    break  # Successful, exit retry loop

                except Exception as e:
                    attempt += 1
                    logger.warning(f"Error fetching paper details (attempt {attempt}/{retries}): {e}")
                    if attempt < retries:
                        time.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        logger.error("Failed to fetch paper details after maximum retries")
                        raise

            # Respect NCBI rate limits (10 requests per second with an API key, 3 without)
            time.sleep(0.1 if self.api_key else 0.34)

        logger.debug(f"Successfully fetched details for {len(papers)} papers")
        return papers

    def _extract_paper_details(self, paper: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract relevant details from a PubMed paper record.

        Args:
            paper: PubMed paper record

        Returns:
            Dictionary with extracted paper details
        """
        try:
            article = paper["MedlineCitation"]["Article"]

            # Extract basic information
            pubmed_id = paper["MedlineCitation"]["PMID"]
            title = article.get("ArticleTitle", "")

            # Extract publication date
            pub_date = ""
            if "PubDate" in article.get("Journal", {}).get("JournalIssue", {}).get("PubDate", {}):
                pub_date_dict = article["Journal"]["JournalIssue"]["PubDate"]
                year = pub_date_dict.get("Year", "")
                month = pub_date_dict.get("Month", "")
                day = pub_date_dict.get("Day", "")

                pub_date_parts = [part for part in [year, month, day] if part]
                pub_date = "/".join(pub_date_parts)

            # Extract authors
            authors = []
            author_list = article.get("AuthorList", [])
            if isinstance(author_list, list):
                for author in author_list:
                    if not isinstance(author, dict):
                        continue

                    author_name = ""
                    if "LastName" in author and "ForeName" in author:
                        author_name = f"{author['LastName']} {author['ForeName']}"
                    elif "LastName" in author and "Initials" in author:
                        author_name = f"{author['LastName']} {author['Initials']}"
                    elif "LastName" in author:
                        author_name = author['LastName']
                    elif "CollectiveName" in author:
                        author_name = author['CollectiveName']

                    # Extract author affiliation
                    affiliations = []
                    if "AffiliationInfo" in author:
                        for affiliation in author["AffiliationInfo"]:
                            if "Affiliation" in affiliation:
                                affiliations.append(affiliation["Affiliation"])

                    # Extract author email
                    email = None
                    for affiliation in affiliations:
                        # Common patterns for emails in affiliations
                        if "@" in affiliation:
                            parts = affiliation.split()
                            for part in parts:
                                if "@" in part and "." in part:
                                    email = part.strip(".,;()[]<>{}")

                    authors.append({
                        "name": author_name,
                        "affiliations": affiliations,
                        "email": email
                    })

            return {
                "pubmed_id": pubmed_id,
                "title": title,
                "publication_date": pub_date,
                "authors": authors,
                "abstract": article.get("Abstract", {}).get("AbstractText", [""])[0] if isinstance(
                    article.get("Abstract", {}).get("AbstractText", []), list) else ""
            }

        except Exception as e:
            logger.warning(
                f"Error extracting paper details (PMID: {paper.get('MedlineCitation', {}).get('PMID', 'unknown')}): {e}")
            # Return minimal information to avoid breaking the pipeline
            return {
                "pubmed_id": paper.get("MedlineCitation", {}).get("PMID", "unknown"),
                "title": "Error extracting paper details",
                "publication_date": "",
                "authors": [],
                "abstract": ""
            }
