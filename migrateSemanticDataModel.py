import requests
import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional


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
    
    Raises:
        requests.exceptions.RequestException: If authentication fails
    """
    print(f"\nAuthenticating to {instance_url}...")
    url = f"https://{instance_url}/services/Soap/u/{version}"
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
    
    body = body.replace("USERNAME", username).replace("PASSWORD", password)
    
    try:
        session_response = requests.post(url, data=body, headers=headers)
        session_response.raise_for_status()
        
        root = ET.fromstring(session_response.text)
        session = root[0].findall(
            "{urn:partner.soap.sforce.com}loginResponse/{urn:partner.soap.sforce.com}result/{"
            "urn:partner.soap.sforce.com}sessionId"
        )[0]
        
        auth_id = session.text
        print(f"✓ Authentication successful")
        return auth_id
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Authentication failed for user {username} on instance {instance_url}")
        print(f"Error: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response code: {e.response.status_code}")
            print(f"Response: {e.response.text}")
        raise


def get_semantic_model(base_url: str, access_token: str, model_api_name: str) -> Dict[str, Any]:
    """Fetch semantic model from org.
    
    Args:
        base_url (str): The base URL for the Salesforce API
        access_token (str): OAuth access token for authentication
        model_api_name (str): API name of the model to fetch
        
    Returns:
        Dict[str, Any]: Semantic model definition
        
    Raises:
        requests.exceptions.RequestException: If the API call fails
    """
    print(f"\nFetching semantic model: {model_api_name}")
    
    url = f"{base_url}/services/data/v62.0/ssot/semantic/models/{model_api_name}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        model_data = response.json()
        print(f"✓ Successfully retrieved semantic model")
        return model_data
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to fetch semantic model: {model_api_name}")
        print(f"Error: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response code: {e.response.status_code}")
            print(f"Response: {e.response.text}")
        raise


def transform_model_payload(
    source_model: Dict[str, Any], 
    new_api_name: str,
    new_label: str
) -> Dict[str, Any]:
    """Transform the source model payload for the destination org.
    
    Args:
        source_model (Dict[str, Any]): Original model definition
        new_api_name (str): New API name for the model
        new_label (str): New label for the model
        
    Returns:
        Dict[str, Any]: Transformed model payload
    """
    print(f"\nTransforming model payload...")
    print(f"  New API Name: {new_api_name}")
    print(f"  New Label: {new_label}")
    
    # Create a new model based on the existing one
    new_model = {
        "apiName": new_api_name,
        "label": new_label,
        "dataspace": source_model.get("dataspace", "default"),
        "semanticCalculatedDimensions": source_model.get("semanticCalculatedDimensions", []),
        "semanticCalculatedMeasurements": source_model.get("semanticCalculatedMeasurements", []),
        "semanticDataObjects": source_model.get("semanticDataObjects", []),
        "semanticGroupings": source_model.get("semanticGroupings", []),
        "semanticLogicalViews": source_model.get("semanticLogicalViews", []),
        "semanticMetrics": source_model.get("semanticMetrics", []),
        "semanticParameters": source_model.get("semanticParameters", []),
        "semanticRelationships": source_model.get("semanticRelationships", [])
    }
    
    print("✓ Successfully transformed model payload")
    return new_model


def create_semantic_model(
    base_url: str, 
    access_token: str, 
    model_payload: Dict[str, Any]
) -> Dict[str, Any]:
    """Create a new semantic model in the destination org.
    
    Args:
        base_url (str): The base URL for the Salesforce API
        access_token (str): OAuth access token for authentication
        model_payload (Dict[str, Any]): The model definition to create
        
    Returns:
        Dict[str, Any]: Created model response
        
    Raises:
        requests.exceptions.RequestException: If the API call fails
    """
    print(f"\nCreating new semantic model...")
    print(f"  API Name: {model_payload['apiName']}")
    print(f"  Label: {model_payload['label']}")
    
    url = f"{base_url}/services/data/v62.0/ssot/semantic/models"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(model_payload))
        response.raise_for_status()
        new_model = response.json()
        
        print(f"✓ Successfully created new semantic model")
        print(f"  Model ID: {new_model.get('id')}")
        return new_model
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to create semantic model")
        print(f"Error: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response code: {e.response.status_code}")
            print(f"Response: {e.response.text}")
        raise


def migrate_semantic_model(source: Dict[str, str], destination: Dict[str, str]) -> Dict[str, Any]:
    """Migrate semantic model from source to destination org.
    
    Args:
        source: Dictionary containing source org details including:
            - org: Salesforce instance URL
            - username: Salesforce username
            - password: Salesforce password
            - model_api_name: API name of model to migrate
            
        destination: Dictionary containing destination org details including:
            - org: Salesforce instance URL
            - username: Salesforce username
            - password: Salesforce password
            - model_api_name: New API name for migrated model
            - model_label: New label for migrated model
            
    Returns:
        Dictionary containing migration results
    """
    try:
        print("\n=== Starting semantic model migration ===")
        
        # Step 1: Authenticate to source org
        print("\n1. Authenticating to source org...")
        source_token = get_session_id(
            source["org"],
            source["username"],
            source["password"]
        )
        source_base_url = f"https://{source['org']}"
        
        # Step 2: Fetch model from source
        print("\n2. Fetching model from source org...")
        source_model = get_semantic_model(
            source_base_url,
            source_token,
            source["model_api_name"]
        )
        
        # Step 3: Authenticate to destination org
        print("\n3. Authenticating to destination org...")
        destination_token = get_session_id(
            destination["org"],
            destination["username"],
            destination["password"]
        )
        destination_base_url = f"https://{destination['org']}"
        
        # Step 4: Transform model payload
        print("\n4. Transforming model payload...")
        transformed_model = transform_model_payload(
            source_model,
            destination["model_api_name"],
            destination["model_label"]
        )
        
        # Step 5: Create model in destination
        print("\n5. Creating model in destination org...")
        new_model = create_semantic_model(
            destination_base_url,
            destination_token,
            transformed_model
        )
        
        print("\n=== Migration completed successfully ===")
        return {
            "success": True,
            "message": "Semantic model migrated successfully",
            "source_model_id": source_model.get("id"),
            "destination_model_id": new_model.get("id"),
            "destination_model_api_name": new_model.get("apiName")
        }
        
    except Exception as e:
        print(f"\n=== Migration failed: {str(e)} ===")
        return {
            "success": False,
            "message": f"Migration failed: {str(e)}"
        }


def main():
    # Example usage
    source = {
        "org": "storm-dc631f52cc1aeb.my.salesforce.com",
        "username": "jcraycraft.6890ccbb70@salesforce.com",
        "password": "orgfarm1234",
        "model_api_name": "Retail_NTO"
    }

    destination = {
        "org": "storm-dc631f52cc1aeb.my.salesforce.com",
        "username": "jcraycraft.6890ccbb70@salesforce.com",
        "password": "orgfarm1234",
        "model_api_name": "Retail_NTO_Clone_June_23",
        "model_label": "Retail NTO Clone June 23"
    }
    
    result = migrate_semantic_model(source, destination)
    print("\nMigration Result:", json.dumps(result, indent=2))


if __name__ == "__main__":
    main() 