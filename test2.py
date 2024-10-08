import requests
import lzma
import csv

# API endpoint URL
url = "https://api.niftykit.com/v3/collections/export/csv"

# Set your API key
api_key = "e2b01faf-5d89-4a7d-8ae5-6b90371b443e"

# Set the headers
headers = {
    "x-api-key": api_key,
}

# Set the query parameters
params = {
    "type": "lzma",  # Assuming the data is compressed with lzma
}

# Make the GET request
response = requests.get(url, headers=headers, params=params)

# Check the response
if response.status_code == 200:
    # Decompress the received data
    compressed_data = response.content
    decompressed_data = lzma.decompress(compressed_data)
    
    # Save the decompressed data to a file
    with open("exported_file.csv", "wb") as file:
        file.write(decompressed_data)
    
    print("CSV file exported successfully.")
else:
    print(f"Failed to export CSV file. Status code: {response.status_code}, Response: {response.text}")
