from flask import Flask, request, jsonify
import face_recognition
import numpy as np
import mysql.connector
import zipfile
import os
from PIL import Image

app = Flask(__name__)

# Database configuration
db_config = {
    'user': os.getenv('MYSQL_USER', 'face'),   
    'password': os.getenv('MYSQL_PASSWORD'),
    'host': os.getenv('MYSQL_HOST', '100.114.2.54'),
    'port': os.getenv('MYSQL_PORT', '3308'),
    'database': os.getenv('MYSQL_DATABASE', 'faces')
}


def get_db_connection():
    return mysql.connector.connect(**db_config)

def save_face_to_db(name, encoding):
    conn = get_db_connection()
    cursor = conn.cursor()

    encoding_str = ','.join(map(str, encoding.tolist()))
    query = "INSERT INTO faces (name, embedding) VALUES (%s, %s)"
    cursor.execute(query, (name, encoding_str))
    conn.commit()

    cursor.close()
    conn.close()

def load_faces_from_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT name, embedding FROM faces"
    cursor.execute(query)

    names = []
    encodings = []

    for name, embedding_str in cursor.fetchall():
        embedding = np.array(list(map(float, embedding_str.split(','))))
        names.append(name)
        encodings.append(embedding)

    cursor.close()
    conn.close()

    return names, encodings

def read_image(file_storage):
    # Read uploaded file into numpy array
    image = Image.open(file_storage.stream)
    return np.array(image)

@app.route('/insert', methods=['POST'])
def insert_face():
    if 'image' not in request.files or 'name' not in request.form:
        return jsonify({'error': 'Missing image or name'}), 400

    image = read_image(request.files['image'])
    name = request.form['name']

    face_locations = face_recognition.face_locations(image)
    num_faces = len(face_locations)

    if num_faces == 0:
        return jsonify({'error': 'No face detected in the image'}), 400
    if num_faces > 1:
        return jsonify({'error': 'Multiple faces detected, please upload an image with exactly one face'}), 400

    face_encoding = face_recognition.face_encodings(image, face_locations)[0]
    save_face_to_db(name, face_encoding)

    return jsonify({'message': 'Face inserted successfully'})

@app.route('/insert_batch', methods=['POST'])
def insert_batch():
    if 'file' not in request.files or 'name' not in request.form:
        return jsonify({'error': 'Missing file or name'}), 400

    # Retrieve the name and the ZIP file
    name = request.form['name']
    zip_file = request.files['file']

    # Temporarily store the zip file
    zip_path = os.path.join('/tmp', zip_file.filename)
    zip_file.save(zip_path)

    # Extract the images from the ZIP file
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall('/tmp')

    # Iterate over all extracted files
    saved_encodings = []
    for file_name in os.listdir('/tmp'):
        if file_name.endswith(('jpg', 'jpeg', 'png')):
            image_path = os.path.join('/tmp', file_name)
            image = read_image(image_path)

            face_locations = face_recognition.face_locations(image)
            num_faces = len(face_locations)

            if num_faces == 0:
                continue  # Skip files with no faces
            if num_faces > 1:
                return jsonify({'error': f"Multiple faces detected in {file_name}, skipping file"}), 400

            # Extract the face encoding and save it
            face_encoding = face_recognition.face_encodings(image, face_locations)[0]
            save_face_to_db(name, face_encoding)
            saved_encodings.append(file_name)

    # Clean up the temporary files
    os.remove(zip_path)
    for file_name in os.listdir('/tmp'):
        os.remove(os.path.join('/tmp', file_name))

    return jsonify({'message': f'{len(saved_encodings)} images inserted successfully from the ZIP file'})
@app.route('/search', methods=['POST'])
def search_faces():
    if 'image' not in request.files:
        return jsonify({'error': 'Missing image'}), 400

    image = read_image(request.files['image'])
    face_locations = face_recognition.face_locations(image)
    face_encodings = face_recognition.face_encodings(image, face_locations)

    known_names, known_encodings = load_faces_from_db()

    matches = []

    for encoding in face_encodings:
        distances = face_recognition.face_distance(known_encodings, encoding)

        if len(distances) == 0:
            matches.append('Unknown')
            continue

        threshold = 0.6
        valid_matches = [(known_names[i], distances[i]) for i in range(len(distances)) if distances[i] < threshold]

        if valid_matches:
            best_match = min(valid_matches, key=lambda x: x[1])
            matches.append(best_match[0])
        else:
            matches.append('Unknown')

    result = {
        'matches': matches,
        'num_people': len(matches)  # <-- new line here
    }
    return jsonify(result)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
