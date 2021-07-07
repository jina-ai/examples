FROM pytorch/pytorch:1.7.0

COPY . /workspace
WORKDIR /workspace

RUN pip install -r requirements.txt

RUN python app.py -t index

ENTRYPOINT ["python", "app.py", "-t", "query_restful"]
