import os
import base64
import requests
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variables
API_KEY = os.getenv("INTERVALS_ICU_API_KEY")
if not API_KEY:
    raise ValueError("API key not found. Make sure to set INTERVALS_API_KEY in your .env file.")

def upload_workout(file_path: str, athlete_id: str, start_date: str, external_id: str) -> requests.Response:
    """
    Uploads a .fit workout file to the Intervals.icu API.

    Args:
        file_path (str): Path to the .fit file.
        athlete_id (str): Athlete ID for the API. This is the athlete's ID on intervals.icu.
        start_date (str): Start date and time of the workout in ISO 8601 format (e.g., "2025-01-10T09:00:00").
        external_id (str): Unique external ID for the workout.

    Returns:
        Response object: The response from the API call.
    """
    url = f"https://intervals.icu/api/v1/athlete/{athlete_id}/events/bulk?upsert=true"
    
    try:
        # Read and encode the .fit file in Base64
        with open(file_path, "rb") as file:
            file_contents = file.read()
            file_contents_base64 = base64.b64encode(file_contents).decode("utf-8")
        
        # Prepare the payload
        payload = [{
            "category": "WORKOUT",
            "start_date_local": start_date,
            "filename": os.path.basename(file_path),
            "file_contents_base64": file_contents_base64,
            "external_id": external_id
        }]
        
        # Make the API request
        response = requests.post(url, auth=("API_KEY", API_KEY), json=payload)
        
        # Check for successful upload
        if response.status_code == 200:
            logging.info("Workout uploaded successfully.")
        else:
            logging.error(f"Error uploading workout: {response.status_code}")
            logging.error(response.text)
        
        return response
    except FileNotFoundError:
        logging.error(f"Error: File not found at path {file_path}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    try:
        file_path = "/Users/ericchuu/structured_workout.fit" # Change to path to your .fit file
        athlete_id = "i73709" # Change to your athlete ID
        start_date = "2025-01-09T09:00:00" # Change to your start date
        external_id = "unique_workout_id_123" # Change to your external ID
        upload_workout(file_path, athlete_id, start_date, external_id)
    except Exception as e:
        logging.error(f"An error occurred: {e}")

