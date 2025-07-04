from lib2to3.pgen2.token import STRING
import os
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, EnvironmentSettings
from pyflink.table.window import Slide


env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(1)
env_settings = (
    EnvironmentSettings.new_instance().in_streaming_mode().use_blink_planner().build()
)
st_env = StreamTableEnvironment.create(env, environment_settings=env_settings)

# Define source
# Define source
st_env.execute_sql(
    f"""
    CREATE TABLE source (
        attrib1 DOUBLE,
        attrib2 DOUBLE,
        attrib3 DOUBLE,
        label INT,
        ts BIGINT,
        rowtime as TO_TIMESTAMP(FROM_UNIXTIME(ts, 'yyyy-MM-dd HH:mm:ss')),
        WATERMARK FOR rowtime AS rowtime - INTERVAL '5' SECOND
    ) WITH (
        'connector' = 'kafka-0.11',
        'topic' = 'training-data',
        'scan.startup.mode' = 'latest-offset',
        'properties.bootstrap.servers' = 'kafka:9092',
        'properties.zookeeper.connect' = 'zookeeper:2181',
        'properties.group.id' = 'Flink-Group',
        'format' = 'json'
    )
    """
)


# Define output sink Dates TIMESTAMP, Descript STRING,
st_env.execute_sql(
    """
    CREATE TABLE sink (
        attrib1 DOUBLE,
        attrib2 DOUBLE,
        attrib3 DOUBLE,
        label INT,
        window_end TIMESTAMP(3)
    ) WITH (
        'connector' = 'print',
        'print-identifier' = 'Drift data: '
    )
"""
)



st_env.from_path("source").window(
    Slide.over("60.seconds").every("2.seconds").on("rowtime").alias("w")
).group_by("attrib1,attrib2,attrib3,label,w").select("attrib1,attrib2,attrib3,label,w.end AS window_end").insert_into("sink")


st_env.execute("PyFlink job")











# import os
# import requests
# import json
# from pyflink.datastream import StreamExecutionEnvironment, TimeCharacteristic
# from pyflink.table import StreamTableEnvironment, CsvTableSink, DataTypes, EnvironmentSettings
# from pyflink.table.descriptors import Schema, Rowtime, Json, Kafka
# from pyflink.table.window import Tumble

# # Flask API endpoint to receive the window data
# FLASK_API_ENDPOINT = "http://localhost:5000/process_window_data"
# def register_transactions_source(st_env):
#     st_env.connect(Kafka()
#                    .version("universal")
#                    .topic("training-data")
#                    .start_from_latest()
#                    .property("zookeeper.connect", "zookeeper:2181")
#                    .property("bootstrap.servers", "kafka:9092")) \
#         .with_format(Json()
#         .fail_on_missing_field(True)
#         .schema(DataTypes.ROW([
#         DataTypes.FIELD("attrib1", DataTypes.DOUBLE()),
#         DataTypes.FIELD("attrib2", DataTypes.DOUBLE()),
#         DataTypes.FIELD("attrib3", DataTypes.DOUBLE()),
#         DataTypes.FIELD("label", DataTypes.INT()),
#         DataTypes.FIELD("ts", DataTypes.TIMESTAMP(3))]))) \
#         .with_schema(Schema()
#         .field("attrib1", DataTypes.DOUBLE())
#         .field("attrib2", DataTypes.DOUBLE())
#         .field("attrib3", DataTypes.DOUBLE())
#         .field("label", DataTypes.INT())
#         .field("rowtime", DataTypes.TIMESTAMP(3))
#         .rowtime(
#         Rowtime()
#             .timestamps_from_field("ts")
#             .watermarks_periodic_bounded(60000))) \
#         .in_append_mode() \
#         .create_temporary_table("source")



# def register_transactions_sink_into_api(st_env):
#     st_env \
#         .connect(Kafka()
#                  .version("universal")
#                  .topic("training-data")
#                  .start_from_earliest()
#                  .property("zookeeper.connect", "zookeeper:2181")
#                  .property("bootstrap.servers", "kafka:9092")) \
#         .with_format(Json()
#                      .fail_on_missing_field(True)
#                      .derive_schema()) \
#         .with_schema(Schema()
#                       .field("attrib1", DataTypes.DOUBLE())
#                       .field("attrib2", DataTypes.DOUBLE())
#                       .field("attrib3", DataTypes.DOUBLE())
#                       .field("label", DataTypes.INT())
#                       .field("ts", DataTypes.TIMESTAMP(3))) \
#         .in_append_mode() \
#         .create_temporary_table("sink_into_api")

#     # Send the window data to the Flask API as JSON through an HTTP request/response
#     def send_window_data_to_api(window_data):
#         headers = {'Content-type': 'application/json'}
#         data = {'window_data': window_data}
#         response = requests.post(FLASK_API_ENDPOINT, data=json.dumps(data), headers=headers)
#         response.raise_for_status()

#     # Define a function that processes the window data before sinking it
#     def process_window_data(window_data):
#         # Send the window data to the Flask API for processing
#         send_window_data_to_api(window_data)

#         # Sink the processed data to a console output
#         print("Processed window data:", window_data)

#     st_env.from_path("source") \
#         .window(Tumble.over("10.hours").on("rowtime").alias("w")) \
#         .group_by("w") \
#         .select("attrib1, attrib2, attrib3, label, w.end() AS window_end") \
#         .map(process_window_data) \
#         .insert_into("sink_into_api")


