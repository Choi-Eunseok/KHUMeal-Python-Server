import cv2

from utils.words import collect_text_in_cell

def build_menu_items(menu_headers, content_blocks, image):
    menu = []
    headers = menu_headers['headers']
    side_headers = menu_headers['side_headers']

    valid_header_indices = [j for j, h in enumerate(headers) if h.get("text")]
    header_count = len(valid_header_indices)

    pending_items_by_day = {j: [] for j in valid_header_indices}
    pending_crops_by_day = {j: [] for j in valid_header_indices}

    def encode_jpg(img_arr):
        ok, buf = cv2.imencode('.jpg', img_arr)
        return buf.tobytes() if ok else None

    for side_header in side_headers:
        appended_for_side = 0
        empty_count = 0

        corner_text = (side_header.get("text") or "").strip()
        
        for j in valid_header_indices:
            header = headers[j]
            day_text = header["text"]

            menu_items = collect_text_in_cell(content_blocks, header['x_start'], header['x_end'], side_header['y_start'], side_header['y_end'])
            if len(menu_items) == 0:
                empty_count += 1
            
            x1, x2 = int(header['x_start']), int(header['x_end'])
            y1, y2 = int(side_header['y_start']), int(side_header['y_end'])
            crop = image[y1:y2, x1:x2]

            if corner_text == "":
                if menu_items:
                    pending_items_by_day[j].extend(menu_items)
                pending_crops_by_day[j].append(crop)
                continue
            
            if pending_items_by_day[j]:
                menu_items = pending_items_by_day[j] + menu_items
                pending_items_by_day[j] = []
            
            if pending_crops_by_day[j]:
                crops = pending_crops_by_day[j] + [crop]
                pending_crops_by_day[j] = []
                merged_crop = cv2.vconcat(crops)
            else:
                merged_crop = crop
            
            image_bytes = encode_jpg(merged_crop)

            menu.append({
                'corner_info': side_header['text'],
                'day_info': day_text,
                'menu_items': menu_items,
                'image': image_bytes
            })
            appended_for_side += 1
        
        if header_count > 0 and empty_count == header_count:
            for _ in range(appended_for_side):
                menu.pop()
    
    if menu:
        last_by_day = {}
        for idx, m in enumerate(menu):
            last_by_day[m['day_info']] = idx

        for j in valid_header_indices:
            if not pending_items_by_day[j] and not pending_crops_by_day[j]:
                continue

            day_text = headers[j]["text"]
            if day_text not in last_by_day:
                continue
            
            tgt_idx = last_by_day[day_text]
            target = menu[tgt_idx]

            if pending_items_by_day[j]:
                target['menu_items'] = target['menu_items'] + pending_items_by_day[j]
            
            if pending_crops_by_day[j]:
                import numpy as np
                target_img = cv2.imdecode(np.frombuffer(target['image'], dtype=np.uint8), cv2.IMREAD_COLOR)
                merged_crop = cv2.vconcat(pending_crops_by_day[j] + [target_img])
                target['image'] = encode_jpg(merged_crop)

            pending_items_by_day[j] = []
            pending_crops_by_day[j] = []

    return menu