from dataclasses import dataclass, field
from typing      import List, Optional

@dataclass
class EmailMatch:
    matched_email: str = field(default=None)
    is_email: bool     = field(default=False)


@dataclass
class Notification:
    channel: str = field(default='<channel>')
    noticer: str = field(default='<notify>')
    kwargs: dict = field(default_factory=dict)


@dataclass
class GeoPoint:
    lat: float = field(default=None)
    lon: float = field(default=None)


@dataclass
class CityInfo:
    city_id:str = field(default=None)
    name_zh:str = field(default=None)
    name_en:str = field(default=None)
    province_zh:str = field(default=None)
    province_en:str = field(default=None)
    geo:GeoPoint = field(default_factory=GeoPoint)


@dataclass
class CitySearchResult:
    success: bool = field(default=False)
    result_num: int = field(default=0)
    matches: List[CityInfo] = field(default_factory=list)