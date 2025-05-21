from typing       import Dict, Optional, Union
from sseclient    import SSEClient
from urllib.parse import urlparse
import threading
import requests
import queue
import json

class MCPClient:
    def __init__(self, endpoint, name='mcp', version='0.1.0'):
        self.client_name = name
        self.client_version = version
        self.server_name = None
        self.server_version = None
        self.base_url = self._parse_base_url(endpoint)
        self.session = None
        self.endpoint = endpoint
        self.endpoint_ready = threading.Event()
        self.response_queues = {}
        self.lock = threading.Lock()
        self._running = True
        self._next_id = 0  # 自增ID计数器

        # 启动消息接收线程
        self.recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
        self.recv_thread.start()
        try:
            self._init_client()
        except:
            self._running = False
    
    def _init_client(self):
        data = self.post(
            method="initialize",
            params={
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": self.client_name,
                    "version": self.client_version,
                }
            }
        )
        data = data.get('result', {}).get("serverInfo", {})
        self.server_name = data.get("name")
        self.server_version = data.get("version")
        self.post(
            method="notifications/initialized",
            wait_for_response=False
        )

    def _parse_base_url(self, endpoint):
        """从endpoint解析基础URL"""
        parsed = urlparse(endpoint)
        return f"{parsed.scheme}://{parsed.netloc}"

    def _recv_loop(self):
        messages = SSEClient(self.endpoint)
        
        event = None
        for msg in messages:
            if not self._running:
                break

            if not msg.data:
                event = msg.event
                continue

            if event == "endpoint" or 'session_id' in msg.data:
                self.session = msg.data
                self.endpoint_ready.set()
                event = msg.event
                continue

            try:
                data = json.loads(msg.data)
                msg_id = data.get("id")
            except json.JSONDecodeError:
                continue

            with self.lock:
                if msg_id in self.response_queues:
                    self.response_queues[msg_id].put(data)
                else:
                    print(f"Unmatched response (id={msg_id})")

    def post(self, method=None, params=None, timeout=10, wait_for_response=True):
        self.endpoint_ready.wait()

        # 构造请求数据
        if method is None:
            raise ValueError("Either method or data must be provided")

        data = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {}
        }


        # 注册响应队列
        if wait_for_response:
            # 生成自增ID（线程安全）
            with self.lock:
                request_id = self._next_id
                data['id'] = request_id
                self._next_id += 1
            with self.lock:
                self.response_queues[request_id] = queue.Queue()

        # 构建完整URL
        full_url = f"{self.base_url}{self.session}"

        try:
            response = requests.post(
                full_url,
                json=data,
                timeout=5
            )
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Request failed: {str(e)}")

        if not wait_for_response:
            return {"status": "sent", "code": response.status_code}

        try:
            with self.lock:
                q = self.response_queues.get(request_id)
            
            if q is None:
                raise ValueError("Response queue not found")

            response_data = q.get(timeout=timeout)
        except queue.Empty:
            raise TimeoutError(f"Response timeout (id={request_id})")
        finally:
            with self.lock:
                if request_id in self.response_queues:
                    del self.response_queues[request_id]

        return response_data
    
    def list_tools(self): # 列出所有工具
        return self.post(
            method="tools/list",
            params={}
        ).get('result', {}).get("tools", [])
    
    def call_tool(self, tool_name, input_data: dict={}):
        return self.post(
            method="tools/call",
            params={
                "name": tool_name,
                "arguments": input_data
            },
            timeout=None
        )

    def close(self):
        self._running = False
    

class MCPGroup:
    def __init__(self):
        from .identify import Identify
        """初始化MCPGroup，管理多个MCPClient实例"""
        self._clients: Dict[str, MCPClient] = {}
        self._bound_identify: Optional[Identify] = None
    
    def add_client(self, client: Union[MCPClient, str]) -> None:
        """添加一个MCPClient到组中
        
        Args:
            client: MCPClient实例或endpoint字符串
        """
        if isinstance(client, str):
            client = MCPClient(endpoint=client)
        
        if not isinstance(client, MCPClient):
            raise TypeError("client must be an instance of MCPClient or a string")
            
        if not client.server_name:
            raise ValueError("client.server_name is not set")
            
        if client.server_name in self._clients:
            raise ValueError(f"client with server_name '{client.server_name}' already exists")
        
        print(f'Added client: {client.server_name} ({client.server_version})')

        self._clients[client.server_name] = client
        
        # 自动绑定到已绑定的Identify实例
        if self._bound_identify:
            self._bound_identify.add_mcp(client)
    
    def remove_client(self, name: str) -> None:
        """从组中移除一个MCPClient
        
        Args:
            name: 要移除的客户端名称
        """
        if name in self._clients:
            # 从已绑定的Identify实例中移除
            if self._bound_identify:
                self._bound_identify.remove_mcp(name)
            del self._clients[name]
    
    def req_client(self, name: str) -> Optional[MCPClient]:
        """获取指定名称的MCPClient
        
        Args:
            name: 客户端名称
            
        Returns:
            MCPClient实例，如果不存在则返回None
        """
        return self._clients.get(name)
    
    def bind(self, identify) -> None:
        """绑定Identify实例并加载所有MCPClient
        
        Args:
            identify: Identify实例
        """
        from .identify import Identify, Mind
        if isinstance(identify, Mind):
            identify = identify.idf
        if not isinstance(identify, Identify):
            raise TypeError("identify must be an instance of Identify")
            
        self._bound_identify = identify
        for client in self._clients.values():
            identify.add_mcp(client)