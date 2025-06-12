import requests
import json

# getSemanticModelCollection
# GET http:///services/data/v62.0/ssot/semantic/models


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

def get_semantic_data_object_collection(org, auth_token, modelApiNameOrId):
    # url = f'https://{org}/services/data/v62.0/ssot/semantic/models'
    url = f'https://{org}/services/data/v62.0/ssot/semantic/models/{modelApiNameOrId}/data-objects'

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {auth_token}'
    }

    req = requests.get(url, headers=headers)

    print(f"Status Code: {req.status_code}")
    print("\nHeaders:")
    print(json.dumps(dict(req.headers), indent=2))
    print("\nResponse Body:")

    # Save the formatted JSON response to a file
    with open('sample-responses/getSemanticDataObjectCollection-response.json', 'w') as f:   
        json.dump(req.json(), f, indent=2)

    print("Response has been saved to getSemanticDataObjectCollection-response.json")

    # Print to console
    print(json.dumps(req.json(), indent=2))

# # This works:
# Brian's Tab Next org:
org = 'storm-dc631f52cc1aeb.my.salesforce.com'
client_id = '3MVG9Rr0EZ2YOVMb5hDLho4ts6.27uw4kvfO9UkOFoRBAsqB96g5uInaQxhNLDziFmAQ37cSShk6oP1AlKIAc'
client_secret = 'CCB1D74A53C328EA748FBF5F4BB2AE4CE50107582B1CDEFE049BF8F1C3576444'


modelApiNameOrId = 'New_Semantic_Model'

# This works:
# Justin's Tab Next org (Radhika instructions via Orgfarm):
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
get_semantic_data_object_collection(org, auth_token, modelApiNameOrId)


