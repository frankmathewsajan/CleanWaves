import requests

response = requests.post(
    "http://localhost:8000/api/data/",
    json={
        "temp": 22.5,
        "lat": 37.7749,
        "lon": -122.4194,
        "alt": 20.0,
        "heading": 99.0
    },
    headers={'Content-Type': 'application/json'}
)
print(response.status_code)