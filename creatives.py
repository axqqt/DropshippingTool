import requests
import json
import os

def search_tiktok_videos(product_name, max_results=20):
    # Note: You would need to replace this with actual API credentials and endpoints
    api_url = "https://api.tiktok.com/v1/search/video"
    headers = {
        "Authorization": "Bearer YOUR_ACCESS_TOKEN"
    }
    params = {
        "keyword": product_name,
        "count": max_results
    }

    response = requests.get(api_url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()['data']
    else:
        print(f"Error: {response.status_code}")
        return []

def display_results(videos):
    for i, video in enumerate(videos, 1):
        print(f"{i}. {video['title']} - {video['video_url']}")

def export_urls_to_file(videos, filename):
    with open(filename, 'w') as f:
        for video in videos:
            f.write(f"{video['video_url']}\n")
    print(f"URLs exported to {filename}")

def main():
    product_name = input("Enter a product name: ")
    videos = search_tiktok_videos(product_name)
    
    if videos:
        display_results(videos)
        export_urls_to_file(videos, f"{product_name}_tiktok_urls.txt")
    else:
        print("No videos found.")

if __name__ == "__main__":
    main()