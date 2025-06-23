import requests
import json
import xml.etree.ElementTree as ET
from typing import Any, Dict


def get_session_id(
    instance_url: str, username: str, password: str, version: str = "64.0"
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
        raise Exception("Authentication failed")
    root = ET.fromstring(session_response.text)
    session = root[0].findall(
        "{urn:partner.soap.sforce.com}loginResponse/{urn:partner.soap.sforce.com}result/{"
        "urn:partner.soap.sforce.com}sessionId"
    )[0]
    auth_id = session.text
    print(f"Successfully authenticated for {username} on {instance_url}")
    return auth_id


def get_dashboard(base_url: str, access_token: str, dashboard_api_name: str) -> Dict[str, Any]:
    """Fetch dashboard definition from source org.
    
    Args:
        base_url: The base URL for the Salesforce API
        access_token: OAuth access token for authentication
        dashboard_api_name: API name of the dashboard to fetch
        
    Returns:
        Dictionary containing the dashboard definition
    """
    endpoint = f"{base_url}/services/data/v64.0/tableau/dashboards/{dashboard_api_name}"
    print(f"Getting dashboard from endpoint: {endpoint}")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        dashboard_data = response.json()
        print("Retrieved dashboard data:", json.dumps(dashboard_data, indent=2))
        return dashboard_data
    except requests.exceptions.HTTPError as e:
        print(f"Error response body: {e.response.text}")
        raise


def transform_dashboard_payload(dashboard: Dict[str, Any], destination_label: str) -> Dict[str, Any]:
    """Transform dashboard payload for destination org.
    
    Args:
        dashboard: Source dashboard definition
        destination_label: New label for the dashboard
        
    Returns:
        Transformed dashboard definition ready for creation
    """
    print("Starting payload transformation...")
    
    # Create a deep copy to avoid modifying the original
    transformed = json.loads(json.dumps(dashboard))
    
    # Remove system-generated and read-only fields
    keys_to_remove = ['permissions', 'createdBy', 'createdDate', 'customViews', 'url', 'id']
    for key in keys_to_remove:
        transformed.pop(key, None)
    print(f"Removed root level keys: {', '.join(keys_to_remove)}")
    
    # Set new dashboard label
    transformed['label'] = destination_label
    print(f"Set dashboard label to: {destination_label}")
    
    # Process layouts and pages
    if 'layouts' in transformed:
        for layout in transformed['layouts']:
            if 'pages' in layout:
                for page in layout['pages']:
                    # Remove page ID and convert label to name if present
                    page.pop('id', None)
                    if 'label' in page:
                        page['name'] = page.pop('label')
                    
                    # Process widgets in page
                    if 'widgets' in page:
                        for widget in page['widgets']:
                            widget.pop('id', None)
        print("Processed layouts and pages")
    
    # Process widgets
    if 'widgets' in transformed:
        for widget_key, widget in transformed['widgets'].items():
            # Remove widget ID
            widget.pop('id', None)
            
            # Remove source label for visualization widgets
            if widget.get('type') == 'visualization' and 'source' in widget:
                source = widget['source']
                if 'label' in source:
                    del source['label']
        print(f"Processed {len(transformed['widgets'])} widgets")
    
    print("Transformation complete. Transformed payload:", json.dumps(transformed, indent=2))
    return transformed


def create_dashboard(base_url: str, access_token: str, dashboard_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Create dashboard in destination org.
    
    Args:
        base_url: The base URL for the Salesforce API
        access_token: OAuth access token for authentication
        dashboard_payload: Transformed dashboard definition
        
    Returns:
        API response from dashboard creation
    """
    endpoint = f"{base_url}/services/data/v64.0/tableau/dashboards"
    print(f"Creating dashboard at endpoint: {endpoint}")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    print("Creating dashboard with payload:", json.dumps(dashboard_payload, indent=2))
    try:
        response = requests.post(endpoint, headers=headers, json=dashboard_payload)
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        response.raise_for_status()
        result = response.json()
        print("Creation response:", json.dumps(result, indent=2))
        return result
    except requests.exceptions.HTTPError as e:
        print(f"Error response body: {e.response.text}")
        raise


def migrate_dashboard(source_org: Dict[str, str], destination_org: Dict[str, str]) -> Dict[str, Any]:
    """Migrate dashboard from source to destination org.
    
    Args:
        source_org: Dictionary containing source org details
        destination_org: Dictionary containing destination org details
        
    Returns:
        API response from dashboard creation in destination org
    """
    try:
        print("\n=== Starting dashboard migration ===")
        
        # Authenticate to source org
        print("\n1. Authenticating to source org...")
        source_token = get_session_id(
            source_org['org'],
            source_org['username'],
            source_org['password']
        )
        
        # Fetch dashboard from source
        print("\n2. Fetching dashboard from source org...")
        source_dashboard = get_dashboard(
            f"https://{source_org['org']}", 
            source_token,
            source_org['dashboard_api_name']
        )
        
        # Transform dashboard payload
        print("\n3. Transforming dashboard payload...")
        transformed_dashboard = transform_dashboard_payload(
            source_dashboard,
            destination_org['dashboard_label']
        )
        
        # Authenticate to destination org
        print("\n4. Authenticating to destination org...")
        dest_token = get_session_id(
            destination_org['org'],
            destination_org['username'],
            destination_org['password']
        )
        
        # Create dashboard in destination
        print("\n5. Creating dashboard in destination org...")
        result = create_dashboard(
            f"https://{destination_org['org']}", 
            dest_token,
            transformed_dashboard
        )
        
        print("\n=== Dashboard migration completed successfully ===")
        return {
            "success": True,
            "message": "Dashboard migrated successfully",
            "result": result
        }
        
    except Exception as e:
        print(f"\n=== Dashboard migration failed: {str(e)} ===")
        return {
            "success": False,
            "message": f"Migration failed: {str(e)}"
        }


if __name__ == "__main__":
    # Example usage
    source_org = {
        'org': 'storm-dc631f52cc1aeb.my.salesforce.com',
        'username': 'jcraycraft.6890ccbb70@salesforce.com',
        'password': 'orgfarm1234',
        'data_space': 'default',
        'dashboard_api_name': '0TrHo0000000006KAA'
    }

    destination_org = {
        'org': 'storm-dc631f52cc1aeb.my.salesforce.com',
        'username': 'jcraycraft.6890ccbb70@salesforce.com',
        'password': 'orgfarm1234',
        'data_space': 'default',
        'dashboard_label': 'New dashboard name june 23'
    }

    result = migrate_dashboard(source_org, destination_org)
    if result["success"]:
        print("New dashboard details:", json.dumps(result["result"], indent=2))
    else:
        print(f"Error: {result['message']}")