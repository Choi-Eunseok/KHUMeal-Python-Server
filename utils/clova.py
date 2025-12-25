import os
import cv2
import requests
import json
import time
import uuid

def save_raw_response(response_json, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(response_json, f, ensure_ascii=False, indent=2)

def parse_clova_response(response_json):
    words_data = []

    for image in response_json.get('images', []):
        for field in image.get('fields', []):
            text = field.get('inferText')
            vertices = field.get('boundingPoly', {}).get('vertices', [])
            if not text or not vertices:
                continue
            
            x_coords = [v['x'] for v in vertices]
            y_coords = [v['y'] for v in vertices]
            
            bbox = (int(min(x_coords)), int(min(y_coords)), 
                    int(max(x_coords)), int(max(y_coords)))
            words_data.append({'text': text, 'bbox': bbox})
            
    return words_data

def extract_text_with_clova_ocr_from_json(json_path):
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            response_json = json.load(f)
        return parse_clova_response(response_json)

def request_clova_ocr_api(api_url, secret_key, image_bytes):
    files = [('file', ('menu.png', image_bytes, 'image/png'))]
    request_json = {
        'message': { 'images': [{'format': 'jpg', 'name': 'menu'}],
                     'requestId': str(uuid.uuid4()), 'version': 'V2',
                     'timestamp': int(round(time.time() * 1000)) }
    }
    payload = {'message': json.dumps(request_json['message']).encode('UTF-8')}
    headers = {'X-OCR-SECRET': secret_key}
    
    response = requests.post(api_url, headers=headers, data=payload, files=files)
    response.raise_for_status()
    
    return response.json()

def extract_text_with_clova_ocr(image, api_url, secret_key, image_path):
    json_path = 'clova_response_cache/' + image_path.rsplit('.', 1)[0] + '_response.json'
    if os.path.exists(json_path):
        return extract_text_with_clova_ocr_from_json(json_path)

    is_success, encoded_image = cv2.imencode(".png", image)
    if not is_success:
        raise Exception("이미지를 PNG 형식으로 인코딩하는 데 실패했습니다.")
    
    response = request_clova_ocr_api(api_url, secret_key, encoded_image.tobytes())
    save_raw_response(response, json_path)

    return parse_clova_response(response)