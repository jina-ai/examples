FROM jinaai/jina

COPY . /workspace
WORKDIR /workspace

install the third-party requirements
RUN pip install -r requirements.txt

for testing the imag& pytest

ENTRYPOINT ["jina", "pod", "--uses", "config.yml"]