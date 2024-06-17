import requests
from bs4 import BeautifulSoup

if __name__ == "__main__":
    url = "https://docs.python.org/3/library/index.html"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        div = soup.find("div", class_="toctree-wrapper compound")

        if div:
            links = div.find_all("a", class_="reference internal", href=True)[:10]

            with open("links.txt", "w", encoding="utf-8") as file:
                for link in links:
                    link_url = "https://docs.python.org/3/library/" + link['href']
                    file.write(link_url + "\n")
                    print(f"Saved link: {link_url}")
        else:
            print("Failed to find the required div in the page.")
    else:
        print(f"Got {response.status_code} when trying to access {url}")
