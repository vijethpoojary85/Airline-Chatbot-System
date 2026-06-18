FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 10000

CMD ["adk", "web", "--host", "0.0.0.0", "--port", "10000"]