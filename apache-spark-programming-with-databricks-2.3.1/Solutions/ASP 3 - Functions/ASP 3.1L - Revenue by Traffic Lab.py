# Databricks notebook source
# MAGIC %md
# MAGIC
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning">
# MAGIC </div>
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC
# MAGIC # Revenue by Traffic Lab
# MAGIC Get the 3 traffic sources generating the highest total revenue.
# MAGIC 1. Aggregate revenue by traffic source
# MAGIC 2. Get top 3 traffic sources by total revenue
# MAGIC 3. Clean revenue columns to have two decimal places
# MAGIC
# MAGIC ##### Methods
# MAGIC - <a href="https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/dataframe.html" target="_blank">DataFrame</a>: **`groupBy`**, **`sort`**, **`limit`**
# MAGIC - <a href="https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/column.html" target="_blank">Column</a>: **`alias`**, **`desc`**, **`cast`**, **`operators`**
# MAGIC - <a href="https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/functions.html" target="_blank">Built-in Functions</a>: **`avg`**, **`sum`**

# COMMAND ----------

# MAGIC %run ../Includes/Classroom-Setup

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC
# MAGIC ### Setup
# MAGIC Run the cell below to create the starting DataFrame **`df`**.

# COMMAND ----------

from pyspark.sql.functions import col

# Purchase events logged on the BedBricks website
df = (spark.read.format("delta").load(DA.paths.events)
      .withColumn("revenue", col("ecommerce.purchase_revenue_in_usd"))
      .filter(col("revenue").isNotNull())
      .drop("event_name")
     )

display(df)

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC
# MAGIC ### 1. Aggregate revenue by traffic source
# MAGIC - Group by **`traffic_source`**
# MAGIC - Get sum of **`revenue`** as **`total_rev`**. 
# MAGIC - Get average of **`revenue`** as **`avg_rev`**
# MAGIC
# MAGIC Remember to import any necessary built-in functions.

# COMMAND ----------

from pyspark.sql.functions import avg, col, sum

traffic_df = (df
              .groupBy("traffic_source")
              .agg(sum(col("revenue")).alias("total_rev"),
                   avg(col("revenue")).alias("avg_rev"))
             )

display(traffic_df)

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC
# MAGIC
# MAGIC **1.1: CHECK YOUR WORK**

# COMMAND ----------

from pyspark.sql.functions import round

expected1 = [(12704560.0, 1083.175), (78800000.3, 983.2915), (24797837.0, 1076.6221), (47218429.0, 1086.8303), (16177893.0, 1083.4378), (8044326.0, 1087.218)]
test_df = traffic_df.sort("traffic_source").select(round("total_rev", 4).alias("total_rev"), round("avg_rev", 4).alias("avg_rev"))
result1 = [(row.total_rev, row.avg_rev) for row in test_df.collect()]

assert(expected1 == result1)
print("All test pass")

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC
# MAGIC ### 2. Get top three traffic sources by total revenue
# MAGIC - Sort by **`total_rev`** in descending order
# MAGIC - Limit to first three rows

# COMMAND ----------

top_traffic_df = traffic_df.sort(col("total_rev").desc()).limit(3)
display(top_traffic_df)

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC
# MAGIC
# MAGIC **2.1: CHECK YOUR WORK**

# COMMAND ----------

expected2 = [(78800000.3, 983.2915), (47218429.0, 1086.8303), (24797837.0, 1076.6221)]
test_df = top_traffic_df.select(round("total_rev", 4).alias("total_rev"), round("avg_rev", 4).alias("avg_rev"))
result2 = [(row.total_rev, row.avg_rev) for row in test_df.collect()]

assert(expected2 == result2)
print("All test pass")

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC
# MAGIC ### 3. Limit revenue columns to two decimal places
# MAGIC - Modify columns **`avg_rev`** and **`total_rev`** to contain numbers with two decimal places
# MAGIC   - Use **`withColumn()`** with the same names to replace these columns
# MAGIC   - To limit to two decimal places, multiply each column by 100, cast to long, and then divide by 100

# COMMAND ----------

final_df = (top_traffic_df
            .withColumn("avg_rev", (col("avg_rev") * 100).cast("long") / 100)
            .withColumn("total_rev", (col("total_rev") * 100).cast("long") / 100)
           )

display(final_df)

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC
# MAGIC
# MAGIC **3.1: CHECK YOUR WORK**

# COMMAND ----------

expected3 = [(78800000.29, 983.29), (47218429.0, 1086.83), (24797837.0, 1076.62)]
result3 = [(row.total_rev, row.avg_rev) for row in final_df.collect()]

assert(expected3 == result3)
print("All test pass")

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC
# MAGIC ### 4. Bonus: Rewrite using a built-in math function
# MAGIC Find a built-in math function that rounds to a specified number of decimal places

# COMMAND ----------

from pyspark.sql.functions import round

bonus_df = (top_traffic_df
            .withColumn("avg_rev", round("avg_rev", 2))
            .withColumn("total_rev", round("total_rev", 2))
           )

display(bonus_df)

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC
# MAGIC
# MAGIC **4.1: CHECK YOUR WORK**

# COMMAND ----------

expected4 = [(78800000.3, 983.29), (47218429.0, 1086.83), (24797837.0, 1076.62)]
result4 = [(row.total_rev, row.avg_rev) for row in bonus_df.collect()]

assert(expected4 == result4)
print("All test pass")

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC
# MAGIC ### 5. Chain all the steps above

# COMMAND ----------

# Solution #1 using round

chain_df = (df
            .groupBy("traffic_source")
            .agg(sum(col("revenue")).alias("total_rev"),
                 avg(col("revenue")).alias("avg_rev"))
            .sort(col("total_rev").desc())
            .limit(3)
            .withColumn("avg_rev", round("avg_rev", 2))
            .withColumn("total_rev", round("total_rev", 2))
           )

display(chain_df)

# COMMAND ----------

# Solution #2 using *100, cast, /100
# chain_df = (df
#             .groupBy("traffic_source")
#             .agg(sum(col("revenue")).alias("total_rev"),
#                  avg(col("revenue")).alias("avg_rev"))
#             .sort(col("total_rev").desc())
#             .limit(3)
#             .withColumn("avg_rev", (col("avg_rev") * 100).cast("long") / 100)
#             .withColumn("total_rev", (col("total_rev") * 100).cast("long") / 100)
#            )

# display(chain_df)

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC
# MAGIC
# MAGIC **5.1: CHECK YOUR WORK**

# COMMAND ----------

method_a = [(78800000.3,  983.29), (47218429.0, 1086.83), (24797837.0, 1076.62)]
method_b = [(78800000.29, 983.29), (47218429.0, 1086.83), (24797837.0, 1076.62)]
result5 = [(row.total_rev, row.avg_rev) for row in chain_df.collect()]

assert result5 == method_a or result5 == method_b
print("All test pass")

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC
# MAGIC ### Clean up classroom

# COMMAND ----------

DA.cleanup()

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC &copy; 2024 Databricks, Inc. All rights reserved.<br/>
# MAGIC Apache, Apache Spark, Spark and the Spark logo are trademarks of the 
# MAGIC <a href="https://www.apache.org/">Apache Software Foundation</a>.<br/>
# MAGIC <br/><a href="https://databricks.com/privacy-policy">Privacy Policy</a> | 
# MAGIC <a href="https://databricks.com/terms-of-use">Terms of Use</a> | 
# MAGIC <a href="https://help.databricks.com/">Support</a>
