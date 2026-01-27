from pydantic import BaseModel
from typing import List, Optional

class Asset(BaseModel):
    id: str
    rank: str
    symbol: str
    name: str
    supply: Optional[str] = None
    maxSupply: Optional[str] = None
    marketCapUsd: Optional[str] = None
    volumeUsd24Hr: Optional[str] = None
    priceUsd: str
    changePercent24Hr: Optional[str] = None
    vwap24Hr: Optional[str] = None
    explorer: Optional[str] = None

class AssetResponse(BaseModel):
    data: List[Asset]
    timestamp: int
