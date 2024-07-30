import csv
import random
from datetime import datetime

def generate_product(prompt):
    # Simulating AI-generated product data
    adjectives = ["Premium", "Deluxe", "Eco-friendly", "Innovative", "Sleek"]
    categories = ["Electronics", "Home & Garden", "Fashion", "Sports & Outdoors", "Beauty"]
    
    title = f"{random.choice(adjectives)} {prompt}"
    body_html = f"<p>High-quality {prompt.lower()} for all your needs.</p>"
    vendor = f"{random.choice(['TechCo', 'EcoGoods', 'FashionHub', 'SportsPro', 'BeautyEssentials'])}"
    product_type = random.choice(categories)
    tags = f"{prompt.lower()}, {product_type.lower()}, {vendor.lower()}"
    
    return {
        "Handle": title.lower().replace(" ", "-"),
        "Title": title,
        "Body (HTML)": body_html,
        "Vendor": vendor,
        "Product Category": product_type,
        "Type": product_type,
        "Tags": tags,
        "Published": "TRUE",
        "Option1 Name": "Size",
        "Option1 Value": random.choice(["Small", "Medium", "Large"]),
        "Option2 Name": "Color",
        "Option2 Value": random.choice(["Red", "Blue", "Green", "Black", "White"]),
        "Option3 Name": "",
        "Option3 Value": "",
        "Variant SKU": f"{random.randint(1000, 9999)}-{random.randint(100, 999)}",
        "Variant Grams": str(random.randint(100, 1000)),
        "Variant Inventory Tracker": "shopify",
        "Variant Inventory Qty": str(random.randint(0, 100)),
        "Variant Inventory Policy": "deny",
        "Variant Fulfillment Service": "manual",
        "Variant Price": f"{random.randint(10, 200)}.{random.randint(0, 99):02d}",
        "Variant Compare At Price": "",
        "Variant Requires Shipping": "TRUE",
        "Variant Taxable": "TRUE",
        "Variant Barcode": f"{random.randint(100000000000, 999999999999)}",
        "Image Src": f"https://example.com/images/{title.lower().replace(' ', '-')}.jpg",
        "Image Position": "1",
        "Image Alt Text": title,
        "Gift Card": "FALSE",
        "SEO Title": title,
        "SEO Description": f"Buy our {title.lower()} - perfect for any {product_type.lower()} enthusiast!",
        "Google Shopping / Google Product Category": "",
        "Google Shopping / Gender": "",
        "Google Shopping / Age Group": "",
        "Google Shopping / MPN": "",
        "Google Shopping / AdWords Grouping": "",
        "Google Shopping / AdWords Labels": "",
        "Google Shopping / Condition": "",
        "Google Shopping / Custom Product": "",
        "Google Shopping / Custom Label 0": "",
        "Google Shopping / Custom Label 1": "",
        "Google Shopping / Custom Label 2": "",
        "Google Shopping / Custom Label 3": "",
        "Google Shopping / Custom Label 4": "",
        "Variant Image": "",
        "Variant Weight Unit": "g",
        "Variant Tax Code": "",
        "Cost per item": f"{random.randint(5, 100)}.{random.randint(0, 99):02d}",
        "Price / International": "",
        "Compare At Price / International": "",
        "Status": "active"
    }

def create_shopify_csv(prompt, num_products):
    products = [generate_product(prompt) for _ in range(num_products)]
    
    filename = f"shopify_products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = products[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for product in products:
            writer.writerow(product)
    
    print(f"CSV file '{filename}' has been created with {num_products} products.")

# Example usage
prompt = input("Enter a product prompt: ")
create_shopify_csv(prompt, 10)