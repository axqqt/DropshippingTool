import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_product_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    products = []
    # Update selectors based on the actual HTML structure
    for item in soup.select('.list-item'):
        try:
            title = item.select_one('.product-title').text.strip()
            price = item.select_one('.product-price').text.strip()
            link = 'https:' + item.select_one('.product-title a')['href']
            image_url = item.select_one('img')['src']
            products.append({
                'title': title,
                'price': price,
                'link': link,
                'image_url': image_url
            })
        except AttributeError as e:
            print(f"Error: {e}")
            continue

    return products

# Example URL; update this with the actual URL you want to scrape
url = 'https://www.aliexpress.com/category/200004176/womens-clothing.html'

product_data = get_product_data(url)

# Convert to DataFrame
df = pd.DataFrame(product_data)

# Save to CSV
csv_file = 'products_for_shopify.csv'
df.to_csv(csv_file, index=False)

print(f"Exported {len(df)} products to {csv_file}")
