from flask import Blueprint, request, jsonify
from google.cloud import storage

# Buat Blueprint untuk image
image_blueprint = Blueprint('image', __name__)

# Konfigurasi Google Cloud Storage
BUCKET_NAME = ''
CLOUD_STORAGE_URL = ''

# Fungsi untuk mengunggah gambar ke Cloud Storage
@image_blueprint.route('/upload', methods=['POST'])
def upload_image():
    # Periksa apakah file gambar ada dalam permintaan
    if 'image' not in request.files:
        return jsonify({'error': 'No image found in request'}), 400
    
    image_file = request.files['image']
    
    if image_file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Simpan file gambar ke Cloud Storage
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(image_file.filename)
    blob.upload_from_file(image_file)

    # URL gambar yang diunggah
    image_url = f"{CLOUD_STORAGE_URL}/{BUCKET_NAME}/{blob.name}"

    # Lakukan pemrosesan gambar menggunakan model ML
    
    # Implementasikan logika pemrosesan gambar di sini

    # Contoh: Mengembalikan URL gambar yang diunggah dan hasil identifikasi dari model
    result = {
        'image_url': image_url,
        'identification_result': 'Hasil identifikasi gambar dari model ML'
    }

    return jsonify(result), 200
