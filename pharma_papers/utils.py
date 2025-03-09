"""
Utility functions for the pharma_papers package.
"""

import csv
import logging
import os
import sys
from typing import List, Dict, Any, Optional

import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def export_to_csv(papers: List[Dict[str, Any]], filename: Optional[str] = None) -> Optional[str]:
    """
    Export papers to a CSV file or print to console.

    Args:
        papers: List of paper dictionaries to export
        filename: Output filename (if None, prints to console)

    Returns:
        Path to the saved file if filename is provided, None otherwise
    """
    # Prepare data for CSV
    data = []
    for paper in papers:
        row = {
            'PubmedID': paper.get('pubmed_id', ''),
            'Title': paper.get('title', ''),
            'Publication Date': paper.get('publication_date', ''),
            'Non-academic Author(s)': '; '.join(paper.get('non_academic_authors', [])),
            'Company Affiliation(s)': '; '.join(paper.get('company_affiliations', [])),
            'Corresponding Author Email': paper.get('corresponding_author_email', '')
        }
        data.append(row)

    # Convert to DataFrame for easier handling
    df = pd.DataFrame(data)

    if filename:
        try:
            # Ensure directory exists
            output_dir = os.path.dirname(os.path.abspath(filename))
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Write to CSV
            df.to_csv(filename, index=False, quoting=csv.QUOTE_NONNUMERIC)
            logger.info(f"Results saved to {filename}")
            return filename
        except Exception as e:
            logger.error(f"Error saving results to {filename}: {e}")
            print(f"Error saving results: {e}", file=sys.stderr)
            # Fall back to printing to console
            print(df.to_csv(index=False, quoting=csv.QUOTE_NONNUMERIC))
            return None
    else:
        # Print to console
        print(df.to_csv(index=False, quoting=csv.QUOTE_NONNUMERIC))
        return None
