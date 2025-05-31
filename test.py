from dlso import *
from rich import print
import time

mind = Mind(Endpoint(
    model='deepseek-v3',
    key='sk-gqBb7gEaQ6FNRpGuimJxJCjoEFoyqGqWoxGQM7z1wrF0OACz',
    endpoint='http://yunwu.ai/v1'
))

m = MCPGroup()
m.bind(mind)
# m.add_client(['python','-m','mcp_server_fetch'])

@mind.on_preparing()
def on_preparing(name):
    print('\nPreparing to call:', name)

@mind.on_calling()
def on_calling(func, args, kwargs):
    print('\nCalling:', func, 'with', f'{args}', f'{kwargs}')

@mind.on_called()
def on_called(name, result):
    print(f'\nCalled:', name)

mind.add_tool([
    file_opration, directory_operation, archive_operation,
    CMA.req_city_id, CMA.req_now, CMA.req_7d_forecast, locate_geo,
    #fetch_web, post_data, download_file,
])

def build_tools():
    desp: dict[str, str] = {}
    for t in mind.functions:
        t = t['function']
        desp[t['name']] = t['description']
    mind._notice = [
        ('system', f'current time: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) }')
    ]

def stream(req:str):
    build_tools()
    mind.add_content('user', req)
    for i in mind.request(stream=True):
        print(i['content'], end='', flush=True)
    print()


try:
    while True:
        text = input('\n>>> ')
        if text == 'exit':
            break
        if text == '/build':
            print(mind.build_memory)
            continue
        stream(text)
except KeyboardInterrupt:
    print('\nBye!')
