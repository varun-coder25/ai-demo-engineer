import requests

url = "https://www.arbeitnow.com/api/job-board-api"

response = requests.get(url, timeout=20)

print("HTTP status:", response.status_code)

data = response.json()

print("Keys:", data.keys())
print("Jobs received:", len(data["data"]))

for job in data["data"][:5]:
    print()
    print("Title:", job.get("title"))
    print("Company:", job.get("company_name"))
    print("Created:", job.get("created_at"))
    print("Remote:", job.get("remote"))
    print("URL:", job.get("url"))