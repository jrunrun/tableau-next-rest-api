import requests
import json


def get_auth_token(org, client_id, client_secret):
    url = f"https://{org}/services/oauth2/token"

    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }

    req = requests.post(url, data=data)
    return req.json()['access_token']


def get_semantic_model(org, model_api_name, auth_token):
    url = f'https://{org}/services/data/v62.0/ssot/semantic/models/{model_api_name}'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {auth_token}'
    }

    req = requests.get(url, headers=headers)
    return req.json()

def create_semantic_model(org, model_api_name, model_data, auth_token):
    url = f'https://{org}/services/data/v62.0/ssot/semantic/models'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {auth_token}'
    }

    
    # Create a new model based on the existing one
    new_model = {
        "apiName": model_api_name,
        "label": f"{model_api_name} Justin",
        "dataspace": "default",
        "semanticCalculatedDimensions": model_data.get('semanticCalculatedDimensions', []),
        "semanticCalculatedMeasurements": model_data.get('semanticCalculatedMeasurements', []),
        "semanticDataObjects": model_data.get('semanticDataObjects', []),
        "semanticGroupings": model_data.get('semanticGroupings', []),
        "semanticLogicalViews": model_data.get('semanticLogicalViews', []),
        "semanticMetrics": model_data.get('semanticMetrics', []),
        "semanticParameters": model_data.get('semanticParameters', []),
        "semanticRelationships": model_data.get('semanticRelationships', [])
    }
    
    # Send POST request to create new model
    req = requests.post(url, headers=headers, data=json.dumps(new_model))
    
    print(f"Status Code: {req.status_code}")
    print("\nHeaders:")
    print(json.dumps(dict(req.headers), indent=2))
    print("\nResponse Body:")
    print(json.dumps(req.json(), indent=2))
    
    return req.json()

# Example authorization headers
headers = {
    "Authorization": "Bearer 00DHo000003yF1p!ARIAQIsY7uHB72amRNWXwU2FF2pFEP6lHSORsYNUwcuwYb9MGW7AqrXndRfvgIg6jubtZNsuvvv31c8m5Y8mafZm5dnz2j9U"
}

org = 'storm-dc631f52cc1aeb.my.salesforce.com'
source_model_api_name = 'Retail_NTO'
destination_model_name = 'Retail_NTO_Clone55'
client_id = '3MVG9Rr0EZ2YOVMb5hDLho4ts6.27uw4kvfO9UkOFoRBAsqB96g5uInaQxhNLDziFmAQ37cSShk6oP1AlKIAc'
client_secret = 'CCB1D74A53C328EA748FBF5F4BB2AE4CE50107582B1CDEFE049BF8F1C3576444'


# Get auth token    
auth_token = get_auth_token(org, client_id, client_secret)

# Get existing model
model_data = get_semantic_model(org, source_model_api_name, auth_token)

# Create new model
new_model = create_semantic_model(org, destination_model_name, model_data, auth_token)
