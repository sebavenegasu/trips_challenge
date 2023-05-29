FROM python:3.8.6

WORKDIR /app

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

COPY . .

RUN echo $PATH
RUN pip freeze

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
