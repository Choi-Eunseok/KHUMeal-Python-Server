import json
import cv2
import numpy as np
import requests
from dotenv import load_dotenv
import os

from utils.utils import to_py_type
from utils.clova import extract_text_with_clova_ocr
from utils.lines import correct_horizontal_lines, detect_header_area_and_valid_vertical_lines, detect_horizontal_lines, detect_valid_horizontal_lines, detect_vertical_lines
from utils.words import detect_content_blocks, group_words_into_blocks, sort_words_in_reading_order
from utils.menu_headers import build_menu_headers
from utils.menu_items import build_menu_items, merge_blank_corner_after

load_dotenv()

IS_DEV_MODE = os.environ.get('IS_DEV_MODE') == 'True'
CLOVA_API_URL = os.environ.get('CLOVA_API_URL')
CLOVA_SECRET_KEY = os.environ.get('CLOVA_SECRET_KEY')

def parse_menu_to_structured_data(image_url = None):
    image_ndarray = np.asarray(bytearray(requests.get(image_url).content), dtype=np.uint8)
    image = cv2.imdecode(image_ndarray, cv2.IMREAD_COLOR)
    image_path = image_url.split("/")[-1]

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    
    horizontal_lines = detect_horizontal_lines(image, edges)
    vertical_lines = detect_vertical_lines(image, edges)

    words = extract_text_with_clova_ocr(image, CLOVA_API_URL, CLOVA_SECRET_KEY, image_path)
    if not words:
        return {'headers': [], 'items': []}
    sorted_words = sort_words_in_reading_order(words)
    all_blocks = group_words_into_blocks(sorted_words)

    horizontal_lines = correct_horizontal_lines(horizontal_lines, vertical_lines, image.shape[0])
    final_vertical_lines, header_vertical_lines, header_y1, header_y2 = detect_header_area_and_valid_vertical_lines(image, horizontal_lines, vertical_lines, words)
    final_horizontal_lines, not_valid_horizontal_lines, highlight_boxes = detect_valid_horizontal_lines(all_blocks, horizontal_lines, header_vertical_lines, header_y1, image.shape[0])

    content_blocks = detect_content_blocks(all_blocks, not_valid_horizontal_lines)
    
    menu_headers = build_menu_headers(final_horizontal_lines, final_vertical_lines, header_y2, content_blocks)
    menu = to_py_type(build_menu_items(menu_headers, content_blocks, image))
    menu = merge_blank_corner_after(menu)

    if IS_DEV_MODE:
        output_file_name="final"
        json_output_path = output_file_name + '.jpg'
        output_image = image.copy()
        for y in not_valid_horizontal_lines:
            cv2.rectangle(output_image, (y[2], y[0]), (image.shape[1], y[1]), (255, 255, 255), -1)
        for box in highlight_boxes:
            x1, y1, x2, y2 = box
            cv2.rectangle(output_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        for y in final_horizontal_lines:
            cv2.line(output_image, (y[1], y[0]), (image.shape[1], y[0]), (0, 0, 255), 2)
        for x in final_vertical_lines:
            cv2.line(output_image, (x[0], x[1]), (x[0], image.shape[0]), (0, 0, 255), 2)
        cv2.imwrite(json_output_path, output_image)
        print(f"선 검출 완료, 결과가 '{json_output_path}' 파일로 저장되었습니다.")
        
        json_output_path = output_file_name + '.json'
        with open(json_output_path, 'w', encoding='utf-8') as f:
            json.dump(menu, f, ensure_ascii=False, indent=2)
        print(f"메뉴 구조가 '{json_output_path}' 파일로 저장되었습니다.")

    return menu
    
# if __name__ == '__main__':
#     # image_url = 'https://www.khu.ac.kr/upload/cross/images/000044/1215.png'
#     image_url = 'https://www.khu.ac.kr/upload/cross/images/000044/20251213085502245_5QRF7ND8.png'
#     # image_url = 'https://www.khu.ac.kr/upload/cross/images/000044/20251222093855803_ONM3ZQ7S.png'
#     # image_url = 'https://www.khu.ac.kr/upload/cross/images/000044/1222.png'
#     all_menu_data = parse_menu_to_structured_data(image_url=image_url)

#     print(json.dumps(all_menu_data, ensure_ascii=False, indent=4))