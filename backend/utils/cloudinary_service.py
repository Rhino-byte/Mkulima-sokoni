"""
Cloudinary service for image uploads
"""
import cloudinary
import cloudinary.uploader
import cloudinary.api
from config import Config
import logging

logger = logging.getLogger(__name__)

# Initialize Cloudinary
try:
    cloudinary.config(
        cloud_name=Config.CLOUDINARY_CLOUD_NAME,
        api_key=Config.CLOUDINARY_API_KEY,
        api_secret=Config.CLOUDINARY_API_SECRET
    )
    logger.info("Cloudinary configured successfully")
except Exception as e:
    logger.warning(f"Cloudinary configuration error: {str(e)}")
    logger.warning("Image uploads will not work until Cloudinary is properly configured")


def upload_image(file, folder='mkulima-bora', resource_type='image'):
    """
    Upload an image to Cloudinary
    
    Args:
        file: File object or file path
        folder: Cloudinary folder path (default: 'mkulima-bora')
        resource_type: Resource type (default: 'image')
    
    Returns:
        dict: Upload result with 'url', 'public_id', 'secure_url', etc.
        None: If upload fails
    """
    try:
        if not Config.CLOUDINARY_CLOUD_NAME or not Config.CLOUDINARY_API_KEY:
            logger.error("Cloudinary credentials not configured")
            return None
        
        # Upload options
        upload_options = {
            'folder': folder,
            'resource_type': resource_type,
            'overwrite': False,
            'invalidate': True,
        }
        
        # Upload the file
        result = cloudinary.uploader.upload(
            file,
            **upload_options
        )
        
        logger.info(f"Image uploaded successfully: {result.get('public_id')}")
        return {
            'url': result.get('url'),
            'secure_url': result.get('secure_url'),
            'public_id': result.get('public_id'),
            'format': result.get('format'),
            'width': result.get('width'),
            'height': result.get('height'),
            'bytes': result.get('bytes'),
            'created_at': result.get('created_at')
        }
        
    except Exception as e:
        logger.error(f"Error uploading image to Cloudinary: {str(e)}")
        return None


def upload_image_from_url(image_url, folder='mkulima-bora'):
    """
    Upload an image from a URL to Cloudinary
    
    Args:
        image_url: URL of the image to upload
        folder: Cloudinary folder path (default: 'mkulima-bora')
    
    Returns:
        dict: Upload result with 'url', 'public_id', 'secure_url', etc.
        None: If upload fails
    """
    try:
        if not Config.CLOUDINARY_CLOUD_NAME or not Config.CLOUDINARY_API_KEY:
            logger.error("Cloudinary credentials not configured")
            return None
        
        upload_options = {
            'folder': folder,
            'overwrite': False,
            'invalidate': True,
        }
        
        result = cloudinary.uploader.upload(
            image_url,
            **upload_options
        )
        
        logger.info(f"Image uploaded from URL successfully: {result.get('public_id')}")
        return {
            'url': result.get('url'),
            'secure_url': result.get('secure_url'),
            'public_id': result.get('public_id'),
            'format': result.get('format'),
            'width': result.get('width'),
            'height': result.get('height'),
            'bytes': result.get('bytes'),
            'created_at': result.get('created_at')
        }
        
    except Exception as e:
        logger.error(f"Error uploading image from URL to Cloudinary: {str(e)}")
        return None


def delete_image(public_id):
    """
    Delete an image from Cloudinary
    
    Args:
        public_id: Public ID of the image to delete
    
    Returns:
        bool: True if deletion successful, False otherwise
    """
    try:
        if not Config.CLOUDINARY_CLOUD_NAME or not Config.CLOUDINARY_API_KEY:
            logger.error("Cloudinary credentials not configured")
            return False
        
        result = cloudinary.uploader.destroy(public_id)
        
        if result.get('result') == 'ok':
            logger.info(f"Image deleted successfully: {public_id}")
            return True
        else:
            logger.warning(f"Image deletion failed: {public_id}")
            return False
            
    except Exception as e:
        logger.error(f"Error deleting image from Cloudinary: {str(e)}")
        return False


def upload_base64_image(base64_string, folder='mkulima-bora', resource_type='image'):
    """
    Upload a base64 encoded image to Cloudinary
    
    Args:
        base64_string: Base64 encoded image string (with or without data URI prefix)
        folder: Cloudinary folder path (default: 'mkulima-bora')
        resource_type: Resource type (default: 'image')
    
    Returns:
        dict: Upload result with 'url', 'public_id', 'secure_url', etc.
        None: If upload fails
    """
    try:
        import base64 as base64_module
        from io import BytesIO
        
        if not Config.CLOUDINARY_CLOUD_NAME or not Config.CLOUDINARY_API_KEY:
            logger.error("Cloudinary credentials not configured")
            return None
        
        # Remove data URI prefix if present (e.g., "data:image/jpeg;base64,")
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # Decode base64 string to bytes
        try:
            image_bytes = base64_module.b64decode(base64_string)
        except Exception as e:
            logger.error(f"Error decoding base64 string: {str(e)}")
            return None
        
        # Create a BytesIO object from the decoded bytes
        image_file = BytesIO(image_bytes)
        
        # Upload options
        upload_options = {
            'folder': folder,
            'resource_type': resource_type,
            'overwrite': False,
            'invalidate': True,
        }
        
        # Upload the file-like object
        result = cloudinary.uploader.upload(
            image_file,
            **upload_options
        )
        
        logger.info(f"Base64 image uploaded successfully: {result.get('public_id')}")
        return {
            'url': result.get('url'),
            'secure_url': result.get('secure_url'),
            'public_id': result.get('public_id'),
            'format': result.get('format'),
            'width': result.get('width'),
            'height': result.get('height'),
            'bytes': result.get('bytes'),
            'created_at': result.get('created_at')
        }
        
    except Exception as e:
        logger.error(f"Error uploading base64 image to Cloudinary: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None


def get_image_url(public_id, transformation=None):
    """
    Get Cloudinary URL for an image with optional transformations
    
    Args:
        public_id: Public ID of the image
        transformation: Optional transformation parameters
    
    Returns:
        str: Image URL
    """
    try:
        if transformation:
            url = cloudinary.CloudinaryImage(public_id).build_url(transformation=transformation)
        else:
            url = cloudinary.CloudinaryImage(public_id).build_url()
        return url
    except Exception as e:
        logger.error(f"Error generating image URL: {str(e)}")
        return None

