FROM python:3.10-slim-bookworm as release

ARG package_name=storage_queue
ARG package_name_shared=shared

WORKDIR /app

COPY ./$package_name_shared/ /app/$package_name_shared

RUN pip install ./$package_name_shared

COPY ./$package_name/ /app/$package_name

RUN pip install ./$package_name

COPY ./$package_name/src/$package_name/storage_queue_process.py /app

CMD ["python", "storage_queue_process.py"]

FROM release as dev

RUN apt-get update && \
    apt-get install -y bash curl && \
    curl -sL https://aka.ms/InstallAzureCLIDeb | bash
