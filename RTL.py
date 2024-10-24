import cv2
import pytesseract
from pytesseract import Output
import os
import re

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

image_folder_path = r'C:\Users\Kingstone\Desktop\All folder\project work\IDRBT_Cheque_Image_Dataset\IDRBT Cheque Image Dataset\300\input_folder'  # Update this with your local directory path


def extract_account_number(text):
    match = re.search(r'\b\d{9,18}\b', text)
    return match.group(0) if match else None


def extract_amount(text):
    match = re.search(r'₹\s*([0-9,]+)', text)
    if match:
        return match.group(1).replace(',', '')
    return None


def validate_fields(name, account_number, amount):

    if not name or len(name.split()) < 2:
        print("Invalid Name")
    else:
        print("Valid Name")


    if not account_number or not account_number.isdigit() or not (9 <= len(account_number) <= 18):
        print("Invalid Account Number")
    else:
        print("Valid Account Number")


    try:
        amount_value = int(amount)
        if amount_value <= 0:
            print("Invalid Amount")
        else:
            print("Valid Amount")
    except (ValueError, TypeError):
        print("Invalid Amount")

    if not name or len(name.split()) < 2 and not account_number or not account_number.isdigit() or not (9 <= len(account_number) <= 18) and amount_value <= 0:
        print (" ### Invalid data ! ###")
    else : 
        print("### Valid data ! ### ") 

    

for file_name in os.listdir(image_folder_path):
    image_path = os.path.join(image_folder_path, file_name)
    if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.bmp')):
        print(f"Processing image: {file_name}")
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Image {file_name} not found or unable to load.")
            continue
        processed_image = image
        custom_config = r'--oem 3 --psm 6'
        ocr_data = pytesseract.image_to_data(processed_image, output_type=Output.DICT, config=custom_config)
        raw_text = pytesseract.image_to_string(processed_image, config=custom_config)
        print("Raw OCR Output:")
        print(raw_text)
    
        name = None
        account_number = None
        amount = None
        for i, text in enumerate(ocr_data['text']):
            text = text.strip()

            if 'Pay' in text and not name:
                for j in range(i + 1, len(ocr_data['text'])):
                    potential_name = ocr_data['text'][j].strip()
                    if potential_name:  # Check if it's non-empty
                        name = potential_name
                        break

            if ('A/c No.' in text or 'Acc No.' in text) and not account_number:
                for j in range(i, len(ocr_data['text'])):
                    if 'A/c No.' in ocr_data['text'][j] or 'Acc No.' in ocr_data['text'][j]:
                        potential_account = ocr_data['text'][j].strip()
                        account_number = extract_account_number(potential_account)
                        break


            if ('₹' in text or 'Rupees' in text) and not amount:
                amount = extract_amount(text)


        print("Name:", name)
        print("Account Number:", account_number)
        print("Amount:", amount)
        validate_fields(name, account_number, amount)


