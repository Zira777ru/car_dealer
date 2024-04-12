# Dockerfile
FROM python:3.10

COPY requirements.txt .
RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7000

CMD ["flask", "run", "--host=0.0.0.0"]