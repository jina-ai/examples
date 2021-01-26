FROM python:3.7.6-slim

WORKDIR /

RUN apt-get update && \
    apt-get install --no-install-recommends -y git \
                                               curl

COPY tests/distributed/requirements.txt /tests/distributed/requirements.txt

RUN python -m pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r tests/distributed/requirements.txt

RUN git clone https://github.com/jina-ai/jinad.git && \
    pip install --no-cache-dir -r jinad/requirements.txt

RUN python -c "from transformers import DistilBertModel, DistilBertTokenizer; x='distilbert-base-cased'; DistilBertModel.from_pretrained(x); DistilBertTokenizer.from_pretrained(x)"

COPY . /

RUN bash get_data.sh ./data && \
    python app.py -t index && \
    rm -rf data

ENTRYPOINT ["python", "jinad/jinad/main.py"]
