SET ROLE bi_analyst;
SELECT count(*) FROM mart.fact_predictive_maintenance; 

SELECT * FROM rv.hub_process; 
RESET ROLE;