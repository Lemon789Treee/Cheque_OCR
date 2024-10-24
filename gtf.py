import cv2
import pytesseract
import os
from pytesseract import Output

# Set up paths for Tesseract and input/output directories
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update this path for Tesseract if needed
input_dir = 'IDRBT_Cheque_Image_Dataset\IDRBT Cheque Image Dataset\300\input_folder'  # Directory containing cheque images

# Lists to store the names of the complete and incomplete images
complete_list = []
incomplete_list = []

# Function to process each cheque image and determine field completeness
def process_cheque(image_path):
    global name, account_number, amount, date

    # Load the cheque image
    img = cv2.imread(image_path)

    # Use pytesseract to extract data from the image
    data = pytesseract.image_to_data(img, output_type=Output.DICT)

    # Print the detected text for debugging
    print(f"Detected text for {image_path}:")
    print(pytesseract.image_to_string(img))

    # Initialize variables for the fields
    name = ""
    account_number = ""
    amount = ""
    date = ""

    # Function to extract relevant fields using bounding boxes (heuristics)
    def extract_fields(data):
        global name, account_number, amount, date
        for i, text in enumerate(data['text']):
            # Extract account number (look for a long sequence of digits)
            if text.isdigit() and len(text) >= 10:
                account_number = text
            # Extract amount (look for typical currency patterns)
            if '₹' in text or ',' in text:
                amount = text
            # Extract date (look for typical date format patterns)
            if len(text) == 10 and text[2] == text[5] == '/':
                date = text
            # Extract name (heuristic for handwritten text above "Pay")
            if i > 0 and data['text'][i-1].lower() == "pay":
                name = text

    # Call the function to extract fields
    extract_fields(data)

    # Check if all fields are filled
    if name and account_number and amount and date:
        complete_list.append(os.path.basename(image_path))
    else:
        incomplete_list.append(os.path.basename(image_path))

# Function to process all images in the directory
def process_directory(input_dir):
    # Loop through all files in the input directory
    for file_name in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file_name)
        # Ensure we're working with images (e.g., PNG, JPG)
        if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            process_cheque(file_path)

    # Print the lists of complete and incomplete images directly in the terminal
    print("\nComplete Cheques:")
    for complete in complete_list:
        print(complete)
    
    print("\nIncomplete Cheques:")
    for incomplete in incomplete_list:
        print(incomplete)

# Run the processing for the input directory
process_directory(input_dir)
