DROP ROLE IF EXISTS auditor_external;
DROP ROLE IF EXISTS bi_analyst;


CREATE ROLE bi_analyst WITH LOGIN PASSWORD 'bi_password_123';
CREATE ROLE auditor_external WITH LOGIN PASSWORD 'audit_password_123';



REVOKE ALL ON SCHEMA stg, rv, bv, mart FROM PUBLIC;

GRANT USAGE ON SCHEMA mart TO bi_analyst;
GRANT SELECT ON ALL TABLES IN SCHEMA mart TO bi_analyst;
ALTER DEFAULT PRIVILEGES IN SCHEMA mart GRANT SELECT ON TABLES TO bi_analyst;


GRANT USAGE ON SCHEMA mart TO auditor_external;


CREATE OR REPLACE VIEW mart.vw_secure_fact_predictive_maintenance AS
SELECT * FROM mart.fact_predictive_maintenance
WHERE 

    (CURRENT_USER = 'auditor_external' AND anomaly_type = 'mechanical_wear')
    OR 

    (CURRENT_USER != 'auditor_external');


GRANT SELECT ON mart.dim_machine TO auditor_external;
GRANT SELECT ON mart.vw_secure_fact_predictive_maintenance TO auditor_external;