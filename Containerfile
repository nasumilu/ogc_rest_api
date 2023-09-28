FROM python:3.11.5-bullseye

WORKDIR /opt/ogc_rest
COPY ./requirements.txt /opt/ogc_rest/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /opt/ogc_rest/requirements.txt
COPY ./app /opt/ogc_rest/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]