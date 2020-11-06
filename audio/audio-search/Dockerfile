FROM jinaai/jina:0.5.5

COPY . /workspace
WORKDIR /workspace

RUN apt-get update && apt-get install --no-install-recommends -y curl libsndfile1 && \
    pip install -r requirements.txt

RUN bash download.sh
RUN python app.py dryrun

ENTRYPOINT ["python", "app.py"]
