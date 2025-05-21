import requests
import json


# url = 'http:///services/data/v62.0/ssot/semantic/models/{modelApiNameOrId}'
# req = requests.get(url)


headers = {
    "Authorization": "Bearer 00DHo000003yF1p!ARIAQIsY7uHB72amRNWXwU2FF2pFEP6lHSORsYNUwcuwYb9MGW7AqrXndRfvgIg6jubtZNsuvvv31c8m5Y8mafZm5dnz2j9U"
}

org = 'storm-dc631f52cc1aeb.my.salesforce.com' 

modelApiNameOrId = 'Retail_NTO'

url = f'https://{org}/services/data/v62.0/ssot/semantic/models/{modelApiNameOrId}'
req = requests.get(url, headers=headers)

print(f"Status Code: {req.status_code}")
print("\nHeaders:")
print(json.dumps(dict(req.headers), indent=2))
print("\nResponse Body:")

# Save the formatted JSON response to a file
with open('semantic_model_response.json', 'w') as f:
    json.dump(req.json(), f, indent=2)

print("Response has been saved to semantic_model_response.json")

# Print to console as well
print(json.dumps(req.json(), indent=2))




