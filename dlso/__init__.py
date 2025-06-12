from .utils import (
    try_for, email, safecode, locate_geo, req_file, flatten,
    save_pickle, load_pickle, save_json, load_json, save_yaml, load_yaml
)
from .identify import (
    Identify,  Mind, Endpoint, to_dict_recursive
)
from .file_system import (
    file_opration, directory_operation, archive_operation
)
from .web_fetch import (
    fetch_web, post_data, download_file, req_content, req_json
)
from .weather_forecast import (
    CMA
)
from .mcp import (
    MCPClient, MCPGroup
)
from .email_client import (
    EmailService
)

__version__ = '0.0.1'