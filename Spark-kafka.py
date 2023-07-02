# Install Confluent Kafka platform.Then confluent connector called “Debezium-postgres-source-connector” from the 
# confluent connector hub in GUI. This connector is responsible to detect the changes at source system and emit 
# event upon any changes and finally push the data to a topic

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "db.public.food"

spark = SparkSession.builder.appName("sparkdev-kafka-integration").master("local[*]").getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("description", StringType(), True),
    StructField("food_name", StringType(), True),
    StructField("price", FloatType(), True),
    StructField("category_id", IntegerType(), True),
    StructField("restaurant_id", IntegerType(), True)
])

df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
    .option("subscribe", KAFKA_TOPIC) \
    .load()

stream_df = df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")

structured_df = stream_df.withColumn("value", from_json("value", schema=schema)) \
    .select(col("key"), col("value.*"))

structured_df.writeStream \
    .format("console") \
    .outputMode("update") \
    .start() \
    .awaitTermination()
