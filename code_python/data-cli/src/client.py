import httpx
from .models import AssetResponse

class CryptoClient:
    BASE_URL = "https://api.coincap.io/v2"

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def get_assets(self, limit: int = 10) -> AssetResponse:
        url = f"{self.BASE_URL}/assets"
        params = {"limit": limit}

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                return AssetResponse.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            raise ValueError(f"HTTP Error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            raise ConnectionError(f"Network Error: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected Error: {e}")
