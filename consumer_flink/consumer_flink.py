from typing import Tuple
from pyflink.table import DataTypes, Row
from pyflink.table.types import RowType
from pyflink.table.udf import udf
import os
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, EnvironmentSettings, DataTypes
from pyflink.table.window import Slide
from pyflink.table.window import Tumble
from pyflink.table.udf import ScalarFunction , TableFunction, udf
from pyflink.table import DataTypes
from datetime import datetime, timedelta
import time
import json
import requests
from pyflink.table.types import RowType, DataTypes
from beta_distribution_drift_detector.bdddc import BDDDC
import numpy as np
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import lightgbm as lgb
from sklearn.metrics import accuracy_score
import sklearn.metrics as metrics
from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
from river import metrics
from river import stream



env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(1)
env_settings = ( EnvironmentSettings.new_instance().in_streaming_mode().use_blink_planner().build())
st_env = StreamTableEnvironment.create(env, environment_settings=env_settings)
st_env.get_config().get_configuration().set_boolean("python.fn-execution.memory.managed", True)
dir_kafka_sql_connect = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                     'flink-sql-connector-kafka_2.11-1.11.2.jar')

dir_kafka_elasticsearch_connect=os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                     'flink-sql-connector-elasticsearch7_2.11-1.11.2.jar')
st_env.get_config().get_configuration().set_string("pipeline.jars", 'file://' + dir_kafka_sql_connect)
st_env.get_config().get_configuration().set_string("pipeline1.jars", 'file://' + dir_kafka_elasticsearch_connect)
dir_requirements  =  '/requirements. txt'
dir_cache  = '/cached_dir/'
if  os.path.exists ( dir_requirements ) :
    if  os . path . exists ( dir_cache ):
        st_env.set_python_requirements ( dir_requirements , dir_cache ) 
    else :
        st_env.set_python_requirements ( dir_requirements)


class Model(ScalarFunction):
    def __init__(self, a, b, win1, win2, q):
        self.a = abs(float(a))
        self.b = abs(float(b))
        self.win1 = int(win1)
        self.win2 = int(win2)
        self.q = abs(float(q))
        self.i = 1
        self.t = []
        self.m = []
        self.m2 = []
        self.yt = []
        self.yp = []
        self.x_new = []
        self.y_new = []
        self.dr = [0]
        self.d = 0
        self.f = 0
        self.tt = 0
        self.th = 0
        self.xt = []
        self.win1_base = 200
        self.win2_base = 1000
        self.win1_max = 1000
        self.win2_max = 5000
        self.metric = None
        self.metric2 = None
        self.classifier = None
        self.BD3 = None
        # load the model
        self.model_name = 'online_ml_model'
        self.model_name = 'online_lgb_ml_model'
        self.redis_params = dict(host='localhost', password='redis_password', port=6379, db=0)
       # self.clf = self.load_model()
        
