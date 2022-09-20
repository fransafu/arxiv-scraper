import requests
from bs4 import BeautifulSoup
import json

def get_website_content(url):
    response = requests.get(url)

    if response.status_code != 200:
        return None

    return response.content

def get_categories(content):
    soup = BeautifulSoup(content, "html.parser")
    content_section = soup.find(id = "content")

    # Remove columns section
    for elem in content_section.find_all("div", { 'class': 'columns' }): 
        elem.decompose()

    titles = content_section.find_all("h2")
    categories = content_section.find_all("ul")

    # Remove section "About arXiv" (last element)
    # TODO: assert is "About arXiv" the last section
    titles.pop()
    categories.pop()

    categories_content = []

    index = 0
    for category in categories:
        category_content = {}
        category_content["category"] = titles[index].text
        category_content["sub_categories"] = []

        for sub_category in category.find_all("li"):
            sub_category_content = {}
            # TODO: we have more information under "sub_category.text"
            # print(sub_category.text)

            links_sub_category = sub_category.find_all("a")

            sub_category_content["sub_category"] = links_sub_category[0].text

            sub_category_content["main_prefix"] = get_attr_labelledby(links_sub_category[0])
            sub_category_content["prefix"] = get_attr_labelledby(links_sub_category[0]).replace("main-", "")
            sub_category_content["sub_category_includes"] = []

            for link_sub_category in links_sub_category:
                if sub_category_content["main_prefix"] == get_attr_labelledby(link_sub_category):
                    sub_category_content["sub_category_main"] = extract_link_metadata(link_sub_category)
                elif "new-" in get_attr_labelledby(link_sub_category):
                    sub_category_content["sub_category_new"] = extract_link_metadata(link_sub_category)
                elif "recent-" in get_attr_labelledby(link_sub_category):
                    sub_category_content["sub_category_recent"] = extract_link_metadata(link_sub_category)
                elif "search-" in get_attr_labelledby(link_sub_category):
                    sub_category_content["sub_category_search"] = extract_link_metadata(link_sub_category)
                else:
                    sub_category_content["sub_category_includes"].append(extract_link_metadata(link_sub_category))

            category_content["sub_categories"].append(sub_category_content)

        index += 1

        categories_content.append(category_content)

    return categories_content

def extract_link_metadata(link):
    return {
        "name": link.text,
        "id": link["id"],
        "link": link["href"] if "arxiv.org" in link["href"] else f'https://arxiv.org/{link["href"]}',
        "labelledby": get_attr_labelledby(link)
    }

def get_attr_labelledby(elem):
    try:
        return elem["aria-labelledby"]
    except:
        return None

def main():
    BASE_URL = "https://arxiv.org/"

    content = get_website_content(BASE_URL)
    categories = get_categories(content)

    with open("categories.json", "w") as f:
        json.dump(categories, f)

if __name__ == "__main__":
    main()
