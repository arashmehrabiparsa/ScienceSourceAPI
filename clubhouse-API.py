import scipy
import requests

def get_clubhouse_data(auth_token, house_url):
    """Fetches data from a Clubhouse house with authorization (if applicable).

    Args:
        auth_token (str): Clubhouse authentication token (if required).
        house_url (str): URL of the Clubhouse house to scrape (replace with actual URL).

    Returns:
        dict: Dictionary containing the fetched data (structure depends on Clubhouse's API).

    Raises:
        Exception: If an error occurs during the request.
    """

    headers = {
        "Authorization": f"Bearer {auth_token}",  # Include authentication token if required
        "CH-Languages": "en-US",
        "CH-Locale": "en_US",
        "Accept": "application/json",
        # ... other headers as needed
    }

    try:
        response = requests.get(house_url, headers=headers)
        response.raise_for_status()  # Raise an exception for non-200 status codes

        return response.json()  # Assuming data is in JSON format

    except requests.exceptions.RequestException as e:
        raise Exception(f"Error getting Clubhouse data: {e}")

# Replace with your actual Clubhouse authentication token (if applicable)
auth_token = "YOUR_CLUBHOUSE_AUTH_TOKEN"  # Replace with actual token

# Replace with the actual URL of the Quantum Photonics House
house_url = "https://www.clubhouse.com/house/quantum-photonics-house"

try:
    clubhouse_data = get_clubhouse_data(auth_token, house_url)

    # Extract PDF URLs from live chat or pinned links
    pdf_urls = extract_pdf_urls(clubhouse_data)

    # Process the extracted PDF URLs (e.g., download, analyze)
    for pdf_url in pdf_urls:
        # ... logic to download or process the PDF ...

except Exception as e:
    print(f"An error occurred: {e}")

def extract_pdf_urls(clubhouse_data):
    """Extracts PDF URLs from Clubhouse data.

    Args:
        clubhouse_data (dict): Dictionary containing Clubhouse data.

    Returns:
        list: List of PDF URLs.
    """

    pdf_urls = []

    # Assuming the data structure is similar to the example below
    for room in clubhouse_data["rooms"]:
        for message in room["messages"]:
            if "text" in message and "pdf" in message["text"].lower():
                pdf_urls.append(message["text"])  # Extract PDF URLs from message text

        for pinned_link in room["pinned_links"]:
            if "url" in pinned_link and "pdf" in pinned_link["url"].lower():
                pdf_urls.append(pinned_link["url"])  # Extract PDF URLs from pinned links

    return pdf_urls