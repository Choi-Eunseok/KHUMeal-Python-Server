import cv2
import numpy as np

from utils.utils import DAYS

def detect_horizontal_lines(image, edges):
    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 180,
        threshold=100,
        minLineLength=image.shape[1] // 8,
        maxLineGap=0
    )

    points = cv2.HoughLinesP(
        edges, 
        rho=1,
        theta=np.pi / 180,
        threshold=100,
        minLineLength=2,
        maxLineGap=0
    )

    y_points = []
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.arctan2(y2 - y1, x2 - x1) * 180.0 / np.pi
            if abs(angle) < 2:
                y_points.append((y1, x1))

    x_points = []
    if points is not None:
        for line in points:
            x1, y1, x2, y2 = line[0]
            angle = np.arctan2(y2 - y1, x2 - x1) * 180.0 / np.pi
            if abs(angle) < 2:
                x_points.append((y1, x1))
    
    if not y_points: return []
    y_points.sort(key=lambda p: (p[0], p[1]))
    x_points.sort(key=lambda p: (p[0], p[1]))
    
    merged_y_points = [y_points[0]] 
    
    for y in y_points[1:]:
        if y[0] - merged_y_points[-1][0] > 5:
            merged_y_points.append(y)
    
    for lines in range(len(merged_y_points)):
        points_x = [p for p in x_points if abs(p[0] - merged_y_points[lines][0]) <= 5]
        if points_x:
            min_x = min(p[1] for p in points_x)
            merged_y_points[lines] = (merged_y_points[lines][0], min_x)

    return merged_y_points

def detect_vertical_lines(image, edges):
    x_points = []
    
    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 180,
        threshold=50,
        minLineLength=200,
        maxLineGap=10
    )

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.arctan2(y2 - y1, x2 - x1) * 180.0 / np.pi
            if 85 < abs(angle) < 95:
                x_points.append(x1)

    if not x_points: return []
    x_points.sort()
    merged_x = [x_points[0]]
    for x in x_points[1:]:
        if x - merged_x[-1] > 5:
            merged_x.append(x)
    return merged_x

def correct_horizontal_lines(horizontal_lines, vertical_lines, y_max):
    for i in range(len(horizontal_lines)):
        left_vertical_line = max((x for x in vertical_lines if x <= horizontal_lines[i][1]), default=0)
        horizontal_lines[i] = (horizontal_lines[i][0], left_vertical_line)
    horizontal_lines.append((y_max, 0))
    horizontal_lines.sort(key=lambda l: l[0])
    return horizontal_lines

def detect_header_area_and_valid_vertical_lines(image, horizontal_lines, vertical_lines, words):
    if image.shape[1] - vertical_lines[-1] < 10:
        vertical_lines.pop()
    
    header_y1 = 0
    header_y2 = 0
    valid_vertical_lines = set()
    valid_vertical_lines.add(horizontal_lines[1][1])
    
    for word in words:
        if any(day in word["text"] for day in DAYS):
            x_min, _, x_max, _ = word["bbox"]
            word_center_x = (x_min + x_max) / 2
            left_line, right_line = 0, image.shape[1]
            for v_line_x in vertical_lines:
                if v_line_x < word_center_x:
                    left_line = max(left_line, v_line_x)
                else:
                    right_line = min(right_line, v_line_x)
            valid_vertical_lines.add(left_line)
            valid_vertical_lines.add(right_line)
            
            for y in horizontal_lines:
                if y[0] >= (word["bbox"][3] + word["bbox"][1]) // 2:
                    if y[0] > header_y2:
                        header_y2 = y[0]
                    break
                header_y1 = y[0]
        if len(valid_vertical_lines) == 7:
            break
    
    not_valid_vertical_lines = sorted(list(set(vertical_lines) - valid_vertical_lines))
    header_vertical_lines = [(x, 0) for x in list(valid_vertical_lines)]
    final_vertical_lines = header_vertical_lines + [(x, header_y2) for x in not_valid_vertical_lines if horizontal_lines[1][1] < x]
    final_vertical_lines.sort(key=lambda l: l[0])
    
    return final_vertical_lines, header_vertical_lines, header_y1, header_y2

# 세로선을 관통하는 텍스트가 있는 행을 찾아 제외
def detect_valid_horizontal_lines(all_blocks, horizontal_lines, header_vertical_lines, header_y1, y_max):
    horizontal_areas = []
    for index in range(len(horizontal_lines) - 1):
        horizontal_areas.append((horizontal_lines[index][0], horizontal_lines[index + 1][0], horizontal_lines[index][1], False))
    
    highlight_boxes = []
    for block in all_blocks:
        x1, y1, x2, y2 = block['bbox']
        is_intersected = False
        height = y2 - y1
        for v_line_x in header_vertical_lines:
            if x1 < v_line_x[0] - height // 3 and v_line_x[0] + height // 3 < x2:
                is_intersected = True
                highlight_boxes.append(block['bbox'])
                break
        if is_intersected:
            for i, (y_start, y_end, x_start, _) in enumerate(horizontal_areas):
                if y_start <= (y1 + y2) // 2 <= y_end:
                    horizontal_areas[i] = (y_start, y_end, x_start, True)
                    break
    
    valid_horizontal_lines = set()
    not_valid_horizontal_lines = set()
    for zone_y_start, zone_y_end, x_start, is_excluded_zone in horizontal_areas:
        if not is_excluded_zone and header_y1 <= zone_y_start:
            valid_horizontal_lines.add(zone_y_start)
            valid_horizontal_lines.add(zone_y_end)
        else:
            not_valid_horizontal_lines.add((zone_y_start, zone_y_end, x_start))
    valid_horizontal_lines.add(y_max)
    final_horizontal_lines = [line for line in horizontal_lines if line[0] in valid_horizontal_lines]
    
    return final_horizontal_lines, not_valid_horizontal_lines, highlight_boxes