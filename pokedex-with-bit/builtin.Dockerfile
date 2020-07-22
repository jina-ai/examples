FROM jinaai/jina:0.3.8-devel

ADD requirements.txt .

RUN apt-get update && apt-get install --no-install-recommends -y git curl && \
    pip install -r requirements.txt

COPY . /

RUN bash download.sh && python app.py index && rm -rf data

ENTRYPOINT ["python", "app.py"]
