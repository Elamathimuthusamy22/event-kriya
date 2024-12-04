import requests
import json

BASE_URL = "http://localhost:9000"  # Replace with your server's base URL

# Test data for event
event_data = {
    "association_name": "Tech Club",
    "event_name": "AI Workshop",
    "secretary": {
        "name": "John Doe",
        "roll": "123456",
        "mobile": "9876543210"
    },
    "convenors": {
        "name": "Jane Smith",
        "roll": "654321",
        "mobile": "1234567890"
    },
    "volunteers": [
        {
            "name": "Alice",
            "roll": "111111",
            "mobile": "5555555555"
        },
        {
            "name": "Bob",
            "roll": "222222",
            "mobile": "6666666666"
        }
    ]
}

# Save event and generate PDF
def save_event():
    url = f"{BASE_URL}/save-event"
    try:
        response = requests.post(url, json=event_data)
        response.raise_for_status()
        data = response.json()
        print("Event saved successfully:")
        print(json.dumps(data, indent=4))
        return data.get("id")  # Return the event ID
    except requests.exceptions.RequestException as e:
        print(f"Error saving event: {e}")
        return None

def generate_pdf(event_id):
    url = f"{BASE_URL}/generate-pdf/{event_id}"
    response = requests.get(url)
    with open("event_details.pdf", "wb") as f:
        f.write(response.content)

if __name__ == "__main__":
    event_id = save_event()
    generate_pdf(event_id)
