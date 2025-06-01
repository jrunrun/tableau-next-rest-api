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
  "label": "connect api 32",
  "datasource": "AwsS3_S3",
  "datastreamType": "CONNECTORSFRAMEWORK",
  "connectorInfo": {
    "connectorType": "DataConnector",
    "connectorDetails": {
      "name": "S3"
    }
  },
  "dataLakeObjectInfo": {
    "label": "connect api 32",
    "name": "connect_api_32__dll",
    "category": "Engagement",
    "recordModifiedFieldName": "starttime",
    "eventDateTimeFieldName": "starttime",
    "orgUnitIdentifierFieldName": "bikeid",
    "dataspaceInfo": [
      {
        "name": "Default"
      }
    ],
    "dataLakeFieldInputRepresentations": [
      {
        "name": "bikeid",
        "label": "bikeid",
        "dataType": "Number",
        "isPrimaryKey": True
      },
      {
        "label": "to_station_id",
        "name": "to_station_id",
        "dataType": "Number",
        "isPrimaryKey": False
      },
      {
        "name": "from_station_id",
        "label": "from_station_id",
        "dataType": "Number",
        "isPrimaryKey": False
      },
      {
        "label": "to_station_name",
        "name": "to_station_name",
        "dataType": "Text",
        "isPrimaryKey": False
      },
      {
        "name": "from_station_name",
        "label": "from_station_name",
        "dataType": "Text",
        "isPrimaryKey": False
      },
      {
        "name": "concate",
        "label": "concate r",
        "dataType": "Text",
        "isPrimaryKey": False
      },
      {
        "name": "starttime",
        "label": "starttime",
        "dataType": "DateTime",
        "isPrimaryKey": False
      }
    ]
  },
  "sourceFields": [
    {
      "name": "bikeid",
      "dataType": "Number"
    },
    {
      "name": "from_station_id",
      "dataType": "Number"
    },
    {
      "name": "to_station_id",
      "dataType": "Number"
    },
    {
      "name": "from_station_name",
      "dataType": "Text"
    },
    {
      "name": "to_station_name",
      "dataType": "Text"
    },
    {
      "name": "starttime",
      "dataType": "DateTime"
    }
  ],
  "mappings": [
    {
      "sourceFieldLabel": "bikeid",
      "targetFieldName": "bikeid"
    },
    {
      "sourceFieldLabel": "to_station_id",
      "targetFieldName": "to_station_id"
    },
    {
      "sourceFieldLabel": "from_station_id",
      "targetFieldName": "from_station_id"
    },
    {
      "sourceFieldLabel": "to_station_name",
      "targetFieldName": "to_station_name"
    },
    {
      "sourceFieldLabel": "from_station_name",
      "targetFieldName": "from_station_name"
    },
    {
      "sourceFieldLabel": "starttime",
      "targetFieldName": "starttime"
    },
    {
      "transformationFormula": "CONCAT(sourceField['to_station_name'],\" \",sourceField['from_station_name'])",
      "targetFieldName": "concate",
      "targetFieldReturntype": "Text"
    }
  ],
  "refreshConfig": {
    "refreshMode": "UPSERT",
    "frequency": {
      "frequencyType": "WEEKLY",
      "refreshDayOfWeek": "Sunday",
      "hours": [
        7
      ]
    }
  },
  "advancedAttributes": {
    "fileName": "*",
    "fileType": "CSV",
    "importDirectory": "divvy",
    "isMissingFileFailure": True,
    "areHeadersIncludedInFile": False
  }
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




