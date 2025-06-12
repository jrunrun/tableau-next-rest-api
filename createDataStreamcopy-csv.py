import requests
import json
from datetime import datetime
import time

# createDataStream
# POST
# https://{dne_cdpInstanceUrl}/services/data/v64.0/ssot/data-streams
# Create a data stream.

# Available Version: 60.0


def get_auth_token(org, client_id, client_secret):
    url = f"https://{org}/services/oauth2/token"

    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }

    req = requests.post(url, data=data)
    return req.json()['access_token']




def create_data_stream(org, auth_token, version, DLO_label, DLO_name, data_stream_name):
    url = f'https://{org}/services/data/{version}/ssot/data-streams'

    print(f"URL for creating data stream: {url}")


    payload = {
    "advancedAttributes": {
        "importDirectory": "005Ho00000KbiO7IAJ/2025-05-31T19:35:28.128Z",
        "fileName": "Sample - Superstore - Orders.csv",
        "delimiter": ",",
        "parentDirectory": "s3://aws-prod1-useast1-cdp3-lakehouse-1/sfdrive/a360-prod-1aa1970a05b744ef86be2f5c8fb49a5d/flup-fileUploads/dc_file_upload",
        "fileType": "CSV"
    },
    "connectorInfo": {
        "connectorDetails": {
            "name": "UploadedFiles"
        },
        "connectorType": "DataConnector"
    },
    "dataLakeObjectInfo": {
        "category": "Profile",
        "dataspaceInfo": [
            {
                "name": "default"
            }
        ],
        "label": "Sample Superstore Orders",
        "name": "Sample_Superstore_Orders__dll",
        "dataLakeFieldInputRepresentations": [
      {
        "dataType": "Number",
        "isPrimaryKey": False,
        "label": "Discount",
        "name": "Discount"
      },
      {
        "dataType": "Text",
        "isPrimaryKey": False,
        "label": "Segment",
        "name": "Segment"
      },
      {
        "dataType": "Number",
        "isPrimaryKey": False,
        "label": "Quantity",
        "name": "Quantity"
      },
      {
        "dataType": "Text",
        "isPrimaryKey": False,
        "label": "Customer Name",
        "name": "Customer_Name"
      },
      {
        "dataType": "Date",
        "isPrimaryKey": False,
        "label": "Order Date",
        "name": "Order_Date"
      },
      {
        "dataType": "Number",
        "isPrimaryKey": False,
        "label": "Sales",
        "name": "Sales"
      },
      {
        "dataType": "Text",
        "isPrimaryKey": False,
        "label": "Row ID",
        "name": "Row_ID"
      },
      {
        "dataType": "Text",
        "isPrimaryKey": False,
        "label": "Customer ID",
        "name": "Customer_ID"
      },
      {
        "dataType": "Text",
        "isPrimaryKey": True,
        "label": "Order ID",
        "name": "Order_ID"
      },
      {
        "dataType": "Text",
        "isPrimaryKey": False,
        "label": "Ship Mode",
        "name": "Ship_Mode"
      },
      {
        "dataType": "Date",
        "isPrimaryKey": False,
        "label": "Ship Date",
        "name": "Ship_Date"
      },
      {
        "dataType": "Text",
        "isPrimaryKey": False,
        "label": "State/Province",
        "name": "State_Province"
      },
      {
        "dataType": "Text",
        "isPrimaryKey": False,
        "label": "City",
        "name": "City"
      },
      {
        "dataType": "Text",
        "isPrimaryKey": False,
        "label": "Product Name",
        "name": "Product_Name"
      },
      {
        "dataType": "Number",
        "isPrimaryKey": False,
        "label": "Postal Code",
        "name": "Postal_Code"
      },
      {
        "dataType": "Text",
        "isPrimaryKey": False,
        "label": "Product ID",
        "name": "Product_ID"
      },
      {
        "dataType": "Text",
        "isPrimaryKey": False,
        "label": "Country/Region",
        "name": "Country_Region"
      },
      {
        "dataType": "Number",
        "isPrimaryKey": False,
        "label": "Profit",
        "name": "Profit"
      },
      {
        "dataType": "Text",
        "isPrimaryKey": False,
        "label": "Sub-Category",
        "name": "Sub_Category"
      },
      {
        "dataType": "Text",
        "isPrimaryKey": False,
        "label": "Category",
        "name": "Category"
      },
      {
        "dataType": "Text",
        "isPrimaryKey": False,
        "label": "Region",
        "name": "Region"
      }
    ]
    },
    "name": "Sample Superstore Orders Test",
    "label": "Sample Superstore Orders Test",
    "datastreamType": "CONNECTORSFRAMEWORK",
    "refreshConfig": {
        "frequency": {
            "frequencyType": "None"
        },
        "refreshMode": "TOTAL_REPLACE"
    },
    "mappings": [
    {
      "sourceFieldLabel": "Order Date",
      "targetFieldName": "Order_Date"
    },
    {
      "sourceFieldLabel": "Order ID",
      "targetFieldName": "Order_ID"
    },
    {
      "sourceFieldLabel": "Quantity",
      "targetFieldName": "Quantity"
    },
    {
      "sourceFieldLabel": "Row ID",
      "targetFieldName": "Row_ID"
    },
    {
      "sourceFieldLabel": "Category",
      "targetFieldName": "Category"
    },
    {
      "sourceFieldLabel": "Country/Region",
      "targetFieldName": "Country_Region"
    },
    {
      "sourceFieldLabel": "Product Name",
      "targetFieldName": "Product_Name"
    },
    {
      "sourceFieldLabel": "Profit",
      "targetFieldName": "Profit"
    },
    {
      "sourceFieldLabel": "Ship Date",
      "targetFieldName": "Ship_Date"
    },
    {
      "sourceFieldLabel": "Customer ID",
      "targetFieldName": "Customer_ID"
    },
    {
      "sourceFieldLabel": "Region",
      "targetFieldName": "Region"
    },
    {
      "sourceFieldLabel": "Customer Name",
      "targetFieldName": "Customer_Name"
    },
    {
      "sourceFieldLabel": "City",
      "targetFieldName": "City"
    },
    {
      "sourceFieldLabel": "Discount",
      "targetFieldName": "Discount"
    },
    {
      "sourceFieldLabel": "State/Province",
      "targetFieldName": "State_Province"
    },
    {
      "sourceFieldLabel": "Sales",
      "targetFieldName": "Sales"
    },
    {
      "sourceFieldLabel": "Sub-Category",
      "targetFieldName": "Sub_Category"
    },
    {
      "sourceFieldLabel": "Segment",
      "targetFieldName": "Segment"
    },
    {
      "sourceFieldLabel": "Ship Mode",
      "targetFieldName": "Ship_Mode"
    },
    {
      "sourceFieldLabel": "Postal Code",
      "targetFieldName": "Postal_Code"
    },
    {
      "sourceFieldLabel": "Product ID",
      "targetFieldName": "Product_ID"
    }
  ],
  "sourceFields": [
    {
      "dataType": "Text",
      "name": "Row ID"
    },
    {
      "dataType": "Text",
      "name": "Order ID"
    },
    {
      "dataType": "Date",
      "format": "MM/dd/yyyy",
      "name": "Order Date"
    },
    {
      "dataType": "Date",
      "format": "MM/dd/yyyy",
      "name": "Ship Date"
    },
    {
      "dataType": "Text",
      "name": "Ship Mode"
    },
    {
      "dataType": "Text",
      "name": "Customer ID"
    },
    {
      "dataType": "Text",
      "name": "Customer Name"
    },
    {
      "dataType": "Text",
      "name": "Segment"
    },
    {
      "dataType": "Text",
      "name": "Country/Region"
    },
    {
      "dataType": "Text",
      "name": "City"
    },
    {
      "dataType": "Text",
      "name": "State/Province"
    },
    {
      "dataType": "Number",
      "name": "Postal Code"
    },
    {
      "dataType": "Text",
      "name": "Region"
    },
    {
      "dataType": "Text",
      "name": "Product ID"
    },
    {
      "dataType": "Text",
      "name": "Category"
    },
    {
      "dataType": "Text",
      "name": "Sub-Category"
    },
    {
      "dataType": "Text",
      "name": "Product Name"
    },
    {
      "dataType": "Number",
      "name": "Sales"
    },
    {
      "dataType": "Number",
      "name": "Quantity"
    },
    {
      "dataType": "Number",
      "name": "Discount"
    },
    {
      "dataType": "Number",
      "name": "Profit"
    }
  ]
}

    payload['dataLakeObjectInfo']['label'] = DLO_label
    payload['dataLakeObjectInfo']['name'] = DLO_name

    payload['name'] = data_stream_name
    payload['label'] = data_stream_name

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {auth_token}'
    }

    with open('./sample-requests/createDataStream-request.json', 'w') as f:
        json.dump(payload, f, indent=2)

    print("Request has been saved to createDataStream-request.json")    

    # Make POST request to create data stream
    req = requests.post(url, headers=headers, json=payload)

    print(f"Status Code: {req.status_code}")

    if req.status_code in [200, 201]:
        print("\nResponse Body:") 
        print(json.dumps(req.json(), indent=2))
        with open('./sample-responses/createDataStream-csv-response.json', 'w') as f:
            json.dump(req.json(), f, indent=2)
        print("Response has been saved to createDataStream-csv-response.json")
        return req.json()
    else:
        print(f"Error: {req.text}")
        return None


