FROM jinaai/jina

# install git
RUN apt-get -y update && apt-get install -y git

# setup the workspace
COPY . /workspace
WORKDIR /workspace

# install the third-party requirements
RUN pip install -r requirements.txt

# for testing the image
RUN pip install pytest && pytest -s -vv
# import clip before
#RUN python -c 'import clip: clip.load('ViT-B/32')'

ENTRYPOINT ["jina", "pod", "--uses", "config.yml"]
