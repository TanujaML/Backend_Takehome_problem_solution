#!/usr/bin/env python3
"""
Example script demonstrating how to use pharma_papers as a module.
"""

import sys

from pharma_papers.paper_processor import PaperProcessor
from pharma_papers.pubmed_client import PubMedClient
from pharma_papers.utils import export_to_csv


def main():
    """
    Example of using pharma_papers as a module to search for cancer immunotherapy papers.
    """
    print("Using pharma_papers as a module to search for cancer immunotherapy papers")

    # Initialize client and processor
    pubmed_client = PubMedClient(email="your.email@example.com", debug=True)
    paper_processor = PaperProcessor(debug=True)

    try:
        # Search PubMed
        print("Searching PubMed...")
        id_list = pubmed_client.search("cancer immunotherapy", max_results=10)
        print(f"Found {len(id_list)} papers")

        if not id_list:
            print("No papers found matching the query.")
            return 0

        # Fetch paper details
        print("Fetching paper details...")
        papers = pubmed_client.fetch_details(id_list)

        # Process papers to identify pharmaceutical affiliations
        print("Identifying papers with pharmaceutical affiliations...")
        pharma_papers = paper_processor.process_papers(papers)

        # Print results
        print(f"Found {len(pharma_papers)} papers with pharmaceutical company affiliations")

        # Export to CSV
        filename = "module_example_output.csv"
        export_to_csv(pharma_papers, filename)
        print(f"Results saved to {filename}")

        return 0

    except Exception as e:
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
