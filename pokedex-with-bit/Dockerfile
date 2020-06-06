FROM jinaai/jina:devel

ADD requirements.txt .

RUN apt-get update && apt-get install --no-install-recommends -y git curl && \
    pip install -r requirements.txt

COPY . /

RUN bash download.sh && python app.py dryrun

ENTRYPOINT ["python", "app.py"]
