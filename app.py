from flask import Flask
from auth import auth_blueprint
from wisata import wisata_blueprint
from image import image_blueprint
from database import database_blueprint
from android import android_blueprint

app = Flask(__name__)

# Menggunakan Blueprint untuk mengatur routing API
app.register_blueprint(auth_blueprint)
app.register_blueprint(wisata_blueprint)
app.register_blueprint(image_blueprint)
app.register_blueprint(database_blueprint)
app.register_blueprint(android_blueprint)

if __name__ == '__main__':
    app.run(debug=True)
