import cv2
import numpy as np
import os
import csv
import re
import tensorflow as tf

# Specify the directory containing the images
IMAGE_DIR = r"C:\Users\Guest2\Personal\Github\speed test CV"

# List of specific image filenames to process
IMAGE_FILES = [
    # ... (list of image filenames)
]

# Load pre-trained models (replace with your chosen models)
object_detection_model = tf.keras.models.load_model("object_detection_model.h5")
ocr_model = tf.keras.models.load_model("ocr_model.h5")
ner_model = tf.keras.models.load_model("ner_model.h5")

def preprocess_image(image_path):
    image = cv2.imread(image_path)
    image = cv2.resize(image, (224, 224))  # Adjust size as needed
    image = image / 255.0
    return image

def detect_text_regions(image):
    # Use object detection model to detect text regions
    # ... (replace with your object detection model code)
    text_regions = object_detection_model.predict(image)
    return text_regions

def extract_text(image, text_regions):
    # Extract text from detected regions using OCR
    # ... (replace with your OCR model code)
    text = ocr_model.predict(image)
    return text

def process_text(text):
    # Tokenize the text
    tokens = tokenize(text)

    # Apply NER to identify entities
    entities = ner_model.predict(tokens)

    # Extract relevant data using regular expressions or other methods
    # ... (implement your data extraction logic)
    speed_data = extract_speed_data(entities)
    ping_data = extract_ping_data(entities)
    server_info = extract_server_info(entities)
    data_usage = extract_data_usage(entities)

    return speed_data, ping_data, server_info, data_usage

def process_speedtest_image(image_path):
    image = preprocess_image(image_path)
    text_regions = detect_text_regions(image)
    text = extract_text(image, text_regions)
    speed_data, ping_data, server_info, data_usage = process_text(text)

    result = {
        'filename': os.path.basename(image_path),
        **speed_data,
        **ping_data,
        **server_info,
        'data_usage_mb': data_usage,
        'AdditionalServers': 'Unknown',
        'ISP': 'Unknown'
    }

    return result

# ... (rest of the original code)

# Specify the directory containing the images
IMAGE_DIR = r"C:\Users\Guest2\Personal\Github\speed test CV"

# List of specific image filenames to process
IMAGE_FILES = [
    "---001---Screenshot 2024-08-24 194305.png",
    "---21---Screenshot 2024-08-24 194305.png",
    "---31---Screenshot 2024-08-24 194332.png",
    "-0x80070750-audiostreamsignalnotfound-Screenshot 2024-08-24 193306.png",
    "-11-Screenshot 2024-08-24 194224.png",
    "1-Screenshot 2024-08-24 193306.png",
    "10-Screenshot 2024-08-24 193306.png",
    "11-Screenshot 2024-08-24 193306.png",
    "12-Screenshot 2024-08-24 193306.png",
    "13-Screenshot 2024-08-24 193306.png",
    "14-Screenshot 2024-08-24 193306.png",
    "15-Screenshot 2024-08-24 193306.png",
    "16-Screenshot 2024-08-24 193306.png",
    "18-Screenshot 2024-08-24 193306.png",
    "18-Screenshot 2024-08-24 194001.png",
    "2-Screenshot 2024-08-24 193306.png",
    "27-Screenshot 2024-08-24 193306.png",
    "3-Screenshot 2024-08-24 193306.png",
    "4-Screenshot 2024-08-24 193306.png",
    "5-Screenshot 2024-08-24 193306.png",
    "52-Screenshot 2024-08-24 194159.png",
    "6-Screenshot 2024-08-24 193306.png",
    "69-Screenshot 2024-08-24 194001.png",
    "7-Screenshot 2024-08-24 193306.png",
    "70-Screenshot 2024-08-24 194053.png",
    "8-Screenshot 2024-08-24 193306.png",
    "81-Screenshot 2024-08-24 194133.png",
    "9-Screenshot 2024-08-24 193306.png"
]

