import requests
from bs4 import BeautifulSoup
import re

def fetch_soup(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'lxml')
    except requests.exceptions.RequestException:
        return None

def extract_title_text(soup):
    return soup.select_one('div.tit .txt06') if soup else None

def extract_nav_board_ids(soup):
    nav_links = soup.select('.tit.txtLeft') if soup else []
    board_ids = []
    if len(nav_links) == 2 and nav_links[1].get('href') != "javascript:void(void)":
        for link in nav_links:
            href = link['href']
            board_id_match = re.search(r"view\('(\d+)',", href)
            if board_id_match:
                board_ids.append(board_id_match.group(1))
        board_ids.sort()
        next_board_id = board_ids[-1] if board_ids else None
        return next_board_id
    return None

def extract_image_url(soup):
    content_area = soup.select_one('.row.contents.clearfix') if soup else None
    if content_area:
        image_tag = content_area.find('img')
        if image_tag and image_tag.get('src'):
            return image_tag['src']
    return None
