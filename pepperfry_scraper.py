import requests
from bs4 import BeautifulSoup as soup
import json
import os
from urllib.parse import urljoin

headers = {'User-Agent': 'Mozilla/5.0'}

items = [
    # just give the items you want your crawler to crawl over
    "arm chairs",
    "bean bags",
    "bench",
    "book cases",
    "chest drawers",
    "coffee table",
    "dining set",
    "garder seating",
    "king beds",
    "queen beds",
    "two seater sofa",
]


def create_url(query):
    prefix_url = "https://www.pepperfry.com/site_product/search?q="
    suffix_url = "&as=0&src=os"
    query = str(query).strip().replace(" ", "+")
    url = prefix_url + query + suffix_url
    return url


def start_requests(items):
    start_urls = [create_url(item) for item in items]

    for i, url in enumerate(start_urls):
        response = requests.get(url, headers=headers)
        parse(response, items[i])


def parse(response, item):
    directory = item
    try:
        os.mkdir(directory)
    except:
        pass

    response_bytes = response.content
    response_soup = soup(response_bytes, "html.parser")

    div_list = response_soup.findAll("div", {"class": "clip-dtl-ttl row"})

    for i, div in enumerate(div_list):
        if i > 20:
            break
        attrs_dict = div.a.attrs
        next_url = attrs_dict["href"]

        next_response = requests.get(next_url, headers=headers)
        parse_next_page(next_response, item)


def parse_next_page(response, item):
    response_bytes = response.content
    response_soup = soup(response_bytes, "html.parser")
    title = ""
    overview = ""
    price = 0
    details_dict = {}

    title = response_soup.findAll("h1", {"class": "v-pro-ttl pf-medium-bold-text"})[0].text

    overview_div = response_soup.findAll("div", {"class": "v-more-info-tab-cont-para-wrap"})[0]
    overview_p_list = overview_div.findAll("p")
    overview = ""
    for para in overview_p_list:
        overview = overview + "\n" + para.text

    price_div = response_soup.findAll("div", {"class": "v-offer-price-wrap pf-margin-bottom5 vipPrice"})[0]
    price_span_list = price_div.findAll("span", {"class": "v-offer-price-amt pf-medium-bold-text"})
    if len(price_span_list) > 0:
        price = price_span_list[0].text
    else:
        price = price_div.findAll("span", {"class": "v-price-mrp-amt-only"})[0].text
        price = price.replace("₹", "").replace(" ", "").replace("MRP", "").replace("\n", "")

    details_div = response_soup.findAll("div", {"class": "v-prod-comp-dtls-list"})[0]
    details_subdiv_list = details_div.findAll("div")
    for detail_subdiv in details_subdiv_list:
        spans_list = detail_subdiv.findAll("span")
        if len(spans_list) > 1:
            details_dict[spans_list[0].text] = spans_list[1].text

    metadata = {
        "Item Title": title,
        "Item Price": price,
        "Overview": overview,
        "Product specifications": details_dict
    }

    directory = item + "\\" + title
    try:
        os.mkdir(directory)
    except:
        pass

    filename = directory + "\\metadata.json"
    with open(filename, "w") as json_file:
        json.dump(metadata, json_file)

    image_div = response_soup.findAll("div", {"class": "vipImage__thumb-wrapper"})[0]
    li_list = image_div.findAll("li")
    for i, list_item in enumerate(li_list):
        image_url = list_item.img.attrs["src"]
        image_abs_url = urljoin(response.url, image_url)
        image_response = requests.get(image_abs_url, headers=headers)
        image_filename = directory + "\\image-" + str(i) + ".jpg"
        with open(image_filename, "wb") as image_file:
            image_file.write(image_response.content)

    print(title)
    print(overview)
    print(price)
    print(details_dict)


start_requests(items)