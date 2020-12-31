FROM jinaai/jina:0.8.2

COPY . /workspace
WORKDIR /workspace

RUN apt-get update && pip install -r requirements.txt

RUN python app.py dryrun

ENTRYPOINT ["python", "app.py"]
