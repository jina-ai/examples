FROM jinaai/jina

RUN pip install torchvision pytest
# RUN pip install jina -U
# setup the workspace
COPY . /workspace
WORKDIR /workspace
# RUN apt-get update -y \
#     && apt-get install wget \
#     && wget https://storage.googleapis.com/image_retrieval_css/pretrained_models/checkpoint_fashion200k.pth \
#     && wget https://github.com/bhavsarpratik/tirg/raw/master/texts.pkl

# install the third-party requirements
# RUN pip install -r requirements.txt

# for testing the image
# RUN pip install pytest
RUN pytest -s -vv tests

ENTRYPOINT ["jina", "pod", "--uses", "config.yml"]