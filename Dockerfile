FROM python:3.11-slim


ARG HTTP_PROXY=http://172.24.17.18:3228
ARG HTTPS_PROXY=http://172.24.17.18:3228
ARG NO_PROXY=localhost,127.0.0.1,172.24.19.0/24,.kshfdev.net

ENV http_proxy=${HTTP_PROXY} \
    https_proxy=${HTTPS_PROXY} \
    no_proxy=${NO_PROXY}


WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt


COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]