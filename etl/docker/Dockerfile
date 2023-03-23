FROM brunneis/python:3.8.6-ubuntu-20.04

WORKDIR /opt

RUN python -m venv develop

COPY requirements.txt .
RUN develop/bin/pip install -r requirements.txt

COPY develop.ini .
COPY *.py ./
COPY etl/ etl/

ENTRYPOINT ["develop/bin/python", "run.py"]
CMD ["develop.ini"]