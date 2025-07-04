FROM apache/flink:1.16.0-scala_2.12-java8
ARG FLINK_VERSION=1.16.0
WORKDIR /

RUN set -ex; \
  apt-get update && \
  apt-get install -y build-essential libssl-dev zlib1g-dev libbz2-dev libffi-dev lzma liblzma-dev && \
  wget https://www.python.org/ftp/python/3.7.9/Python-3.7.9.tgz && \
  tar -xvf Python-3.7.9.tgz && \
  cd Python-3.7.9 && \
  ./configure --without-tests --enable-shared && \
  make -j4 && \
  make install && \
  ldconfig /usr/local/lib && \
  cd .. && rm -f Python-3.7.9.tgz && rm -rf Python-3.7.9 && \
  ln -s /usr/local/bin/python3 /usr/local/bin/python && \
  ln -s /usr/local/bin/pip3 /usr/local/bin/pip && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* && \
  python -m pip install --upgrade pip; \
  pip install apache-flink==${FLINK_VERSION}; \
  pip install kafka-python;

# Download connector libraries
RUN mkdir -p /opt/flink
RUN wget -P /opt/flink/lib/ https://repo.maven.apache.org/maven2/org/apache/flink/flink-json/${FLINK_VERSION}/flink-json-${FLINK_VERSION}.jar; \
    wget -P /opt/flink/lib/ https://repo.maven.apache.org/maven2/org/apache/flink/flink-sql-connector-kafka/${FLINK_VERSION}/flink-sql-connector-kafka-${FLINK_VERSION}.jar; \
    wget -P /opt/flink/lib/ https://repo.maven.apache.org/maven2/org/apache/flink/flink-sql-connector-elasticsearch7/${FLINK_VERSION}/flink-sql-connector-elasticsearch7-${FLINK_VERSION}.jar;

RUN echo "taskmanager.memory.jvm-metaspace.size: 512m" >> /opt/flink/conf/flink-conf.yaml;

RUN pip3 install numpy
#RUN pip3 install lightgb


COPY requirements.txt  /requirements.txt
# COPY lgb_model.pkl  /lgb_model.pkl
# COPY flink_consumer.py /app/flink_consumer.py
COPY fraud_river_ml.py /fraud_river_ml.py
# COPY ./pyflink_riverml/drift_detectorml.py /drift_detectorml.py
COPY beta_distribution_drift_detector /beta_distribution_drift_detector














RUN python -m pip install --upgrade pip
COPY . .
RUN pip3 --no-cache-dir --verbose install -r /requirements.txt



# Set the environment variable for Flask
ENV FLASK_APP=/fraud_river_ml.py

# Expose the port that Flask is running on
EXPOSE 5000

# COPY . /app



# Run the command to start Flask
CMD ["flask", "run", "--host=0.0.0.0"]














# FROM flink:1.11.2-scala_2.11
# WORKDIR /
# RUN apt-get update -y && \
#     apt-get install -y python3.7 python3-pip python3.7-dev && rm -rf /var/lib/apt/lists/*
# RUN ln -s /usr/bin/python3 /usr/bin/python
# RUN pip3 install apache-flink==1.11.2
# RUN wget -P /opt/flink/lib/ https://repo.maven.apache.org/maven2/org/apache/flink/flink-sql-connector-kafka-0.11_2.11/1.11.2/flink-sql-connector-kafka-0.11_2.11-1.11.2.jar;
# RUN wget -P /opt/flink/lib/ https://repo.maven.apache.org/maven2/org/apache/flink/flink-json/1.11.2/flink-json-1.11.2.jar;
# COPY . .
























# ARG FLINK_VERSION=1.14.3
# FROM flink:1.14.3-scala_2.11

# RUN set -ex; \
#   apt-get update; \
#   apt-get -y install python3.9; \
#   apt-get -y install python3.9-dev; \
#   apt-get -y install python3.9-distutils; \
#   wget -O /tmp/get-pip.py https://bootstrap.pypa.io/get-pip.py; \
#   python3.9 /tmp/get-pip.py; \
#   ln -s /usr/bin/python3.9 /usr/bin/python; \
#   ln -s /usr/bin/pip3 /usr/bin/pip


# # Install Flink dependencies
# RUN apt-get update && \
#     apt-get install -y openjdk-11-jdk && \
#     rm -rf /var/lib/apt/lists/* && \
#     rm -rf /var/cache/apt/archives/*

# # Install system dependencies
# RUN apt-get update && apt-get install -y wget



# RUN set -ex; \
#   apt-get update; \
#   python -m pip install --upgrade pip; \
#   pip install apache-flink;

