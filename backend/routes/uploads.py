"""
Image upload routes for Phase 3
"""
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from utils.cloudinary_service import upload_image, upload_image_from_url
from auth.firebase_auth import verify_firebase_token
import logging
import os

logger = logging.getLogger(__name__)

uploads_bp = Blueprint('uploads', __name__, url_prefix='/api/uploads')

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@uploads_bp.route('/image', methods=['POST'])
def upload_image_file():
    """
    Upload an image file to Cloudinary
    Expects: multipart/form-data with 'image' file field
    Optional: 'folder' field to specify Cloudinary folder
    """
    try:
        # Check if file is present
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'error': 'Invalid file type',
                'allowed_types': list(ALLOWED_EXTENSIONS)
            }), 400
        
        # Get folder from request or use default
        folder = request.form.get('folder', 'mkulima-bora')
        
        # Upload to Cloudinary
        result = upload_image(file, folder=folder)
        
        if not result:
            return jsonify({'error': 'Failed to upload image to Cloudinary'}), 500
        
        return jsonify({
            'success': True,
            'image': {
                'url': result['url'],
                'secure_url': result['secure_url'],
                'public_id': result['public_id'],
                'format': result['format'],
                'width': result.get('width'),
                'height': result.get('height'),
                'bytes': result.get('bytes')
            },
            'message': 'Image uploaded successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error uploading image: {str(e)}")
        return jsonify({'error': str(e)}), 500


@uploads_bp.route('/image/url', methods=['POST'])
def upload_image_from_url_endpoint():
    """
    Upload an image from URL to Cloudinary
    Expects: { "image_url": "...", "folder": "..." (optional) }
    """
    try:
        data = request.get_json()
        image_url = data.get('image_url')
        
        if not image_url:
            return jsonify({'error': 'image_url is required'}), 400
        
        # Get folder from request or use default
        folder = data.get('folder', 'mkulima-bora')
        
        # Upload to Cloudinary
        result = upload_image_from_url(image_url, folder=folder)
        
        if not result:
            return jsonify({'error': 'Failed to upload image from URL to Cloudinary'}), 500
        
        return jsonify({
            'success': True,
            'image': {
                'url': result['url'],
                'secure_url': result['secure_url'],
                'public_id': result['public_id'],
                'format': result['format'],
                'width': result.get('width'),
                'height': result.get('height'),
                'bytes': result.get('bytes')
            },
            'message': 'Image uploaded from URL successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error uploading image from URL: {str(e)}")
        return jsonify({'error': str(e)}), 500


@uploads_bp.route('/profile-image', methods=['POST'])
def upload_profile_image():
    """
    Upload a profile image (for farmer or buyer)
    Expects: multipart/form-data with 'image' file field
    Optional: 'user_type' field ('farmer' or 'buyer')
    """
    try:
        # Check if file is present
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'error': 'Invalid file type',
                'allowed_types': list(ALLOWED_EXTENSIONS)
            }), 400
        
        # Get user type from request
        user_type = request.form.get('user_type', 'profile')
        folder = f'mkulima-bora/profiles/{user_type}'
        
        # Upload to Cloudinary
        result = upload_image(file, folder=folder)
        
        if not result:
            return jsonify({'error': 'Failed to upload profile image to Cloudinary'}), 500
        
        return jsonify({
            'success': True,
            'image_url': result['secure_url'],
            'public_id': result['public_id'],
            'message': 'Profile image uploaded successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error uploading profile image: {str(e)}")
        return jsonify({'error': str(e)}), 500


@uploads_bp.route('/base64', methods=['POST'])
def upload_base64_image_endpoint():
    """
    Upload a base64 encoded image to Cloudinary
    Expects: { "image": "data:image/...;base64,...", "folder": "..." (optional), "image_type": "..." (optional) }
    """
    try:
        from utils.cloudinary_service import upload_base64_image
        
        data = request.get_json()
        base64_string = data.get('image')
        
        if not base64_string:
            return jsonify({'error': 'base64 image string is required'}), 400
        
        # Get folder from request or use default
        folder = data.get('folder', 'mkulima-bora')
        
        # If image_type is provided, use appropriate folder structure
        image_type = data.get('image_type', '')
        if image_type == 'id-front' or image_type == 'id-back':
            user_type = data.get('user_type', 'farmer')
            folder = f'mkulima-bora/profiles/{user_type}/id-documents'
        elif image_type == 'selfie':
            user_type = data.get('user_type', 'farmer')
            folder = f'mkulima-bora/profiles/{user_type}/selfies'
        elif image_type == 'profile':
            user_type = data.get('user_type', 'farmer')
            folder = f'mkulima-bora/profiles/{user_type}'
        
        # Upload to Cloudinary
        result = upload_base64_image(base64_string, folder=folder)
        
        if not result:
            return jsonify({'error': 'Failed to upload base64 image to Cloudinary'}), 500
        
        return jsonify({
            'success': True,
            'image': {
                'url': result['url'],
                'secure_url': result['secure_url'],
                'public_id': result['public_id'],
                'format': result['format'],
                'width': result.get('width'),
                'height': result.get('height'),
                'bytes': result.get('bytes')
            },
            'message': 'Base64 image uploaded successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error uploading base64 image: {str(e)}")
        return jsonify({'error': str(e)}), 500
