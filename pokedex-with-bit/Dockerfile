FROM jinaai/jina

# setup the workspace
COPY . /workspace
WORKDIR /workspace

RUN apt-get update && apt-get install --no-install-recommends -y git curl libmagic1 wget tar \
    && pip install -r requirements.txt

RUN bash get_data.sh && bash download.sh && python app.py index

ENTRYPOINT ["python", "app.py", "search"]
