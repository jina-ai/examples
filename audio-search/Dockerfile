FROM jinaai/jina:1.2.0

COPY . /workspace
WORKDIR /workspace

RUN apt-get update && apt-get install --no-install-recommends -y curl libsndfile1 && \
    pip install -r requirements.txt

RUN bash get_data.sh
RUN bash download_model.sh
RUN python app.py -t dryrun

ENTRYPOINT ["python", "app.py"]
