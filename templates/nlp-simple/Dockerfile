FROM pytorch/pytorch:latest

COPY . /workspace
WORKDIR /workspace

RUN pip install -r requirements.txt

RUN python -c "from transformers import DistilBertModel, DistilBertTokenizer; x='distilbert-base-cased'; DistilBertModel.from_pretrained(x); DistilBertTokenizer.from_pretrained(x)"

ENTRYPOINT ["python", "app.py", "-t", "query_restful"]

LABEL author="Your name (email)"
LABEL type="app"
LABEL kind="example"
LABEL avatar="None"
LABEL description="Your description"
LABEL documentation="http://your.url"
LABEL keywords="[NLP, text, distilbert, example]"
LABEL license="apache-2.0"
LABEL name="project name"
LABEL platform="linux/amd64"
LABEL update="None"
LABEL url="http://your.url"
LABEL vendor="Your company"
LABEL version="0.0.1"
