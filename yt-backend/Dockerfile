FROM python:3.12.12-slim

COPY ./requirements.txt ./
RUN pip install -r ./requirements.txt

COPY ./api.py ./
COPY ./models.py ./
COPY ./services.py ./
COPY ./ytapi.py ./
COPY ./charts ./charts
EXPOSE 8080

RUN useradd app
USER app

CMD ["fastapi", "run",  "--port", "8080"]