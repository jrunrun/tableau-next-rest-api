import requests
import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, Set, List, Optional
import random
import string
from migrateVisualizations import VisualizationMigrator
from migrateDashboard import get_dashboard, transform_dashboard_payload, create_dashboard, get_session_id
from migrateSemanticDataModel import get_semantic_model, create_semantic_model


class DashboardSuperMigrator:
    def __init__(self, source: Dict[str, str], destination: Dict[str, str]):
        """Initialize the super migrator.
        
        Args:
            source: Dictionary containing source org details
            destination: Dictionary containing destination org details
        """
        self.source = source
        self.destination = destination
        self.source_token = None
        self.destination_token = None
        self.api_version = "64.0"
        self.semantic_id_map = {}  # Maps source SDM IDs to destination SDM IDs
        self.viz_id_map = {}  # Maps source visualization IDs to destination visualization IDs

    def authenticate(self, org_config: Dict[str, str]) -> str:
        """Authenticate to Salesforce org and return session ID."""
        return get_session_id(
            org_config["org"],
            org_config["username"],
            org_config["password"]
        )

    def get_visualization(self, visualization_id: str) -> Dict[str, Any]:
        """Fetch visualization from source org."""
        if not self.source_token:
            self.source_token = self.authenticate(self.source)

        url = f"https://{self.source['org']}/services/data/v{self.api_version}/tableau/visualizations/{visualization_id}"
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
            print(f"Retrieved visualization {visualization_id}")
            return visualization_data
        except requests.exceptions.HTTPError as e:
            print(f"Error response body: {e.response.text}")
            raise

    def extract_visualization_ids(self, dashboard: Dict[str, Any]) -> Set[str]:
        """Extract unique visualization IDs from dashboard widgets."""
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

    def get_semantic_model_id(self, visualization: Dict[str, Any]) -> Optional[str]:
        """Extract semantic model ID from visualization."""
        if "dataSource" in visualization and "id" in visualization["dataSource"]:
            sdm_id = visualization["dataSource"]["id"]
            print(f"  ✓ Found semantic model ID: {sdm_id}")
            return sdm_id
        return None

    def generate_random_suffix(self, length: int = 4) -> str:
        """Generate a random alphanumeric suffix.
        
        Args:
            length: Length of the suffix to generate
            
        Returns:
            Random string of specified length containing only letters and numbers
        """
        # Use only letters and numbers to ensure valid API name
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    def migrate_semantic_model(self, model_id: str) -> str:
        """Migrate semantic model from source to destination org.
        
        Returns:
            str: ID of the created semantic model in destination org
        """
        print(f"\nMigrating semantic model: {model_id}")
        
        # Get source model
        source_model = get_semantic_model(
            f"https://{self.source['org']}", 
            self.source_token, 
            model_id
        )
        
        # Generate valid API name (only underscores and alphanumeric, no spaces, no consecutive underscores)
        prefix = self.destination['semantic_model_label_prefix'].replace(' ', '_').replace('-', '_')
        prefix = ''.join(c for c in prefix if c.isalnum() or c == '_')  # Remove any other special chars
        random_suffix = self.generate_random_suffix()
        new_api_name = f"{source_model['apiName']}_{prefix}_{random_suffix}"
        # Remove consecutive underscores and ensure doesn't end with underscore
        while '__' in new_api_name:
            new_api_name = new_api_name.replace('__', '_')
        if new_api_name.endswith('_'):
            new_api_name = new_api_name[:-1]
        
        # Transform model for destination
        transformed_model = {
            "apiName": new_api_name,
            "label": f"{source_model['label']} {self.destination['semantic_model_label_prefix']} {random_suffix}",
            "dataspace": self.destination["data_space"],
            "semanticCalculatedDimensions": source_model.get('semanticCalculatedDimensions', []),
            "semanticCalculatedMeasurements": source_model.get('semanticCalculatedMeasurements', []),
            "semanticDataObjects": source_model.get('semanticDataObjects', []),
            "semanticGroupings": source_model.get('semanticGroupings', []),
            "semanticLogicalViews": source_model.get('semanticLogicalViews', []),
            "semanticMetrics": source_model.get('semanticMetrics', []),
            "semanticParameters": source_model.get('semanticParameters', []),
            "semanticRelationships": source_model.get('semanticRelationships', [])
        }
        
        print(f"  Transformed API Name: {new_api_name}")
        print(f"  Transformed Label: {transformed_model['label']}")
        
        # Create in destination
        if not self.destination_token:
            self.destination_token = self.authenticate(self.destination)
            
        new_model = create_semantic_model(
            f"https://{self.destination['org']}", 
            self.destination_token,
            transformed_model
        )
        
        return new_model["id"]

    def migrate_visualization(self, visualization: Dict[str, Any]) -> str:
        """Migrate visualization from source to destination org.
        
        Returns:
            str: ID of the created visualization in destination org
        """
        print(f"\nMigrating visualization: {visualization['id']}")
        
        # Transform visualization
        transformed_viz = visualization.copy()
        
        # Remove system fields and URLs
        fields_to_remove = [
            "id", "createdBy", "createdDate", "lastModifiedBy", 
            "lastModifiedDate", "permissions", "url"
        ]
        for field in fields_to_remove:
            transformed_viz.pop(field, None)
        
        # Clean up nested objects
        if "view" in transformed_viz:
            view_fields_to_remove = ["id", "isOriginal", "url"]
            for field in view_fields_to_remove:
                transformed_viz["view"].pop(field, None)
        
        if "fields" in transformed_viz:
            for field_key in transformed_viz["fields"]:
                transformed_viz["fields"][field_key].pop("id", None)
                transformed_viz["fields"][field_key].pop("url", None)
        
        if "workspace" in transformed_viz:
            workspace_fields_to_remove = ["id", "url"]
            for field in workspace_fields_to_remove:
                transformed_viz["workspace"].pop(field, None)
        
        if "dataSource" in transformed_viz:
            datasource_fields_to_remove = ["url"]
            for field in datasource_fields_to_remove:
                transformed_viz["dataSource"].pop(field, None)
            # Update semantic model reference if it exists
            old_sdm_id = transformed_viz["dataSource"].get("id")
            if old_sdm_id and old_sdm_id in self.semantic_id_map:
                transformed_viz["dataSource"]["id"] = self.semantic_id_map[old_sdm_id]
                print(f"  ✓ Updated semantic model reference: {old_sdm_id} → {self.semantic_id_map[old_sdm_id]}")
        
        # Update label
        transformed_viz["label"] = f"{self.destination['visualization_label_prefix']}{visualization['label']}"
        print(f"  ✓ Set visualization label: {transformed_viz['label']}")
        
        # Create in destination
        if not self.destination_token:
            self.destination_token = self.authenticate(self.destination)
            
        viz_migrator = VisualizationMigrator(self.source, self.destination)
        new_viz = viz_migrator.create_visualization(transformed_viz)
        
        print(f"  ✓ Created visualization in destination org")
        return new_viz["id"]

    def migrate(self) -> Dict[str, Any]:
        """Execute the full migration process."""
        try:
            print("\n=== Starting super migration ===")
            
            # Step 1: Authenticate to source org
            print("\n1. Authenticating to source org...")
            self.source_token = self.authenticate(self.source)
            
            # Step 2: Get source dashboard
            print("\n2. Fetching dashboard from source org...")
            source_dashboard = get_dashboard(
                f"https://{self.source['org']}", 
                self.source_token,
                self.source["dashboard_api_name"]
            )
            
            # Step 3: Extract visualization IDs
            print("\n3. Extracting visualization IDs from dashboard...")
            viz_ids = self.extract_visualization_ids(source_dashboard)
            
            # Step 4: Get each visualization and its semantic model
            print("\n4. Fetching visualizations and semantic models...")
            semantic_models_to_migrate = set()
            visualizations_to_migrate = []
            
            for viz_id in viz_ids:
                visualization = self.get_visualization(viz_id)
                visualizations_to_migrate.append(visualization)
                
                # Get semantic model ID if it exists
                sdm_id = self.get_semantic_model_id(visualization)
                if sdm_id:
                    semantic_models_to_migrate.add(sdm_id)
            
            # Step 5: Migrate semantic models
            print(f"\n5. Migrating {len(semantic_models_to_migrate)} semantic models...")
            for sdm_id in semantic_models_to_migrate:
                new_sdm_id = self.migrate_semantic_model(sdm_id)
                self.semantic_id_map[sdm_id] = new_sdm_id
                print(f"  ✓ Migrated semantic model: {sdm_id} → {new_sdm_id}")
            
            # Step 6: Migrate visualizations
            print(f"\n6. Migrating {len(visualizations_to_migrate)} visualizations...")
            for visualization in visualizations_to_migrate:
                old_viz_id = visualization["id"]
                new_viz_id = self.migrate_visualization(visualization)
                self.viz_id_map[old_viz_id] = new_viz_id
                print(f"  ✓ Migrated visualization: {old_viz_id} → {new_viz_id}")
            
            # Step 7: Update dashboard visualization references
            print("\n7. Updating dashboard visualization references...")
            if "widgets" in source_dashboard:
                for widget_key, widget in source_dashboard["widgets"].items():
                    if widget_key.startswith("visualization_"):
                        if "source" in widget and "id" in widget["source"]:
                            old_id = widget["source"]["id"]
                            if old_id in self.viz_id_map:
                                widget["source"]["id"] = self.viz_id_map[old_id]
                                print(f"    ✓ Updated visualization reference: {old_id} → {self.viz_id_map[old_id]}")
                            else:
                                print(f"    ⚠ No mapping found for visualization ID: {old_id}")
                        else:
                            print(f"    ⚠ No source ID found in widget: {widget_key}")
            else:
                print("    ⚠ No widgets found in dashboard")
            
            # Step 8: Transform dashboard payload
            print("\n8. Transforming dashboard payload...")
            transformed_dashboard = transform_dashboard_payload(
                source_dashboard,
                self.destination["dashboard_label"]
            )
            
            # Step 9: Create dashboard in destination
            print("\n9. Creating dashboard in destination org...")
            if not self.destination_token:
                self.destination_token = self.authenticate(self.destination)
                
            new_dashboard = create_dashboard(
                f"https://{self.destination['org']}", 
                self.destination_token,
                transformed_dashboard
            )
            
            print("\n=== Migration completed successfully ===")
            return {
                "success": True,
                "message": "Dashboard, visualizations, and semantic models migrated successfully",
                "dashboard_id": new_dashboard["id"],
                "visualization_mappings": self.viz_id_map,
                "semantic_model_mappings": self.semantic_id_map
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
        "visualization_label_prefix": "Cloned Viz - ",
        "semantic_model_label_prefix": "Cloned Model - "
    }
    
    migrator = DashboardSuperMigrator(source, destination)
    result = migrator.migrate()
    print("\nMigration Result:", json.dumps(result, indent=2))


if __name__ == "__main__":
    main() 