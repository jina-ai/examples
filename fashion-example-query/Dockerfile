FROM jinaai/jina:0.5.5

COPY . /workspace
WORKDIR /workspace

RUN apt-get update && pip install -r requirements.txt

RUN python app.py index

ENTRYPOINT ["python", "app.py", "query"]