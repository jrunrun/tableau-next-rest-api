# 1. upload csv to s3
# 2. create data stream
# 3. run data stream
# 4. create dmo mapping or create semantic model


import simple_salesforce
from simple_salesforce import Salesforce, SalesforceMalformedRequest
import requests
import xml.etree.ElementTree as ET
import json


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

def generate_s3_access_credential(path: str, sf: Salesforce, org: str):
    """Generate AWS S3 access credentials for uploading files to Amazon S3 via Salesforce Data Cloud.

    Args:
        path (str): The path in the drive for which to generate credentials (e.g., "$tua$").

    Returns:
        Optional[dict]: The response containing AWS credentials and location, or None if failed.
    """
    endpoint = "/services/data/v63.0/ssot/sf-drive/actions/generate-credential"
    payload = {"path": path}
    try:
        print(f"Requesting S3 access credential for path: {path}")
        response = sf.restful(
            endpoint, method="POST", data=json.dumps(payload)
        )
        print(f"Received S3 access credential response: {response}")
        return response
    except SalesforceMalformedRequest as e:
        print(
            f"SalesforceMalformedRequest error while generating S3 credential: {e}"
        )
        return None
    except Exception as e:
        print(f"Unexpected error while generating S3 credential: {e}")
        return None


org = 'storm-dc631f52cc1aeb.my.salesforce.com'
username = 'jcraycraft.6890ccbb70@salesforce.com'
password = 'orgfarm1234'
data_space = 'default'

auth_token = get_session_id(org, username, password)

sf = Salesforce(
    session_id=auth_token, 
    instance_url="https://" + org, 
    version='v63.0'
)

generate_s3_access_credential(data_space, sf, org)