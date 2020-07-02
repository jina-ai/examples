FROM pytorch/pytorch:latest

WORKDIR /

ENV DATA_DIR /

COPY . /

RUN python -m pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements_docker.txt

RUN python -c "from transformers import DistilBertModel, DistilBertTokenizer; x='distilbert-base-cased'; DistilBertModel.from_pretrained(x); DistilBertTokenizer.from_pretrained(x)"

RUN python prepare_data.py && python app.py -t index -n 10000

RUN rm -f /urban-dictionary-words-dataset.zip /jina/urbandict/urbandict-word-defs.csv

CMD ["python", "app.py","-t","query"]
