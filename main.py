import cv2
import numpy as np
import cv2
import time  
import os
import sys
import warnings
import requests
import random
import pymysql
import mysql.connector

pymysql.install_as_MySQLdb()
from flask import Flask, jsonify, render_template, Response, make_response, jsonify, render_template, session
from keras.models import load_model
from statistics import mode
from utils.datasets import get_labels
from utils.inference import detect_faces
from utils.inference import draw_text
from utils.inference import draw_bounding_box
from utils.inference import apply_offsets
from utils.inference import load_detection_model
from utils.preprocessor import preprocess_input


from flask_restx import Resource, Api, reqparse
from flask_cors import  CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt, os,random
from flask_mail import Mail, Message

app = Flask(__name__)
api = Api(app)
CORS(app)
# port = int(os.environ.get("RAILWAY_PORT", 5000))
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:@127.0.0.1:3306/movie_emotion"
# app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'whateveryouwant'
# mail env config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")
mail = Mail(app)
# mail env config
db = SQLAlchemy(app)



class Users(db.Model):
    id       = db.Column(db.Integer(), primary_key=True, nullable=False)
    firstname     = db.Column(db.String(30), nullable=False)
    lastname     = db.Column(db.String(30), nullable=False)
    email    = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    is_verified = db.Column(db.Boolean(),nullable=False)
    token     = db.Column(db.String(5), nullable=False)
    createdAt = db.Column(db.Date)
    updatedAt = db.Column(db.Date)

