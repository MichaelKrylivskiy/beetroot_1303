import aiohttp
import asyncio
from aiofiles import open as aioopen
from bs4 import BeautifulSoup


async def fetch_page(session, url):
    async with session.get(url) as response:
        if response.status == 200:
            return await response.text()
        else:
            print(f"Got {response.status} when trying to access {url}")
            return None


async def parse_page(content):
    soup = BeautifulSoup(content, "html.parser")
    div = soup.find("div", class_="toctree-wrapper compound")
    if div:
        links = div.find_all("a", class_="reference internal", href=True)[:10]
        return ["https://docs.python.org/3/library/" + link['href'] for link in links]
    else:
        print("Failed to find the required div in the page.")
        return []


async def save_links(links, file_path):
    async with aioopen(file_path, "w", encoding="utf-8") as file:
        for link in links:
            await file.write(link + "\n")
            print(f"Saved link: {link}")


async def main():
    url = "https://docs.python.org/3/library/index.html"
    async with aiohttp.ClientSession() as session:
        page_content = await fetch_page(session, url)
        if page_content:
            links = await parse_page(page_content)
            await save_links(links, "links.txt")


if __name__ == "__main__":
    asyncio.run(main())
