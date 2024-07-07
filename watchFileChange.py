import time
import requests
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            print(f"New file detected: {event.src_path}")
            process_new_file(event.src_path)

def process_new_file(file_path):
    print(f"Processing new file: {file_path}")
    
    url = 'http://localhost:8000/api/v1/upload'
    headers = {
        'Authorization': 'b211a732f3fed3446c679382db7b2645b965495e9206ba6614e077d0bb6f7465'
    }
    
    with open(file_path, 'rb') as file:
        files = {'file': file}
        response = requests.post(url, headers=headers, files=files)
    
    if response.status_code == 200:
        try:
            json_response = response.json()
            print("Received JSON response:")
            print(json.dumps(json_response, indent=2))
            
            # You can add more specific handling of the JSON data here
            # For example:
            # if 'status' in json_response and json_response['status'] == 'success':
            #     print("File processed successfully by the API")
            # else:
            #     print("API reported an issue with the file")
            
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