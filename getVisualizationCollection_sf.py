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

def get_visualizations_with_sf(sf) -> dict[str, Any]:
    """Fetch all available visualizations using simple-salesforce.
    
    Args:
        sf: Authenticated Salesforce instance from simple-salesforce
            Example: sf = Salesforce(
                instance_url='https://your-instance.salesforce.com',
                session_id='your-session-id'
            )
            
    Returns:
        Dictionary containing the visualization collection response
        
    Raises:
        requests.exceptions.RequestException: If the API request fails
    """
    
    # Define the endpoint
    endpoint = "/services/data/v64.0/tableau/visualizations"
    
    try:
        # Print full URL for debugging
        print(f"Making request to endpoint: {endpoint}")
        
        # Make the GET request using sf.restful
        response = sf.restful(endpoint, method='GET')
        
        # Save the formatted JSON response to a file
        with open('./sample-responses/getVisualizations-response.json', 'w') as f:
            json.dump(response, f, indent=2)
            
        print("Response has been saved to getVisualizations-response.json")
        
        # Print formatted response to console
        print("Response:")
        print(json.dumps(response, indent=2))
        
        return response
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching visualizations: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"\nStatus Code: {e.response.status_code}")
            print("\nHeaders:")
            print(json.dumps(dict(e.response.headers), indent=2))
            print("\nResponse Body:")
            print(f"Error: {e.response.text}")
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

get_visualizations_with_sf(sf)