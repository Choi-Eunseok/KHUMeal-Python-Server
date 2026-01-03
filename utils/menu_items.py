import cv2
import numpy as np

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
            image_bytes = buf.tobytes()
            
            menu_item = {
                'corner_info': side_header['text'],
                'day_info': header['text'],
                'menu_items': menu_items,
                'image': image_bytes
            }
            menu.append(menu_item)
        
        if empty_count == len(menu_headers['headers']) - 1:
            for _ in range(len(menu_headers['headers']) - 1):
                menu.pop()
    
    return menu

def _decode_jpg_bytes(b: bytes):
    if not b:
        return None
    arr = np.frombuffer(b, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    return img

def _encode_jpg(img):
    ok, buf = cv2.imencode(".jpg", img)
    return buf.tobytes() if ok else None

def merge_blank_corner_after(menu):
    pending = {}
    out = []
    last_index_by_day = {}

    for m in menu:
        day = (m.get("day_info") or "").strip()
        corner = (m.get("corner_info") or "").strip()
        items = m.get("menu_items") or []
        img_bytes = m.get("image")

        if corner == "":
            p = pending.setdefault(day, {"items": [], "images": []})
            if items:
                p["items"].extend(items)
            if img_bytes:
                p["images"].append(img_bytes)
            continue

        if day in pending:
            p = pending.pop(day)

            if p["items"]:
                m["menu_items"] = p["items"] + items

            if p["images"]:
                imgs = [i for i in (_decode_jpg_bytes(b) for b in p["images"]) if i is not None]
                cur = _decode_jpg_bytes(img_bytes) if img_bytes else None

                if cur is not None:
                    imgs.append(cur)

                if imgs:
                    widths = [im.shape[1] for im in imgs]
                    w = min(widths)
                    norm = [im[:, :w] if im.shape[1] != w else im for im in imgs]

                    merged = cv2.vconcat(norm)
                    m["image"] = _encode_jpg(merged)

        out.append(m)
        last_index_by_day[day] = len(out) - 1

    for day, p in pending.items():
        if day not in last_index_by_day:
            continue

        idx = last_index_by_day[day]
        tgt = out[idx]

        if p["items"]:
            tgt["menu_items"] = (tgt.get("menu_items") or []) + p["items"]
        
        if p["images"]:
            imgs = [i for i in (_decode_jpg_bytes(b) for b in p["images"]) if i is not None]
            cur = _decode_jpg_bytes(tgt.get("image")) if tgt.get("image") else None
            if cur is not None:
                imgs.append(cur)

            if imgs:
                widths = [im.shape[1] for im in imgs]
                w = min(widths)
                norm = [im[:, :w] if im.shape[1] != w else im for im in imgs]
                merged = cv2.vconcat(norm)
                tgt["image"] = _encode_jpg(merged)

    return out