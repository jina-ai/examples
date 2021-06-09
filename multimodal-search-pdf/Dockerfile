FROM jinaai/jina:1.2.0

COPY . /workspace
WORKDIR /workspace

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "app.py", "-t", "query"]

LABEL author="Jina AI Dev-Team (dev-team@jina.ai)"
LABEL type="app"
LABEL kind="example"
LABEL avatar="None"
LABEL description="Jina App on searching text, image, and partial PDF in PDF files"
LABEL keywords="[examples, PDF]"
LABEL license="apache-2.0"
LABEL name="multimodal-search-PDF"
LABEL platform="linux/amd64"
LABEL vendor="Jina AI Limited"
LABEL version="0.0.2"
