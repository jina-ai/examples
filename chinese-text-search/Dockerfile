FROM pytorch/pytorch:latest

COPY . /workspace
WORKDIR /workspace

RUN pip install -r requirements.txt

RUN python -c "from transformers import DistilBertModel, DistilBertTokenizer; x='distilbert-base-cased'; DistilBertModel.from_pretrained(x); DistilBertTokenizer.from_pretrained(x)"

ENTRYPOINT ["python", "app.py", "-t", "query_restful"]

LABEL author="Alex C-G (alex.cg@jina.ai)"
LABEL type="app"
LABEL kind="example"
LABEL avatar="None"
LABEL description="Jina App for searching sentences from Wikipedia"
LABEL documentation="https://github.com/alexcg1/jina-wikipedia-sentences"
LABEL keywords="[NLP, wikipedia, text, distilbert, example]"
LABEL license="apache-2.0"
LABEL name="jina-wikipedia-sentences-30k"
LABEL platform="linux/amd64"
LABEL update="None"
LABEL url="https://github.com/alexcg1/jina-wikipedia-sentences"
LABEL vendor="Jina AI Limited"
LABEL version="0.2.8"
