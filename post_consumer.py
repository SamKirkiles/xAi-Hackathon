import time
from time import sleep
import grok
import requests 
from datetime import datetime, timezone, timedelta

def start_poll():

    while True:

        current_time_unix = time.time()

        # Get the time 60 seconds ago in Unix timestamp format
        current_time = datetime.now(timezone.utc)

        # Subtract 1 minute (60 seconds) from the current time
        time_1_minute_ago = current_time - timedelta(minutes=1)

        # Get the time 1 minute ago in ISO 8601 format
        time_1_minute_ago_rfc3339 = time_1_minute_ago.strftime('%Y-%m-%dT%H:%M:%SZ')

        bearer_token = ""

        # Twitter API endpoint
        url = "https://api.twitter.com/2/users/1845203589314273280/mentions?start_time="+str(time_1_minute_ago_rfc3339)

        # Set up headers with the authorization token
        headers = {
            "Authorization": f"Bearer {bearer_token}"
        }

        # Send the request
        response = requests.get(url, headers=headers)

        # Check the response
        if response.status_code == 200:
            # Print the JSON response if successful
            res = response.json()
            print(grok.check_review(str(res)))

        else:
            # Print an error message if the request fails
            print(f"Error: {response.status_code}")
            print(response.text)

        sleep(45)