# 1. upload csv to s3
# 2. create data stream
# 3. run data stream
# 4. create dmo mapping or create semantic model


import simple_salesforce
from simple_salesforce import Salesforce, SalesforceMalformedRequest
import requests
import xml.etree.ElementTree as ET
import json
from typing import Any


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

def get_visualizations_with_requests(base_url: str, access_token: str) -> dict[str, Any]:
    """Fetch all available visualizations using requests.
    
    Args:
        base_url: The base URL for the Tableau API (e.g., 'https://your-instance.salesforce.com')
        access_token: OAuth access token for authentication
        
    Returns:
        Dictionary containing the visualization collection response
        
    Raises:
        requests.exceptions.RequestException: If the API request fails
    """
    import requests
    
    # Construct the endpoint using the standard Salesforce API format
    endpoint = f"{base_url}/services/data/v64.0/tableau/dashboards"
    print(f"Endpoint: {endpoint}")
    
    # Set up headers with authentication
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        # Make the GET request
        response = requests.get(endpoint, headers=headers)
        
        # Print response details for debugging
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print("Response Text:")
        try:
            print(json.dumps(response.json(), indent=2))
            # Save the formatted JSON response to a file
            with open('./sample-responses/getDashboardCollection-response.json', 'w') as f:
                json.dump(response.json(), f, indent=2)
            print("Response has been saved to getDashboardCollection-response.json")
        except json.JSONDecodeError:
            print(response.text)
        
        # Raise an error for bad status codes
        response.raise_for_status()
        
        # Return the JSON response
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching visualizations: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response Status Code: {e.response.status_code}")
            print(f"Response Headers: {e.response.headers}")
            print(f"Response Text: {e.response.text}")
        raise

org = 'storm-dc631f52cc1aeb.my.salesforce.com'
username = 'jcraycraft.6890ccbb70@salesforce.com'
password = 'orgfarm1234'
data_space = 'default'

auth_token = get_session_id(org, username, password)

sf = Salesforce(
    session_id=auth_token, 
    instance_url="https://" + org, 
    version='v64.0'
)

get_visualizations_with_requests("https://" + org, auth_token)