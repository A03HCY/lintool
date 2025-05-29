from dlso.email_client import *

e = EmailEndpoint(
    account='acdphc@qq.com',
    authorization='qrhwucnhkozkdebb'
)

print(e)

email_service = EmailService(e)

print(email_service.search(folder='*'))

print(email_service.fetch([1], folder='*'))