# Databricks notebook source
# MAGIC %md
# MAGIC # Compute Used: Serverless

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC # Accelerating analytics with DatabricksIQ
# MAGIC
# MAGIC DatabricksIQ is the engine that powers Databricks' Data Intelligence Platform. In addition to backend features like liquid clustering and serverless autoscaling which use machine learning to optimize performance, there are a number of features that make it easier for data professionals to discover, curate, and analyze data using generative AI.  This demo focuses on the various ways that DatabricksIQ can be used:
# MAGIC
# MAGIC * **Intelligent Search** to find the right data for your use case
# MAGIC * **AI-assisted Authoring** with the Assistant in the Notebook and SQL Editor
# MAGIC * **AI-generated documentation** for tables and columns in Unity Catalog
# MAGIC * **Genie Spaces** for talking to your data in natural language

# COMMAND ----------

# MAGIC %md
# MAGIC #### About this notebook
# MAGIC
# MAGIC * 99% of code is generated by the Assistant
# MAGIC * Prompts are included and can be re-executed to generate similar results  
# MAGIC * LLMs are probabilistic by nature, so the same prompt may generate different responses

# COMMAND ----------

# MAGIC %md
# MAGIC #### The data: Patients table
# MAGIC The 'Patients' table contains detailed demographic information about each patient in the database, including identifiers, personal details, and location data. This table serves as a comprehensive repository of patient profiles, enabling healthcare providers to track and manage patient information efficiently. The data in this table is crucial for understanding the patient population, analyzing trends, and providing personalized care. It plays a vital role in ensuring accurate record-keeping, facilitating communication between healthcare professionals, and improving overall patient outcomes.
# MAGIC
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC USE CATALOG quickstart_catalog_vkm_external;
# MAGIC USE SCHEMA dbdemos_hls_readmission;

# COMMAND ----------

# MAGIC %md
# MAGIC ### Finding tables with the Assistant
# MAGIC
# MAGIC You can use natural language or shortcuts to tell the Assistant to find tables related to your subject.  <br>
# MAGIC
# MAGIC **Prompt**: /findTables patients <br><br>
# MAGIC
# MAGIC Clicking on the `patients` table, the Assistant gives us a few choices of how to proceed with the data:
# MAGIC
# MAGIC 1. **Suggest a few starter SQL queries**
# MAGIC 2. **Describe the table**
# MAGIC 3. **Query the table using natural language**
# MAGIC
# MAGIC Let's explore each of these options.
# MAGIC
# MAGIC <img src='https://github.com/bigdatavik/notebookassets/blob/bde4afbc2e684a9cd17d994f1d379091299e24da/common/findTables.gif?raw=true' width="800" height="600">
# MAGIC
# MAGIC
# MAGIC
# MAGIC
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ### **Prompt:** Find the Patients table

# COMMAND ----------

# DBTITLE 1,List tables
# List all tables in the database to find the patients table
tables_df = spark.sql("SHOW TABLES IN quickstart_catalog_vkm_external.dbdemos_hls_readmission")

# Display the tables DataFrame
display(tables_df)

# COMMAND ----------

# MAGIC %md
# MAGIC #### Explain Code in cell
# MAGIC <img src='https://github.com/bigdatavik/notebookassets/blob/bde4afbc2e684a9cd17d994f1d379091299e24da/common/explain.gif?raw=true' width="800" height="600">

# COMMAND ----------

# MAGIC %md
# MAGIC ### **Prompt**: Read the patients from my catalog

# COMMAND ----------

# DBTITLE 1,Read Bronze table
# Read data from the patients Delta table
patients_df = spark.read.table("quickstart_catalog_vkm_external.dbdemos_hls_readmission.patients")

# Display the DataFrame
display(patients_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ### **Prompt**: Rename column Id to patient_Id and calculate age from birthdate and filter patients older than 18 

# COMMAND ----------

# DBTITLE 1,Transform Bronze table
from pyspark.sql.functions import col, current_date, datediff, floor

# Rename column Id to patientId
patients_df = patients_df.withColumnRenamed("Id", "patient_id")

# Calculate age from birthdate and filter patients older than 18
patients_with_age_df = patients_df.withColumn(
    "age", 
    floor(datediff(current_date(), col("birthdate")) / 365.25)
).filter(col("age") > 18)

# Display the new DataFrame
display(patients_with_age_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ### **Prompt**: Write the results to a silver table with schema evolution enabled

# COMMAND ----------

# DBTITLE 1,Write Silver table
# Write the filtered DataFrame to a Silver table with schema evolution enabled
patients_with_age_df.write.format("delta") \
    .mode("overwrite") \
    .option("mergeSchema", "true") \
    .saveAsTable("quickstart_catalog_vkm_external.dbdemos_hls_readmission.silver_patients")

# COMMAND ----------

# MAGIC %md
# MAGIC ### **Prompt**: Read the silver Patients table and **define** age groups and calculate average healthcare expenses, healthcare coverage, and income by age group and create a gold table

# COMMAND ----------

# DBTITLE 1,Transform Silver to Gold table
from pyspark.sql.functions import col, when, avg

# Read the silver Patients table
silver_patients_df = spark.table("quickstart_catalog_vkm_external.dbdemos_hls_readmission.silver_patients")

# Define age groups
silver_patients_df = silver_patients_df.withColumn(
    "age_group",
    when(col("age") < 18, "0-17")
    .when((col("age") >= 18) & (col("age") <= 35), "18-35")
    .when((col("age") > 35) & (col("age") <= 50), "36-50")
    .when((col("age") > 50) & (col("age") <= 65), "51-65")
    .otherwise("65+")
)

# Calculate average healthcare expenses, healthcare coverage, and income by age group
age_group_agg_df = silver_patients_df.groupBy("age_group").agg(
    avg("healthcare_expenses").alias("avg_healthcare_expenses"),
    avg("healthcare_coverage").alias("avg_healthcare_coverage"),
    avg("income").alias("avg_income")
)

# Write the results to a gold table
age_group_agg_df.write.format("delta") \
    .option("mergeSchema", "true") \
    .mode("overwrite") \
    .saveAsTable("quickstart_catalog_vkm_external.dbdemos_hls_readmission.gold_age_group_aggregates")

# COMMAND ----------

# MAGIC %md
# MAGIC We can also use the Assistant from the notebook cells directly:

# COMMAND ----------

# MAGIC %md
# MAGIC ### **Prompt**: Read the silver Patients table and **define** age groups and calculate average healthcare expenses, healthcare coverage, and income by age group and create a gold table
# MAGIC
# MAGIC <img src='https://github.com/bigdatavik/notebookassets/blob/bde4afbc2e684a9cd17d994f1d379091299e24da/common/AssistantPrompt.gif?raw=true' width="800" height="600">
# MAGIC
# MAGIC
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Diagnosing Errors
# MAGIC
# MAGIC If you run into errors during the course of your work, the Assistant will do its best to help out.  Let's create an error and see what happens. <br><br>
# MAGIC
# MAGIC <img src="https://github.com/bigdatavik/notebookassets/blob/b4208e46d79239f4ef682f22e3c6637cd5ce787c/common/diagnose_error.gif?raw=true" width=900>
# MAGIC
# MAGIC Try it yourself below: Use new thread from AI Assistant

# COMMAND ----------

# DBTITLE 1,Numeric String Concatenation
1 + "x"

# COMMAND ----------

str(1) + "x"

# COMMAND ----------


