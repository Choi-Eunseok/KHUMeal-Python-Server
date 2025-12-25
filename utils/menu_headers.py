from utils.words import collect_text_in_cell

from utils.utils import CORNER_KEYWORDS, parse_korean_date

def build_side_headers(vxs, item_horizontal_lines, content_blocks, current_left, parent, boundary_x):
    if boundary_x <= current_left:
        return
    
    next_left = next((x for x in vxs if x > current_left), None)
    lines_for_current_col = [h for h in item_horizontal_lines if h[1] <= current_left and parent['y_start'] <= h[0] <= parent['y_end']]
    for i in range(len(lines_for_current_col) - 1):
        y_start = lines_for_current_col[i][0]
        y_end   = lines_for_current_col[i + 1][0]
        x_start = current_left
        x_end   = next_left

        texts = collect_text_in_cell(content_blocks, x_start, x_end, y_start, y_end)
        if texts:
            text = texts[0]
            keyword = next((k for k in CORNER_KEYWORDS if k in text), '')
        else:
            keyword = ''
        
        item = {
            'x_start': int(x_start),
            'x_end': int(x_end),
            'y_start': int(y_start),
            'y_end': int(y_end),
            'text': keyword,
        }

        if 'children' not in parent:
            parent['children'] = []
        parent['children'].append(item)

        build_side_headers(vxs, item_horizontal_lines, content_blocks, next_left, item, boundary_x)

def get_side_headers(parent, prefix=''):
    text = ''
    if parent.get('text') and parent['text']:
        text = parent['text'].replace('\"', '').replace('\'', '')
    if prefix and text:
        text = prefix + ' ' + text
    elif prefix:
        text = prefix
    
    if 'children' not in parent or not parent['children']:
        return [{
            'text': text,
            'x_start': parent['x_start'],
            'x_end': parent['x_end'],
            'y_start': parent['y_start'],
            'y_end': parent['y_end'],
        }]
    
    result = []
    for child in parent['children']:
        result.extend(
            get_side_headers(child, text)
        )
    return result

def build_menu_headers(final_horizontal_lines, final_vertical_lines, header_y2, content_blocks):
    menu = {
        'headers': [],
        'side_headers': []
    }

    side_headers = {
        'text': '',
        'children': [],
        'y_start': 0,
        'y_end': final_horizontal_lines[-1][0]
    }

    first_horizontal_line = final_horizontal_lines[0][0]
    second_horizontal_line = final_horizontal_lines[1][0]

    header_vertical_lines = [v for v in final_vertical_lines if v[1] < header_y2]
    header_vertical_lines.sort(key=lambda v: v[0])

    for i in range(len(header_vertical_lines) - 1):
        x_start = header_vertical_lines[i][0]
        x_end   = header_vertical_lines[i + 1][0]
        y_start = first_horizontal_line
        y_end   = second_horizontal_line

        texts = collect_text_in_cell(content_blocks, x_start, x_end, y_start, y_end)
        text = ''
        if texts:
            text = texts[0]
        
        date = parse_korean_date(text)
        if not date:
            text = ''
        else:
            text = str(date)

        cell = {
            'x_start': int(x_start),
            'x_end': int(x_end),
            'y_start': int(y_start),
            'y_end': int(y_end),
            'text': text
        }
        menu['headers'].append(cell)

    item_horizontal_lines = final_horizontal_lines[1:]

    vxs = sorted([v[0] for v in final_vertical_lines])
    build_side_headers(vxs, item_horizontal_lines, content_blocks, vxs[0], side_headers, header_vertical_lines[1][0])

    menu['side_headers'] = get_side_headers(side_headers)

    return menu