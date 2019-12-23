import os
import uuid
from kface import Kface
from flask import Flask, jsonify, request, redirect, render_template
from werkzeug.utils import secure_filename
import PIL
from PIL import Image, ImageDraw
from cachetools import cached, TTLCache

kf = Kface()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__, static_url_path='/match', static_folder='./match', )
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', './uploads')
app.config['MATCH_FOLDER'] = os.getenv('MATCH_FOLDER', './match')
cache = TTLCache(maxsize=100, ttl=60)


@cached(cache)
def read_data():
    kf.populeate_from_redis()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_resize_image(file, rotate=True):
    pid = uuid.uuid4().hex
    mywidth = 1024
    img = Image.open(file)
    if rotate:
        img = autorotate(img)
    wpercent = (mywidth / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    img = img.resize((mywidth, hsize), PIL.Image.ANTIALIAS)
    filename = "{}.jpg".format(pid)
    img.save(os.path.join(app.config['MATCH_FOLDER'], filename))
    return filename

def mark_faces_locations(faces):
    filename = os.path.join(app.config['MATCH_FOLDER'], faces['upload_file'])
    img = Image.open(filename)
    draw = ImageDraw.Draw(img)
    n = 0
    for location in faces['locations']:
        y = location[0];
        xx = location[1];
        yy = location[2];
        x = location[3];
        draw.rectangle([x, y, xx, yy])
        draw.text((x, y),faces['names'][n], (255, 0, 0))
        n = n + 1
    img.save(filename)

def autorotate(image):
    try:
        exif = image._getexif()
    except AttributeError as e:
        return image
    (width, height) = image.size
    # print "\n===Width x Heigh: %s x %s" % (width, height)
    if not exif:
        return image
        # TODO figure out more rotate checks
        if width > height:
            image = image.rotate(90)
            return image
    else:

        orientation_key = 274 # cf ExifTags
        if orientation_key in exif:
            orientation = exif[orientation_key]
            rotate_values = {
                3: 180,
                6: 270,
                8: 90
            }
            if orientation in rotate_values:
                # Rotate and save the picture
                image = image.rotate(rotate_values[orientation])
                return image
        else:
            return image
            # TODO figure out more rotate checks
            if width > height:
                image = image.rotate(90)
                return image
    return image

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = save_resize_image(file)
            return jsonify(detect_faces_in_image(filename))

    return render_template("index.html")

@app.route('/who', methods=['POST'])
def who_is_it():
    read_data()
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = save_resize_image(file)
            return jsonify(detect_faces_in_image(filename))

@app.route('/who2', methods=['POST'])
def who_is_it2():
    read_data()
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = save_resize_image(file, rotate=False)
            return jsonify(detect_faces_in_image(filename))

@app.route('/who3', methods=['POST'])
def who_is_it3():
    read_data()
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = save_resize_image(file, rotate=False)
            faces = detect_faces_in_image(filename)
            mark_faces_locations(faces)
            return faces

@app.route('/upload', methods=['GET', 'POST'])
def upload_face_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        name = request.form.get('name', None)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if not name:
            name = file.filename

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            kf.get_or_set(filename, app.config['UPLOAD_FOLDER'], name)
            return jsonify({"name": filename, "response": "added"})

    return '''
    <!doctype html>
    <title>Upload a picture for me to know?</title>
    <h1>Upload a picture with face, the file name will be the known face!</h1>
    <form method="POST" enctype="multipart/form-data">
      <input type="file" name="file">
      <input type="submit" value="Upload">
    </form>
    '''

@app.route('/list_name', methods=['GET'])
def list_names():
    return jsonify(kf.return_names())

def detect_faces_in_image(file):
    result = kf.match_face(file, app.config['MATCH_FOLDER'])
    return result



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True, threaded=False)

