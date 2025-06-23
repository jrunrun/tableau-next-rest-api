import requests
import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, Set, List
from migrateVisualizations import VisualizationMigrator
from migrateDashboard import get_dashboard, transform_dashboard_payload, create_dashboard, get_session_id


def extract_visualization_ids(dashboard: Dict[str, Any]) -> Set[str]:
    """Extract unique visualization IDs from dashboard widgets.
    
    Args:
        dashboard: Dashboard definition containing widgets
        
    Returns:
        Set of unique visualization IDs
    """
    viz_ids = set()
    
    if "widgets" in dashboard:
        print("Scanning dashboard widgets for visualizations...")
        for widget_key, widget in dashboard["widgets"].items():
            print(f"  Checking widget: {widget_key}")
            if widget_key.startswith("visualization_"):
                print(f"    Found visualization widget: {widget_key}")
                if "source" in widget and "id" in widget["source"]:
                    viz_id = widget["source"]["id"]
                    viz_ids.add(viz_id)
                    print(f"    ✓ Extracted visualization ID: {viz_id}")
                else:
                    print("    ⚠ No visualization source ID found")
    
    print(f"\nFound {len(viz_ids)} unique visualization IDs:")
    for viz_id in viz_ids:
        print(f"  - {viz_id}")
    return viz_ids


def get_visualization(base_url: str, access_token: str, visualization_id: str) -> Dict[str, Any]:
    """Fetch visualization from source org.
    
    Args:
        base_url: The base URL for the Salesforce API
        access_token: OAuth access token for authentication
        visualization_id: ID of the visualization to fetch
        
    Returns:
        Visualization definition
    """
    endpoint = f"{base_url}/services/data/v64.0/tableau/visualizations/{visualization_id}"
    print(f"Getting visualization from endpoint: {endpoint}")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        visualization_data = response.json()
        print(f"Retrieved visualization {visualization_id}")
        return visualization_data
    except requests.exceptions.HTTPError as e:
        print(f"Error response body: {e.response.text}")
        raise


def migrate_dashboard_and_visualizations(source: Dict[str, str], destination: Dict[str, str]) -> Dict[str, Any]:
    """Migrate dashboard and its visualizations from source to destination org.
    
    Args:
        source: Dictionary containing source org details including:
            - org: Salesforce instance URL
            - username: Salesforce username
            - password: Salesforce password
            - data_space: Data space name
            - dashboard_api_name: API name of dashboard to migrate
            
        destination: Dictionary containing destination org details including:
            - org: Salesforce instance URL
            - username: Salesforce username
            - password: Salesforce password
            - data_space: Data space name
            - dashboard_label: New label for migrated dashboard
            - visualization_label_prefix: Prefix for migrated visualization labels
            
    Returns:
        Dictionary containing migration results
    """
    try:
        print("\n=== Starting dashboard and visualizations migration ===")
        
        # Step 1: Authenticate to source org
        print("\n1. Authenticating to source org...")
        source_token = get_session_id(
            source["org"],
            source["username"],
            source["password"]
        )
        source_base_url = f"https://{source['org']}"
        
        # Step 2: Fetch dashboard from source
        print("\n2. Fetching dashboard from source org...")
        source_dashboard = get_dashboard(
            source_base_url,
            source_token,
            source["dashboard_api_name"]
        )
        
        # Step 3: Extract visualization IDs
        print("\n3. Extracting visualization IDs from dashboard...")
        viz_ids_to_fetch = extract_visualization_ids(source_dashboard)
        
        # Step 4: Fetch visualizations from source
        print("\n4. Fetching visualizations from source org...")
        visualizations_to_migrate = []
        for viz_id in viz_ids_to_fetch:
            visualization = get_visualization(source_base_url, source_token, viz_id)
            visualizations_to_migrate.append(visualization)
        
        # Step 5: Authenticate to destination org
        print("\n5. Authenticating to destination org...")
        destination_token = get_session_id(
            destination["org"],
            destination["username"],
            destination["password"]
        )
        destination_base_url = f"https://{destination['org']}"
        
        # Step 6: Create visualizations in destination
        print("\n6. Creating visualizations in destination org...")
        print(f"Number of visualizations to migrate: {len(visualizations_to_migrate)}")
        viz_id_map = {}
        viz_migrator = VisualizationMigrator(source, destination)
        
        for idx, visualization in enumerate(visualizations_to_migrate, 1):
            print(f"\nProcessing visualization {idx}/{len(visualizations_to_migrate)}:")
            print(f"  Original ID: {visualization.get('id', 'Unknown ID')}")
            print(f"  Label: {visualization.get('label', 'Unknown Label')}")
            
            try:
                # Transform visualization
                # Keep the original visualization label
                destination["visualization_label"] = visualization.get("label", "Unknown")
                print("  Transforming visualization...")
                transformed_viz = viz_migrator.transform_payload(visualization)
                
                # Create visualization
                print("  Creating visualization in destination org...")
                new_viz = viz_migrator.create_visualization(transformed_viz)
                
                if new_viz and "id" in new_viz:
                    viz_id_map[visualization["id"]] = new_viz["id"]
                    print(f"  ✓ Successfully created visualization: {visualization['id']} → {new_viz['id']}")
                else:
                    print("  ⚠ Warning: Created visualization but received unexpected response format")
                    print(f"  Response: {json.dumps(new_viz, indent=2)}")
            except Exception as e:
                print(f"  ✗ Error creating visualization: {str(e)}")
                raise
        
        print(f"\nVisualization migration summary:")
        print(f"  Total visualizations processed: {len(visualizations_to_migrate)}")
        print(f"  Successfully mapped: {len(viz_id_map)}")
        print(f"  ID mappings: {json.dumps(viz_id_map, indent=2)}")
        
        # Step 7: Update dashboard visualization references
        print("\n7. Updating dashboard visualization references...")
        if "widgets" in source_dashboard:
            for widget_key, widget in source_dashboard["widgets"].items():
                if widget_key.startswith("visualization_"):
                    if "parameters" in widget and "visualizationParameters" in widget["parameters"]:
                        old_id = widget["parameters"]["visualizationParameters"]["id"]
                        if old_id in viz_id_map:
                            widget["parameters"]["visualizationParameters"]["id"] = viz_id_map[old_id]
        
        # Step 8: Transform dashboard payload
        print("\n8. Transforming dashboard payload...")
        transformed_dashboard = transform_dashboard_payload(
            source_dashboard,
            destination["dashboard_label"]
        )
        
        # Step 9: Create dashboard in destination
        print("\n9. Creating dashboard in destination org...")
        new_dashboard = create_dashboard(
            destination_base_url,
            destination_token,
            transformed_dashboard
        )
        
        print("\n=== Migration completed successfully ===")
        return {
            "success": True,
            "message": "Dashboard and visualizations migrated successfully",
            "dashboard_id": new_dashboard["id"],
            "visualization_mappings": viz_id_map
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
        "data_space": "default",
        "dashboard_api_name": "0TrHo0000000006KAA"
    }

    destination = {
        "org": "storm-dc631f52cc1aeb.my.salesforce.com",
        "username": "jcraycraft.6890ccbb70@salesforce.com",
        "password": "orgfarm1234",
        "data_space": "default",
        "dashboard_label": "New dashboard name",
        "visualization_label_prefix": "Cloned Viz - "
    }
    
    result = migrate_dashboard_and_visualizations(source, destination)
    print("\nMigration Result:", json.dumps(result, indent=2))


if __name__ == "__main__":
    main() 