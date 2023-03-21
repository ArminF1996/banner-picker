from flask import Blueprint, render_template, request, flash, redirect, url_for
import random
import string
import time

bp = Blueprint("uploader", __name__)


@bp.route("/csv", methods=['GET', 'POST'])
def upload_csv():
    if request.method == 'GET':
        return render_template('upload_csv.html')
    else:
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            prefix = "/tmp/"
            file_name = ''.join(random.choices(string.ascii_lowercase, k=15)) + str(int(time.time()))
            #TODO send uploaded file to kafka
            #file.stream.read(), request.values['csv-type'], request.values['quarter'], logfile_complete_path
            with open(prefix + file_name, 'w') as f:
                f.write('This process has not yet started!')
            return redirect(url_for('uploader.import_result', log_file=file_name))


@bp.route("/csv/log/<string:log_file>", methods=['GET'])
def import_result(log_file):
    prefix = "/tmp/"
    with open(prefix + log_file, "r") as f:
        content = f.read()
    return render_template("import_log.html", str=content)