# RUN wget -P /opt/flink/lib/ https://repo.maven.apache.org/maven2/org/apache/flink/flink-json/${FLINK_VERSION}/flink-json-${FLINK_VERSION}.jar; \
#     wget -P /opt/flink/lib/ https://repo.maven.apache.org/maven2/org/apache/flink/flink-csv/${FLINK_VERSION}/flink-csv-${FLINK_VERSION}.jar; \
#     wget -P /opt/flink/lib/ https://repo.maven.apache.org/maven2/org/apache/flink/flink-sql-connector-elasticsearch6_2.11/${FLINK_VERSION}/flink-sql-connector-elasticsearch6_2.11-${FLINK_VERSION}.jar; \
#     wget -P /opt/flink/lib/ https://repo.maven.apache.org/maven2/org/apache/flink/flink-sql-connector-kafka_2.11/${FLINK_VERSION}/flink-sql-connector-kafka_2.11-${FLINK_VERSION}.jar; \



# COPY pyflink_riverml/requirements.txt /requirements.txt
# RUN pip install --no-cache-dir --verbose -r /requirements.txt

# # Copy the PyFlink job files
# COPY pyflink_riverml/drift_consumer.py /drift_consumer.py
# COPY pyflink_riverml/drift_detectorml.py /drift_detectorml.py
# COPY pyflink_riverml/beta_distribution_drift_detector /beta_distribution_drift_detector

# # Set the environment variable for Flask
# ENV FLASK_APP=/drift_detectorml.py

# # Expose the port that Flask is running on
# EXPOSE 5000

# # Start Flask
# CMD ["flask", "run", "--host=0.0.0.0"]
































# FROM flink:1.14.3-scala_2.12

# # Install Python and dependencies
# RUN apt-get update && \
#     apt-get install -y python3.9 python3-pip && \
#     rm -rf /var/lib/apt/lists/*

# # Install Flink connectors and libraries
# # RUN flink-cdc.sh kafka --version 2.12-2.8.1
# RUN /usr/local/flink/bin/flink-sql-client.sh embedded -DenablePython=true && \
#     /usr/local/flink/bin/flink-sql-client.sh embedded -DenablePython=true -e "CREATE TABLE kafka_input (message STRING) WITH ('connector'='kafka', 'topic'='training-data', 'properties.bootstrap.servers'='kafka:9092', 'properties.group.id'='Flink-Group', 'format'='json', 'json.fail-on-missing-field'='false', 'json.ignore-parse-errors'='true')"

# RUN pip3 install apache-flink==1.14.3

# # Install additional dependencies
# RUN apt-get update && \
#     apt-get install -y openjdk-11-jdk libgomp1 && \
#     rm -rf /var/lib/apt/lists/*

# RUN pip3 install numpy

# # Copy the PyFlink job files
# COPY pyflink_riverml/requirements.txt /requirements.txt
# COPY pyflink_riverml/drift_detectorml.py /drift_detectorml.py
# COPY pyflink_riverml/beta_distribution_drift_detector /beta_distribution_drift_detector

# # Install Python dependencies
# RUN pip3 --no-cache-dir --verbose install -r /requirements.txt

# # Set the environment variable for Flask
# ENV FLASK_APP=/drift_detectorml.py

# # Expose the port that Flask is running on
# EXPOSE 5000

# # Start Flask
# CMD ["flask", "run", "--host=0.0.0.0"]




























# FROM flink:1.11.2-scala_2.11
# # set the working directory
# WORKDIR /
# RUN apt-get update -y && \
#     apt-get install -y python3.7 python3-pip python3.7-dev && rm -rf /var/lib/apt/lists/*
# RUN ln -s /usr/bin/python3 /usr/bin/python

# RUN wget -P /opt/flink/lib/ https://repo.maven.apache.org/maven2/org/apache/flink/flink-sql-connector-kafka-0.11_2.11/1.11.2/flink-sql-connector-kafka-0.11_2.11-1.11.2.jar;
# RUN wget -P /opt/flink/lib/ https://repo.maven.apache.org/maven2/org/apache/flink/flink-json/1.11.2/flink-json-1.11.2.jar;
# RUN pip3 install apache-flink==1.11.2
# # Install OpenJDK 11
# RUN apt-get update && \
#     apt-get install -y openjdk-11-jdk && \
#     rm -rf /var/lib/apt/lists/* && \
#     rm -rf /var/cache/apt/archives/*

# # Set environment variables
# ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64/
# ENV PATH=$PATH:$JAVA_HOME/bin

# RUN apt-get update && \
#     apt-get install -y libgomp1


# RUN pip3 install numpy
# #RUN pip3 install lightgbm


# # Copy the PyFlink job files
# COPY . .

# # COPY ./pyflink_riverml/requirements.txt  /requirements.txt
# # # COPY flink_consumer.py /app/flink_consumer.py
# # COPY ./pyflink_riverml/fraud_river_ml.py /fraud_river_ml.py
# # # COPY ./pyflink_riverml/drift_detectorml.py /drift_detectorml.py
# # COPY ./pyflink_riverml/beta_distribution_drift_detector /beta_distribution_drift_detector


# RUN python -m pip install --upgrade pip
# # COPY . .
# RUN pip3 --no-cache-dir --verbose install -r /requirements.txt



# # Set the environment variable for Flask
# ENV FLASK_APP=/fraud_river_ml.py

# # Expose the port that Flask is running on
# EXPOSE 5000

# # COPY . /app



# # Run the command to start Flask
# CMD ["flask", "run", "--host=0.0.0.0"]