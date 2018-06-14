import requests
import oauthlib
import requests_oauthlib
import json
import codecs

client_id = '1950a258-227b-4e31-a9cf-717495945fc2' # a.k.a. Powershell
client_secret = '' # Optional
username = 'your_username' # Do NOT store actual user name!
password = 'your_password' # Do NOT store actual password!
scope = 'openid'
resource = "https://api.partnercenter.microsoft.com"


from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session
oauth = OAuth2Session(client=LegacyApplicationClient(client_id=client_id))
token = oauth.fetch_token(token_url='https://login.windows.net/common/oauth2/token',
        username=username, password=password, client_id=client_id,
        client_secret=client_secret, scope=scope, resource=resource)
#print(token)

bearer_token = 'Bearer ' + token['access_token']

base_url = 'https://api.partnercenter.microsoft.com/v1'

headers = {'Accept': 'application/json', 'Authorization': bearer_token }

# Get list of all customers
# Also see: https://docs.microsoft.com/en-us/partner-center/develop/get-a-list-of-customers

size= 100
request_url = base_url + "/customers?size=%d" % size

response = requests.get(request_url, headers = headers)

if response.status_code == requests.codes.ok:
        response.encoding = "utf-8-sig" # To remove annoying Unicode BOM

        customers_dict = response.json()

        for customer in customers_dict['items']:
                print("Customer:", customer['companyProfile']['companyName'],
                        "Tenant ID:", customer['companyProfile']['tenantId'],
                        "Domain Name:", customer['companyProfile']['domain'])
                # Retrieve order history of customer
                # Also see: https://docs.microsoft.com/en-us/partner-center/develop/get-all-of-a-customer-s-orders
                request_url = base_url + customer['links']['self']['uri'] + "/orders"

                response = requests.get(request_url, headers = headers)
                if response.status_code == requests.codes.ok:
                        response.encoding = "utf-8-sig" # To remove annoying Unicode BOM

                        orders_dict = response.json()
                        print(">>> Total orders:", orders_dict['totalCount'])
                        idx = 1
                        for order in orders_dict['items']:
                                print(">>> Order entry:", idx)
                                for lineItem in order['lineItems']:
                                        print(">>> >>> Order ID:", order['id'], ", OfferId:", lineItem['offerId'], ", OfferName:", lineItem.get('friendlyName', "empty"), 
                                        ", Quantity:", lineItem['quantity'], ", CreationDate:", order['creationDate'],
                                        ", Status:", order['status'], ", ObjectType:", order['attributes']['objectType']  )
                                idx = idx + 1

                print("\n")

print('Done!')
