import requests
import xml.etree.ElementTree as ET
import re

feed_url = 'https://www.winnipegfreepress.com/rss/'
try:
    response = requests.get(feed_url, timeout=15)
    root = ET.fromstring(response.content)

    item = root.find('.//item')
    if item is not None:
        print('=== First article details ===')
        title = item.findtext('title', '').strip()
        print(f'Title: {title}')

        description = item.findtext('description', '')
        print(f'Description length: {len(description)}')

        # Check for img tags in description
        if '<img' in description:
            print('Found image tags in description')
            # Simple regex for img src
            img_pattern = r'<img[^>]+src=["\']([^"\']+)["\']'
            matches = re.findall(img_pattern, description)
            if matches:
                print(f'Image URLs found: {len(matches)}')
                for url in matches[:2]:  # Show first 2
                    print(f'  {url}')

        # Show first 300 chars of description
        print(f'Description preview: {description[:300]}...')

except Exception as e:
    print(f'Error: {e}')