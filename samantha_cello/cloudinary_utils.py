# cloudinary_utils.py
import os
import cloudinary
from cloudinary.utils import cloudinary_url

def init_cloudinary():
    """Initialize Cloudinary with environment variables"""
    cloudinary.config(
        cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
        api_key=os.environ.get('CLOUDINARY_API_KEY'),
        api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
        secure=True
    )

def get_cloudinary_url(filename):
    """Generate a Cloudinary URL for the given filename."""
    url, _ = cloudinary_url(filename)
    return url