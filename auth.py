from flask import Flask, request, jsonify
import mysql.connector
from google.cloud import storage

app = Flask(__name__)

# Konfigurasi database
db = mysql.connector.connect(
    host="localhost", # Ganti sesuai dengan pengaturan database phpMyAdmin
    user="username", # Ganti sesuai dengan pengaturan database phpMyAdmin 
    password="password", # Ganti sesuai dengan pengaturan database phpMyAdmin
    database="database_name" # Ganti sesuai dengan pengaturan database phpMyAdmin
)

# Konfigurasi Google Cloud Storage
storage_client = storage.Client.from_service_account_json('access-user-photo-data-4299fe680af4.json')
bucket_name = 'foto-user-travellens'

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
    username = request.json.get('username')
    email = request.json.get('email')
    password = request.json.get('password')
    confirm_password = request.json.get('confirm_password')

    cursor = db.cursor()

    # Memeriksa apakah password dan konfirmasi password cocok
    if password != confirm_password:
        return jsonify({'message': 'Password dan konfirmasi password tidak cocok'}), 400

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

# Route untuk edit profile
@app.route('/profile/edit/<int:user_id>', methods=['PUT'])
def edit_profilee(user_id):
    cursor = db.cursor()

    # Mendapatkan data yang akan diupdate dari body permintaan
    data = request.get_json()
    new_username = data.get('username')
    new_email = data.get('email')
    new_address = data.get('address')
    new_phone = data.get('phone')
    new_photo = request.files.get('photo')

    # Mengecek apakah user dengan user_id tertentu ada di database
    query_check_user = "SELECT * FROM users WHERE id = %s"
    cursor.execute(query_check_user, (user_id,))
    user = cursor.fetchone()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Mengupdate data pengguna dalam database
    query_update_user = "UPDATE users SET username = %s, email = %s, address = %s, phone = %s WHERE id = %s"
    cursor.execute(query_update_user, (new_username, new_email, new_address, new_phone, user_id))
    db.commit()

    # Mengunggah foto baru ke Google Cloud Storage
    file = request.files.get('profile_picture')
    if file:
        filename = f"profile_{user_id}.jpg"  # otomatis mengatur nama file sesuai dengan ID pengguna
        blob = storage_client.bucket(bucket_name).blob(filename)
        blob.upload_from_file(file)

        # Mengupdate nama file foto di database
        query_update_photo = "UPDATE users SET photo = %s WHERE id = %s"
        cursor.execute(query_update_photo, (filename, user_id))
        db.commit()

    # Mengambil data terbaru dari database
    query_get_user = "SELECT * FROM users WHERE id = %s"
    cursor.execute(query_get_user, (user_id,))
    updated_user = cursor.fetchone()

    # Menyiapkan respons JSON dengan data terbaru
    profile = {
        'username': updated_user[1],
        'email': updated_user[3],
        'address': updated_user[5],
        'phone': updated_user[6],
        'photo': updated_user[4]
    }
    return jsonify(profile)


# Route untuk profile
@app.route('/profile', methods=['GET'])
def get_profile():
    # Mendapatkan data pengguna dari database
    user_id = request.args.get('user_id')  # Mendapatkan ID pengguna dari parameter URL
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    result = cur.fetchone()
    cur.close()

    if not result:
        return jsonify({'message': 'Pengguna tidak ditemukan'}), 404

    # Mendapatkan informasi nama depan dan alamat pengguna
    first_name = result['first_name']
    address = result['address']

    # Mengambil URL foto profil dari Google Cloud Storage
    filename = f"profile_{user_id}.jpg"  # otomatis mengatur nama file sesuai dengan ID pengguna
    blob = storage_client.bucket(bucket_name).blob(filename)
    photo_url = blob.public_url

    # Mengembalikan respons dengan informasi pengguna
    return jsonify({
        'message': f'Halo, {first_name}',
        'address': address,
        'photo_url': photo_url
    }), 200

if __name__ == '__main__':
    app.run()
