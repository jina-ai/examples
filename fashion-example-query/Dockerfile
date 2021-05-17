FROM jinaai/jina:1.2.0

COPY . /workspace
WORKDIR /workspace

RUN apt-get update && pip install -r requirements.txt

RUN python app.py -t index

ENTRYPOINT ['python', 'app.py', '-t', 'query']