#        self.classifier=self.load_lgbm_model()
        self.interval_dump_seconds = 30  # Model save interval is 30 seconds
        self.last_dump_time = datetime.now() # last time the model was saved

        # domain of y
        self.classes = list(range(2))
        self.metric_counter = None # The number of all samples from the beginning of the job to the present
        self.metric_predict_acc = 0 # model prediction accuracy (evaluated with the past 10 samples)
        self.metric_distribution_y = None # distribution of label y
        self.metric_total_60_sec = None # number of samples trained in the past 10 seconds
        self.metric_right_60_sec = None # The number of correctly predicted samples in the past 10 seconds
        
        self.drift_check_interval =timedelta(seconds=60)
        self.BD3=BDDDC(warn_level=self.a, drift_level=self.b)
         # ... existing code ...
        self.accuracy = 0.0
        self.precisions = [] 
        self.recalls = []
        self.f1s=[]
        self.metric = metrics.Accuracy()
        self.classifier=self.load_lgbm_model()
  
        self.start_time_total = time.time()
        self.start_time_window = self.start_time_total

    def open(self, function_context):
        """
        Access the indicator system and register the indicators so that you can view the operation of the algorithm in real time on the webui (localhost:8081).
        :param function_context:
        :return:
        """
        metric_group = function_context.get_metric_group().add_group("online_ml")

        self.metric_counter = metric_group.counter('sample_count') # number of trained samples
        metric_group.gauge("prediction_acc", lambda: int(self.metric_predict_acc * 100))
        self.metric_distribution_y = metric_group.distribution("metric_distribution_y")
        self.metric_total_60_sec = metric_group.meter("total_60_sec", time_span_in_seconds=60)
        self.metric_right_60_sec = metric_group.meter("right_60_sec", time_span_in_seconds=60)
        self.training_window = []
        self.prediction_window = []   
        self.BD3 = BDDDC(warn_level=self.a, drift_level=self.b)
        self.is_model_trained = False
        self.training_data = []       




    def eval(self, attrib1, attrib2, attrib3, label):
        # Online learning, that is, training models one by one
        xi = [attrib1, attrib2, attrib3]
        yi = [label]
        
        # Train the model on the first win1 data point and make subsequent predictions
        if not self.is_model_trained:
            self.training_data.append((xi, yi))
            if len(self.training_data) == self.win1:
                X_train, y_train = zip(*self.training_data)
                self.classifier.fit(X_train, y_train)
                self.is_model_trained = True
                self.dump_lgb_model()
              
        else:
            y_pred = self.classifier.predict([xi])
            y_true = tuple(yi)
            y_pred = tuple(y_pred)
            self.metric_counter.inc(y_true == y_pred)
            self.metric = self.metric.update(y_true, y_pred)
            self.t.append(self.i)
            self.m.append(self.metric.get() * 100)
            self.yt.append(yi)
            self.yp.append(y_pred)
            self.xt.append(xi)

            
            if self.i > 2 * self.win1:
                yt_window = self.yt[self.i - self.win1:]
                yp_window = self.yp[self.i - self.win1:]
                prev_yt_window = self.yt[self.i - 2 * self.win1 : self.i - self.win1]
                prev_yp_window = self.yp[self.i - 2 * self.win1 : self.i - self.win1]
                
                acc = accuracy_score(yt_window, yp_window)
                prev_acc = accuracy_score(prev_yt_window, prev_yp_window)   
                
                precision = precision_score(yt_window, yp_window)
                recall = recall_score(yt_window, yp_window)
                f1 = f1_score(yt_window, yp_window)
                
                latency = self.calculate_latency(yt_window, yp_window)  # Replace with your latency calculation logic
                throughput = self.calculate_throughput(yt_window, yp_window)  # Replace with your throughput calculation logic
                predictions = pd.Series(self.yt[self.i - self.win1:])
                labels = pd.Series(self.yp[self.i - self.win1:])
                try:
                    BD3.add_element(np.array(predictions, ndmin=1), np.array(labels, ndmin=1))
                except:
                    pass

                if self.d == 0 and self.BD3.detected_warning_zone():
                    self.x_new.append(xi)
                    self.y_new.append(yi)
                    self.d = 1

                if self.d == 1:
                    self.tt = len(self.y_new)
                    if self.BD3.detected_change():
                        self.dr.append(self.i)
                        self.f = self.i
                        if self.tt < self.win1:
                            self.classifier.fit(self.xt[self.i - self.win1 :], self.yt[self.i - self.win1 :])
                        else:
                            self.classifier.fit(self.x_new, self.y_new)
                        self.d = 2
                        self.BD3 = BDDDC(warn_level=self.a, drift_level=self.b)
                    elif self.tt == self.win2:
                        self.x_new = []
                        self.y_new = []
                        self.d = 0
                    else:
                        self.x_new.append(xi)
                        self.y_new.append(yi)

                if self.d == 2:
                    self.tt = len(self.y_new)
                    self.x_new.append(xi)
                    self.y_new.append(yi)
                    if self.tt >= self.win1:
                        if self.th == 0:
                            self.classifier.fit(self.x_new, self.y_new)
                            self.th = 1
                        if self.th == 1 and self.tt == self.win2:
                            self.classifier.fit(self.x_new, self.y_new)
                            self.x_new = []
                            self.y_new = []
                            self.d = 0
                            self.th = 0
                    self.dump_lgb_model()

                # Calculate average accuracy
                avg_accuracy = sum(self.m[-self.win1:]) / self.win1
                # Calculate average precision
                avg_precision = precision*100
                # Calculate average recall
                avg_recall = recall*100
                # Calculate average F1 score
                avg_f1 = f1*100
                # Calculate latency (replace with your latency calculation logic)
                latency = self.calculate_latency(yt_window, yp_window)
                # Calculate throughput (replace with your throughput calculation logic)
                throughput = self.calculate_throughput(yt_window, yp_window)
                return avg_accuracy, avg_precision, avg_recall, f1, latency, throughput
        self.i += 1
        return (0,0,0,0,0,0)
    def calculate_latency(self, yt_window, yp_window):
        current_time = time.time()
        latency = round(current_time - self.start_time_window, 4)
        self.start_time_window = current_time
        return latency
    
    def calculate_throughput(self, yt_window, yp_window):
        num_instances = len(yt_window)
        current_time = time.time()
        time_elapsed = current_time - self.start_time_window
        throughput = round(num_instances / time_elapsed, 4)
        return throughput

    def load_model(self):
        """
        Load the model, if there is a model in redis, it will be loaded from redis first,
        otherwise a new model will be initialized
        :return:
        """
        import redis
        import pickle
        import logging
        from sklearn.linear_model import SGDClassifier

        r = redis.StrictRedis(**self.redis_params)
        clf = None

        try:
            clf = pickle.loads(r.get(self.model_name))
        except TypeError:
            logging.info('There is no model with the specified name in Redis, so a new model is initialized')
        except (redis.exceptions.RedisError, TypeError, Exception):
            logging.warning('Redis encountered an exception, so initialize a new model')
        finally:
            clf = clf or SGDClassifier(alpha=0.01, loss='log', penalty='l1')

        return clf

    def load_lgbm_model(self):
        """
        Load the model, if there is a model in redis, it will be loaded from redis first,
        otherwise a new model will be initialized
        :return:
        """
        import redis
        import pickle
        import logging
        import lightgbm as lgb

        r = redis.StrictRedis(**self.redis_params)
        clf = None

        try:
            clf = pickle.loads(r.get(self.model_name))
        except TypeError:
            logging.info('There is no model with the specified name in Redis, so a new model is initialized')
        except (redis.exceptions.RedisError, TypeError, Exception):
            logging.warning('Redis encountered an exception, so initialize a new lightgbm model')
        finally:
            clf = clf or  lgb.LGBMClassifier() 

        return clf    
    
    
    def  dump_model ( self ):
     """
    Saves the model when the specified time interval has elapsed since the last attempt to save the model
    :return:
    """
     import  pickle
     import  redis
     import  logging

     if ( datetime . now () -  self . last_dump_time ). seconds  >=  self . interval_dump_seconds :
         r  =  redis . StrictRedis ( ** self . redis_params )

         try :
             r . set ( self . model_name , pickle . dumps ( self . clf , protocol = pickle . HIGHEST_PROTOCOL ))
         except ( redis . exceptions . RedisError , TypeError , Exception ):
             logging.warning ( ' Unable to connect to Redis to store model data' )

         self . last_dump_time  =  datetime . now () # Whether the update is successful or not, update the save time
  

    def  dump_lgb_model ( self ):
     """
    Saves the model when the specified time interval has elapsed since the last attempt to save the model
    :return:
    """
     import  pickle
     import  redis
     import  logging

     if ( datetime . now () -  self . last_dump_time ). seconds  >=  self . interval_dump_seconds :
         r  =  redis . StrictRedis ( ** self . redis_params )

         try :
             r . set ( self . model_name , pickle . dumps ( self . clf , protocol = pickle . HIGHEST_PROTOCOL ))
         except ( redis . exceptions . RedisError , TypeError , Exception ):
             logging.warning ( ' Unable to connect to Redis to store model data' )

         self . last_dump_time  =  datetime . now () # Whether the update is successful or not, update the save time


