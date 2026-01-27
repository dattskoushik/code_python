import typer
from typing import Optional
from enum import Enum
from pathlib import Path
from .client import CryptoClient
from .storage import save_to_json, save_to_csv

app = typer.Typer()

class OutputFormat(str, Enum):
    json = "json"
    csv = "csv"

@app.command()
def fetch(
    limit: int = typer.Option(10, help="Number of assets to fetch"),
    format: OutputFormat = typer.Option(OutputFormat.json, help="Output format (json or csv)"),
    output: Optional[Path] = typer.Option(None, help="Output file path")
):
    """
    Fetch cryptocurrency data from CoinCap API.
    """
    client = CryptoClient()
    try:
        typer.echo(f"Fetching top {limit} assets...")
        response = client.get_assets(limit=limit)
        data = response.data
        typer.echo(f"Successfully fetched {len(data)} assets.")

        if output:
            # If output does not have an extension, append one based on format
            if not output.suffix:
                output = output.with_suffix(f".{format.value}")

            if format == OutputFormat.json:
                save_to_json(data, str(output))
            elif format == OutputFormat.csv:
                save_to_csv(data, str(output))
            typer.echo(f"Data saved to {output}")
        else:
            # Print to stdout if no output file
            for asset in data:
                typer.echo(f"{asset.rank}. {asset.name} ({asset.symbol}): ${float(asset.priceUsd):.2f}")

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)
