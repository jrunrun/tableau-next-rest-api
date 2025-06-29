import requests
import json
import xml.etree.ElementTree as ET

# getSemanticModelCollection
# GET http:///services/data/v62.0/ssot/semantic/models


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


def get_semantic_data_object(org, session_id, modelApiNameOrId, dataObjectName):
    url = f'https://{org}/services/data/v62.0/ssot/semantic/models/{modelApiNameOrId}/data-objects/{dataObjectName}'

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {session_id}'
    }

    req = requests.get(url, headers=headers)

    print(f"Status Code: {req.status_code}")
    print("\nHeaders:")
    print(json.dumps(dict(req.headers), indent=2))
    print("\nResponse Body:")

    # Save the formatted JSON response to a file
    with open('sample-responses/getSemanticDataObject-response.json', 'w') as f:   
        json.dump(req.json(), f, indent=2)

    print("Response has been saved to getSemanticDataObject-response.json")
    print(json.dumps(req.json(), indent=2))

# Example configuration
org = 'storm-dc631f52cc1aeb.my.salesforce.com'
username = 'jcraycraft.6890ccbb70@salesforce.com'
password = 'orgfarm1234'
modelApiNameOrId = 'New_Semantic_Model'
dataObjectName = 'Retail_NTO_Dataverse'


# Get session ID
session_id = get_session_id(org, username, password)

# Get semantic data object using session ID
get_semantic_data_object(org, session_id, modelApiNameOrId, dataObjectName)


