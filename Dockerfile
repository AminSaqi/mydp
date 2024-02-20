FROM python:3.10-slim


WORKDIR /var/lib

COPY /requirements.txt .
RUN pip install -r requirements.txt


WORKDIR /var/projects/mydp/src

COPY /src .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "warning"]