FROM python:3.12.1-slim-bookworm
RUN useradd --create-home --shell /bin/sh appuser
WORKDIR /home/appuser/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
USER appuser
COPY . .
CMD [ "bash", "./run_docker.sh" ]
