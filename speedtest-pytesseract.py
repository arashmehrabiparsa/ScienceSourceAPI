import cv2
import numpy as np
import pytesseract
from PIL import Image
import re

def preprocess_image(image_path):
    # Read the image
    img = cv2.imread(image_path)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding to preprocess the image
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    
    # Apply dilation to connect text components
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    gray = cv2.dilate(gray, kernel, iterations=1)
    
    return gray

def extract_text(preprocessed_image):
    # Perform OCR on the preprocessed image
    text = pytesseract.image_to_string(Image.fromarray(preprocessed_image))
    return text

def extract_speed_data(text):
    # Extract download and upload speeds
    download_speed = re.search(r'DOWNLOAD\s*([\d.]+)\s*Mbps', text, re.IGNORECASE)
    upload_speed = re.search(r'UPLOAD\s*([\d.]+)\s*Mbps', text, re.IGNORECASE)
    
    return {
        'download': float(download_speed.group(1)) if download_speed else None,
        'upload': float(upload_speed.group(1)) if upload_speed else None
    }

def extract_ping_data(text):
    # Extract ping, jitter, and loss
    ping = re.search(r'PING\s*(\d+)\s*ms', text, re.IGNORECASE)
    jitter = re.search(r'JITTER\s*(\d+)\s*ms', text, re.IGNORECASE)
    loss = re.search(r'LOSS\s*([\d.]+)%', text, re.IGNORECASE)
    
    return {
        'ping': int(ping.group(1)) if ping else None,
        'jitter': int(jitter.group(1)) if jitter else None,
        'loss': float(loss.group(1)) if loss else None
    }

def extract_server_info(text):
    # Extract server name and location
    server_info = re.search(r'([A-Za-z\s]+),\s*([A-Za-z\s]+)', text)
    
    return {
        'server_name': server_info.group(1).strip() if server_info else None,
        'server_location': server_info.group(2).strip() if server_info else None
    }

def extract_data_usage(text):
    # Extract data used
    data_used = re.search(r'Data Used\s*([\d.]+)\s*([MG]B)', text, re.IGNORECASE)
    
    if data_used:
        amount = float(data_used.group(1))
        unit = data_used.group(2).upper()
        return amount * (1 if unit == 'MB' else 1024)  # Convert to MB
    return None

def process_speedtest_image(image_path):
    preprocessed = preprocess_image(image_path)
    text = extract_text(preprocessed)
    
    speed_data = extract_speed_data(text)
    ping_data = extract_ping_data(text)
    server_info = extract_server_info(text)
    data_usage = extract_data_usage(text)
    
    result = {
        **speed_data,
        **ping_data,
        **server_info,
        'data_usage_mb': data_usage
    }
    
    return result

# Example usage
image_path = 'path_to_your_speedtest_image.png'
result = process_speedtest_image(image_path)
print(result)