FROM pytorch/pytorch:latest

ADD requirements.txt .

RUN apt-get update && apt-get install --no-install-recommends -y curl

RUN python -m pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir transformers jina[http]

RUN python -c "import torchvision.models as models; models.mobilenet_v2(pretrained=True)"

COPY . /

RUN bash get_data.sh && python app.py index && rm -rf /data
#RUN bash get_data_local.sh /17flowers.tgz && python app.py index && rm -rf /data

ENTRYPOINT ["python", "app.py", "search"]