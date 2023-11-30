import cv2
import os

def process_image(file_path, cleaned_path , mask_path):
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    print(f"Processing: {file_path}")
    image = cv2.imread(file_path)
    if image is None:
        print(f"Failed to load the image {file_path}")
        return
    result = cv2.inpaint(image, mask, 3, cv2.INPAINT_TELEA)
    os.makedirs(os.path.dirname(cleaned_path), exist_ok=True)
    cv2.imwrite(cleaned_path, result)
    print(f"Processed to: {file_path}")
