from flask import Flask, request, render_template, send_from_directory
import os
import cv2
import base64
from red import detect_red_square

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def getvalue():
    if 'name' not in request.form or 'image' not in request.files:
        return "Missing required fields", 400

    name = request.form['name']
    file = request.files['image']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    width, height, annotated_image = detect_red_square(filepath, name)
    print(f"width: {width}, height: {height}")

    _, encoded_image = cv2.imencode('.jpg', annotated_image)
    annotated_image_data = base64.b64encode(encoded_image).decode('utf-8')

    if annotated_image is not None and width != 0 and height != 0:
        return render_template('drag.html', n=name, fp1=filepath,
                               annotated_image=annotated_image_data, w=width, h=height)
    else:
        
        return render_template('reddrag.html', n=name,
                               annotated_image=annotated_image_data, fp1=filepath)


@app.route('/redbox', methods=['POST'])
def redboxvalues():
    name = request.form['name']
    filepath = request.form['fp1']
    image = request.form['annotated_image']
    rw = float(request.form['drag_width'])
    rh = float(request.form['drag_height'])
    return render_template('drag.html', n=name, fp1=filepath,
                           annotated_image=image, w=rw, h=rh)


@app.route('/pass', methods=['POST'])
def pass_data():
    name = request.form['name']
    annotated_image = request.form['annotated_image']
    coords = request.form['coords']
    filepathorig = request.form['fp1']
    hw = float(request.form['drag_width'])
    hh = float(request.form['drag_height'])
    rw = float(request.form['rw'])
    rh = float(request.form['rh'])

    fp = os.path.basename(filepathorig)

    def pixels_to_feet(pixels, ppf):
        return pixels / ppf

    known_width_feet = 2.0
    ppf = rw / known_width_feet

    red_w_feet = round(pixels_to_feet(rw, ppf), 2)
    red_h_feet = round(pixels_to_feet(rh, ppf), 2)
    hwidth_feet = round(pixels_to_feet(hw, ppf), 2)
    hheight_feet = round(pixels_to_feet(hh, ppf), 2)

    print(f"ppf: {ppf}, hw: {hw}, hh: {hh}")

    return render_template('pass.html', n=name, fp=fp, final_image=annotated_image,
                           c=coords, hw=hw, hh=hh, rw=rw, rh=rh,
                           rwft=red_w_feet, rhft=red_h_feet,
                           hwft=hwidth_feet, hhft=hheight_feet)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == "__main__":
    app.run()
