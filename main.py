import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import urllib.parse

# LangChain setup
template = """
Answer the question below.

Here is the conversation history : {history}

Question : {question}

Answer:
"""

model = OllamaLLM(model="llama2")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

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
        url = f"{base_url}&page={i}"
        print(f"Scraping page {i}...")
        products = get_product_data(url)
        all_products.extend(products)
        time.sleep(random.uniform(1, 3))
    return all_products

def prepare_shopify_csv(df):
    shopify_df = pd.DataFrame()
    
    shopify_df['Handle'] = df['title'].apply(lambda x: x.lower().replace(' ', '-'))
    shopify_df['Title'] = df['title']
    shopify_df['Body (HTML)'] = df['description']
    shopify_df['Vendor'] = 'AliExpress'
    shopify_df['Product Category'] = df['category']
    shopify_df['Type'] = df['category']
    shopify_df['Tags'] = df['category']
    shopify_df['Published'] = 'TRUE'
    shopify_df['Option1 Name'] = 'Title'
    shopify_df['Option1 Value'] = 'Default Title'
    shopify_df['Option2 Name'] = ''
    shopify_df['Option2 Value'] = ''
    shopify_df['Option3 Name'] = ''
    shopify_df['Option3 Value'] = ''
    shopify_df['Variant SKU'] = df.index.map(lambda x: f'ALI-{x}')
    shopify_df['Variant Grams'] = '0'
    shopify_df['Variant Inventory Tracker'] = 'shopify'
    shopify_df['Variant Inventory Qty'] = '1'
    shopify_df['Variant Inventory Policy'] = 'deny'
    shopify_df['Variant Fulfillment Service'] = 'manual'
    shopify_df['Variant Price'] = df['price']
    shopify_df['Variant Compare At Price'] = ''
    shopify_df['Variant Requires Shipping'] = 'TRUE'
    shopify_df['Variant Taxable'] = 'TRUE'
    shopify_df['Variant Barcode'] = ''
    shopify_df['Image Src'] = df['image_url']
    shopify_df['Image Position'] = '1'
    shopify_df['Image Alt Text'] = df['title']
    shopify_df['Gift Card'] = 'FALSE'
    shopify_df['SEO Title'] = df['title']
    shopify_df['SEO Description'] = df['description'].apply(lambda x: x[:160] + '...' if len(x) > 160 else x)
    shopify_df['Google Shopping / Google Product Category'] = ''
    shopify_df['Google Shopping / Gender'] = ''
    shopify_df['Google Shopping / Age Group'] = ''
    shopify_df['Google Shopping / MPN'] = ''
    shopify_df['Google Shopping / AdWords Grouping'] = ''
    shopify_df['Google Shopping / AdWords Labels'] = ''
    shopify_df['Google Shopping / Condition'] = ''
    shopify_df['Google Shopping / Custom Product'] = ''
    shopify_df['Google Shopping / Custom Label 0'] = ''
    shopify_df['Google Shopping / Custom Label 1'] = ''
    shopify_df['Google Shopping / Custom Label 2'] = ''
    shopify_df['Google Shopping / Custom Label 3'] = ''
    shopify_df['Google Shopping / Custom Label 4'] = ''
    shopify_df['Variant Image'] = ''
    shopify_df['Variant Weight Unit'] = 'kg'
    shopify_df['Variant Tax Code'] = ''
    shopify_df['Cost per item'] = ''
    shopify_df['Status'] = 'active'
    
    return shopify_df

# Main execution
if __name__ == "__main__":
    # Get user input for product category
    product_category = input("Enter the product category you want to scrape (e.g., 'women clothing', 'electronics', etc.): ")
    
    # Encode the user input for use in the URL
    encoded_category = urllib.parse.quote(product_category)
    
    # Construct the base URL with the user's input
    base_url = f'https://www.aliexpress.com/wholesale?SearchText={encoded_category}'
    
    num_pages = int(input("Enter the number of pages to scrape: "))

    all_products = scrape_multiple_pages(base_url, num_pages)
    print(f"Total products scraped: {len(all_products)}")

    relevant_products = classify_products_with_llama(all_products)
    print(f"Relevant products found: {len(relevant_products)}")

    # Convert to DataFrame
    df = pd.DataFrame(relevant_products)

    # Prepare Shopify-compatible CSV
    shopify_df = prepare_shopify_csv(df)

    # Save to CSV
    csv_file = f'aliexpress_{product_category.replace(" ", "_")}_for_shopify.csv'
    shopify_df.to_csv(csv_file, index=False)
    print(f"Exported {len(shopify_df)} relevant products to {csv_file}")

    # Also save the original scraped data
    original_csv_file = f'aliexpress_{product_category.replace(" ", "_")}_original.csv'
    df.to_csv(original_csv_file, index=False)
    print(f"Exported original data for {len(df)} products to {original_csv_file}")