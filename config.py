# Databricks notebook source
# MAGIC %md
# MAGIC # This notebook is aimed for downloading data from kaggle

# COMMAND ----------

# MAGIC %pip install kaggle

# COMMAND ----------

# DBTITLE 1,kaggle credentials
import os
os.environ['kaggle_username'] = 'yash5raj5'
os.environ['kaggle_key'] = '9693818d1ed3e043f757e57093a8458b'

# another and BETTER way is to make databricks backed secret scope
#os.environ['kaggle_username'] =dbutils.secrets.get("solution-accelerator-cicd","kaggle_user_name")
#os.envrion['kaggle_key'] = dbutils.secrets.get("solution-accelerator-cicd", "kaggle-key")

# COMMAND ----------

# MAGIC %md
# MAGIC Downloading the data from Kaggle

# COMMAND ----------

# MAGIC %sh 
# MAGIC cd /databricks/driver
# MAGIC export KAGGLE_USERNAME=$kaggle_username
# MAGIC export KAGGLE_KEY=$kaggle_key
# MAGIC kaggle datasets download -d frtgnn/dunnhumby-the-complete-journey
# MAGIC unzip dunnhumby-the-complete-journey.zip

# COMMAND ----------

dbutils.fs.mv("file:/databricks/driver/campaign_desc.csv", "dbfs:/tmp/completejourney/bronze/campaign_desc.csv")
dbutils.fs.mv("file:/databricks/driver/campaign_table.csv", "dbfs:/tmp/completejourney/bronze/campaign_table.csv")
dbutils.fs.mv("file:/databricks/driver/causal_data.csv", "dbfs:/tmp/completejourney/bronze/causal_data.csv")
dbutils.fs.mv("file:/databricks/driver/coupon.csv", "dbfs:/tmp/completejourney/bronze/coupon.csv")
dbutils.fs.mv("file:/databricks/driver/coupon_redempt.csv", "dbfs:/tmp/completejourney/bronze/coupon_redempt.csv")
dbutils.fs.mv("file:/databricks/driver/hh_demographic.csv", "dbfs:/tmp/completejourney/bronze/hh_demographic.csv")
dbutils.fs.mv("file:/databricks/driver/product.csv", "dbfs:/tmp/completejourney/bronze/product.csv")
dbutils.fs.mv("file:/databricks/driver/transaction_data.csv", "dbfs:/tmp/completejourney/bronze/transaction_data.csv")
