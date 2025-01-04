import requests
from bs4 import BeautifulSoup
import json
import time

def scrape_products(input_class,base_url, pages=5):
    products = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # Loop through the pages
    for page in range(1, pages + 1):
        print(f"Scraping page {page}...")
        url = f"{base_url}?page={page}"
        
        try:
            # Send request to the website and get the content
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Check if request was successful
            soup = BeautifulSoup(response.content, 'html.parser')

            # Locate the product listings (using class defined in the webpage)
            product_listings = soup.find_all('div', class_=input_class)

            if not product_listings:
                print(f"No product listings found on page {page}.")
            
            for product in product_listings:
                title = product.find('a', class_='title').text.strip()
                price = product.find('h4', class_='pull-right').text.strip()
                description = product.find('p', class_='description').text.strip()
                product_url = "https://webscraper.io" + product.find('a')['href']
                image_url = product.find('img')['src']
                
                # Append the data to the products list
                products.append({
                    'Title': title,
                    'Price': price,
                    'Description': description,
                    'Product URL': product_url,
                    'Image URL': image_url
                })
            
            # Pause between requests to avoid overwhelming the server
            time.sleep(2)

        except requests.exceptions.RequestException as e:
            print(f"Error while scraping page {page}: {e}")
            continue
    
    return products

def save_to_json(data, filename='scraped_data.json'):
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"Data saved to {filename}")
    except Exception as e:
        print(f"Error saving data to {filename}: {e}")

if __name__ == "__main__":
    BASE_URL = "https://webscraper.io/test-sites/e-commerce/allinone"
    input_class = "col-md-4 col-xl-4 col-lg-4"
    scraped_products = scrape_products(input_class, BASE_URL, pages=5)
    
    if scraped_products:
        save_to_json(scraped_products)
    else:
        print("No data was scraped.")
