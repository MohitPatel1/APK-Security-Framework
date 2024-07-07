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
    
    upload_url = 'http://127.0.0.1:8000/api/v1/upload'
    report_url = 'http://127.0.0.1:8000/api/v1/report_json'
    headers = {
        'Authorization': 'b211a732f3fed3446c679382db7b2645b965495e9206ba6614e077d0bb6f7465'
    }
    
    # Check if the file exists and has a supported extension
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist.")
        return
    
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension not in ['.apk', '.zip', '.ipa', '.appx']:
        print(f"Error: File {file_path} is not a supported type (apk, zip, ipa, appx).")
        return
    
    # Prepare the file for upload
    with open(file_path, 'rb') as file:
        files = {'file': (os.path.basename(file_path), file, 'application/octet-stream')}
        
        # Send the POST request for upload
        upload_response = requests.post(upload_url, headers=headers, files=files)
    
    if upload_response.status_code == 200:
        try:    
            upload_json = upload_response.json()
            print("Received JSON response from upload:")
            print(json.dumps(upload_json, indent=2))
            print(upload_json['hash'])
            
            # Prepare the data payload for report
            data = {
                'hash': upload_json['hash']
            }
            
            # Send the POST request for report
            report_response = requests.post(report_url, headers=headers, data=data)
            
            if report_response.status_code == 200:
                try:
                    report_json = report_response.json()
                    print("Received JSON response from report:")
                    print(json.dumps(report_json, indent=2))
                    
                    # Save the JSON response to a file
                    save_json_report(report_json)
                except json.JSONDecodeError:
                    print("Received a response from report, but it was not valid JSON")
                    print(f"Raw response: {report_response.text}")
            else:
                print(f"Failed to get report. Status code: {report_response.status_code}")
                print(f"Response content: {report_response.text}")
            
        except json.JSONDecodeError:
            print("Received a response from upload, but it was not valid JSON")
            print(f"Raw response: {upload_response.text}")
    else:
        print(f"Failed to upload file. Status code: {upload_response.status_code}")
        print(f"Response content: {upload_response.text}")

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