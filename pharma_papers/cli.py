"""
Command-line interface for the pharma_papers package.
"""

import logging
import sys
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from pharma_papers.paper_processor import PaperProcessor
from pharma_papers.pubmed_client import PubMedClient
from pharma_papers.utils import export_to_csv

# Set up typer app
app = typer.Typer(help="Fetch research papers from PubMed with pharmaceutical company affiliations")

# Set up rich console for pretty output
console = Console()


def setup_logging(debug: bool = False) -> None:
    """
    Configure logging level based on debug flag.

    Args:
        debug: Enable debug logging
    """
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


@app.command()
def main(
        query: str = typer.Argument(
            ...,
            help="PubMed query string (follows PubMed's query syntax)"
        ),
        file: Optional[str] = typer.Option(
            None,
            "-f", "--file",
            help="Output filename for CSV results (if not provided, prints to console)"
        ),
        debug: bool = typer.Option(
            False,
            "-d", "--debug",
            help="Enable debug mode with verbose logging"
        ),
        max_results: int = typer.Option(
            100,
            "-m", "--max",
            help="Maximum number of results to fetch from PubMed"
        ),
        email: str = typer.Option(
            "user@example.com",
            "--email",
            help="Email address for NCBI API (required by their terms of service)"
        ),
        api_key: Optional[str] = typer.Option(
            None,
            "--api-key",
            help="NCBI API key for higher rate limits (optional)"
        ),
) -> None:
    """
    Fetch research papers based on a PubMed query and identify those with authors
    affiliated with pharmaceutical or biotech companies.

    Results are returned as a CSV file with details about the papers and their
    non-academic authors.
    """
    # Set up logging
    setup_logging(debug)

    # Initialize client and processor
    pubmed_client = PubMedClient(email=email, api_key=api_key, debug=debug)
    paper_processor = PaperProcessor(debug=debug)

    try:
        with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
        ) as progress:
            # Search PubMed
            search_task = progress.add_task(f"Searching PubMed for: {query}", total=1)
            id_list = pubmed_client.search(query, max_results=max_results)
            progress.update(search_task, completed=1)

            if not id_list:
                console.print("[bold red]No papers found matching the query.[/bold red]")
                sys.exit(0)

            # Fetch paper details
            fetch_task = progress.add_task(f"Fetching details for {len(id_list)} papers", total=1)
            papers = pubmed_client.fetch_details(id_list)
            progress.update(fetch_task, completed=1)

            # Process papers to identify pharmaceutical affiliations
            process_task = progress.add_task("Identifying papers with pharmaceutical affiliations", total=1)
            pharma_papers = paper_processor.process_papers(papers)
            progress.update(process_task, completed=1)

            # Export results
            export_task = progress.add_task("Exporting results", total=1)
            export_to_csv(pharma_papers, file)
            progress.update(export_task, completed=1)

        # Print summary
        console.print(
            f"[bold green]Found {len(pharma_papers)} papers with pharmaceutical company affiliations[/bold green]")
        if file:
            console.print(f"[bold green]Results saved to: {file}[/bold green]")

    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
        if debug:
            raise
        sys.exit(1)


if __name__ == "__main__":
    app()
