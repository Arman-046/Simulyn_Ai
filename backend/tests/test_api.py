import requests

url = "http://127.0.0.1:8000/api/generate_population"
payload = {
    "scenario": {
        "product_name": {"value": "Test Product"},
        "category": {"value": "Tech"},
        "industry": {"value": "Tech"},
        "business_model": {"value": "B2C"},
        "target_audience": {"value": "Gamers"},
        "price": {"value": 99.99},
        "currency": {"value": "USD"},
        "launch_region": {"value": "North America"},
        "marketing_budget": {"value": 500000},
        "competitors": {"value": "Apple"}
    },
    "num_nodes": 50
}
try:
    response = requests.post(url, json=payload)
    print("STATUS", response.status_code)
    print("RESPONSE", response.text[:500])
except Exception as e:
    print("ERROR", e)
