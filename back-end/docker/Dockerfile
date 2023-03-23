FROM brunneis/python:3.8.6-ubuntu-20.04

WORKDIR /opt/backend

RUN python -m venv develop-env
RUN develop-env/bin/pip install pip --upgrade

COPY etl/etl/ ../etl/etl/
COPY etl/setup.py ../etl/

COPY back-end/requirements.txt .
RUN develop-env/bin/pip install -r requirements.txt

COPY back-end/static/ static/
COPY back-end/templates/ templates/

COPY back-end/develop.ini .
COPY back-end/*.py ./
COPY back-end/backend/ backend/

ENTRYPOINT ["develop-env/bin/python", "run.py"]
CMD ["develop.ini"]