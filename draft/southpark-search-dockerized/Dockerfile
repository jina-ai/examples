FROM python:3.7.6-slim

WORKDIR /

RUN apt-get update && \
    apt-get install --no-install-recommends -y git \
                                               curl

COPY requirements.txt /
COPY jinad/requirements.txt /jinad_requirements.txt

RUN python -m pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r jinad_requirements.txt

RUN python -c "from transformers import DistilBertModel, DistilBertTokenizer; x='distilbert-base-cased'; DistilBertModel.from_pretrained(x); DistilBertTokenizer.from_pretrained(x)"

COPY . /

RUN bash get_data.sh ./data && \
    python app.py -t index && \
    rm -rf data

ENTRYPOINT ["python", "jinad/jinad/main.py"]
