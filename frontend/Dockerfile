FROM python:3.12.12-slim

COPY ./requirements.txt ./
RUN pip install -r ./requirements.txt

COPY ./main.py ./
EXPOSE 8080

RUN useradd app
USER app

CMD ["python", "main.py"]

