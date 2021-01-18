# annoy indexer has some more complex dependencies
FROM jinaai/jina

# setup the workspace
COPY . /workspace
WORKDIR /workspace

# uninstall jina so that jina[hub] installs everything with Faiss and Annoy

RUN apt-get update && apt-get install --no-install-recommends -y curl gcc build-essential \
    && pip uninstall -y jina \
    && pip install -r requirements.txt && pip install -r faiss-requirements.txt && pip install -r annoy-requirements.txt

ENV JINA_USES_FAISS='yaml/hub-faiss-indexer.yml'
ENV JINA_USES_ANNOY='yaml/hub-annoy-indexer.yml'

RUN ./get_siftsmall.sh && ./generate_training_data.sh

RUN python app.py -t index

ENTRYPOINT ["./entrypoint.sh", "faiss"]

LABEL author="Jina AI Dev-Team (dev-team@jina.ai)"
LABEL type="app"
LABEL kind="example"
LABEL avatar="None"
LABEL description="Jina App using Faiss and Annoy to search in SIFT_128_ANN dataset preindexed with jina"
LABEL documentation="https://github.com/jina-ai/examples/tree/master/advanced-vector-search"
LABEL keywords="[examples, faiss, annoy, ANN]"
LABEL license="apache-2.0"
LABEL name="advancedvectorsearch"
LABEL platform="linux/amd64"
LABEL update="None"
LABEL url="https://github.com/jina-ai/examples/tree/master/advanced-vector-search"
LABEL vendor="Jina AI Limited"
LABEL version="0.0.1"
