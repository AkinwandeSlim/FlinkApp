"""
Load real-time models from Redis and provide prediction services
"""
import numpy as np
import redis
import pickle
import logging
import base64
from flask_cors import CORS
from flask import request, Flask, jsonify, render_template
from PIL import Image
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

# Settings
redis_params = dict(
    host='localhost',
    password='redis_password',
    port=6379,
    db=0
)
model_key = 'online_ml_model'

# Create app
app = Flask(__name__)
CORS(app)

# Model
clf = None


def load_latest_clf_model():
    """
    Load the latest model
    :return: Loaded model
    """
    # Connect to Redis
    r = redis.StrictRedis(**redis_params)

    model = None
    try:
        model = pickle.loads(r.get(model_key))
    except TypeError:
        logging.exception('No model found in Redis. Please check the key.')
    except (redis.exceptions.RedisError, TypeError, Exception) as err:
        logging.exception(f'Redis encountered an exception: {err}')

    return model


def format_svg_base64(s: str) -> np.array:
    """
    Format the base64 string of an SVG image into an 8x8 grayscale array required by the model,
    and return it flattened into a 1D array.
    :param s: SVG image base64 string
    :return: np.array
    """
    # Base64 to SVG
    with open('digit.svg', 'wb') as f:
        f.write(base64.b64decode(s))

    # SVG to PNG
    drawing = svg2rlg("digit.svg")
    renderPM.drawToFile(drawing, "digit.png", fmt="PNG")

    # Resize PNG to fit into the target size of 8x8 as it may not be a regular shape
    target_w, target_h = 8, 8  # Target width and height
    png = Image.open('digit.png')
    w, h = png.size  # Original width and height
    scale = min(target_w / w, target_h / h)  # Determine the scaling ratio to fit into 8x8
    new_w, new_h = int(w * scale), int(h * scale)  # Scaled width and height
    png = png.resize((new_w, new_h), Image.BILINEAR)  # Resize

    # Paste the resized PNG onto a blank target image and fill the surroundings with white
    new_png = Image.new('RGB', (target_w, target_h), (255, 255, 255))  # Create a blank target image
    new_png.paste(png, ((target_w - new_w) // 2, (target_h - new_h) // 2))  # Paste in the middle of the target image

    # Color inversion (from white-on-black to black-on-white as required by the model),
    # compress the values to the range of 0-16, and reshape the size to 1x64
    array = 255 - np.array(new_png.convert('L'))  # Invert the colors
    array = (array / 255) * 16  # Compress the pixel values to the range of 0-16
    array = array.reshape(1, -1)  # Reshape to 1x64

    return array


@app.route('/')
def home():
    """
    Render the 'web.html' template for the home page
    """
    return render_template('web.html')


@app.route('/predict', methods=['POST'])
def predict():
    """
    Endpoint for model prediction
    """
    global clf
    img_string = request.form['imgStr']
    # Format the SVG base64 string into the required data format for the model
    data = format_svg_base64(img_string)
    # Load the model from Redis every time
    model = load_latest_clf_model()
    clf = model or clf  # If loading from Redis fails, use the last valid loaded model
    # Model prediction
    predict_y = int(clf.predict(data)[0])
    return jsonify({'success': True, 'predict_result': predict_y}), 201


if __name__ == '__main__':
    app.run(host='52.152.233.40', port=8066, debug=True)