def extract_text_from_image(image, lower_color, upper_color):
    # Create a mask for the specified color range
    mask = cv2.inRange(image, lower_color, upper_color)
    
    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Sort contours by area (largest first)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    
    # Extract text from the largest contour
    if contours:
        x, y, w, h = cv2.boundingRect(contours[0])
        roi = image[y:y+h, x:x+w]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        return binary
    return None

def extract_speed_data(image):
    # Define color ranges for download and upload speeds (adjust as needed)
    download_color = np.array([0, 200, 0])  # Green
    upload_color = np.array([0, 0, 200])  # Red
    
    download_text = extract_text_from_image(image, download_color - 30, download_color + 30)
    upload_text = extract_text_from_image(image, upload_color - 30, upload_color + 30)
    
    # Here you would use OCR to convert the binary images to text
    # For now, we'll return placeholder values
    return {'download': 100.0, 'upload': 50.0}

def extract_ping_data(image):
    # Define color range for ping data (adjust as needed)
    ping_color = np.array([200, 200, 0])  # Yellow
    
    ping_text = extract_text_from_image(image, ping_color - 30, ping_color + 30)
    
    # Here you would use OCR to convert the binary image to text
    # For now, we'll return placeholder values
    return {'ping': 20, 'jitter': 5, 'loss': 0.1}

def extract_server_info(image):
    # This would require more advanced text detection and OCR
    # For now, we'll return placeholder values
    return {'server_name': 'Unknown', 'server_location': 'Unknown'}

def extract_data_usage(image):
    # This would require more advanced text detection and OCR
    # For now, we'll return a placeholder value
    return 100.0

def process_speedtest_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise Exception(f"Failed to load image: {image_path}")
    
    speed_data = extract_speed_data(image)
    ping_data = extract_ping_data(image)
    server_info = extract_server_info(image)
    data_usage = extract_data_usage(image)
    
    result = {
        'filename': os.path.basename(image_path),
        **speed_data,
        **ping_data,
        **server_info,
        'data_usage_mb': data_usage,
        'AdditionalServers': 'Unknown',
        'ISP': 'Unknown'
    }
    
    return result

def process_specific_images(directory, image_files):
    results = []
    for filename in image_files:
        image_path = os.path.join(directory, filename)
        if os.path.exists(image_path):
            try:
                result = process_speedtest_image(image_path)
                results.append(result)
                print(f"Processed {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
        else:
            print(f"File not found: {filename}")
    return results

def save_to_csv(results, output_file):
    if not results:
        print("No results to save.")
        return
    
    keys = results[0].keys()
    with open(output_file, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(results)
    print(f"Results saved to {output_file}")

def merge_with_original_csv(original_csv, new_results, output_file):
    # Read the original CSV
    with open(original_csv, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        original_data = list(reader)

    # Create a dictionary of new results keyed by filename
    new_results_dict = {result['filename']: result for result in new_results}

    # Update the original data with new results
    for row in original_data:
        filename = f"{row['Id']}.png"  # Assuming the Id corresponds to the filename
        if filename in new_results_dict:
            new_data = new_results_dict[filename]
            row.update({
                'Jitter': new_data['jitter'],
                'Loss': new_data['loss'],
                'DataUsedDown': new_data['data_usage_mb'],
                'DataUsedUp': new_data['data_usage_mb'],
                'AdditionalServers': new_data['AdditionalServers'],
                'ISP': new_data['ISP']
            })

    # Write the updated data to a new CSV file
    keys = original_data[0].keys()
    with open(output_file, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(original_data)
    print(f"Updated results saved to {output_file}")

# Main execution
if __name__ == "__main__":
    results = process_specific_images(IMAGE_DIR, IMAGE_FILES)
    output_file = os.path.join(IMAGE_DIR, "speedtest_results_new.csv")
    save_to_csv(results, output_file)
    print(f"Processed {len(results)} images.")

    # Merge with original CSV
    original_csv = os.path.join(IMAGE_DIR, "My Speedtest Results.csv")
    merged_output = os.path.join(IMAGE_DIR, "speedtest_results_merged.csv")
    merge_with_original_csv(original_csv, results, merged_output)
