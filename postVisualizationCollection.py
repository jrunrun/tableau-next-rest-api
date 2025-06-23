import simple_salesforce
from simple_salesforce import Salesforce, SalesforceMalformedRequest
import requests
import xml.etree.ElementTree as ET
import json
from typing import Any


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

def post_visualization_collection_with_requests(base_url: str, access_token: str) -> dict[str, Any]:
    """Fetch all available visualizations using requests.
    
    Args:
        base_url: The base URL for the Tableau API (e.g., 'https://your-instance.salesforce.com')
        access_token: OAuth access token for authentication
        
    Returns:
        Dictionary containing the visualization collection response
        
    Raises:
        requests.exceptions.RequestException: If the API request fails
    """
    import requests
    
    # Construct the endpoint using the standard Salesforce API format
    endpoint = f"{base_url}/services/data/v64.0/tableau/visualizations" + "?minVersion=-1"
    print(f"Endpoint: {endpoint}")
    
    # Set up headers with authentication
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
                "id": "",
                "label": "Copy of Sales by State",
                "name": "Sales_by_State",
                "dataSource": {
                    "id": "2SMHo0000008OIFOA2",
                    "label": "NTO_External",
                    "name": "New_Semantic_Model",
                    "type": "SemanticModel"
                },
                "workspace": {
                    "id": "1DyHo0000000006KAA",
                    "label": "TabEmbed",
                    "name": "TabEmbed"
                },
                "visualSpecification": {
                    "columns": ["F2"],
                    "forecasts": {},
                    "legends": {
                        "F4": {
                            "isVisible": False,
                            "position": "Right",
                            "title": {
                                "isVisible": True,
                                "titleText": "SUM(Gross Margin)"
                            }
                        }
                    },
                    "marks": {
                        "ALL": {
                            "encodings": [{
                                "fieldKey": "F4",
                                "type": "Color"
                            }],
                            "isAutomatic": False,
                            "stack": {
                                "isAutomatic": True,
                                "isStacked": True
                            },
                            "type": "Bar"
                        }
                    },
                    "measureValues": [],
                    # "mode": "Visualization",
                    "referenceLines": {},
                    "rows": ["F1"],
                    "style": {
                        "axis": {
                            "F2": {
                                "isVisible": True,
                                "range": {
                                    "includeZero": True,
                                    "type": "Auto"
                                },
                                "scale": {
                                    "format": {
                                        "numberFormatInfo": {
                                            "decimalPlaces": 2,
                                            "displayUnits": "Auto",
                                            "includeThousandSeparator": True,
                                            "negativeValuesFormat": "Auto",
                                            "prefix": "",
                                            "suffix": "",
                                            "type": "NumberShort"
                                        }
                                    }
                                },
                                "ticks": {
                                    "majorTicks": {
                                        "type": "Auto"
                                    },
                                    "minorTicks": {
                                        "type": "Auto"
                                    }
                                },
                                "titleText": "Sales"
                            }
                        },
                        "fieldLabels": {
                            "columns": {
                                "showLabels": True
                            },
                            "rows": {
                                "showLabels": True
                            }
                        },
                        "fit": "Standard",
                        "headers": {
                            "F1": {
                                "hiddenValues": [],
                                "isVisible": True,
                                "showMissingValues": False
                            }
                        },
                        "marks": {
                            "ALL": {
                                "color": {
                                    "color": ""
                                },
                                "label": {
                                    "canOverlapLabels": False,
                                    "marksToLabel": {
                                        "type": "All"
                                    },
                                    "showMarkLabels": False
                                }
                            }
                        },
                        "panes": {
                            "F2": {
                                "defaults": {
                                    "format": {
                                        "numberFormatInfo": {
                                            "decimalPlaces": 2,
                                            "displayUnits": "Auto",
                                            "includeThousandSeparator": True,
                                            "negativeValuesFormat": "Auto",
                                            "prefix": "",
                                            "suffix": "",
                                            "type": "Number"
                                        }
                                    }
                                }
                            },
                            "F4": {
                                "defaults": {
                                    "format": {
                                        "numberFormatInfo": {
                                            "decimalPlaces": 2,
                                            "displayUnits": "Auto",
                                            "includeThousandSeparator": True,
                                            "negativeValuesFormat": "Auto",
                                            "prefix": "",
                                            "suffix": "",
                                            "type": "Number"
                                        }
                                    }
                                }
                            }
                        },
                        "referenceLines": {},
                        "showDataPlaceholder": False,
                        "title": {
                            "isVisible": True
                        }
                    }
                },
                "fields": {
                    "F1": {
                        "displayCategory": "Discrete",
                        "fieldName": "State",
                        "objectName": "Retail_NTO_Dataverse",
                        "role": "Dimension",
                        "type": "Field"
                    },
                    "F2": {
                        "displayCategory": "Continuous",
                        "fieldName": "Sales",
                        "function": "Sum",
                        "objectName": "Retail_NTO_Dataverse",
                        "role": "Measure",
                        "type": "Field"
                    },
                    "F3": {
                        "displayCategory": "Continuous",
                        "fieldName": "Sales",
                        "function": "Sum",
                        "objectName": "Retail_NTO_Dataverse",
                        "role": "Measure",
                        "type": "Field"
                    },
                    "F4": {
                        "displayCategory": "Continuous",
                        "fieldName": "Gross_Margin",
                        "function": "Sum",
                        "objectName": "Retail_NTO_Dataverse",
                        "role": "Measure",
                        "type": "Field"
                    }
                },
                "view": {
                    "label": "default",
                    "name": "Sales_by_State_default",
                    "viewSpecification": {
                        "filters": [],
                        "sortOrders": {
                            "columns": [],
                            "fields": {
                                "F1": {
                                    "byField": "F3",
                                    "order": "Descending",
                                    "type": "Nested"
                                }
                            },
                            "rows": []
                        }
                    }
                },
                "interactions": []
            }
    try:
        # Save the payload to a file
        with open('./sample-requests/postVisualizationCollection-request.json', 'w') as f:
            json.dump(payload, f, indent=2)
        print("Payload has been saved to postVisualizationCollection-request.json")
        
        # Make the POST request
        response = requests.post(endpoint, headers=headers, data=json.dumps(payload))
        
        # Print response details for debugging
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print("Response Text:")
        try:
            print(json.dumps(response.json(), indent=2))
            # Save the formatted JSON response to a file
            with open('./sample-responses/postVisualizationCollection-response.json', 'w') as f:
                json.dump(response.json(), f, indent=2)
            print("Response has been saved to postVisualizationCollection-response.json")
        except json.JSONDecodeError:
            print(response.text)
        
        # Raise an error for bad status codes
        response.raise_for_status()
        
        # Return the JSON response
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching visualizations: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response Status Code: {e.response.status_code}")
            print(f"Response Headers: {e.response.headers}")
            print(f"Response Text: {e.response.text}")
        raise

org = 'storm-dc631f52cc1aeb.my.salesforce.com'
username = 'jcraycraft.6890ccbb70@salesforce.com'
password = 'orgfarm1234'
data_space = 'default'

auth_token = get_session_id(org, username, password)

sf = Salesforce(
    session_id=auth_token, 
    instance_url="https://" + org, 
    version='v64.0'
)

post_visualization_collection_with_requests("https://" + org, auth_token)