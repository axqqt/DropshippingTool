import csv
from datetime import datetime
import time
import random
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import os

# Set up OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def ai_analyze_prompt(prompt):
    """
    Use OpenAI to analyze the prompt and extract key terms.
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that extracts key search terms from product prompts."},
            {"role": "user", "content": f"Extract key search terms from this prompt: {prompt}"}
        ]
    )
    key_terms = response.choices[0].message.content.split(', ')
    return key_terms

def search_aliexpress(key_terms, num_products):
    """
    Search AliExpress for products using key terms.
    """
    search_url = f"https://www.aliexpress.com/wholesale?SearchText={'+'.join(key_terms)}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    product_links = []
    for item in soup.find_all('a', class_='manhattan--container--1lP57Ag'):
        if len(product_links) >= num_products:
            break
        product_links.append('https:' + item['href'])
    
    return product_links

def ai_analyze_product(url):
    """
    Use OpenAI to analyze a product URL and generate product details.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract basic product information
    title = soup.find('h1', class_='product-title-text').text.strip()
    price = soup.find('span', class_='product-price-value').text.strip()
    description = soup.find('div', class_='product-description').text.strip()
    
    # Use OpenAI to analyze and enhance the product details
    ai_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that analyzes product information and generates enhanced details for e-commerce listings."},
            {"role": "user", "content": f"Analyze this product and generate enhanced details for a Shopify store:\nTitle: {title}\nPrice: {price}\nDescription: {description}"}
        ]
    )
    ai_analysis = ai_response.choices[0].message.content
    
    # Parse AI analysis to extract structured data
    # (This is a simplified example; you might want to implement more robust parsing)
    ai_lines = ai_analysis.split('\n')
    ai_data = {}
    for line in ai_lines:
        if ':' in line:
            key, value = line.split(':', 1)
            ai_data[key.strip()] = value.strip()
    
    return {
        "Handle": f"product-{random.randint(1000, 9999)}",
        "Title": ai_data.get('Title', title),
        "Body (HTML)": f"<p>{ai_data.get('Description', description)}</p>",
        "Vendor": "AliExpress",
        "Product Category": ai_data.get('Category', ''),
        "Type": ai_data.get('Type', ''),
        "Tags": ai_data.get('Tags', ''),
        "Published": "TRUE",
        "Option1 Name": "Size",
        "Option1 Value": ai_data.get('Size', 'One Size'),
        "Option2 Name": "Color",
        "Option2 Value": ai_data.get('Color', 'Default'),
        "Variant SKU": f"SKU-{random.randint(1000, 9999)}",
        "Variant Price": price,
        "Variant Inventory Qty": str(random.randint(10, 100)),
        "Image Src": soup.find('img', class_='magnifier-image')['src'],
    }

def create_shopify_csv(prompt, num_products):
    key_terms = ai_analyze_prompt(prompt)
    product_urls = search_aliexpress(key_terms, num_products)
    products = []

    for url in product_urls:
        product_data = ai_analyze_product(url)
        products.append(product_data)
        time.sleep(random.uniform(2, 5))  # Polite scraping

    filename = f"ai_analyzed_{prompt.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = products[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for product in products:
            writer.writerow(product)
    
    print(f"CSV file '{filename}' has been created with {len(products)} AI-analyzed products.")

# Example usage
prompt = input("Enter a product prompt: ")
num_products = int(input("Enter number of products to analyze: "))
create_shopify_csv(prompt, num_products)