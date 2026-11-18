
import os
import uuid
from pathlib import Path
from decimal import Decimal

import psycopg
from dotenv import load_dotenv

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, sum, count
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    DoubleType
)


# ==========================================
# PROJECT CONFIGURATION
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env", override=True)

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "sales-transactions-stream"

KAFKA_PACKAGE = (
    "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.6"
)

POSTGRES_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", "5435")),
    "dbname": os.getenv("POSTGRES_DB", "ecommerce_dw"),
    "user": os.getenv("POSTGRES_USER", "ecommerce_user"),
    "password": os.getenv("POSTGRES_PASSWORD")
}

RUN_ID = str(uuid.uuid4())

CHECKPOINT_PATH = (
    PROJECT_ROOT
    / "data"
    / "checkpoints"
    / "spark_kafka_postgres"
    / RUN_ID
)


# ==========================================
# CREATE POSTGRESQL TABLE
# ==========================================

def initialize_streaming_table():

    if not POSTGRES_CONFIG["password"]:
        raise ValueError(
            "POSTGRES_PASSWORD belum ditemukan di file .env"
        )

    sql_path = (
        PROJECT_ROOT
        / "warehouse"
        / "sql"
        / "05_create_streaming_table.sql"
    )

    create_table_sql = sql_path.read_text(encoding="utf-8")

    with psycopg.connect(**POSTGRES_CONFIG) as conn:
        conn.execute(create_table_sql)

    print("PostgreSQL streaming table is ready!")


# ==========================================
# WRITE SPARK AGGREGATION TO POSTGRESQL
# ==========================================

def write_to_postgres(batch_df, batch_id):

    rows = batch_df.collect()

    if not rows:
        print(f"Batch {batch_id}: no records.")
        return

    insert_sql = """
        INSERT INTO fact_sales_streaming (
            run_id,
            family_name,
            total_transactions,
            total_sales,
            updated_at
        )
        VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)

        ON CONFLICT (run_id, family_name)
        DO UPDATE SET
            total_transactions = EXCLUDED.total_transactions,
            total_sales = EXCLUDED.total_sales,
            updated_at = CURRENT_TIMESTAMP;
    """

    records = [
        (
            RUN_ID,
            row["family"],
            int(row["total_transactions"]),
            Decimal(str(row["total_sales"] or 0))
        )
        for row in rows
    ]

    with psycopg.connect(**POSTGRES_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.executemany(insert_sql, records)

    print(
        f"Batch {batch_id}: "
        f"{len(records)} family records saved to PostgreSQL."
    )


# ==========================================
# MAIN STREAMING PROCESS
# ==========================================

def start_streaming():

    initialize_streaming_table()

    spark = (
        SparkSession.builder
        .appName("EcommerceKafkaPostgresStreaming")
        .master("local[*]")
        .config("spark.jars.packages", KAFKA_PACKAGE)
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    print("\nSpark Session Started!")
    print(f"Spark Version: {spark.version}")
    print(f"Run ID: {RUN_ID}")

    schema = StructType([
        StructField("id", IntegerType(), True),
        StructField("date", StringType(), True),
        StructField("store_nbr", IntegerType(), True),
        StructField("family", StringType(), True),
        StructField("sales", DoubleType(), True),
        StructField("onpromotion", IntegerType(), True)
    ])

    kafka_stream = (
        spark.readStream
        .format("kafka")
        .option(
            "kafka.bootstrap.servers",
            KAFKA_BOOTSTRAP_SERVERS
        )
        .option("subscribe", KAFKA_TOPIC)
        .option("startingOffsets", "latest")
        .load()
    )

    parsed_stream = (
        kafka_stream
        .select(
            from_json(
                col("value").cast("string"),
                schema
            ).alias("data")
        )
        .select("data.*")
    )

    sales_summary = (
        parsed_stream
        .groupBy("family")
        .agg(
            count("*").alias("total_transactions"),
            sum("sales").alias("total_sales")
        )
    )

    query = (
        sales_summary.writeStream
        .outputMode("complete")
        .foreachBatch(write_to_postgres)
        .option(
            "checkpointLocation",
            str(CHECKPOINT_PATH)
        )
        .trigger(processingTime="5 seconds")
        .start()
    )

    print("\nSpark → Kafka → PostgreSQL is running!")
    print("Waiting for incoming transactions...\n")

    try:
        query.awaitTermination()
    except KeyboardInterrupt:
        print("\nStopping Spark streaming...")
    finally:
        query.stop()
        spark.stop()
        print("Spark streaming stopped.")


if __name__ == "__main__":
    start_streaming()
