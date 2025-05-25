from dlso.email import *

e = EmailEndpoint(
    account='acdphc@qq.com',
    authorization='qrhwucnhkozkdebb'
)

print(e)

email_service = EmailService(e)
print(email_service.fetch([2712]))