class Histori(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    nama = db.Column(db.String(30), nullable=False)
    nama_gerakan = db.Column(db.String(30), nullable=False)
    tanggal = db.Column(db.Date)

    user = db.relationship('Users', backref=db.backref('histori', lazy=True))


# class History(db.Model):
#     id = db.Column(db.Integer(), primary_key=True, nullable=False)
#     nama = db.Column(db.String(30), nullable=False)
#     jenis_kendaraan = db.Column(db.String(30), nullable=False)
#     tanggal = db.Column(db.Date)
#     waktu = db.Column(db.Time)




# Email functions
# https://medium.com/@stevenrmonaghan/password-reset-with-flask-mail-protocol-ddcdfc190968
# https://www.youtube.com/watch?v=g_j6ILT-X0k
# https://stackoverflow.com/questions/72547853/unable-to-send-email-in-c-sharp-less-secure-app-access-not-longer-available

#history
# historyParser = reqparse.RequestParser()
# historyParser.add_argument('jenis_kendaraan', type=str, help='Jenis Kendaraan', location='json', required=True)
# historyParser.add_argument('tanggal', type=str, help='Tanggal', location='json', required=True)
# historyParser.add_argument('waktu', type=str, help='Waktu', location='json', required=True)

# @app.route('/history')
# def get_history():
#     args = historyParser.parse_args()
#     jenis_kendaraan = args['jenis_kendaraan']
#     tanggal = args['tanggal']
#     waktu = args['waktu']

#     # Lanjutkan dengan logika lainnya untuk mendapatkan data history
#     history_list = History.query.all()
#     history_data = []
#     for history in history_list:
#         history_data.append({
#             'nama': history.nama,
#             'jenis_kendaraan': history.jenis_kendaraan,
#             'tanggal': history.tanggal.strftime('%Y-%m-%d'),
#             'waktu': history.waktu.strftime('%H:%M:%S')
#         })
#     return jsonify(history_data)



#parserRegister
regParser = reqparse.RequestParser()
regParser.add_argument('firstname', type=str, help='firstname', location='json', required=True)
regParser.add_argument('lastname', type=str, help='lastname', location='json', required=True)
regParser.add_argument('email', type=str, help='Email', location='json', required=True)
regParser.add_argument('password', type=str, help='Password', location='json', required=True)
regParser.add_argument('confirm_password', type=str, help='Confirm Password', location='json', required=True)


@api.route('/register')
class Registration(Resource):
    @api.expect(regParser)
    def post(self):
        # BEGIN: Get request parameters.
        args        = regParser.parse_args()
        firstname   = args['firstname']
        lastname    = args['lastname']
        email       = args['email']
        password    = args['password']
        password2  = args['confirm_password']
        is_verified = False

        # cek confirm password
        if password != password2:
            return {
                'messege': 'Password tidak cocok'
            }, 400

        #cek email sudah terdaftar
        user = db.session.execute(db.select(Users).filter_by(email=email)).first()
        if user:
            return "Email sudah terpakai silahkan coba lagi menggunakan email lain"
        user          = Users()
        user.firstname    = firstname
        user.lastname     = lastname
        user.email    = email
        user.password = generate_password_hash(password)
        user.is_verified = is_verified
        db.session.add(user)
        msg = Message(subject='Verification OTP',sender=os.environ.get("MAIL_USERNAME"),recipients=[user.email])
        token =  random.randrange(10000,99999)
        session['email'] = user.email
        user.token = str(token)
        print("Isi session email:", session['email'])
        print("Isi session token:", user.token)
        msg.html=render_template(
        'verify_email.html', token=token)
        mail.send(msg)
        db.session.commit()
        return {'message':
            'Registrasi Berhasil. Silahkan cek email untuk verifikasi.'}, 201

otpparser = reqparse.RequestParser()
otpparser.add_argument('otp', type=str, help='otp', location='json', required=True)
otpparser.add_argument('email', type=str, help='email', location='json', required=True)
# @api.route('/verifikasi')
# class Verify(Resource):
#     @api.expect(otpparser)
#     def post(self):
#         args = otpparser.parse_args()
#         otp = args['otp']
#         if 'token' in session:
#             sesion = session['token']
#             if otp == sesion:
#                 email = session['email']

#                 user = Users.query.filter_by(email=email).first()
#                 user.is_verified = True

#                 db.session.commit()  # Melakukan komit ke database

#                 if db.session.is_active:  # Memeriksa apakah sesi masih aktif
#                     session.pop('token', None)
#                     print("Perubahan berhasil dikommit ke database")
#                     return {'message': 'Email berhasil diverifikasi'}
#                 else:
#                     print("Terjadi kesalahan saat melakukan komit")
#                     db.session.rollback()  # Mengembalikan perubahan jika terjadi kesalahan
#                     return {'message': 'Terjadi kesalahan pada server'}

#             else:
#                 return {'message': 'Kode OTP Salah'}
#         else:
#             return {'message': 'Kode OTP Salah'}

@api.route('/verifikasi')
class Verify(Resource):
    @api.expect(otpparser)
    def post(self):
        args = otpparser.parse_args()
        otp = args['otp']
        print("Kode OTP:", otp)  # Cetak kode OTP di log
        if args['email'] != '':
            email = args['email']

            user = Users.query.filter_by(email=email).first()
            if user.token == otp :
                user.is_verified = True
                user.token = None
                db.session.commit()
            # session.pop('token',None)
                print('Email berhasil diverifikasi')
                return {'message' : 'Email berhasil diverifikasi'}
        # if 'token' in args:
        #     sesion = args ['token']
        #     print("Token:", sesion)
        #     else:
        #         return {'message' : 'Kode Otp Salah'}
            else:
                return {'message' : 'OTP salah'}

logParser = reqparse.RequestParser()
logParser.add_argument('email', type=str, help='Email', location='json', required=True)
logParser.add_argument('password', type=str, help='Password', location='json', required=True)

@api.route('/login')
class LogIn(Resource):
    @api.expect(logParser)
    def post(self):
        args        = logParser.parse_args()
        email       = args['email']
        password    = args['password']
        # cek jika kolom email dan password tidak terisi
        print(email)
        print(password)
        if not email or not password:
            return {
                'message': 'Email Dan Password Harus Diisi'
            }, 400
        #cek email sudah ada
        user = db.session.execute(
            db.select(Users).filter_by(email=email)).first()
        if not user:
            return {
                'message': 'Email / Password Salah'
            }, 400
        else:
            user = user[0]
        #cek password
        if check_password_hash(user.password, password):
            if user.is_verified == True:
                token= jwt.encode({
                        "user_id":user.id,
                        "user_email":user.email,
                        "exp": datetime.utcnow() + timedelta(days= 1)
                },app.config['SECRET_KEY'],algorithm="HS256")
                print(f'Token: {token}')
                return {'message' : 'Login Berhasil',
                        'token' : token
                        },200
                
            else:
                return {'message' : 'Email Belum Diverifikasi ,Silahka verifikasikan terlebih dahulu '},401
        else:
            return {
                'message': 'Email / Password Salah'
            }, 400
def decodetoken(jwtToken):
    decode_result = jwt.decode(
               jwtToken,
               app.config['SECRET_KEY'],
               algorithms = ['HS256'],
            )
    return decode_result

authParser = reqparse.RequestParser()
authParser.add_argument('Authorization', type=str, help='Authorization', location='headers', required=True)
@api.route('/user')
class DetailUser(Resource):
       @api.expect(authParser)
       def get(self):
        args = authParser.parse_args()
        bearerAuth  = args['Authorization']
        try:
            jwtToken    = bearerAuth[7:]
            token = decodetoken(jwtToken)
            user =  db.session.execute(db.select(Users).filter_by(email=token['user_email'])).first()
            user = user[0]
            data = {
                'firstname' : user.firstname,
                'lastname' : user.lastname,
                'email' : user.email
            }
        except:
            return {
                'message' : 'Token Tidak valid,Silahkan Login Terlebih Dahulu!'
            }, 401

        return data, 200

editParser = reqparse.RequestParser()
editParser.add_argument('firstname', type=str, help='Firstname', location='json', required=True)
editParser.add_argument('lastname', type=str, help='Lastname', location='json', required=True)
editParser.add_argument('Authorization', type=str, help='Authorization', location='headers', required=True)
@api.route('/edituser')
class EditUser(Resource):
       @api.expect(editParser)
       def put(self):
        args = editParser.parse_args()
        bearerAuth  = args['Authorization']
        firstname = args['firstname']
        lastname = args['lastname']
        datenow =  datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        try:
            jwtToken    = bearerAuth[7:]
            token = decodetoken(jwtToken)
            user = Users.query.filter_by(email=token.get('user_email')).first()
            user.firstname = firstname
            user.lastname = lastname
            user.updatedAt = datenow
            db.session.commit()
        except:
            return {
                'message' : 'Token Tidak valid,Silahkan Login Terlebih Dahulu!'
            }, 401
        return {'message' : 'Update User Sukses'}, 200


verifyParser = reqparse.RequestParser()
verifyParser.add_argument(
    'otp', type=str, help='firstname', location='json', required=True)


# @api.route('/verify')
# class Verify(Resource):
#     @api.expect(verifyParser)
#     def post(self):
#         args = verifyParser.parse_args()
#         otp = args['otp']
#         try:
#             user = Users.verify_token(otp)
#             if user is None:
#                 return {'message' : 'Verifikasi gagal'}, 401
#             user.is_verified = True
#             db.session.commit()
#             return {'message' : 'Akun sudah terverifikasi'}, 200
#         except Exception as e:
#             print(e)
#             return {'message' : 'Terjadi error'}, 200

#editpasswordParser
editPasswordParser =  reqparse.RequestParser()
editPasswordParser.add_argument('current_password', type=str, help='current_password',location='json', required=True)
editPasswordParser.add_argument('new_password', type=str, help='new_password',location='json', required=True)
@api.route('/editpassword')
class Password(Resource):
    @api.expect(authParser,editPasswordParser)
    def put(self):
        args = editPasswordParser.parse_args()
        argss = authParser.parse_args()
        bearerAuth  = argss['Authorization']
        cu_password = args['current_password']
        newpassword = args['new_password']
        try:
            jwtToken    = bearerAuth[7:]
            token = decodetoken(jwtToken)
            user = Users.query.filter_by(id=token.get('user_id')).first()
            if check_password_hash(user.password, cu_password):
                user.password = generate_password_hash(newpassword)
                db.session.commit()
            else:
                return {'message' : 'Password Lama Salah'},400
        except:
            return {
                'message' : 'Token Tidak valid! Silahkan, Sign in!'
            }, 401
        return {'message' : 'Password Berhasil Diubah'}, 200

#histori parser
historiParser = reqparse.RequestParser()
historiParser.add_argument('nama', type=str, help='Nama', location='json', required=True)
historiParser.add_argument('nama_gerakan', type=str, help='Nama Gerakan', location='json', required=True)
historiParser.add_argument('tanggal', type=str, help='Tanggal', location='json', required=True)

#membuat histori baru
@api.route('/add-histori')
class AddHistoriResource(Resource):
    @api.expect(authParser, historiParser)
    def post(self):
        args = authParser.parse_args()
        bearerAuth = args['Authorization']

        jwtToken = bearerAuth[7:]
        token = decodetoken(jwtToken)
        user_id = token['user_id']

        args = historiParser.parse_args()
        nama = args['nama']
        nama_gerakan = args['nama_gerakan']
        tanggal = datetime.strptime(args['tanggal'], '%Y-%m-%d').date()

        histori = Histori(user_id=user_id, nama=nama, nama_gerakan=nama_gerakan, tanggal=tanggal)
        db.session.add(histori)
        db.session.commit()

        return {'message': 'Histori berhasil ditambahkan'}, 201

#menampilkan data histori bedasarkan id
@api.route('/read-histori')
class ReadHistori(Resource):
    @api.expect(authParser)
    def get(self):
        # Mendapatkan user_id dari token yang terverifikasi
        # user_id = get_jwt_identity()
        args = authParser.parse_args()
        bearerAuth = args['Authorization']

        jwtToken = bearerAuth[7:]
        token = decodetoken(jwtToken)
        user_id = token['user_id']

        # Mengambil data histori berdasarkan user_id
        histori = Histori.query.filter_by(user_id=user_id).all()
        if not histori:
            return {'message': 'Histori tidak ditemukan'}, 404

        histori_data = []
        for h in histori:
            histori_data.append({
                'id': h.id,
                'nama': h.nama,
                'nama_gerakan': h.nama_gerakan,
                'tanggal': h.tanggal.strftime('%Y-%m-%d')
            })

        return histori_data, 200
    
    

# =================================================================================== #

# Create a connection to the MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="movie_emotion"
)

