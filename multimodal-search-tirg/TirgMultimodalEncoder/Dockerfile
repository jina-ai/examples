FROM jinaai/jina

RUN pip install torchvision pytest

# setup the workspace
COPY . /workspace
WORKDIR /workspace

# install the third-party requirements
# RUN pip install -r requirements.txt

# for testing the image
# RUN pip install pytest
RUN pytest -s -vv tests

ENTRYPOINT ["jina", "pod", "--uses", "config.yml"]