from dlso import Mind, Endpoint
from rich import print
from dlso.system_api import *
from dlso.web_api import *
from dlso.data.cma import *
from dlso.mcp import *

from test_lib import *

client = MCPClient(
    endpoint='https://mcp.api-inference.modelscope.cn/sse/d3938d6f10af4e'
)

print(f'Connected to MCP server: {client.server_name} {client.server_version}')

qwq = Endpoint(
    model='deepseek-v3',
    key='sk-gqBb7gEaQ6FNRpGuimJxJCjoEFoyqGqWoxGQM7z1wrF0OACz',
    endpoint='http://yunwu.ai/v1'
)

mind = Mind(model=qwq)

mind.idf.add_mcp(client)

def on_call(func, args, kwargs):
    print('\nCall:', func, f'{args}, {kwargs}')
mind.idf.on_call = on_call

def on_preparing(name):
    print('\nPreparing to call:', name)
mind.on_preparing_call = on_preparing

mind.add_tool([file_opration, directory_operation,
               CMA.req_city_id, CMA.req_now, CMA.req_7d_forecast,
               get_web, post_data, download_file,
               bocha_websearch_tool])

@mind.tool()
def locate_geo():
    '''
    获取用户的大致地理位置. 百度API.
    '''
    return req_json('https://qifu-api.baidubce.com/ip/local/geo/v1/district').get('data')
    # return req_json('https://my.ip.cn/json/').get('data')

def build_tools():
    desp: dict[str, str] = {}
    for t in mind.functions:
        t = t['function']
        desp[t['name']] = t['description']
    mind._notice = [
        #('system', f'You can internally and derectly call tool(s) as bellow without asking user for permission:\n{desp}'),
        #('system', f'Current time: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) }')
    ]

def stream(req:str):
    build_tools()
    mind.add_memory('user', req)
    for i in mind.request(stream=True):
        print(i['content'], end='', flush=True)
    print()

stream('当地明天的天气')