import requests
import json
from typing import Dict, Any
import xml.etree.ElementTree as ET

class VisualizationMigrator:
    def __init__(self, source_org: Dict[str, str], destination_org: Dict[str, str]):
        self.source_org = source_org
        self.destination_org = destination_org
        self.source_token = None
        self.destination_token = None
        self.api_version = "64.0"  # Latest stable version

    def get_session_id(self, instance_url: str, username: str, password: str) -> str:
        """Get a Salesforce session ID using SOAP login.

        Args:
            instance_url (str): Salesforce instance URL.
            username (str): Salesforce username.
            password (str): Salesforce password.

        Returns:
            str: Session ID.
        """
        url = f"https://{instance_url}/services/Soap/u/{self.api_version}"
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

    def authenticate(self, org_config: Dict[str, str]) -> str:
        """Authenticate to Salesforce org and return session ID."""
        return self.get_session_id(
            instance_url=org_config["org"],
            username=org_config["username"],
            password=org_config["password"]
        )

    def get_visualization(self, visualization_api_name: str) -> Dict[str, Any]:
        """Fetch visualization from source org."""
        if not self.source_token:
            self.source_token = self.authenticate(self.source_org)

        url = f"https://{self.source_org['org']}/services/data/v{self.api_version}/tableau/visualizations/{visualization_api_name}"
        print(f"Getting visualization from endpoint: {url}")
        
        headers = {
            "Authorization": f"Bearer {self.source_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            visualization_data = response.json()
            print("Retrieved visualization data:", json.dumps(visualization_data, indent=2))
            return visualization_data
        except requests.exceptions.HTTPError as e:
            print(f"Error response body: {e.response.text}")
            raise
        
    def transform_payload(self, visualization: Dict[str, Any]) -> Dict[str, Any]:
        """Transform the visualization payload for the destination org."""
        print("Starting payload transformation...")
        
        # Create a deep copy to avoid modifying the original
        transformed = json.loads(json.dumps(visualization))
        
        # Delete root-level keys
        root_keys_to_delete = [
            "createdBy", "createdDate", "lastModifiedBy",
            "lastModifiedDate", "permissions", "id"
        ]
        for key in root_keys_to_delete:
            transformed.pop(key, None)
        print(f"Removed root level keys: {', '.join(root_keys_to_delete)}")
        
        # Remove 'id' and 'isOriginal' from view
        if "view" in transformed:
            transformed["view"].pop("id", None)
            transformed["view"].pop("isOriginal", None)
            print("Removed 'id' and 'isOriginal' from view")
        
        # Strip 'id' fields from each defined field
        if "fields" in transformed:
            for field_key in transformed["fields"]:
                transformed["fields"][field_key].pop("id", None)
            print(f"Removed 'id' from {len(transformed['fields'])} fields")
        
        # Remove workspace url
        if "workspace" in transformed:
            transformed["workspace"].pop("url", None)
            print("Removed workspace URL")
        
        # Remove url from dataSource if present
        if "dataSource" in transformed and "url" in transformed["dataSource"]:
            transformed["dataSource"].pop("url", None)
            print("Removed URL from dataSource")
        
        # Set destination label
        transformed["label"] = self.destination_org["visualization_label"]
        print(f"Set visualization label to: {transformed['label']}")
        
        print("Transformation complete. Transformed payload:", json.dumps(transformed, indent=2))
        return transformed

    def create_visualization(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create visualization in destination org."""
        if not self.destination_token:
            self.destination_token = self.authenticate(self.destination_org)

        url = f"https://{self.destination_org['org']}/services/data/v{self.api_version}/tableau/visualizations"
        print(f"Creating visualization at endpoint: {url}")
        
        headers = {
            "Authorization": f"Bearer {self.destination_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        print("Creating visualization with payload:", json.dumps(payload, indent=2))
        try:
            response = requests.post(url, json=payload, headers=headers)
            print(f"Response Status Code: {response.status_code}")
            print(f"Response Headers: {response.headers}")
            response.raise_for_status()
            result = response.json()
            print("Creation response:", json.dumps(result, indent=2))
            return result
        except requests.exceptions.HTTPError as e:
            print(f"Error response body: {e.response.text}")
            raise

    def migrate(self) -> Dict[str, Any]:
        """Execute the full migration process."""
        try:
            print("\n=== Starting visualization migration ===")
            
            # Get visualization from source
            print("\n1. Fetching visualization from source org...")
            visualization = self.get_visualization(
                self.source_org["visualization_api_name"]
            )
            
            # Transform the payload
            print("\n2. Transforming visualization payload...")
            transformed_payload = self.transform_payload(visualization)
            
            # Create in destination
            print("\n3. Creating visualization in destination org...")
            result = self.create_visualization(transformed_payload)
            
            print("\n=== Visualization migration completed successfully ===")
            return {
                "success": True,
                "message": "Visualization migrated successfully",
                "result": result
            }
            
        except Exception as e:
            print(f"\n=== Visualization migration failed: {str(e)} ===")
            return {
                "success": False,
                "message": f"Migration failed: {str(e)}"
            }

def main():
    # Example usage
    source_org = {
        "org": "storm-dc631f52cc1aeb.my.salesforce.com",
        "username": "jcraycraft.6890ccbb70@salesforce.com",
        "password": "orgfarm1234",
        "data_space": "default",
        "visualization_api_name": "1AKHo000000GmaEOAS"
    }

    destination_org = {
        "org": "storm-dc631f52cc1aeb.my.salesforce.com",
        "username": "jcraycraft.6890ccbb70@salesforce.com",
        "password": "orgfarm1234",
        "data_space": "default",
        "visualization_label": "New visualization name june 23"
    }

    migrator = VisualizationMigrator(source_org, destination_org)
    result = migrator.migrate()
    if result["success"]:
        print("New visualization details:", json.dumps(result["result"], indent=2))
    else:
        print(f"Error: {result['message']}")

if __name__ == "__main__":
    main() 