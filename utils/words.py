def sort_words_in_reading_order(words_data, y_tolerance=5):
    if not words_data:
        return []

    words_data.sort(key=lambda w: w['bbox'][1])
    
    lines = []
    current_line = [words_data[0]]

    for word in words_data[1:]:
        if word['text'] == "|":
            continue

        last_word_in_line = current_line[-1]
        last_word_y_center = (last_word_in_line['bbox'][1] + last_word_in_line['bbox'][3]) / 2
        current_word_y_center = (word['bbox'][1] + word['bbox'][3]) / 2

        if abs(last_word_y_center - current_word_y_center) < y_tolerance:
            current_line.append(word)
        else:
            lines.append(current_line)
            current_line = [word]
    
    lines.append(current_line)

    for line in lines:
        line.sort(key=lambda w: w['bbox'][0])

    sorted_words = [word for line in lines for word in line]
    
    return sorted_words

def group_words_into_blocks(words_data, y_tolerance=5, x_tolerance=0):
    if not words_data:
        return []

    blocks = []
    current_block = [words_data[0]]

    for word in words_data[1:]:
        last_word_in_block = current_block[-1]
        
        last_word_y_center = (last_word_in_block['bbox'][1] + last_word_in_block['bbox'][3]) / 2
        current_word_y_center = (word['bbox'][1] + word['bbox'][3]) / 2
        is_on_same_line = abs(last_word_y_center - current_word_y_center) < y_tolerance

        horizontal_gap = word['bbox'][0] - last_word_in_block['bbox'][2]
        is_horizontally_close = horizontal_gap < (word['bbox'][3] - word['bbox'][1]) // 3 + x_tolerance

        if is_on_same_line and is_horizontally_close:
            current_block.append(word)
        else:
            x_start = min(w['bbox'][0] for w in current_block)
            y_start = min(w['bbox'][1] for w in current_block)
            x_end = max(w['bbox'][2] for w in current_block)
            y_end = max(w['bbox'][3] for w in current_block)
            full_text = " ".join([w['text'] for w in current_block])
            blocks.append({'text': full_text, 'bbox': (x_start, y_start, x_end, y_end)})
            
            current_block = [word]
    
    if current_block:
        x_start = min(w['bbox'][0] for w in current_block)
        y_start = min(w['bbox'][1] for w in current_block)
        x_end = max(w['bbox'][2] for w in current_block)
        y_end = max(w['bbox'][3] for w in current_block)
        full_text = " ".join([w['text'] for w in current_block])
        blocks.append({'text': full_text, 'bbox': (x_start, y_start, x_end, y_end)})
    
    return blocks

def collect_text_in_cell(content_blocks, x_start, x_end, y_start, y_end):
    texts = []
    for block in content_blocks:
        x1, y1, x2, y2 = block['bbox']
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        if x_start <= cx <= x_end and y_start <= cy <= y_end:
            texts.append(block['text'])
    return texts

def detect_content_blocks(all_blocks, not_valid_horizontal_lines):
    content_blocks = []
    
    for block in all_blocks:
        x1, y1, x2, y2 = block['bbox']
        y_center = (y1 + y2) // 2
        is_in_excluded_zone = False
        for zone_y_start, zone_y_end, x_start in not_valid_horizontal_lines:
            if zone_y_start <= y_center <= zone_y_end:
                is_in_excluded_zone = True
                break
        if is_in_excluded_zone:
            continue
        content_blocks.append(block)
    
    return content_blocks