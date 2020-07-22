FROM jinaai/jina:0.3.8-devel

ADD requirements.txt .

RUN apt-get update

COPY . /

ENTRYPOINT ["python", "app.py"]
