FROM jinaai/jina:0.3.8-devel

ADD requirements.txt .

RUN apt-get update && pip install -r requirements.txt

COPY . /

RUN python app.py dryrun

ENTRYPOINT ["python", "app.py"]
