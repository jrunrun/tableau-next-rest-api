import requests
import json
import xml.etree.ElementTree as ET


def get_session_id(
    instance_url: str, username: str, password: str, version: str = "62.0"
) -> str:
    """Get a Salesforce session ID using SOAP login.

    Args:
        instance_url (str): Salesforce instance URL.
        username (str): Salesforce username.
        password (str): Salesforce password.
        version (str): API version.

    Returns:
        str: Session ID.
    """
    url = "https://" + instance_url + "/services/Soap/u/" + version
    headers = {"Content-Type": "text/xml; charset=UTF-8", "SOAPAction": "login"}
    body = """<?xml version="1.0" encoding="utf-8" ?>
                <env:Envelope xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xmlns:env="http://schemas.xmlsoap.org/soap/envelope/">
                <env:Body>
                <n1:login xmlns:n1="urn:partner.soap.sforce.com">
                <n1:username>USERNAME</n1:username>
                <n1:password>PASSWORD</n1:password>
                </n1:login>
                </env:Body>
                </env:Envelope>"""
    body = body.replace("USERNAME", username)
    body = body.replace("PASSWORD", password)
    session_response = requests.post(url, data=body, headers=headers)
    if session_response.status_code != 200:
        print(f"Login Failed! for user {username} on instance {instance_url}")
        print("Response code: ", session_response.status_code)
        print("Res: ", session_response.text)
        exit(1)
    root = ET.fromstring(session_response.text)
    session = root[0].findall(
        "{urn:partner.soap.sforce.com}loginResponse/{urn:partner.soap.sforce.com}result/{"
        "urn:partner.soap.sforce.com}sessionId"
    )[0]
    auth_id = session.text
    print(f"Auth ID: {auth_id}")
    return auth_id


def get_semantic_model(org, model_api_name, session_id):
    url = f'https://{org}/services/data/v62.0/ssot/semantic/models/{model_api_name}'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {session_id}'
    }

    req = requests.get(url, headers=headers)
    return req.json()

def create_semantic_model(org, model_api_name, model_data, session_id):
    url = f'https://{org}/services/data/v62.0/ssot/semantic/models'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {session_id}'
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

# Configuration
org = 'storm-dc631f52cc1aeb.my.salesforce.com'
username = 'jcraycraft.6890ccbb70@salesforce.com'
password = 'orgfarm1234'
source_model_api_name = 'Retail_NTO'
destination_model_name = 'Retail_NTO_Clone5566_june_23'

# Get session ID
session_id = get_session_id(org, username, password)

# Get existing model
model_data = get_semantic_model(org, source_model_api_name, session_id)

# Create new model
new_model = create_semantic_model(org, destination_model_name, model_data, session_id)
