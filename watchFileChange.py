import time
import requests
import json
import os
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            print(f"New file detected: {event.src_path}")
            process_new_file(event.src_path)

def save_json_report(json_data):
    # Create the jsonReports directory if it doesn't exist
    os.makedirs("jsonReports", exist_ok=True)
    
    # Generate a filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"jsonReports/report_{timestamp}.json"
    
    # Write the JSON data to the file
    with open(filename, 'w') as f:
        json.dump(json_data, f, indent=2)
    
    print(f"JSON report saved to {filename}")

def process_new_file(file_path):
    print(f"Processing new file: {file_path}")
    
    url = 'http://127.0.0.1:8000/api/v1/report_json'
    headers = {
        'Authorization': 'b211a732f3fed3446c679382db7b2645b965495e9206ba6614e077d0bb6f7465'
    }
    
    # Prepare the data payload
    data = {
        'hash': "5683c6f7c03b48ab80bc2adddeff895f"
    }
    
    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code == 200:
        try:    
            json_response = response.json()
            print("Received JSON response:")
            print(json.dumps(json_response, indent=2))
            
            # Save the JSON response to a file
            save_json_report(json_response)
            
        except json.JSONDecodeError:
            print("Received a response, but it was not valid JSON")
            print(f"Raw response: {response}")
            print(f"Raw response: {response.text}")
    else:
        print(f"Failed to upload file. Status code: {response.status_code}")
        print(f"Response content: {response.text}")

def watch_directory(path):
    event_handler = NewFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    watch_directory("RakshakScraper")