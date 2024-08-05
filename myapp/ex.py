from flask import Flask, request, jsonify
import psycopg2
from passlib.hash import bcrypt  
from datetime import datetime
import os
import boto3
from botocore.exceptions import NoCredentialsError
import cv2
import numpy as np
import tempfile


app = Flask(__name__)

os.environ['AWS_ACCESS_KEY_ID'] = 'AKIAJ7JHH2CF7ZL36UYQ'
os.environ['AWS_SECRET_ACCESS_KEY'] = '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'
S3_BUCKET_NAME = "dyqareports"
S3_REGION_NAME = "ap-south-1"

s3 = boto3.client("s3", aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'], region_name=S3_REGION_NAME)


conn = psycopg2.connect(
    database="cleaning-dev",
    user="Medyaan",
    password="adyeLDeI4lXCjYY6ojdOCA",
    host="street-plover-3346.7s5.cockroachlabs.cloud",
    port="26257"
)



cursor = conn.cursor()


def create_customuser_table():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customuser (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) UNIQUE,
            last_name VARCHAR(255),
            first_name VARCHAR(255),
            mobile_number VARCHAR(20) UNIQUE,
            password VARCHAR(255),
            otp VARCHAR(10) NULL,
            role VARCHAR(20),
            is_active BOOLEAN DEFAULT true,
            created_by VARCHAR(255),
            modified_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT current_timestamp,
            modified_by VARCHAR(255),
            email VARCHAR(255) UNIQUE NULL
        )
    ''')
    conn.commit()

clean_details_table = """
CREATE TABLE IF NOT EXISTS clean_details (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    session VARCHAR(255),
    image_url VARCHAR(255),  
    created_by VARCHAR(255),
    modified_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    modified_at TIMESTAMP DEFAULT NOW()
);
"""

cursor = conn.cursor()
cursor.execute(clean_details_table)
conn.commit()



def hash_password(password):
    return bcrypt.hash(password)

def verify_password(password, hashed_password):
    return bcrypt.verify(password, hashed_password)



# API for admin registration
@app.route('/admin/register', methods=['POST'])
def admin_register():
    try:
        create_customuser_table()  

        

        data = request.json
        username = data.get('username')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        mobile_number = data.get('mobile_number')
        email = data.get('email')
        password = data.get('password')
        
        hashed_password = hash_password(password)

        if not (username and first_name and last_name and mobile_number and email and password):
            return jsonify({'status':'error','message': 'All fields are required'}), 400

        cursor.execute("SELECT * FROM customuser WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            return jsonify({'status':'error','message': 'Email already exists'}), 400
        
        cursor.execute("SELECT * FROM customuser WHERE mobile_number = %s", (mobile_number,))
        existing_user = cursor.fetchone()
        if existing_user:
            return jsonify({'status':'error','message': 'mobile_number already exists'}), 400
        
        cursor.execute("SELECT * FROM customuser WHERE username = %s", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            return jsonify({'status':'error','message': 'username already exists'}), 400
        
        cursor.execute(
            "INSERT INTO customuser (username, first_name, last_name, mobile_number, email, password, role) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (username, first_name, last_name, mobile_number, email, hashed_password, 'admin')
        )
        conn.commit()
        return jsonify({'status':'success','message': 'Admin registered successfully'}), 201
    except Exception as e:
        return jsonify ({"status":"error", "message":str(e)}), 400



# API for admin login
@app.route('/admin/login', methods=['POST'])
def admin_login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not (email and password):
            return jsonify({'status':'error','message':'Enter all fields required'}),400
        
        cursor.execute("SELECT password, role FROM customuser WHERE email = %s", (email,))
        user_data = cursor.fetchone()

        if user_data:
            hashed_password = user_data[0]
            role = user_data[1]

            if verify_password(password, hashed_password):
                if role == 'admin':
                    return jsonify({'status':'success','message': 'Admin login successful'}), 200
                else:
                    return jsonify({'status':'error','message': 'Admin access denied'}), 403
            else:
                return jsonify({'status':'error','message': 'Invalid password'}), 401
        else:
            return jsonify({'status':'error','message': 'User not found'}), 404
    
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}), 400
    


    
@app.route('/admin/add_users', methods=['POST'])
def add_users():
    try:
        data=request.json
        username = data.get('username')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        mobile_number = data.get('mobile_number')
        password = data.get('password')
        
        hashed_password = hash_password(password)
        if not (username and first_name and last_name and mobile_number and password):
                return jsonify({'status':'error','message': 'All fields are required'}), 400
        
        cursor.execute("SELECT * FROM customuser WHERE mobile_number = %s", (mobile_number,))
        existing_user = cursor.fetchone()
        if existing_user:
            return jsonify({'status':'error','message': 'mobile_number already exists'}), 400
            
        cursor.execute("SELECT * FROM customuser WHERE username = %s", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            return jsonify({'status':'error','message': 'username already exists'}), 400

        role = 'user'
        cursor.execute(
            "INSERT INTO customuser (username, first_name, last_name, mobile_number, password, role) VALUES (%s, %s, %s, %s, %s, %s)",
            (username, first_name, last_name, mobile_number, hashed_password, role)
        )
        conn.commit()
        return jsonify({'message': 'User added successfully'}), 201
    except Exception as e:
        return jsonify({'status':'error','message':str(e)})





# API for user login
@app.route('/user/login', methods=['POST'])
def user_login():
    try:
        data = request.json
        mobile_number = data.get('mobile_number')
        password = data.get('password')
        if not (mobile_number and password):
                return jsonify({'status':'error','message':'Enter all fields required'}), 400

        cursor.execute("SELECT password, role FROM customuser WHERE mobile_number = %s", (mobile_number,))
        user_data = cursor.fetchone()

        if user_data:
            hashed_password = user_data[0]
            role = user_data[1]

            if verify_password(password, hashed_password):
                if role == 'user':
                    return jsonify({'status':'success','message': 'User login successful'}), 200
                else:
                    return jsonify({'status':'error','message': 'Admin does not have user privileges'}), 403
            else:
                return jsonify({'status':'error','message': 'Invalid password'}), 401
        else:
            return jsonify({'status':'error','message': 'User not found'}), 404
    except Exception as e:
        return jsonify({'status':'error', 'message':str(e)})
    



            
@app.route('/admin/get_users', methods=['GET'])
def admin_get_users():
    cursor.execute("SELECT id, username, first_name, last_name, mobile_number FROM customuser WHERE role = 'user'")
    users = cursor.fetchall()

    if users:
        user_details = []
        for user in users:
            user_id, username, first_name, last_name, mobile_number = user
            user_details.append({
                "id": user_id,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "mobile_number": mobile_number
            })
        return jsonify({'message': 'User details retrieved successfully', 'data': user_details}), 200
    else:
        return jsonify({'message': 'No users with the "user" role found', 'data': []}), 200
    


def calculate_mean_pixel_difference(image1, image2):
    if image1.shape != image2.shape:
        raise ValueError("Image dimensions do not match")

    abs_diff = cv2.absdiff(image1, image2)
    mean_diff = np.mean(abs_diff)
    return mean_diff

# Function to calculate normalized cross-correlation (NCC)
def calculate_normalized_cross_correlation(image1, image2):
    image1_gray = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    image2_gray = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

    result = cv2.matchTemplate(image1_gray, image2_gray, cv2.TM_CCORR_NORMED)
    _, _, _, max_loc = cv2.minMaxLoc(result)
    ncc = result[max_loc[1], max_loc[0]]

    return ncc

# Route to handle user image upload and comparison
@app.route("/user_view", methods=['POST'])
def user_view():
    try:
        today_date = datetime.now().date()
        mobile_number = request.form.get("mobile_number")
        session = request.form.get("session")

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM customuser WHERE mobile_number = %s", (mobile_number,))
            user_id = cursor.fetchone()

            if not user_id:
                return jsonify({"error": f"User with mobile number {mobile_number} not found"}), 404

            user_id = user_id[0]

            if session not in ["morning", "afternoon", "evening"]:
                return jsonify({'error': 'Invalid session'}), 400

            user_uploaded_image = request.files.get("image")

            if user_uploaded_image is not None:
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_filename = temp_file.name
                    user_uploaded_image.save(temp_filename)

                image1_object_key = "2023-09-20_evening.jpg"
                image1_stream = s3.get_object(Bucket=S3_BUCKET_NAME, Key=image1_object_key)['Body'].read()
                image1_np = np.frombuffer(image1_stream, np.uint8)
                image1 = cv2.imdecode(image1_np, cv2.IMREAD_COLOR)
                image2_np = cv2.imread(temp_filename)
                image_filename = f"{today_date}_{session}.jpg"

                


                mean_diff = calculate_mean_pixel_difference(image1, image2_np)

                ncc = calculate_normalized_cross_correlation(image1, image2_np)

                mean_diff = float(mean_diff)
                ncc = float(ncc)

                image_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{image_filename}"

                s3.upload_file(
                    temp_filename,
                    S3_BUCKET_NAME,
                    image_filename,
                    ExtraArgs={"ContentType": "image/jpeg", "ACL": "public-read"}
                )
               
                cursor.execute(
                    "INSERT INTO clean_details (date, session, mean_pixel_diff, normalized_cross_correlation, created_by, image_url) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    (today_date, session, mean_diff, ncc, user_id, image_url)
                )


                conn.commit()

                os.remove(temp_filename)

                return jsonify({'message': 'Cleaning record added successfully', 'mean_pixel_diff': mean_diff, 'normalized_cross_correlation': ncc, 'id': user_id,'image_url':image_url}), 200
            else:
                return jsonify({"error": "No user image uploaded"}), 400

        except NoCredentialsError:
            return jsonify({'error': 'AWS credentials not found'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 400





if __name__ == '__main__':
    app.run()
