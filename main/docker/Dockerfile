# Base image for Python and Spark
FROM openjdk:8-jdk-alpine

# Install python, pip, and other dependencies
RUN apk add --no-cache python3 py3-pip bash && \
    ln -sf python3 /usr/bin/python

# Install PySpark
ENV PYSPARK_VERSION=3.5.2
RUN pip3 install pyspark==$PYSPARK_VERSION

# Install Kafka Python client and protobuf
RUN pip3 install confluent-kafka protobuf google-api-python-client google-auth-httplib2 google-auth-oauthlib pandas

# Set the working directory
WORKDIR /app

# Copy project files to the container
COPY . /app

# Command to run the main Python script
CMD ["python", "/app/main.py"]
