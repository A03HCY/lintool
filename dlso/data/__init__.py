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