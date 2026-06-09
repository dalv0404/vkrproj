SET ROLE auditor_external;
SELECT DISTINCT anomaly_type FROM mart.vw_secure_fact_predictive_maintenance;

SELECT * FROM mart.fact_predictive_maintenance;
RESET ROLE;