# Create a cursor object to execute SQL queries
cursor = db.cursor()

USE_WEBCAM = True  # If false, loads video file source

# parameters for loading data and images
emotion_model_path = './models/emotion_model.hdf5'
emotion_labels = get_labels('fer2013')

# hyper-parameters for bounding boxes shape
frame_window = 10
emotion_offsets = (20, 40)

# loading models
face_cascade = cv2.CascadeClassifier('./models/haarcascade_frontalface_default.xml')
emotion_classifier = load_model(emotion_model_path)

# getting input model shapes for inference
emotion_target_size = emotion_classifier.input_shape[1:3]

# starting lists for calculating modes
emotion_window = []

# Select video or webcam feed
cap = None
if USE_WEBCAM:
    cap = cv2.VideoCapture(0)  # Webcam source
else:
    cap = cv2.VideoCapture('./demo/dinner.mp4')  # Video file source

# API URL for movie recommendations
API_URL = "https://yts.torrentbay.net/api/v2/list_movies.json"

# Set of movie genres
GENRES = ["Comedy", "Fantasy", "Romance", "Film-Noir", "Drama", "Sci-Fi", "Action", "Thriller", "Mystery", "Animation", "Adventure"]

# API request parameters
PARAMS = {"limit": 5}

# Dictionary to store emotion count
emotion_count = {}


