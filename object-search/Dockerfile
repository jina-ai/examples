FROM jinaai/jina:1.0.8

ADD requirements.txt .

RUN apt-get update && apt-get install --no-install-recommends -y git curl libmagic1 \ 
    && pip install -r requirements.txt

COPY . /

ENTRYPOINT ["python", "app.py"]
