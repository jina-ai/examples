FROM jinaai/jina:0.4.1-devel

ADD requirements.txt .

RUN apt-get update

COPY . /

ENTRYPOINT ["python", "app.py"]