def gen_frames():
    global emotion_count

    # Variable to keep track of captured images for recommendation
    captured_images = []
    start_time = time.time()

    while cap.isOpened():  # True:
        ret, bgr_image = cap.read()

        gray_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
        rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)

        faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5,
                                              minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)

        for face_coordinates in faces:
            x1, x2, y1, y2 = apply_offsets(face_coordinates, emotion_offsets)
            gray_face = gray_image[y1:y2, x1:x2]
            try:
                gray_face = cv2.resize(gray_face, (emotion_target_size))
            except:
                continue

            gray_face = preprocess_input(gray_face, True)
            gray_face = np.expand_dims(gray_face, 0)
            gray_face = np.expand_dims(gray_face, -1)
            emotion_prediction = emotion_classifier.predict(gray_face)
            emotion_probability = np.max(emotion_prediction)
            emotion_label_arg = np.argmax(emotion_prediction)
            emotion_text = emotion_labels[emotion_label_arg]
            emotion_window.append(emotion_text)

            if len(emotion_window) > frame_window:
                emotion_window.pop(0)
            
            # Store emotion count in dictionary
            emotion_count = {emotion: emotion_window.count(emotion) for emotion in set(emotion_window)}

            try:
                emotion_mode = mode(emotion_window)
            except:
                continue

            if emotion_text == 'angry':
                color = emotion_probability * np.asarray((255, 0, 0))
            elif emotion_text == 'sad':
                color = emotion_probability * np.asarray((0, 0, 255))
            elif emotion_text == 'happy':
                color = emotion_probability * np.asarray((255, 255, 0))
            elif emotion_text == 'surprise':
                color = emotion_probability * np.asarray((0, 255, 255))
            else:
                color = emotion_probability * np.asarray((0, 255, 0))

            color = color.astype(int)
            color = color.tolist()

            draw_bounding_box(face_coordinates, rgb_image, color)
            draw_text(face_coordinates, rgb_image, emotion_mode,
                      color, 0, -45, 1, 1)

            # Generate the response frame
            bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
            ret, jpeg = cv2.imencode('.jpg', bgr_image)
            frame = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

            # Capture the image for recommendation every 3 seconds
            current_time = time.time()
            if current_time - start_time >= 3:
                captured_images.append(bgr_image)
                start_time = current_time

                # Keep only the last 3 captured images
                if len(captured_images) > 3:
                    captured_images.pop(0)

    # Insert the captured images into the database
    for image in captured_images:
        image_filename = f"captured_images/{time.time()}.jpg"
        cv2.imwrite(image_filename, image)
        query = "INSERT INTO captured_images (image_path, emotion) VALUES (%s, %s)"
        values = (image_filename, emotion_mode)
        cursor.execute(query, values)
        db.commit()

    cap.release()


