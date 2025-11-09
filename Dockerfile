FROM python:3.11-slim

RUN pip install --no-cache-dir uv

WORKDIR /app


COPY . .

RUN uv pip install --system --no-cache -r requirements.txt

EXPOSE 10000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "10000"]
