import requests
from bs4 import BeautifulSoup
import time
import csv

# Define the URL pattern for all 20 pages
URL_PATTERN = 'https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%252+C283&ref=sr_pg_{}'

# Define the header row for the CSV file
header = ['ProductURL', 'Description', 'ASIN', 'ProductDescription', 'Manufacturer']

# Open a new CSV file and write the header row to it
with open('products.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(header)

    # Loop through all 20 pages and scrape the data
    for page_num in range(1, 21):
        # Construct the URL for this page
        url = URL_PATTERN.format(page_num)

        # Send a GET request to the URL and handle any errors that occur
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f'Error: {e}')
            continue

        # Parse the HTML content of the response using BeautifulSoup and handle any errors that occur
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f'Error: {e}')
            continue

        # Find all product listings on this page and handle any errors that occur
        try:
            products = soup.find_all('div', {'data-component-type': 's-search-result'})
        except Exception as e:
            print(f'Error: {e}')
            continue

        # Loop through each product and extract its data
        for product in products:
            # Extract the ProductURL and hit it to fetch additional information
            try:
                product_url = product.find('a', {'class': 'a-link-normal'})['href']
            except (KeyError, TypeError) as e:
                print(f'Error: {e}')
                continue

            if not product_url.startswith('http'):
                product_url = 'https://www.amazon.in' + product_url

            print('ProductURL:', product_url)

            # Send a GET request to the ProductURL and handle any errors that occur
            try:
                response_product = requests.get(product_url)
                response_product.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f'Error: {e}')
                continue

            # Parse the HTML content of the response using BeautifulSoup and handle any errors that occur
            try:
                soup_product = BeautifulSoup(response_product.content, 'html.parser')
            except Exception as e:
                print(f'Error: {e}')
                continue

            # Extract Description, ASIN, ProductDescription and Manufacturer
            try:
                description_elem = soup_product.find('span', {'id': 'productTitle'})
                description = description_elem.text.strip() if description_elem else None

                asin = None
                if '/dp/' in product_url:
                    asin_start_index = product_url.index('/dp/') + 4
                    asin_end_index = asin_start_index + 10
                    asin = product_url[asin_start_index:asin_end_index]

                product_description_elem = soup_product.find('div', {'id': 'productDescription'})
                product_description = product_description_elem.text.strip() if product_description_elem else None

                manufacturer_elem = soup_product.find('a', {'id': 'bylineInfo'})
                manufacturer = manufacturer_elem.text.strip() if manufacturer_elem else None
            except Exception as e:
                 print(f'Error: {e}')
                 continue

            # Add the data to the CSV file
            row = [product_url, description, asin, product_description, manufacturer]
            writer.writerow(row)

        # Add a delay between requests to avoid overloading the server
        time.sleep(1)