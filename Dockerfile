FROM python:3.12-alpine
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN apk add wireshark-common
RUN pip install -r requirements.txt
COPY . /app
EXPOSE 5000
CMD ["gunicorn" , "-b", "0.0.0.0:5000", "pvdmem_app:app"]
