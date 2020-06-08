FROM jinaai/jina:devel

ADD requirements.txt .



RUN apt-get update && apt-get install --no-install-recommends -y git curl && \
    pip install -r requirements.txt

COPY . /


RUN curl https://storage.googleapis.com/tensorflow/keras-applications/mobilenet_v2/mobilenet_v2_weights_tf_dim_ordering_tf_kernels_1.0_96_no_top.h5 --silent

RUN python app.py dryrun

ENTRYPOINT ["python", "app.py"]
