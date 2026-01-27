import json
import csv
from src.storage import save_to_json, save_to_csv
from src.models import Asset

def test_save_to_json(tmp_path):
    asset = Asset(
        id="bitcoin", rank="1", symbol="BTC", name="Bitcoin",
        priceUsd="60000.00"
    )
    filepath = tmp_path / "output.json"

    save_to_json([asset], str(filepath))

    assert filepath.exists()
    with open(filepath) as f:
        data = json.load(f)
        assert data[0]["id"] == "bitcoin"

def test_save_to_csv(tmp_path):
    asset = Asset(
        id="bitcoin", rank="1", symbol="BTC", name="Bitcoin",
        priceUsd="60000.00"
    )
    filepath = tmp_path / "output.csv"

    save_to_csv([asset], str(filepath))

    assert filepath.exists()
    with open(filepath) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["symbol"] == "BTC"