# def transactions_job():
#     s_env = StreamExecutionEnvironment.get_execution_environment()
#     s_env.set_parallelism(1)
#     s_env.set_stream_time_characteristic(TimeCharacteristic.EventTime)
#     st_env = StreamTableEnvironment \
#         .create(s_env, environment_settings=EnvironmentSettings
#                 .new_instance()
#                 .in_streaming_mode()
#                 .use_blink_planner().build())

#     register_transactions_source(st_env)
#     register_transactions_sink_into_api(st_env)

#     st_env.execute("app")

# if __name__ == '__main__':
#     transactions_job()

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    


# def register_transactions_sink_into_csv(st_env):
#     result_file = "pyflink_river/output/output_file.csv"
#     if os.path.exists(result_file):
#         os.remove(result_file)
#     st_env.register_table_sink("sink_into_csv",
#                                CsvTableSink(["prediction"],
#                                             [DataTypes.STRING(),
#                                            ],
#                                             result_file))






# def transactions_job():
#     s_env = StreamExecutionEnvironment.get_execution_environment()
#     s_env.set_parallelism(1)
#     s_env.set_stream_time_characteristic(TimeCharacteristic.EventTime)
#     st_env = StreamTableEnvironment \
#         .create(s_env, environment_settings=EnvironmentSettings
#                 .new_instance()
#                 .in_streaming_mode()
#                 .use_blink_planner().build())

#     register_transactions_source(st_env)
#     register_transactions_sink_into_csv(st_env)

#     st_env.from_path("source") \
#         .window(Tumble.over("10.hours").on("rowtime").alias("w")) \
#         .group_by("w").select("attrib1, attrib2, attrib3, label, w.end AS window_end") \
#         .insert_into("sink_into_csv")

#     st_env.execute("app")


# if __name__ == '__main__':
#     transactions_job()
















# @udf(input_types=[DataTypes.STRING()], result_type=DataTypes.ROW(
#     [DataTypes.FLOAT(), DataTypes.FLOAT(), DataTypes.FLOAT(), DataTypes.INT(), DataTypes.BIGINT()]))
# def transform_record(record):
#     data = json.loads(record)
#     return data['attrib1'], data['attrib2'], data['attrib3'], data['label'], data['ts']

# @udf(input_types=[DataTypes.ARRAY(DataTypes.ROW(
#     [DataTypes.FLOAT(), DataTypes.FLOAT(), DataTypes.FLOAT(), DataTypes.INT(), DataTypes.BIGINT()]))],
#      result_type=DataTypes.STRING())
# def evaluate_window(records):
#     data = {'records': [r.asdict() for r in records]}
#     response = requests.post('http://102.37.154.172:5000/predict', json=data)
#     return response.text

# def run_consumer(output_path, kafka_bootstrap_servers, kafka_topic):
#     env = StreamExecutionEnvironment.get_execution_environment()
#     env.set_parallelism(1)
#     env_settings = (
#         EnvironmentSettings.new_instance().in_streaming_mode().use_blink_planner().build()
#     )
#     t_env = StreamTableEnvironment.create(env, environment_settings=env_settings)

#     # Define source
#     t_env.execute_sql(
#         f"""
#         CREATE TABLE source (
#             attrib1 DOUBLE,
#             attrib2 DOUBLE,
#             attrib3 DOUBLE,
#             label INT,
#             ts BIGINT,
#             rowtime as TO_TIMESTAMP(FROM_UNIXTIME(ts, 'yyyy-MM-dd HH:mm:ss')),
#             WATERMARK FOR rowtime AS rowtime - INTERVAL '5' SECOND
#         ) WITH (
#             'connector' = 'kafka-0.11',
#             'topic' = '{kafka_topic}',
#             'scan.startup.mode' = 'latest-offset',
#             'properties.bootstrap.servers' = '{kafka_bootstrap_servers}',
#             'properties.zookeeper.connect' = '{kafka_bootstrap_servers}',
#             'properties.group.id' = 'flink-group',
#             'format' = 'json'
#         )
#         """
#     )

#     transformed_stream = t_env.from_path('source').select(transform_record('value'))


#     sliding_window = transformed_stream.window(Tumble.over('30.seconds').every('10.seconds').on('ts').alias('w'))

#     result_stream = sliding_window.group_by().select(evaluate_window(sliding_window))

    
    
#     # Define sink
#     t_env.execute_sql(
#         f"""
#         CREATE TABLE sink (
#             prediction STRING
#         ) WITH (
#             'connector' = 'filesystem',
#             'path' = '{output_path}',
#             'format' = 'csv',
#             'sink.rolling-policy.file-size' = '100MB',
#             'sink.rolling-policy.rollover-interval' = '1h',
#             'sink.rolling-policy.check-interval' = '10s'
#         )
#         """
#     )

#     # Write output to file
#     result_stream.add_sink(
#         FlinkFileSink()
#         .with_bucket_assigner(DateTimeBucketAssigner())
#         .with_output_file_config(OutputFileConfig.builder().with_part_prefix('part').build())
#         .with_encoder(SimpleStringEncoder())
#         .build(output_path)
#     )

#     env.execute()


# if __name__ == '__main__':
#     logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")

#     parser = argparse.ArgumentParser()
#     parser.add_argument('--output', dest='output', required=True, help='Output file to write fraud results to')
# #     parser.add_argument('--bootstrap-servers', dest='bootstrap_servers', required=True, help='Kafka bootstrap servers')
# #     parser.add_argument('--topic', dest='topic', required=True, help='Kafka topic to consume from')

#     args = parser.parse_args()

#     bootstrap_servers='kafka:9092'
#     topic='training-data'
# #     run_consumer(args.output, args.bootstrap_servers, args.topic)
#     run_consumer(args.output, bootstrap_servers, topic)
