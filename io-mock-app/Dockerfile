FROM jinaai/jina:devel

ADD requirements.txt .

RUN apt-get update

COPY . /

ENTRYPOINT ["python", "app.py"]
