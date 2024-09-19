import cloudinary.uploader
from fastapi import UploadFile

async def upload_image_to_cloudinary(file: UploadFile):
    try:
        result = cloudinary.uploader.upload(file.file, folder="avatars/")
        return result
    except Exception as e:
        print(f"Cloudinary upload error: {e}")
        return None
