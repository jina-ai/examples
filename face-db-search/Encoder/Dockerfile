FROM pytorch/pytorch:latest

ADD FaceNetEncoder.py encode.yml requirements.txt install.sh ./

RUN apt-get update && apt-get install --no-install-recommends -y libglib2.0-0 libsm6 libxext6 libxrender-dev git
RUN pip install -r requirements.txt
RUN bash install.sh

RUN python -c "from facenet_pytorch import InceptionResnetV1; model = InceptionResnetV1(pretrained='vggface2').eval()"

COPY . /

ENTRYPOINT ["jina", "pod", "--uses", "encode.yml"]