def run_data_stream(org, auth_token, version, record_id):
  url = f'https://{org}/services/data/{version}/ssot/data-streams/{record_id}/actions/run'

  headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {auth_token}'
  }

  req = requests.post(url, headers=headers)

  print(f"Status Code: {req.status_code}")
  print("\nHeaders:")
  print(json.dumps(dict(req.headers), indent=2))
  print("\nResponse Body:")
  
  if req.status_code == 200:
    print(f"Datastream run triggered successfully: {req.json()}")
    return True
  else:
    print(f"Error: {req.text}")
    return False



# Configuration
org = 'storm-dc631f52cc1aeb.my.salesforce.com'
client_id = '3MVG9Rr0EZ2YOVMb5hDLho4ts6.27uw4kvfO9UkOFoRBAsqB96g5uInaQxhNLDziFmAQ37cSShk6oP1AlKIAc'
client_secret = 'CCB1D74A53C328EA748FBF5F4BB2AE4CE50107582B1CDEFE049BF8F1C3576444'
version = 'v63.0'
# source_stream_id = 'Insurance_Claims_Dataverse_1745859943423__dll'
unique_id = '56'
data_stream_name = 'Sample Superstore Orders Test' + unique_id
# "name": "Sample Superstore Orders Test",
# "label": "Sample Superstore Orders Test",

DLO_label = 'Sample Superstore Orders Test DLO' + unique_id
DLO_name = 'Sample_Superstore_Orders_Test_DLO' + '_' + unique_id + '__dll'
# "label": "Sample Superstore Orders",
# "name": "Sample_Superstore_Orders__dll",

# Get auth token    
auth_token = get_auth_token(org, client_id, client_secret)

# Get existing data stream
# stream_data = get_data_stream(org, auth_token, version, source_stream_id)




# Create new data stream
# if stream_data:
#     print(f"Creating new data stream: {destination_stream_name}")
#     new_stream = create_data_stream(org, auth_token, version, stream_data, destination_stream_name)

new_stream = create_data_stream(org, auth_token, version, DLO_label, DLO_name, data_stream_name)

if new_stream:
    recordId = new_stream['recordId']
    print(f"Record ID: {recordId}")
    print("Waiting 10 seconds before running the data stream...")
    time.sleep(10)  # Wait for 10 seconds
    run_data_stream(org, auth_token, version, recordId)
else:
    print("Failed to create data stream. Please check the error messages above.")
