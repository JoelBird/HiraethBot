import requests
import lzutf8
import csv

# API endpoint URL
url = "https://example.com/v3/collections/import/csv"

# Path to your CSV file
csv_file_path = "path/to/your/file.csv"

# Read the CSV file
with open(csv_file_path, "r") as file:
    csv_data = file.read()

# Encode the CSV data using lzutf8
encoded_data = lzutf8.compress(csv_data.encode("utf-8"))

# Set your API key
api_key = "e2b01faf-5d89-4a7d-8ae5-6b90371b443e"

# Set the headers
headers = {
    "x-api-key": api_key,
    "Content-Type": "application/octet-stream",
}

# Make the POST request
response = requests.post(url, headers=headers, data=encoded_data)

# Check the response
if response.status_code == 200:
    print("CSV file uploaded successfully.")
else:
    print(f"Failed to upload CSV file. Status code: {response.status_code}, Response: {response.text}")
