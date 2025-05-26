from dlso   import *
from jinja2 import Template
from rich   import print

temp = Template(req_file('aqg.md')).render(
    material=req_file('m.md'),
    request=req_file('r.md'),
)

mind = Mind(Endpoint(
    model='deepseek-v3', #'gemini-2.5-pro-preview-05-06',
    key='sk-gqBb7gEaQ6FNRpGuimJxJCjoEFoyqGqWoxGQM7z1wrF0OACz',
    endpoint='http://yunwu.ai/v1'
))
mind.add_predefined_prompt('system', temp)

def stream(req:str):
    mind.add_content('user', req)
    for i in mind.request(stream=True, max_tokens=16384, temperature=0.1):
        print(i['content'], end='', flush=True)
    print()

stream('start.')