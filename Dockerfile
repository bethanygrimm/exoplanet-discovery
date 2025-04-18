FROM python:3.12

RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt
COPY src/ /app/src/
COPY test/ /app/src/

RUN chmod 764 /app/src/api.py /app/src/worker.py /app/src/jobs.py

ENTRYPOINT ["python"]
