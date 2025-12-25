import json

from utils.utils import parse_date_range_flexible
from utils.crawl import fetch_soup, extract_title_text, extract_nav_board_ids, extract_image_url

def find_recent_menu(base_url, board_id, keyword):
    recent_menu = {}
    current_board_id = board_id
    prev_board_id = board_id
    while True:
        target_url = base_url + str(current_board_id)
        soup = fetch_soup(target_url)
        if not soup:
            return {}

        title_text = extract_title_text(soup)
        if not title_text:
            return {}

        start_date, end_date = parse_date_range_flexible(title_text.text)
        if not start_date or not end_date:
            break

        next_board_id = extract_nav_board_ids(soup)
        is_latest_post = (next_board_id is None)

        image_url = extract_image_url(soup)

        if keyword in title_text.text:
            recent_menu = {
                "base_date": str(start_date),
                "board_id": current_board_id,
                "image_url": image_url,
                "prev_board_id": prev_board_id
            }
        
        if is_latest_post:
            break
        else:
            prev_board_id = current_board_id
            current_board_id = next_board_id
    return recent_menu

# if __name__ == '__main__':
#     base_url = "https://www.khu.ac.kr/kor/user/bbs/BMSR00040/view.do?menuNo=200283&catId=136&boardId="
#     board_id = "320538"
#     # keyword = "청운관"
#     keyword = "푸른솔"

#     # base_url = "https://www.khu.ac.kr/kor/user/bbs/BMSR00040/view.do?menuNo=200283&catId=137&boardId="
#     # board_id = "320474"
#     # keyword = "2기숙사"
#     # keyword = "학생회관"
    
#     recent_menu = find_recent_menu(base_url=base_url, board_id=board_id, keyword=keyword)
#     print(json.dumps(recent_menu, ensure_ascii=False, indent=4))