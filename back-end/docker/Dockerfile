FROM brunneis/python:3.8.6-ubuntu-20.04

WORKDIR /opt

RUN python -m venv develop-env
RUN develop-env/bin/pip install pip --upgrade

COPY requirements.txt .
RUN develop-env/bin/pip install -r requirements.txt

COPY static/ static/
COPY templates/ templates/

COPY develop.ini .
COPY *.py ./
COPY backend/ backend/

ENTRYPOINT ["develop-env/bin/python", "run.py"]
CMD ["develop.ini"]