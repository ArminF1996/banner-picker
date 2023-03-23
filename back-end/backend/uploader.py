from flask import Blueprint, render_template, request, redirect, url_for
from kafka import KafkaProducer
import random
import string
import time
from backend import configs
import logging

logger = logging.getLogger(__name__)
producer = KafkaProducer(bootstrap_servers=configs.KAFKA_BOOTSTRAP_SERVERS,
                         compression_type=configs.KAFKA_COMPRESSION_TYPE,
                         retries=configs.KAFKA_RETRIES)

bp = Blueprint("uploader", __name__)


@bp.route("/csv", methods=['GET', 'POST'])
def upload_csv():
    if request.method == 'GET':
        return render_template('upload_csv.html')
    else:
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            file_name = ''.join(random.choices(string.ascii_lowercase, k=15)) + str(int(time.time()))
            try:
                key = configs.LOGS_PATH_PREFIX + file_name + "_" + request.values['csv-type'] \
                      + "_" + request.values['quarter']
                producer.send(configs.KAFKA_TOPIC_NAME, key=str.encode(key),
                              value=file.stream.read()).get(configs.KAFKA_PRODUCE_TIMEOUT)
                with open(configs.LOGS_PATH_PREFIX + file_name, 'w') as f:
                    f.write('The import process for \"{}\" has not been done yet!'.format(file.filename))
                return redirect(url_for('uploader.import_result', log_file=file_name))
            except Exception as e:
                logger.error("Can not produce message to kafka", e)
                return redirect(request.url)


@bp.route("/csv/log/<string:log_file>", methods=['GET'])
def import_result(log_file):
    with open(configs.LOGS_PATH_PREFIX + log_file, "r") as f:
        content = f.read()
    return render_template("import_log.html", str=content)
