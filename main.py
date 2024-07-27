import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import shopify
import schedule
import threading
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

history = [];

# LangChain setup
template = """
Answer the question below.

Here is the conversation history : {history}

Question : {question}

Answer:
"""

model = OllamaLLM(model="llama2")  # Changed to llama2 as llama3 doesn't exist
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

# Shopify setup
shop_url = "your-store.myshopify.com"  # Replace with your actual shop URL
api_version = '2023-04'
private_app_password = 'your_private_app_password'  # Replace with your actual password

shopify.ShopifyResource.set_site(f"https://{shop_url}/admin/api/{api_version}")
shopify.ShopifyResource.set_user("your_api_key")  # Replace with your actual API key
shopify.ShopifyResource.set_password(private_app_password)

# Verify Shopify connection
try:
    shop = shopify.Shop.current()
    print(f"Connected to Shopify store: {shop.name}")
except Exception as e:
    print(f"Failed to connect to Shopify: {e}")
    exit(1)

def get_product_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    products = []

    for item in soup.select('.product-item'):
        try:
            title = item.select_one('.product-title').text.strip()
            price = item.select_one('.product-price').text.strip()
            link = item.select_one('a')['href']
            image_url = item.select_one('img')['src']
            description = item.select_one('.product-description').text.strip()
            products.append({
                'title': title,
                'price': price,
                'link': link,
                'image_url': image_url,
                'description': description
            })
        except AttributeError as e:
            print(f"Error parsing product: {e}")
            continue

    return products

def classify_products_with_llama(products):
    def get_llama_classification(title, description):
        question = f"Classify this product: Title: {title}, Description: {description}"
        result = chain.invoke({"history": "", "question": question})
        return result.strip()

    relevant_products = []
    for product in products:
        category = get_llama_classification(product['title'], product['description'])
        if category:
            product['category'] = category
            relevant_products.append(product)
    
    return relevant_products

def scrape_multiple_pages(base_url, num_pages):
    all_products = []
    for i in range(1, num_pages + 1):
        url = f"{base_url}?page={i}"
        print(f"Scraping page {i}...")
        products = get_product_data(url)
        all_products.extend(products)
        time.sleep(random.uniform(1, 3))
    return all_products

def update_stock(product, stock):
    try:
        shopify_product = shopify.Product.find(product['shopify_id'])
        variant = shopify_product.variants[0]
        variant.inventory_quantity = stock
        variant.save()
        print(f"Updated stock for product {product['title']} to {stock}")
    except Exception as e:
        print(f"Failed to update stock for product {product['title']}: {e}")

def check_and_update_stock():
    df = pd.read_csv('aliexpress_women_products.csv')
    for index, row in df.iterrows():
        aliexpress_url = row['link']
        try:
            response = requests.get(aliexpress_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            stock_element = soup.select_one('.product-quantity-tip')
            if stock_element:
                stock = int(stock_element.text.strip().split()[0])
                df.at[index, 'stock'] = stock
                update_stock(row, stock)
            
            if stock == 0:
                substitute = find_substitute(row['title'])
                if substitute:
                    df.at[index, 'substitute'] = substitute['link']
        except Exception as e:
            print(f"Error checking stock for {row['title']}: {e}")
    
    df.to_csv('aliexpress_women_products.csv', index=False)

def find_substitute(product_title):
    search_url = f"https://www.aliexpress.com/wholesale?SearchText={product_title.replace(' ', '+')}"
    try:
        response = requests.get(search_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        first_result = soup.select_one('.product-item')
        if first_result:
            link = first_result.select_one('a')['href']
            return {'link': link}
    except Exception as e:
        print(f"Error finding substitute for {product_title}: {e}")
    return None

def run_stock_check():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Main execution
if __name__ == "__main__":
    base_url = 'https://www.aliexpress.com/category/200003482/women-clothing.html'
    num_pages = 5  # Adjust as needed

    all_products = scrape_multiple_pages(base_url, num_pages)
    print(f"Total products scraped: {len(all_products)}")

    relevant_products = classify_products_with_llama(all_products)
    print(f"Relevant products found: {len(relevant_products)}")

    # Convert to DataFrame and save to CSV
    df = pd.DataFrame(relevant_products)
    df['stock'] = 0  # Initialize stock
    df['substitute'] = ''  # Initialize substitute column
    df['shopify_id'] = ''  # Initialize Shopify ID column

    # Create products in Shopify and get their IDs
    for index, row in df.iterrows():
        try:
            new_product = shopify.Product()
            new_product.title = row['title']
            new_product.body_html = row['description']
            new_product.vendor = 'AliExpress'
            new_product.product_type = row['category']
            
            variant = shopify.Variant()
            variant.price = row['price']
            variant.sku = f"ALI-{index}"
            new_product.variants = [variant]
            
            new_product.save()
            df.at[index, 'shopify_id'] = new_product.id
            print(f"Created Shopify product: {new_product.title}")
        except Exception as e:
            print(f"Failed to create Shopify product for {row['title']}: {e}")

    csv_file = 'aliexpress_women_products.csv'
    df.to_csv(csv_file, index=False)
    print(f"Exported {len(df)} relevant products to {csv_file}")

    # Schedule stock checks
    schedule.every(1).hour.do(check_and_update_stock)

    # Run the stock check in a separate thread
    stock_thread = threading.Thread(target=run_stock_check)
    stock_thread.start()

    print("Stock checking started. Press Ctrl+C to stop.")

    # Keep the main thread running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping stock checking...")
        # You might want to add any cleanup code here