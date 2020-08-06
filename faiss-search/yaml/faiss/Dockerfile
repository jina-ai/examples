FROM conda/miniconda3-centos7:latest

WORKDIR /

RUN conda update -n base conda && \
    conda install -y -c pytorch faiss-cpu

COPY faiss.yml .

RUN conda install pip
RUN pip install jina==0.4.1 \
                uvloop

ENTRYPOINT ["jina", "pod", "--uses", "faiss.yml"]