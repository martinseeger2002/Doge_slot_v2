import os
import qrcode
from PIL import Image

def generate_qr_without_text(slot_address, file_path=None):
    if not slot_address:
        print("Error: slot_address is None or empty.")
        return  # Optionally, handle this situation more gracefully

    # Define the directory and filename based on slot_address
    base_dir = 'C:/Doge_slot_2/static/images/slot_qr_codes'
    file_name = f'{slot_address}.png'
    file_path = os.path.join(base_dir, file_name)
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Generate QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,
        border=1,
    )
    qr.add_data(slot_address)
    qr.make(fit=True)

    # Create and save QR code image
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img = qr_img.convert("RGB")
    qr_img.save(file_path)
