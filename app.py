from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

# Konfigurasi database
db = mysql.connector.connect(
    host="localhost", # Ganti sesuai dengan pengaturan database phpMyAdmin
    user="username", # Ganti sesuai dengan pengaturan database phpMyAdmin 
    password="password", # Ganti sesuai dengan pengaturan database phpMyAdmin
    database="database_name" # Ganti sesuai dengan pengaturan database phpMyAdmin
)

# konfigurasi Cloud Storage
bucket_name = "upload-by-user"
storage_client = storage.Client.from_service_account_json("/CapstoneProjectBangkit2023/travellensapp-fefd9f0826d5.json")

# Route untuk login
@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']

    cursor = db.cursor()

    # Query untuk memeriksa keberadaan username dan password yang cocok di database
    query = "SELECT * FROM users WHERE username = %s AND password = %s"
    values = (username, password)
    cursor.execute(query, values)

    # Memeriksa hasil query
    if cursor.rowcount == 1:
        # Jika login berhasil, kirimkan pesan berhasil
        return jsonify({'message': 'Login berhasil!'})
    else:
        # Jika login gagal, kirimkan pesan gagal
        return jsonify({'message': 'Login gagal!'})

# Route untuk registrasi
@app.route('/register', methods=['POST'])
def register():
    username = request.json['username']
    password = request.json['password']
    email = request.json['email']

    cursor = db.cursor()

    # Query untuk memeriksa apakah username atau email sudah digunakan
    check_query = "SELECT * FROM users WHERE username = %s OR email = %s"
    check_values = (username, email)
    cursor.execute(check_query, check_values)

    # Memeriksa hasil query
    if cursor.rowcount > 0:
        # Jika username atau email sudah ada, kirimkan pesan gagal
        return jsonify({'message': 'Username atau email sudah digunakan!'})

    # Jika username atau email belum digunakan, lakukan registrasi
    insert_query = "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)"
    insert_values = (username, password, email)
    cursor.execute(insert_query, insert_values)
    db.commit()

    # Registrasi berhasil, kirimkan pesan berhasil
    return jsonify({'message': 'Registrasi berhasil!'})

# Route untuk upload gambar by user
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file:
        filename = file.filename
        blob = storage_client.bucket(bucket_name).blob(filename)
        blob.upload_from_file(file)
        return jsonify({'message': 'Upload berhasil!'})
    else:
        return jsonify({'message': 'Upload gagal!'})

if __name__ == '__main__':
    app.run()
