FROM python:3.10

WORKDIR /app

COPY . .
RUN pip install --upgrade pip  && \
    pip install --no-cache-dir -r req.txt

EXPOSE 8000
CMD ["python3", "main.py"]