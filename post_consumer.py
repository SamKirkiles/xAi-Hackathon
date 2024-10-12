import time

def start_poll():
    current_time = time.time()

    # Get the timestamp of the last 30 seconds 
    last_minute_timestamp = current_time - 60

    # Print the Unix timestamp (rounded to an integer)
    print(int(last_minute_timestamp))
    
    print("Got a post")