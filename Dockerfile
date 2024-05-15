FROM python:3.10-slim-bookworm as release

WORKDIR /app

COPY ./requirements.txt /app
COPY ./storage_queue_process.py /app
COPY ./models.py /app

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./storage_queue_process.py"]

FROM release as dev

RUN apt-get update && \
    apt-get install -y bash curl && \
    curl -sL https://aka.ms/InstallAzureCLIDeb | bash