a=0.99
b=0.95
win1=10
win2=20
q=0.1
# Register the eval_model function as a UDF function with st_env
result_type = RowType([DataTypes.FIELD("avg_accuracy", DataTypes.FLOAT()),
                       DataTypes.FIELD("avg_precision", DataTypes.FLOAT()),
                       DataTypes.FIELD("avg_recall", DataTypes.FLOAT()),
                       DataTypes.FIELD("avg_f1", DataTypes.FLOAT()),
                       DataTypes.FIELD("latency", DataTypes.FLOAT()),
                      DataTypes.FIELD("throughput", DataTypes.FLOAT())])

model = udf(Model(a,b,win1,win2,q), input_types=[DataTypes.FLOAT(), DataTypes.FLOAT(), DataTypes.FLOAT(), DataTypes.INT()], result_type=result_type)
st_env.register_function('train_predict', model)
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
        'connector' ='kafka-0.11',
        'topic' = '{os.environ["KAFKA_TOPIC"]}',
        'scan.startup.mode' = 'latest-offset',
        'properties.bootstrap.servers' = '{os.environ["KAFKA_HOST"]}',
        'properties.zookeeper.connect' = '{os.environ["ZOOKEEPER_HOST"]}',
        'properties.group.id' = '{os.environ["KAFKA_CONSUMER_GROUP"]}',
        'format' = 'json'
    )
    """
)



# Define output sink Dates TIMESTAMP, Descript STRING,
st_env.execute_sql(
    """
    CREATE TABLE sink (
       _c0 ROW<`avg_accuracy` FLOAT, `avg_precision` FLOAT,`avg_recall` FLOAT, `avg_f1` FLOAT,`latency` FLOAT,`throughput` FLOAT>
    ) WITH (
        'connector' = 'elasticsearch-7',
        'hosts' = 'http://elasticsearch:9200',
        'index' = 'Drift_data',
        'document-id.key-delimiter' = '$',
        'sink.bulk-flush.max-size' = '42mb',
        'sink.bulk-flush.max-actions' = '32',
        'sink.bulk-flush.interval' = '1000',
        'sink.bulk-flush.backoff.delay' = '1000',
        'format' = 'json'
)

""")








#Define output sink Dates TIMESTAMP, Descript STRING,

st_env.execute_sql(
    """
    CREATE TABLE target_sink (
        avg_accuracy FLOAT,
        avg_precision FLOAT,
        avg_recall FLOAT,
        avg_f1 FLOAT,
        latency FLOAT,
        throughput FLOAT
    ) WITH (
        'connector' = 'print',
        'print-identifier' = 'Drift data: '
    )
"""
)




st_env.from_path("source")\
.select("train_predict(attrib1, attrib2, attrib3, label)") \
.insert_into("sink") 






# Execute the job
st_env.execute("PyFlink job")