def fetch_movie(genre):
    PARAMS["genre"] = genre
    try:
        response = requests.get(url=API_URL, params=PARAMS)
        json_data = response.json()
        if json_data["status"] == "ok" and json_data["data"]["movie_count"] > 0:
            movies = json_data["data"]["movies"]
            return movies
    except:
        pass
    return None


# Fungsi untuk menghentikan program
def stop_program():
    sys.exit()


@app.route('/detection')
def index():
    return render_template('detection.html')


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/button-clicked')
def button_clicked():
    global emotion_count

    # Variable to keep track of captured images for history
    captured_images = []

    # Check if emotion_count is not empty
    if emotion_count:
        # Get most frequent emotion
        max_emotion = max(emotion_count, key=emotion_count.get)

        # Determine movie genre based on emotion
        if max_emotion in ['angry', 'fear', 'sad', 'disgust', 'surprise']:
            genre = random.choice(['Comedy', 'Fantasy', 'Romance', 'Film-Noir'])
        else:
            genre = random.choice(['Drama', 'Fantasy', 'Sci-Fi', 'Romance', 'Action', 'Thriller', 'Mystery', 'Animation', 'Adventure'])

        # Fetch movie recommendations
        movies = fetch_movie(genre)

        # Process movie recommendations
        output = ""
        if movies:
            output += f"<h2>Movie Recommendations for {max_emotion}</h2>"
            for movie in movies:
                title = movie['title']
                summary = movie['summary']
                url = movie['url']
                output += f"<h3>{title}</h3>"
                output += f"<p>{summary}</p>"
                output += f"<p>URL: <a href='{url}'>{url}</a></p>"

                # Insert the recommended movie titles into the database
                movie_title = movie['title']
                query = "INSERT INTO recommended_movies (emotion, movie_title) VALUES (%s, %s)"
                values = (max_emotion, movie_title)
                cursor.execute(query, values)
                db.commit()
        else:
            output += "No movie recommendations available."
    else:
        # Handle the case when emotion_count is empty
        output = "No emotions detected."

    # Capture the image for history
    for _ in range(3):
        # Capture frame from video feed
        ret, bgr_image = cap.read()
        if not ret:
            break

        # Generate a unique filename for the image
        image_filename = f"history_images/{time.time()}.jpg"

        # Save the image file
        cv2.imwrite(image_filename, bgr_image)

        # Insert the captured image information into the database
        query = "INSERT INTO captured_images (image_path, emotion) VALUES (%s, %s)"
        values = (image_filename, max_emotion)
        cursor.execute(query, values)
        db.commit()

        # Add the image filename to the captured_images list
        captured_images.append(image_filename)

    return output

@app.route('/buttonStop')
def stop_program_route():
    stop_program()
    return 'Program stopped'  # Mengembalikan respons saat program dihentikan

if __name__ == '__main__':
    # app.run(ssl_context='adhoc', debug=True)
    app.run(host='0.0.0.0' , debug=True)