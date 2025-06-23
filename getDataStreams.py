import json
import simple_salesforce
import requests
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


def get_data_streams(org, auth_token, version):
    url = f'https://{org}/services/data/{version}/ssot/data-streams' + '?limit=100'

    print(f"URL for getting data streams: {url}")

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {auth_token}'
    }

    req = requests.get(url, headers=headers)

    print(f"Status Code: {req.status_code}")
    print("\nHeaders:")
    print(json.dumps(dict(req.headers), indent=2))
    print("\nResponse Body:")

    if req.status_code == 200:
        # Save the formatted JSON response to a file
        with open('./sample-responses/getDataStreams-response.json', 'w') as f:
            json.dump(req.json(), f, indent=2)

        print("Response has been saved to getDataStreams-response.json")

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

# This works:
# # Justin's Tab Next org (Radhika instructions via Orgfarm):
# org = 'orgfarm-ef60436573.test13.my.pc-rnd.salesforce.com'
# client_id = '3MVG9kfeuo6xCm.pZ4_qdu_PhqIsuIBOpnpN_p66AXqTIVnptJ21r2NaGIf6WlnJJPRyiciWzhZiBZ1SNLgM9'
# client_secret = '80733EDD3B5BFBD8D55CF08E4C736C6118EB78A25D75AD6C09336C6D77C56071'


# # This works:
# org = 'storm-4dd15a23353ff1.my.salesforce.com'
# client_id = '3MVG9aNlkJwuH9vNgV7dXX1mD8GNBYtkSyCXndzm6SOm.MbFeeb91ah9LUompVf83kEnPwbcpdSCJyDJZZti5'
# client_secret = '5221881FFC65D1D328C202C8BAC234209A9F515A01C402A3CD5FBFCEB7E00570'





username = 'jcraycraft.6890ccbb70@salesforce.com'
password = 'orgfarm1234'





# Get auth token    
# auth_token = get_auth_token(org, client_id, client_secret)
auth_token = get_session_id(org, username, password)

# Get semantic models
get_data_streams(org, auth_token, version)






