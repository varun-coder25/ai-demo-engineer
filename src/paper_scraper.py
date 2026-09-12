import aiohttp
import xml.etree.ElementTree as ET


ARXIV_API_URL = "https://export.arxiv.org/api/query"

NAMESPACE = {
    "atom": "http://www.w3.org/2005/Atom"
}


async def fetch_papers_by_ids(arxiv_ids, batch_size=50):
    all_xml = []

    for i in range(0, len(arxiv_ids), batch_size):
        batch = arxiv_ids[i:i + batch_size]

        search_query = " OR ".join(
            f"id:{arxiv_id}" for arxiv_id in batch
        )

        params = {
            "search_query": search_query,
            "start": 0,
            "max_results": len(batch),
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                ARXIV_API_URL,
                params=params
            ) as response:
                response.raise_for_status()
                xml_data = await response.text()
                all_xml.append(xml_data)

    return all_xml


def parse_papers(xml_data):
    root = ET.fromstring(xml_data)

    papers = []

    for entry in root.findall("atom:entry", NAMESPACE):
        title = entry.find("atom:title", NAMESPACE)
        published = entry.find("atom:published", NAMESPACE)
        paper_id = entry.find("atom:id", NAMESPACE)

        if title is None or published is None or paper_id is None:
            continue

        authors = []

        for author in entry.findall("atom:author", NAMESPACE):
            name = author.find("atom:name", NAMESPACE)

            if name is not None:
                authors.append(name.text.strip())

        url = paper_id.text.strip()
        arxiv_id = url.rstrip("/").split("/")[-1]

        if "v" in arxiv_id:
            arxiv_id = arxiv_id.rsplit("v", 1)[0]

        papers.append({
            "arxiv_id": arxiv_id,
            "title": " ".join(title.text.split()),
            "authors": authors,
            "paper_url": url,
            "published_date": published.text.strip(),
        })

    return papers