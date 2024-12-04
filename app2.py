import requests
import json

BASE_URL = "http://localhost:9000"  # Replace with your server's base URL

# Test data
event_data = {
    "association_name": "Tech Club",
    "event_name": "AI Workshop",
    "secretary_name": ["John Doe"],
    "secretary_roll": ["123456"],
    "secretary_mobile": ["9876543210"],
    "convenor_name": ["Jane Smith"],
    "convenor_roll": ["654321"],
    "convenor_mobile": ["1234567890"],
    "volunteer_name": ["Alice", "Bob"],
    "volunteer_roll": ["111111", "222222"],
    "volunteer_mobile": ["5555555555", "6666666666"]
}

def save_event():
    """
    Test the /save-event endpoint.
    """
    url = f"{BASE_URL}/save-event"
    try:
        print(url)
        response = requests.post(url, json=event_data)
        response.raise_for_status()
        data = response.json()
        print("Event saved successfully:")
        print(json.dumps(data, indent=4))
        return data.get("id")  # Return the event ID
    except requests.exceptions.RequestException as e:
        print(str(e))
        print(f"Error saving event: {e}")
        return None

def generate_pdf(event_id):
    """
    Test the /generate-pdf/<event_id> endpoint.
    """
    url = f"{BASE_URL}/generate-pdf/{event_id}"
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Save the PDF file
        pdf_filename = "filled_form.pdf"
        with open(pdf_filename, "wb") as pdf_file:
            pdf_file.write(response.content)

        print(f"PDF generated successfully and saved as '{pdf_filename}'")
    except requests.exceptions.RequestException as e:
        print(f"Error generating PDF: {e}")

if __name__ == "__main__":
    # Save event and get the event ID
    event_id = save_event()

    # If event was saved successfully, generate the PDF
    if event_id:
        generate_pdf(event_id)