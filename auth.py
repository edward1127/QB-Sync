# from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from quickbooks import QuickBooks
# selfchanged version of intuitlib.client
from intuitlib_self_version.client import AuthClient
import os

'''
When make a request it will automatically print the content of response Change it in intuitlib.ulib if it's in production mode.
'''

auth_client = AuthClient(
        client_id= os.getenv("INTUIT_CLIENT_ID"), 
        client_secret= os.getenv("INTUIT_CLIENT_SECRET"), 
        environment= os.getenv("INTUIT_ENVIRONMENT"), 
        redirect_uri= os.getenv("INTUIT_REDIRECT_URI") 
    )

# get get_authorization_url
print ('authorization_url: ' + auth_client.get_authorization_url([Scopes.ACCOUNTING]))

client = QuickBooks(
        auth_client=auth_client,
      # refresh_token = already set refresh token in TOKEN_SHEET
        company_id=os.getenv("INTUIT_COMPANY_ID"),
    )



