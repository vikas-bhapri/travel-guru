FROM python:3.12-slim

WORKDIR /app

# Copy dependency manifest first for Docker layer caching
COPY requirements.txt requirements.txt

# Install service dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy service source into a package-friendly path
COPY . /app/auth_svc

ENV PYTHONPATH=/app

EXPOSE 8001

# Launch FastAPI via module path so relative imports resolve
CMD ["uvicorn", "auth_svc.main:app", "--host", "0.0.0.0", "--port", "8001"]

