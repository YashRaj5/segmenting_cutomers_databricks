# Databricks notebook source
# MAGIC %pip install dython==0.7.1

# COMMAND ----------

# DBTITLE 1,importing required libraries
from sklearn.preprocessing import quantile_transform
import dython
import math
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# COMMAND ----------

# DBTITLE 1,derive relavant metrics
# MAGIC %sql
# MAGIC USE journey;
# MAGIC  
# MAGIC DROP VIEW IF EXISTS household_metrics;
# MAGIC  
# MAGIC CREATE VIEW household_metrics
# MAGIC AS
# MAGIC   WITH 
# MAGIC     targeted_products_by_household AS (
# MAGIC       SELECT DISTINCT
# MAGIC         b.household_id,
# MAGIC         c.product_id
# MAGIC       FROM campaigns a
# MAGIC       INNER JOIN campaigns_households b
# MAGIC         ON a.campaign_id=b.campaign_id
# MAGIC       INNER JOIN coupons c
# MAGIC         ON a.campaign_id=c.campaign_id
# MAGIC       ),
# MAGIC     product_spend AS (
# MAGIC       SELECT
# MAGIC         a.household_id,
# MAGIC         a.product_id,
# MAGIC         a.day,
# MAGIC         a.basket_id,
# MAGIC         CASE WHEN a.campaign_coupon_discount > 0 THEN 1 ELSE 0 END as campaign_coupon_redemption,
# MAGIC         CASE WHEN a.manuf_coupon_discount > 0 THEN 1 ELSE 0 END as manuf_coupon_redemption,
# MAGIC         CASE WHEN a.instore_discount > 0 THEN 1 ELSE 0 END as instore_discount_applied,
# MAGIC         CASE WHEN b.brand = 'Private' THEN 1 ELSE 0 END as private_label,
# MAGIC         a.amount_list,
# MAGIC         a.campaign_coupon_discount,
# MAGIC         a.manuf_coupon_discount,
# MAGIC         a.total_coupon_discount,
# MAGIC         a.instore_discount,
# MAGIC         a.amount_paid  
# MAGIC       FROM transactions_adj a
# MAGIC       INNER JOIN products b
# MAGIC         ON a.product_id=b.product_id
# MAGIC       )
# MAGIC   SELECT
# MAGIC  
# MAGIC     x.household_id,
# MAGIC  
# MAGIC     -- Purchase Date Level Metrics
# MAGIC     COUNT(DISTINCT x.day) as purchase_dates,
# MAGIC     COUNT(DISTINCT CASE WHEN y.product_id IS NOT NULL THEN x.day ELSE NULL END) as pdates_campaign_targeted,
# MAGIC     COUNT(DISTINCT CASE WHEN x.private_label = 1 THEN x.day ELSE NULL END) as pdates_private_label,
# MAGIC     COUNT(DISTINCT CASE WHEN y.product_id IS NOT NULL AND x.private_label = 1 THEN x.day ELSE NULL END) as pdates_campaign_targeted_private_label,
# MAGIC     COUNT(DISTINCT CASE WHEN x.campaign_coupon_redemption = 1 THEN x.day ELSE NULL END) as pdates_campaign_coupon_redemptions,
# MAGIC     COUNT(DISTINCT CASE WHEN x.campaign_coupon_redemption = 1 AND x.private_label = 1 THEN x.day ELSE NULL END) as pdates_campaign_coupon_redemptions_on_private_labels,
# MAGIC     COUNT(DISTINCT CASE WHEN x.manuf_coupon_redemption = 1 THEN x.day ELSE NULL END) as pdates_manuf_coupon_redemptions,
# MAGIC     COUNT(DISTINCT CASE WHEN x.instore_discount_applied = 1 THEN x.day ELSE NULL END) as pdates_instore_discount_applied,
# MAGIC     COUNT(DISTINCT CASE WHEN y.product_id IS NOT NULL AND x.instore_discount_applied = 1 THEN x.day ELSE NULL END) as pdates_campaign_targeted_instore_discount_applied,
# MAGIC     COUNT(DISTINCT CASE WHEN x.private_label = 1 AND x.instore_discount_applied = 1 THEN x.day ELSE NULL END) as pdates_private_label_instore_discount_applied,
# MAGIC     COUNT(DISTINCT CASE WHEN y.product_id IS NOT NULL AND x.private_label = 1 AND x.instore_discount_applied = 1 THEN x.day ELSE NULL END) as pdates_campaign_targeted_private_label_instore_discount_applied,
# MAGIC     COUNT(DISTINCT CASE WHEN x.campaign_coupon_redemption = 1 AND x.instore_discount_applied = 1 THEN x.day ELSE NULL END) as pdates_campaign_coupon_redemption_instore_discount_applied,
# MAGIC     COUNT(DISTINCT CASE WHEN x.campaign_coupon_redemption = 1 AND x.private_label = 1 AND x.instore_discount_applied = 1 THEN x.day ELSE NULL END) as pdates_campaign_coupon_redemption_private_label_instore_discount_applied,
# MAGIC     COUNT(DISTINCT CASE WHEN x.manuf_coupon_redemption = 1 AND x.instore_discount_applied = 1 THEN x.day ELSE NULL END) as pdates_manuf_coupon_redemption_instore_discount_applied,
# MAGIC  
# MAGIC     -- List Amount Metrics
# MAGIC     COALESCE(SUM(x.amount_list),0) as amount_list,
# MAGIC     COALESCE(SUM(CASE WHEN y.product_id IS NOT NULL THEN 1 ELSE 0 END * x.amount_list),0) as amount_list_with_campaign_targeted,
# MAGIC     COALESCE(SUM(x.private_label * x.amount_list),0) as amount_list_with_private_label,
# MAGIC     COALESCE(SUM(CASE WHEN y.product_id IS NOT NULL THEN 1 ELSE 0 END * x.private_label * x.amount_list),0) as amount_list_with_campaign_targeted_private_label,
# MAGIC     COALESCE(SUM(x.campaign_coupon_redemption * x.amount_list),0) as amount_list_with_campaign_coupon_redemptions,
# MAGIC     COALESCE(SUM(x.campaign_coupon_redemption * x.private_label * x.amount_list),0) as amount_list_with_campaign_coupon_redemptions_on_private_labels,
# MAGIC     COALESCE(SUM(x.manuf_coupon_redemption * x.amount_list),0) as amount_list_with_manuf_coupon_redemptions,
# MAGIC     COALESCE(SUM(x.instore_discount_applied * x.amount_list),0) as amount_list_with_instore_discount_applied,
# MAGIC     COALESCE(SUM(CASE WHEN y.product_id IS NOT NULL THEN 1 ELSE 0 END * x.instore_discount_applied * x.amount_list),0) as amount_list_with_campaign_targeted_instore_discount_applied,
# MAGIC     COALESCE(SUM(x.private_label * x.instore_discount_applied * x.amount_list),0) as amount_list_with_private_label_instore_discount_applied,
# MAGIC     COALESCE(SUM(CASE WHEN y.product_id IS NOT NULL THEN 1 ELSE 0 END * x.private_label * x.instore_discount_applied * x.amount_list),0) as amount_list_with_campaign_targeted_private_label_instore_discount_applied,
# MAGIC     COALESCE(SUM(x.campaign_coupon_redemption * x.instore_discount_applied * x.amount_list),0) as amount_list_with_campaign_coupon_redemption_instore_discount_applied,
# MAGIC     COALESCE(SUM(x.campaign_coupon_redemption * x.private_label * x.instore_discount_applied * x.amount_list),0) as amount_list_with_campaign_coupon_redemption_private_label_instore_discount_applied,
# MAGIC     COALESCE(SUM(x.manuf_coupon_redemption * x.instore_discount_applied * x.amount_list),0) as amount_list_with_manuf_coupon_redemption_instore_discount_applied
# MAGIC  
# MAGIC   FROM product_spend x
# MAGIC   LEFT OUTER JOIN targeted_products_by_household y
# MAGIC     ON x.household_id=y.household_id AND x.product_id=y.product_id
# MAGIC   GROUP BY 
# MAGIC     x.household_id;
# MAGIC     
# MAGIC SELECT * FROM household_metrics;

# COMMAND ----------


