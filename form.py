import requests

# Google Form URL converted to the formResponse endpoint
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSemlBSMvQsQZnAudDXMWXGldJGdZW6VkoDAwbQKsuTGlgZfNg/formResponse"

# Function to submit the form with hardcoded data
def submit_google_form():
    # Hardcoded data to fill the form fields
    form_data = {
        "entry.1641021725": "BOL-1234",     # Example Bill of Lading Number
        "entry.1026077439": "C-567",        # Example Container Number
        "entry.1115772852": "John Doe",     # Example Consignee Name
        "entry.1466739846": "123 Elm St",   # Example Consignee Address
        "entry.1733712848": "01/01/2025",   # Fixed Date
        "entry.1492261839": "5",            # Fixed Line Items Count
        "entry.605394403": "100",           # Fixed Average Gross Weight
        "entry.1951650481": "500"           # Fixed Average Price
    }

    # Submit the form using a POST request
    response = requests.post(GOOGLE_FORM_URL, data=form_data)

    # Check if the submission was successful
    if response.status_code == 200:
        print("Form submitted successfully!")
    else:
        print("Failed to submit the form. Status code:", response.status_code)

# Run the function
if __name__ == "__main__":
    submit_google_form()