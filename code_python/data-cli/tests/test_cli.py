import pytest
from typer.testing import CliRunner
import respx
from src.cli import app

runner = CliRunner()

@respx.mock
def test_cli_fetch_success(tmp_path):
    mock_data = {
        "data": [
            {
                "id": "bitcoin",
                "rank": "1",
                "symbol": "BTC",
                "name": "Bitcoin",
                "supply": "18000000",
                "maxSupply": "21000000",
                "marketCapUsd": "1000000000",
                "volumeUsd24Hr": "500000000",
                "priceUsd": "60000.00",
                "changePercent24Hr": "1.5",
                "vwap24Hr": "60050.00"
            }
        ],
        "timestamp": 1617753600000
    }

    respx.get("https://api.coincap.io/v2/assets").respond(json=mock_data)

    result = runner.invoke(app, ["--limit", "1"])
    assert result.exit_code == 0
    assert "Bitcoin" in result.stdout
    assert "Successfully fetched 1 assets" in result.stdout

@respx.mock
def test_cli_fetch_save_file(tmp_path):
    mock_data = {
        "data": [
             {
                "id": "bitcoin",
                "rank": "1",
                "symbol": "BTC",
                "name": "Bitcoin",
                "priceUsd": "60000.00"
            }
        ],
        "timestamp": 123456789
    }
    respx.get("https://api.coincap.io/v2/assets").respond(json=mock_data)

    output_file = tmp_path / "data.json"
    result = runner.invoke(app, ["--output", str(output_file)])
    assert result.exit_code == 0
    assert output_file.exists()
