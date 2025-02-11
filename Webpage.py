from flask import Flask, request, jsonify
from PIL import Image
import io

app = Flask(__name__)

@app.route('/Testing', methods=['POST'])
def testing():
    """
    Expects a form-data key 'image' containing the uploaded image.
    Returns the width and height of the image as JSON.
    """
    uploaded_file = request.files.get('image')
    if not uploaded_file:
        return jsonify({"error": "No image found in form-data"}), 400
    
    image_bytes = uploaded_file.read()  # Read the file data into memory
    image = Image.open(io.BytesIO(image_bytes))
    
    width, height = image.size
    return jsonify({"width": width, "height": height}), 200

if __name__ == '__main__':
    # Start the Flask development server
    # Access it at http://localhost:5000/Testing
    app.run(host='0.0.0.0', port=5000, debug=True)
