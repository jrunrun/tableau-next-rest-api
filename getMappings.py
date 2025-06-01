import requests
import json

# getDataStreams
# GET
# https://{dne_cdpInstanceUrl}/services/data/v64.0/ssot/data-streams
# Get a list of data streams.
# Available Version: 60.0


def get_auth_token(org, client_id, client_secret):
    url = f"https://{org}/services/oauth2/token"

    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }

    req = requests.post(url, data=data)

    # Print to console
    print(json.dumps(req.json(), indent=2))
    return req.json()['access_token']


def get_connection(org, auth_token, version, dmo_developer_name, dlo_developer_name):
    base_url = f'https://{org}/services/data/{version}/ssot/data-model-object-mappings'
    
    print(f"URL for getting mappings: {base_url}")

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {auth_token}'
    }

    params = {
        'dmoDeveloperName': dmo_developer_name,
        'dloDeveloperName': dlo_developer_name
    }

    print("Request URL:", base_url)
    print("Request Parameters:", params)
    print("Full URL with params:", req.url)

    req = requests.get(base_url, headers=headers, params=params)

    print(f"Status Code: {req.status_code}")
    print("\nHeaders:")
    print(json.dumps(dict(req.headers), indent=2))
    print("\nResponse Body:")

    if req.status_code == 200:
        # Save the formatted JSON response to a file
        with open('./sample-responses/getMappings-response.json', 'w') as f:
            json.dump(req.json(), f, indent=2)

        print("Response has been saved to getMappings-response.json")

        # Print to console
        print(json.dumps(req.json(), indent=2))
    else:
        print(f"Status Code: {req.status_code}")
        print("\nHeaders:")
        print(json.dumps(dict(req.headers), indent=2))
        print("\nResponse Body:")
        print(f"Error: {req.text}")

# # This works:
# Brian's Tab Next org:
# org = 'g43wknrqmjqtgyjzh0ytg9bvh0.c360a.salesforce.com'
org = 'storm-dc631f52cc1aeb.my.salesforce.com'
client_id = '3MVG9Rr0EZ2YOVMb5hDLho4ts6.27uw4kvfO9UkOFoRBAsqB96g5uInaQxhNLDziFmAQ37cSShk6oP1AlKIAc'
client_secret = 'CCB1D74A53C328EA748FBF5F4BB2AE4CE50107582B1CDEFE049BF8F1C3576444'
version = 'v63.0'
connectionId = '9cgHo000000wl7JIAQ'
dmo_developer_name = 'Sample_Superstore_Orderscsv__dlm'
dlo_developer_name = 'Sample_Superstore_Orderscsv__dll'

# This works:
# # Justin's Tab Next org (Radhika instructions via Orgfarm):
# org = 'orgfarm-ef60436573.test13.my.pc-rnd.salesforce.com'
# client_id = '3MVG9kfeuo6xCm.pZ4_qdu_PhqIsuIBOpnpN_p66AXqTIVnptJ21r2NaGIf6WlnJJPRyiciWzhZiBZ1SNLgM9'
# client_secret = '80733EDD3B5BFBD8D55CF08E4C736C6118EB78A25D75AD6C09336C6D77C56071'


# # This works:
# org = 'storm-4dd15a23353ff1.my.salesforce.com'
# client_id = '3MVG9aNlkJwuH9vNgV7dXX1mD8GNBYtkSyCXndzm6SOm.MbFeeb91ah9LUompVf83kEnPwbcpdSCJyDJZZti5'
# client_secret = '5221881FFC65D1D328C202C8BAC234209A9F515A01C402A3CD5FBFCEB7E00570'










# Get auth token    
auth_token = get_auth_token(org, client_id, client_secret)

# Get semantic models
get_connection(org, auth_token, version, dmo_developer_name, dlo_developer_name)






