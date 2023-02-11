FROM python:3.9-slim


WORKDIR /var/lib

COPY /requirements.txt .
RUN pip install -r requirements.txt


WORKDIR /var/projects/mydp/src

COPY /src .


CMD ["python", "app.py"]