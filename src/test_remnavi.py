import requests
import xml.etree.ElementTree as ET

url = "https://remnavi.com/feed.php?q=ai&posted_within=1"

response = requests.get(url, timeout=20)

print("HTTP status:", response.status_code)

root = ET.fromstring(response.text)

items = root.findall(".//item")

print("Jobs received:", len(items))

for item in items[:5]:
    print()
    print("Title:", item.findtext("title"))
    print("Date:", item.findtext("pubDate"))
    print("URL:", item.findtext("link"))