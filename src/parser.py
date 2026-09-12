from bs4 import BeautifulSoup


def extract_text(html):
    soup = BeautifulSoup(html, "html.parser")

    for element in soup(["script", "style", "noscript"]):
        element.decompose()

    text = soup.get_text(separator=" ", strip=True)

    return text