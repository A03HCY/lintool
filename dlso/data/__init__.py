from dataclasses import dataclass, field
from typing      import List

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

email_service_map = {
    'qq.com': {
        'imap': 'imap.qq.com',
        'smtp': 'smtp.qq.com',
    },
    '163.com': {
        'imap': 'imap.163.com',
        'smtp': 'smtp.163.com',
    },
    'gmail.com': {
        'imap': 'imap.gmail.com',
        'smtp': 'smtp.gmail.com',
    },
    'outlook.com': {
        'imap': 'imap-mail.outlook.com',
        'smtp': 'smtp.office365.com',
    },
}

@dataclass
class EmailEndpoint:
    imap: str = field(default=None)
    smtp: str = field(default=None)
    ssl: bool = field(default=True)
    account: str = field(default=None)
    authorization: str = field(default=None)

    def __init__(self, imap=None, smtp=None, ssl=True, account=None, authorization=None):
        self.imap = imap
        self.smtp = smtp
        self.ssl = ssl
        self.account = account
        self.authorization = authorization
        email_service = self.account.split('@')[-1]
        if not self.imap:
            self.imap = email_service_map.get(email_service, {}).get('imap')
        if not self.smtp:
            self.smtp = email_service_map.get(email_service, {}).get('smtp')
        if not self.imap:
            self.imap = 'imap.' + email_service
        if not self.smtp:
            self.smtp = 'smtp.' + email_service

@dataclass
class EmailAttachment:
    filename: str = field(default=None)
    content_type: str = field(default=None)
    content: bytes = field(default=None)
    is_inline: bool = field(default=False)
    cid: str = field(default=None)  # Content-ID

@dataclass
class EmailRecvContent:
    email_id: str = field(default=None)
    subject: str = field(default=None)
    from_addr: dict = field(default_factory=dict)  # {"name":..., "addr":...}
    to_addrs: list = field(default_factory=list)   # list[{"name":..., "addr":...}]
    cc: list = field(default_factory=list)
    bcc: list = field(default_factory=list)
    reply_to: dict = field(default_factory=dict)   # {"name":..., "addr":...}
    date: str = field(default=None)
    message_id: str = field(default=None)
    in_reply_to: str = field(default=None)
    references: str = field(default=None)
    text: str = field(default=None)
    html: str = field(default=None)
    attachments: list[EmailAttachment] = field(default_factory=list)
    flags: list = field(default_factory=list)