import dlso

ep = dlso.Endpoint(
    model='text-embedding-3-small',
    key='sk-fxZcN6GZbKn5hk6BjgwypFevWl5oO2rF6xNMA3YwVmZOR3WN',
    endpoint='https://yunwu.ai/v1'
)

print(ep.embed('hello world', 'text-embedding-3-large'))