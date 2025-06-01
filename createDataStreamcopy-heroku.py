import requests
import json

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


# def get_data_stream(org, auth_token, version, recordIdOrDeveloperName):
#     url = f'https://{org}/services/data/{version}/ssot/data-streams/{recordIdOrDeveloperName}'

#     print(f"URL for getting data streams: {url}")

#     headers = {
#         'Content-Type': 'application/json',
#         'Authorization': f'Bearer {auth_token}'
#     }

#     req = requests.get(url, headers=headers)

#     print(f"Status Code: {req.status_code}")
#     print("\nHeaders:")
#     print(json.dumps(dict(req.headers), indent=2))

#     if req.status_code == 200:
#         # Save the formatted JSON response to a file
#         with open('./sample-responses/getDataStream-response.json', 'w') as f:
#             json.dump(req.json(), f, indent=2)

#         print("Response has been saved to getDataStream-response.json")
#         # print(json.dumps(req.json(), indent=2))
#         return req.json()
#     else:
#         print(f"Error: {req.text}")
#         return None


def create_data_stream(org, auth_token, version):
    url = f'https://{org}/services/data/{version}/ssot/data-streams'

    print(f"URL for creating data stream: {url}")


    payload = {
    "connectorInfo": {
      "connectorDetails": {
        "name": "Dataverse", 
        "sourceObject": "d2pbagf1jq37ti" 
      },
      "connectorType": "HerokuPostgres"
    },
    "dataLakeObjectInfo": {
      "category": "Engagement",  
      "dataspaceInfo": [
        { "name": "default" }
      ],
      "label": "Insurance_Claims_Dataverse_1745859943423"
    },
    "name": "Justin_Test_Dataverse",  
    "label": "Justin_Test_Dataverse", 
    "datastreamType": "CONNECTORSFRAMEWORK",
    "refreshConfig": {
    "frequency": {
      "hours": [],
      "refreshDayOfMonth": []
    },
    "hasHeaders": False,
    "isAccelerationEnabled": False,
    "refreshMode": "TOTAL_REPLACE",
    "shouldFetchImmediately": False,
    "shouldTreatMissingFilesAsFailures": False
  },
    "datasource": "HerokuPostgres_Dataverse",
    "sourceFields": [
    {
      "datatype": "Text",
      "name": "Agent"
    },
    {
      "datatype": "Text",
      "name": "Policy Type"
    },
    {
      "datatype": "Number",
      "name": "Annualized Premium Amount"
    },
    {
      "datatype": "Text",
      "name": "Business Line"
    },
    {
      "datatype": "Text",
      "name": "City"
    },
    {
      "datatype": "Text",
      "name": "Claim Number"
    },
    {
      "datatype": "Number",
      "name": "Claim Paid Amount"
    },
    {
      "datatype": "Text",
      "name": "Claim Process Status"
    },
    {
      "datatype": "Text",
      "name": "Claim Reason"
    },
    {
      "datatype": "Text",
      "name": "Claim Status"
    },
    {
      "datatype": "DateTime",
      "format": "MM/dd/yyyy HH:mm:ss.SSS",
      "name": "Close Date"
    },
    {
      "datatype": "Text",
      "name": "County"
    },
    {
      "datatype": "Number",
      "name": "Damages Amount"
    },
    {
      "datatype": "Number",
      "name": "Deductible"
    },
    {
      "datatype": "DateTime",
      "format": "MM/dd/yyyy HH:mm:ss.SSS",
      "name": "Event Date"
    },
    {
      "datatype": "Text",
      "name": "Is Closed Flag"
    },
    {
      "datatype": "Text",
      "name": "Is Reimbursed Flag"
    },
    {
      "datatype": "DateTime",
      "format": "MM/dd/yyyy HH:mm:ss.SSS",
      "name": "Open Date"
    },
    {
      "datatype": "Text",
      "name": "Policy Holder"
    },
    {
      "datatype": "Text",
      "name": "Policy Number"
    },
    {
      "datatype": "Text",
      "name": "Agent Group"
    }
  ]
  }

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
    print("\nHeaders:")
    print(json.dumps(dict(req.headers), indent=2))
    print("\nResponse Body:")

    if req.status_code == 200:
        print(json.dumps(req.json(), indent=2))
        return req.json()
    else:
        print(f"Error: {req.text}")
        return None


# Configuration
org = 'storm-dc631f52cc1aeb.my.salesforce.com'
client_id = '3MVG9Rr0EZ2YOVMb5hDLho4ts6.27uw4kvfO9UkOFoRBAsqB96g5uInaQxhNLDziFmAQ37cSShk6oP1AlKIAc'
client_secret = 'CCB1D74A53C328EA748FBF5F4BB2AE4CE50107582B1CDEFE049BF8F1C3576444'
version = 'v63.0'
source_stream_id = 'Insurance_Claims_Dataverse_1745859943423__dll'
destination_stream_name = 'Insurance_Claims_Dataverse_Clone'
destination_stream_api_name = 'Insurance_Claims_Dataverse_Clone'

# Get auth token    
auth_token = get_auth_token(org, client_id, client_secret)

# Get existing data stream
# stream_data = get_data_stream(org, auth_token, version, source_stream_id)




# Create new data stream
# if stream_data:
#     print(f"Creating new data stream: {destination_stream_name}")
#     new_stream = create_data_stream(org, auth_token, version, stream_data, destination_stream_name)

new_stream = create_data_stream(org, auth_token, version)




