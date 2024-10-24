import os
import cv2
import pytesseract
from pytesseract import Output
import re
import logging
from tqdm import tqdm
from PIL import Image, ImageFile
from paddleocr import PaddleOCR

# Set the path to the Tesseract executable if needed
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Initialize PaddleOCR
ocr = PaddleOCR(lang='en')

# Input and output directories
input_folder = r'C:\Users\Kingstone\Desktop\All folder\project work\IDRBT_Cheque_Image_Dataset\IDRBT Cheque Image Dataset\300\input_folder'  # Update with your image folder path
output_folder = r'IDRBT_Cheque_Image_Dataset/IDRBT Cheque Image Dataset/300/output_folder copy'
os.makedirs(output_folder, exist_ok=True)

# Error log file
error_log_file = os.path.join(output_folder, 'ocr_errors.log')
logging.basicConfig(filename=error_log_file, level=logging.ERROR)

# Output file
output_file = os.path.join(output_folder, 'ocr_results.txt')

# Prepare output file
with open(output_file, 'w') as f:
    f.write("Merged OCR Results:\n\n")

# Helper function to extract account number
def extract_account_number(text):
    match = re.search(r'\b\d{9,18}\b', text)
    return match.group(0) if match else None

# Helper function to extract amount
def extract_amount(text):
    match = re.search(r'₹\s*([0-9,]+)', text)
    if match:
        return match.group(1).replace(',', '')
    return None

# Function to validate extracted fields
def validate_fields(name, account_number, amount):
    # Simple name validation: not empty and at least two words
    if not name or len(name.split()) < 2:
        print("Invalid Name")
    else:
        print("Valid Name")
    
    # Validate account number (length between 9 and 18 digits)
    if not account_number or not account_number.isdigit() or not (9 <= len(account_number) <= 18):
        print("Invalid Account Number")
    else:
        print("Valid Account Number")
    
    # Validate amount (should be a positive number)
    try:
        amount_value = int(amount)
        if amount_value <= 0:
            print("Invalid Amount")
        else:
            print("Valid Amount")
    except (ValueError, TypeError):
        print("Invalid Amount")

# Process all images in the input folder
with tqdm(total=len(os.listdir(input_folder)), desc="Processing Images", unit="image") as pbar:
    for file_name in os.listdir(input_folder):
        image_path = os.path.join(input_folder, file_name)

        # Check if it's an image file
        if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.bmp')):
            print(f"Processing image: {file_name}")
            try:
                image = Image.open(image_path)
            except Exception as e:
                logging.error(f"Error opening image {file_name}: {e}")
                pbar.update(1)
                continue

            combined_text = f"--- Results for {file_name} ---\n"

            try:
                # Use PaddleOCR
                result = ocr.ocr(image_path)

                # Extract the text from PaddleOCR result
                paddleocr_text = "\n".join([line[1][0] for line in result[0]])

                # Combine with Tesseract OCR if needed (this is optional, just PaddleOCR is used here)
                gray_image = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2GRAY)
                custom_config = r'--oem 3 --psm 6'
                ocr_data = pytesseract.image_to_data(gray_image, output_type=Output.DICT, config=custom_config)

                # Initialize fields
                name = None
                account_number = None
                amount = None

                # Iterate over OCR data to search for specific fields
                for i, text in enumerate(ocr_data['text']):
                    text = text.strip()

                    # Search for the name field (heuristically searching after "Pay")
                    if 'Pay' in text and not name:
                        for j in range(i + 1, len(ocr_data['text'])):
                            potential_name = ocr_data['text'][j].strip()
                            if potential_name:
                                name = potential_name
                                break

                    # Search for account number field
                    if ('A/c No.' in text or 'Acc No.' in text) and not account_number:
                        account_number = extract_account_number(text)

                    # Search for the amount field
                    if '₹' in text or 'Rupees' in text and not amount:
                        amount = extract_amount(text)

                # Output extracted fields
                combined_text += f"Name: {name}\nAccount Number: {account_number}\nAmount: {amount}\n"

                # Validate fields
                validate_fields(name, account_number, amount)

                # Write combined result to file
                with open(output_file, 'a') as f:
                    f.write(combined_text + "\n\n")

            except Exception as e:
                logging.error(f"Error processing OCR for {file_name}: {e}")

            # Dispose of the image
            image.close()

            pbar.update(1)

print(f"OCR results have been saved to {output_file}.")
print(f"Any errors have been logged to {error_log_file}.")
