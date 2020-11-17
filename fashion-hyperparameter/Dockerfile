FROM python:3.7.9-slim

WORKDIR /

RUN apt-get update && \
    apt-get install --no-install-recommends -y git \
                                               curl

COPY tests/hyperparameter/requirements.txt /tests/hyperparameter/requirements.txt

RUN python -m pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r tests/hyperparameter/requirements.txt

RUN git clone https://github.com/jina-ai/jinad.git && \
    pip install --no-cache-dir -r jinad/requirements.txt

RUN python -c "from transformers import DistilBertModel, DistilBertTokenizer; x='distilbert-base-cased'; DistilBertModel.from_pretrained(x); DistilBertTokenizer.from_pretrained(x)"

COPY . /

ENTRYPOINT ["python", "jinad/jinad/main.py"]
