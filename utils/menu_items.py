import base64
import cv2

from utils.words import collect_text_in_cell

def build_menu_items(menu_headers, content_blocks, image):
    menu = []
    for side_header in menu_headers['side_headers']:
        empty_count = 0
        for j, header in enumerate(menu_headers['headers']):
            if not header["text"]:
                continue

            menu_items = collect_text_in_cell(content_blocks, header['x_start'], header['x_end'], side_header['y_start'], side_header['y_end'])
            if len(menu_items) == 0:
                empty_count += 1
            
            x1, x2 = int(header['x_start']), int(header['x_end'])
            y1, y2 = int(side_header['y_start']), int(side_header['y_end'])
            crop = image[y1:y2, x1:x2]
            _, buf = cv2.imencode('.jpg', crop)
            
            menu_item = {
                'corner_info': side_header['text'],
                'day_info': header['text'],
                'menu_items': menu_items,
                'image': base64.b64encode(buf).decode('utf-8')
            }
            menu.append(menu_item)
        
        if empty_count == len(menu_headers['headers']) - 1:
            for _ in range(len(menu_headers['headers']) - 1):
                menu.pop()
    
    return menu