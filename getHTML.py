import wget 
from links import linksCO, linksNY, linksMA, linksCA, linksWA, linksRI, linksDC, linksCT, gen 
import wget
import os
import requests


# for file_number, link in enumerate(linksRI):
    
#     filename = f'pfl{str(file_number)}.html'
#     output_path = os.path.join("websites", filename)
#     wget.download(link, out=output_path)


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

if not os.path.exists('websites'):
    os.makedirs('websites')

for file_number, link in enumerate(linksDC):
    try:
        response = requests.get(link, headers=headers)
        response.raise_for_status()  # Check if the request was successful
        filename = f'pfl{str(file_number)}.html'
        output_path = os.path.join("websites", filename)
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(response.text)
        print(f"Downloaded: {filename}")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # HTTP error
    except Exception as err:
        print(f"Other error occurred: {err}")  # Other error

print("Download completed.")