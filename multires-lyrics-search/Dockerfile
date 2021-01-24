FROM jinaai/jina

# setup the workspace
COPY . /workspace
WORKDIR /workspace

RUN pip uninstall -y jina && pip install -r requirements.txt && mkdir data && mv lyrics-data.csv data/

ENV JINA_DATA_PATH='data/lyrics-data.csv'
ENV JINA_SHARDS='10'
ENV JINA_MAX_DOCS='10000'

EXPOSE 65481

RUN python app.py index

ENTRYPOINT ["python", "app.py", "search"]

LABEL author="Jina AI Dev-Team (dev-team@jina.ai)"
LABEL type="app"
LABEL kind="example"
LABEL avatar="None"
LABEL description="Jina App using recursive Document structure to search for lyrics from a songs database, the database contains 10k songs"
LABEL documentation="https://github.com/jina-ai/examples/tree/master/multires-lyrics-search"
LABEL keywords="[examples, nlp, lyrics, text]"
LABEL license="apache-2.0"
LABEL name="multireslyricssearch"
LABEL platform="linux/amd64"
LABEL update="None"
LABEL url="https://github.com/jina-ai/examples/tree/master/multires-lyrics-search"
LABEL vendor="Jina AI Limited"
LABEL version="0.0.2"
