from dlso import try_for
import requests
import os
import time


# 全局会话对象
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

# 全局配置
CONFIG = {
    'timeout': 30,
    'max_retries': 3
}


@try_for(3)
def req_json(url: str) -> dict:
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

@try_for(3)
def req_content(url: str) -> str:
    r = requests.get(url)
    r.raise_for_status()
    return r.content.decode('utf-8')

def fetch_web(url: str, params: dict = None, headers: dict = None) -> dict:
    '''
    获取互联网内容，如网页，js代码等
    
    Args:
        url: 目标URL
        params: URL参数
        headers: 自定义请求头
        
    Returns:
        包含状态码和网页内容的字典
    '''
    merged_headers = headers or {}
    
    for attempt in range(CONFIG['max_retries']):
        try:
            response = session.get(
                url, 
                params=params, 
                headers=merged_headers, 
                timeout=CONFIG['timeout']
            )
            return {
                'success': True,
                'status_code': response.status_code,
                'content': response.text,
                'url': response.url
            }
        except Exception as e:
            if attempt == CONFIG['max_retries'] - 1:
                return {
                    'success': False,
                    'message': f"请求失败: {str(e)}",
                    'url': url
                }
            time.sleep(1)  # 重试前等待1秒
    
    return {
        'success': False,
        'message': "请求失败: 达到最大重试次数",
        'url': url
    }

def post_data(url: str, data: dict = None, json_data: dict = None, headers: dict = None) -> dict:
    '''
    发送POST请求
    
    Args:
        url: 目标URL
        data: 表单数据
        json_data: JSON数据
        headers: 自定义请求头
        
    Returns:
        包含状态码和响应内容的字典
    '''
    merged_headers = headers or {}
    
    for attempt in range(CONFIG['max_retries']):
        try:
            response = session.post(
                url, 
                data=data, 
                json=json_data, 
                headers=merged_headers, 
                timeout=CONFIG['timeout']
            )
            return {
                'success': True,
                'status_code': response.status_code,
                'content': response.text,
                'url': response.url
            }
        except Exception as e:
            if attempt == CONFIG['max_retries'] - 1:
                return {
                    'success': False,
                    'message': f"请求失败: {str(e)}",
                    'url': url
                }
            time.sleep(1)  # 重试前等待1秒
    
    return {
        'success': False,
        'message': "请求失败: 达到最大重试次数",
        'url': url
    }

def download_file(url: str, save_path: str, chunk_size: int = 1024) -> dict:
    '''
    下载文件到指定路径
    
    Args:
        url: 文件URL
        save_path: 保存路径
        chunk_size: 每次读取的块大小（字节）
        
    Returns:
        包含下载结果信息的字典
    '''
    # 创建目录（如果不存在）
    try:
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
    except Exception as e:
        return {
            'success': False,
            'message': f"创建目录失败: {str(e)}",
            'url': url,
            'save_path': save_path
        }
    
    for attempt in range(CONFIG['max_retries']):
        try:
            response = session.get(url, stream=True, timeout=CONFIG['timeout'])
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'message': f"请求失败: HTTP状态码 {response.status_code}",
                    'status_code': response.status_code,
                    'url': url,
                    'save_path': save_path
                }
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
            
            return {
                'success': True,
                'message': f"文件下载成功",
                'url': url,
                'save_path': save_path,
                'file_size': downloaded_size,
                'total_size': total_size
            }
        except Exception as e:
            if attempt == CONFIG['max_retries'] - 1:
                return {
                    'success': False,
                    'message': f"下载失败: {str(e)}",
                    'url': url,
                    'save_path': save_path
                }
            time.sleep(1)  # 重试前等待1秒
    
    return {
        'success': False,
        'message': "下载失败: 达到最大重试次数",
        'url': url,
        'save_path': save_path
    }