FROM jinaai/jina

# setup the workspace
COPY . /workspace
WORKDIR /workspace

# install the third-party requirements
RUN pip install -r requirements.txt

# for testing the image
RUN pip install pytest && pytest -s -vv

ENTRYPOINT ["jina", "pod", "--uses", "config.yml"]
