FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir -e ".[dev,analytics]"

COPY . .

CMD ["python", "main.py"]
