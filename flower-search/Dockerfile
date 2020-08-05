FROM pytorch/pytorch:latest

WORKDIR /

ENV ENCODER yaml/encode.yml
ENV TMP_WORKSPACE /workspace

RUN apt-get update && \
    apt-get install --no-install-recommends -y curl libmagic-dev

RUN python -m pip install --no-cache-dir click \
                               jina[http]==0.4.1 \
                               jina[devel]==0.4.1 \
                               pillow

RUN python -c "import torchvision.models as models; models.mobilenet_v2(pretrained=True)"

COPY . /

RUN bash get_data.sh && \
    python app.py -t index -n 1000 && \
    rm -rf /tmp/jina/flower

CMD ["python", "app.py","-t","query"]