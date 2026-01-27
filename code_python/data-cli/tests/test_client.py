import pytest
import respx
import httpx
from src.client import CryptoClient

@respx.mock
def test_get_assets_success():
    client = CryptoClient()
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

    response = client.get_assets(limit=1)
    assert len(response.data) == 1
    assert response.data[0].name == "Bitcoin"
    assert response.timestamp == 1617753600000

@respx.mock
def test_get_assets_http_error():
    client = CryptoClient()
    respx.get("https://api.coincap.io/v2/assets").respond(status_code=500)

    with pytest.raises(ValueError, match="HTTP Error: 500"):
        client.get_assets()

@respx.mock
def test_get_assets_network_error():
    client = CryptoClient()
    respx.get("https://api.coincap.io/v2/assets").mock(side_effect=httpx.RequestError("Failure"))

    with pytest.raises(ConnectionError, match="Network Error"):
        client.get_assets()
