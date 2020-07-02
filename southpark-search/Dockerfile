FROM pytorch/pytorch:latest

WORKDIR /

RUN apt-get update && \
    apt-get install --no-install-recommends -y git \
                                               curl

RUN python -m pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir transformers \
                               jina[http]

RUN python -c "from transformers import DistilBertModel, DistilBertTokenizer; x='distilbert-base-cased'; DistilBertModel.from_pretrained(x); DistilBertTokenizer.from_pretrained(x)"

COPY . /

RUN bash get_data.sh ./data && \
    python app.restful.py dryrun

ENTRYPOINT ["python", "app.restful.py"]
