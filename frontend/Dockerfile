FROM python:3.12.12-slim

WORKDIR /app

COPY ./requirements.txt ./
RUN pip install -r ./requirements.txt

COPY ./main.py ./
EXPOSE 8501

CMD ["streamlit", "run", "main.py","--server.port=8501", "--server.address=0.0.0.0"]