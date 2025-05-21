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
class AlarmInfo:
    id: str = field(default=None)
    title: str = field(default=None)
    headline: str = field(default=None)
    effective_time: str = field(default=None)
    description: str = field(default=None)
    geo: GeoPoint = field(default_factory=GeoPoint)


@dataclass
class AlarmResult:
    success: bool = field(default=False)
    alarms:List[AlarmInfo] = field(default_factory=list)


@dataclass
class CityID:
    id: str = field(default=None)
    city_zh: str = field(default=None)
    city_en: str = field(default=None)
    country: str = field(default=None)


@dataclass
class WeatherNow:
    precipitation: float = field(default=None)
    temperature: float = field(default=None)
    pressure: float = field(default=None)
    humidity: float = field(default=None)
    wind_degree: float = field(default=None)
    wind_speed: float = field(default=None)
    city: CityID = field(default_factory=CityID)
    time: str = field(default=None)


@dataclass
class HourlyForecast:
    time: str = field(default=None)
    temperature: str = field(default=None)
    precipitation: str = field(default=None)
    wind_speed: str = field(default=None)
    wind_direction: str = field(default=None)
    pressure: str = field(default=None)
    humidity: str = field(default=None)
    cloudiness: str = field(default=None)

@dataclass
class WeatherForecast:
    date: str
    day_weather: str
    day_wind: str
    night_weather: str
    night_wind: str
    high: str
    low: str
    hours: List[HourlyForecast] = field(default_factory=list)