FROM flink:1.11.2-scala_2.11
WORKDIR /opt

# Install Python and dependencies
RUN apt-get update -y && \
    apt-get install -y python3.7 python3-pip python3.7-dev && \
    rm -rf /var/lib/apt/lists/*
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN pip3 install --upgrade pip

# Install Flink Python package
RUN pip3 install apache-flink==1.11.2

# Install required system dependencies
RUN apt-get update && \
    apt-get install -y libblas-dev liblapack-dev

# Download Flink connectors
RUN wget -P /opt/flink/lib/ https://repo.maven.apache.org/maven2/org/apache/flink/flink-sql-connector-kafka-0.11_2.11/1.11.2/flink-sql-connector-kafka-0.11_2.11-1.11.2.jar && \
    wget -P /opt/flink/lib/ https://repo.maven.apache.org/maven2/org/apache/flink/flink-json/1.11.2/flink-json-1.11.2.jar  && \
    wget -P /opt/flink/lib/ https://repo.maven.apache.org/maven2/org/apache/flink/flink-sql-connector-elasticsearch7_2.11/1.11.2/flink-sql-connector-elasticsearch7_2.11-1.11.2.jar
# Copy application files
COPY . .

# Install Python dependencies
COPY ./consumer_flink/requirements.txt .
RUN pip3 install -r requirements.txt

# Install scikit-multiflow
RUN pip3 install --upgrade scikit-multiflow
RUN pip3 install "numpy<1.24"
# Copy Flink connector and drift detector
COPY ./consumer_flink/flink-sql-connector-kafka-0.11_2.11-1.11.2.jar .

COPY ./consumer_flink/flink-sql-connector-elasticsearch7_2.11-1.11.2.jar .
COPY ./consumer_flink/beta_distribution_drift_detector .

# Copy Flink connector to current directory
RUN cp /opt/flink/lib/flink-sql-connector-kafka-0.11_2.11-1.11.2.jar .


# Copy Flink connector to current directory
RUN cp /opt/flink/lib/flink-sql-connector-elasticsearch7_2.11-1.11.2.jar .


# Set the entrypoint command
CMD python -u $SCRIPT



# FROM apache/flink:1.16.0-scala_2.12-java8
# ARG FLINK_VERSION=1.16.0

# # Install python3.7 and pyflink
# # Pyflink does not yet function with python3.9, and this image is build on
# # debian bullseye which ships with that version, so build python3.7 here.
# RUN set -ex; \
#   apt-get update && \
#   apt-get install -y build-essential libssl-dev zlib1g-dev libbz2-dev libffi-dev lzma liblzma-dev && \
#   wget https://www.python.org/ftp/python/3.7.9/Python-3.7.9.tgz && \
#   tar -xvf Python-3.7.9.tgz && \
#   cd Python-3.7.9 && \
#   ./configure --without-tests --enable-shared && \
#   make -j4 && \
#   make install && \
#   ldconfig /usr/local/lib && \
#   cd .. && rm -f Python-3.7.9.tgz && rm -rf Python-3.7.9 && \
#   ln -s /usr/local/bin/python3 /usr/local/bin/python && \
#   ln -s /usr/local/bin/pip3 /usr/local/bin/pip && \
#   apt-get clean && \
#   rm -rf /var/lib/apt/lists/* && \
#   python -m pip install --upgrade pip; \
#   pip install apache-flink==${FLINK_VERSION}; \
#   pip install kafka-python;

# # Download connector libraries
# RUN wget -P /opt/flink/lib/ https://repo.maven.apache.org/maven2/org/apache/flink/flink-json/${FLINK_VERSION}/flink-json-${FLINK_VERSION}.jar; \
#     wget -P /opt/flink/lib/ https://repo.maven.apache.org/maven2/org/apache/flink/flink-sql-connector-kafka/${FLINK_VERSION}/flink-sql-connector-kafka-${FLINK_VERSION}.jar; \
#     wget -P /opt/flink/lib/ https://repo.maven.apache.org/maven2/org/apache/flink/flink-sql-connector-elasticsearch7/${FLINK_VERSION}/flink-sql-connector-elasticsearch7-${FLINK_VERSION}.jar;


# RUN echo "taskmanager.memory.jvm-metaspace.size: 512m" >> /opt/flink/conf/flink-conf.yaml;


# COPY ./consumer_flink/requirements.txt .
# # RUN pip3  install --no-cache -r requirements.txt
# COPY . .
# # # Load flink.jar into b.py
# # RUN echo "import subprocess\nsubprocess.run(['cp', '/opt/flink/lib/flink-sql-connector-kafka-0.11_2.11-1.11.2.jar', './flink-sql-connector-kafka-0.11_2.11-1.11.2.jar'])" > load_flink.py && python load_flink.py && rm load_flink.py

# CMD python -u $SCRIPT