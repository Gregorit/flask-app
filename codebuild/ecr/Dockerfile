FROM python:3.9.5-slim-buster

RUN apt-get update && apt-get install -y git && \
    git clone git@github.com:komarserjio/notejam.git
WORKDIR /flask
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python runserver.py"]
