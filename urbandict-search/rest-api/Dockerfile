FROM pytorch/pytorch:latest

WORKDIR /

RUN python -m pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir transformers jina[scipy] jina[http] -i https://pypi.tuna.tsinghua.edu.cn/simple/

COPY . /



RUN python -c "from transformers import DistilBertModel, DistilBertTokenizer; x='distilbert-base-cased'; DistilBertModel.from_pretrained(x); DistilBertTokenizer.from_pretrained(x)"

RUN python prepare_data.py

RUN python app.py index && rm -rf /data

ENTRYPOINT ["python", "app.py", "search"]
