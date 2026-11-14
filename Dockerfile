FROM python:3.13-slim

WORKDIR /code

# Install dependencies first so Docker can cache this layer
# and skip it when only the source code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY evals ./evals
COPY data ./data

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
