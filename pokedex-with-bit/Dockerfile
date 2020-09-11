FROM jinaai/jina:0.5.4

ADD requirements.txt .

RUN echo "Acquire::http::Proxy \"http://192.168.50.64:7890\";" > /etc/apt/apt.conf
RUN apt-get update && apt-get install --no-install-recommends -y git curl libmagic1 && \
    pip install -r requirements.txt

COPY . /

RUN bash download.sh && python app.py dryrun

ENTRYPOINT ["python", "app.py"]
