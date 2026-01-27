# Day 06: Building a Robust Data CLI with Typer

**Author:** dattskoushik
**Date:** 2023-10-06

## The Problem
In the lifecycle of a Data Engineer, ad-hoc data retrieval is a frequent necessity. Whether it's inspecting the latest state of a third-party API, debugging integration issues, or grabbing a snapshot of market data for local analysis, relying on tools like `curl` or Postman often feels cumbersome for repetitive tasks. `curl` output is hard to read without piping to `jq`, and Postman is a heavy GUI.

Developers need a lightweight, scriptable, and strongly-typed way to pull data from external sources and persist it locally in structured formats like JSON or CSV for immediate consumption by other tools (e.g., Pandas, Excel).

## The Solution
For Day 06, I built a Command Line Interface (CLI) tool using **Typer**, a modern library for building CLIs that leverages Python 3.6+ type hints. This tool interacts with the **CoinCap API** to fetch real-time cryptocurrency market data.

### Key Features
1.  **Type-Safe Arguments**: Using `typer`, command-line arguments are automatically validated based on Python type hints.
2.  **Robust Networking**: Utilizing `httpx` for efficient HTTP requests with proper error handling for network failures and status codes.
3.  **Data Validation**: All incoming data is validated against **Pydantic** models. This ensures that we only process data that matches our schema, failing fast on malformed responses.
4.  **Flexible Output**: The tool supports exporting data to both JSON (for developers) and CSV (for analysts) formats.

### Architecture
-   **`src/client.py`**: Encapsulates the API interaction logic, handling timeouts and exceptions.
-   **`src/models.py`**: Defines the data structure using Pydantic `BaseModel`.
-   **`src/storage.py`**: Handles file I/O, ensuring directory existence and format conversion.
-   **`src/cli.py`**: The entry point that orchestrates the flow using Typer commands.

### Code Snippet: The CLI Entry Point
```python
@app.command()
def fetch(
    limit: int = typer.Option(10, help="Number of assets to fetch"),
    format: OutputFormat = typer.Option(OutputFormat.json, help="Output format"),
    output: Optional[Path] = typer.Option(None, help="Output file path")
):
    client = CryptoClient()
    try:
        typer.echo(f"Fetching top {limit} assets...")
        response = client.get_assets(limit=limit)

        if output:
            save_data(response.data, output, format)
            typer.echo(f"Data saved to {output}")
        else:
            display_data(response.data)

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)
```

## Use Cases
1.  **Market Snapshots**: A cron job can run this CLI every hour to save a CSV snapshot of the crypto market, building a historical dataset over time.
2.  **Integration Testing**: The CLI can be used in CI/CD pipelines to verify that the upstream API is reachable and returning valid data before deploying dependent services.
3.  **Data Ingestion**: Serving as the "Extract" step in a lightweight ETL pipeline, feeding data into a local SQLite database or a data lake.

## Conclusion
Building a CLI with Typer turns a simple script into a professional developer tool. By combining it with Pydantic for validation and httpx for networking, we ensure that our data ingestion process is reliable, maintainable, and easy to use.
