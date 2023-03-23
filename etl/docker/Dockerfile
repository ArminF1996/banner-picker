FROM brunneis/python:3.8.6-ubuntu-20.04

WORKDIR /opt/etl

RUN python -m venv develop-env
RUN develop-env/bin/pip install pip --upgrade
COPY setup.py .
RUN develop-env/bin/pip install .

COPY *.py ./
COPY develop.ini .
COPY etl/ etl/

ENTRYPOINT ["develop-env/bin/python", "run.py"]
CMD ["develop.ini"]