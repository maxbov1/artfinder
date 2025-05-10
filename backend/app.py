from flask import Flask, request, jsonify
from tools.search_faiss import search_top_k
import os
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "temp_uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/classify", methods=["POST"])
def classify_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    image_file = request.files['image']
    filename = secure_filename(image_file.filename)
    temp_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{filename}")
    image_file.save(temp_path)

    try:
        matches = search_top_k(temp_path, k=10)

        return jsonify({
            "matches": matches
        })
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4000)

