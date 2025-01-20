FROM python:3.12.4
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
COPY . .
RUN pip3 install -r requirements.txt
CMD ["python3", "<file name>"]
