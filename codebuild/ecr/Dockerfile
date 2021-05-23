FROM python:2

RUN apt-get update && apt-get install -y git && \
    git clone https://github.com/komarserjio/notejam.git
WORKDIR /notejam/flask
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python runserver.py"]
