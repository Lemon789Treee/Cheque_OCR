import os
import numpy as np
from paddleocr import PaddleOCR
from PIL import Image, ImageFile
import logging
from tqdm import tqdm

input_folder_path = r'C:\Users\Kingstone\Desktop\All folder\project work\IDRBT_Cheque_Image_Dataset\IDRBT Cheque Image Dataset\\300\input_folder'
output_folder = r'C:\Users\Kingstone\Desktop\All folder\project work\IDRBT_Cheque_Image_Dataset\IDRBT Cheque Image Dataset\\300\output_folder'
output_file = os.path.join(output_folder, 'ocr_results_test_paddle_full.txt')
verified_output_file = os.path.join(output_folder, 'verified_ocr_results.txt')  # File for images with name, account number, and amount

os.makedirs(output_folder, exist_ok=True)

ImageFile.LOAD_TRUNCATED_IMAGES = True

# Initialize PaddleOCR with the desired language (English in this case)
ocr = PaddleOCR(lang='en')

error_log_file = 'ocr_errors.log'
logging.basicConfig(filename=error_log_file, level=logging.ERROR)

# Prepare output files
with open(output_file, 'w') as f:
    f.write("Merged OCR Results:\n\n")

with open(verified_output_file, 'w') as vf:
    vf.write("Verified OCR Results (Name, Account Number, Amount):\n\n")

# Get list of image files in the input folder
image_files = [f for f in os.listdir(input_folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.bmp', '.gif'))]

# Define keywords to look for in the OCR result
name_keywords = ['name' , 'pay ']
account_keywords = ['account', 'acc no', 'account number' , 'Alc.No.' , 'AC.No.' , "A/c.No." ]
amount_keywords = ['amount', 'amt' , 'Rupees']

with tqdm(total=len(image_files), desc="Processing Images", unit="image") as pbar:
    for image_file in image_files:
        image_path = os.path.join(input_folder_path, image_file)
        combined_text = f"--- Results for {image_file} ---\n"

        try:
            # Open the image
            image = Image.open(image_path)

            # Perform OCR using PaddleOCR
            result = ocr.ocr(image_path)

            # Extract the text from the OCR result
            paddleocr_text = "\n".join([line[1][0] for line in result[0]])
            combined_text += "\n" + paddleocr_text + "\n"

            print(f"OCR output for {image_file}:\n{paddleocr_text}")  # Debugging: Print OCR result for each image

            # Check if the text contains the required fields
            contains_name = any(keyword in paddleocr_text.lower() for keyword in name_keywords)
            contains_account = any(keyword in paddleocr_text.lower() for keyword in account_keywords)
            contains_amount = any(keyword in paddleocr_text.lower() for keyword in amount_keywords)

            print(f"Contains name: {contains_name}, account: {contains_account}, amount: {contains_amount}")  # Debugging: Check keyword matches

        except Exception as e:
            logging.error(f"Error processing PaddleOCR for {image_file}: {e}")
            paddleocr_text = ""

        # Write the results to the main output file
        if paddleocr_text.strip():
            with open(output_file, 'a') as f:
                f.write(combined_text + "\n\n")

        # Write to the verified file if name, account number, and amount are found
        if contains_name and contains_account and contains_amount:
            with open(verified_output_file, 'a') as vf:
                vf.write(combined_text + "\n\n")

        # Dispose of the image from memory
        image.close()

        pbar.update(1)

print(f"OCR results have been saved to {output_file}.")
print(f"Verified OCR results have been saved to {verified_output_file}.")
print(f"Any errors have been logged to {error_log_file}.")