DROP SCHEMA IF EXISTS dv CASCADE;
CREATE SCHEMA IF NOT EXISTS stg;
CREATE SCHEMA IF NOT EXISTS rv;   
CREATE SCHEMA IF NOT EXISTS bv;   
CREATE SCHEMA IF NOT EXISTS mart; 


CREATE TABLE IF NOT EXISTS rv.hub_process (
    hk_process CHAR(32) PRIMARY KEY,
    process_instance_key BIGINT NOT NULL,
    load_dt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rec_src VARCHAR(50) DEFAULT 'camunda.process_instance'
);

CREATE TABLE IF NOT EXISTS rv.hub_machine (
    hk_machine CHAR(32) PRIMARY KEY,
    machine_id VARCHAR(100) NOT NULL,
    load_dt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rec_src VARCHAR(50) DEFAULT 'camunda.variable'
);

CREATE TABLE IF NOT EXISTS rv.hub_batch (
    hk_batch CHAR(32) PRIMARY KEY,
    batch_id VARCHAR(100) NOT NULL,
    load_dt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rec_src VARCHAR(50) DEFAULT 'camunda.variable'
);


CREATE TABLE IF NOT EXISTS rv.link_process_machine (
    hk_link CHAR(32) PRIMARY KEY,
    hk_process CHAR(32) REFERENCES rv.hub_process(hk_process),
    hk_machine CHAR(32) REFERENCES rv.hub_machine(hk_machine),
    load_dt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rec_src VARCHAR(50) DEFAULT 'camunda.variable'
);

CREATE TABLE IF NOT EXISTS rv.link_process_batch (
    hk_link CHAR(32) PRIMARY KEY,
    hk_process CHAR(32) REFERENCES rv.hub_process(hk_process),
    hk_batch CHAR(32) REFERENCES rv.hub_batch(hk_batch),
    load_dt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rec_src VARCHAR(50) DEFAULT 'camunda.variable'
);


DROP TABLE IF EXISTS rv.sat_machine_telemetry CASCADE;
CREATE TABLE rv.sat_machine_telemetry (
    hk_process CHAR(32) REFERENCES rv.hub_process(hk_process),
    load_dt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    hash_diff CHAR(32),
    vibration NUMERIC,
    temperature NUMERIC,
    anomaly_type VARCHAR(100),
    rec_src VARCHAR(50) DEFAULT 'camunda.variable',
    PRIMARY KEY (hk_process, load_dt)
) PARTITION BY RANGE (load_dt);


CREATE TABLE rv.sat_machine_telemetry_default PARTITION OF rv.sat_machine_telemetry DEFAULT;

CREATE TABLE IF NOT EXISTS rv.sat_batch_quality (
    hk_process CHAR(32) REFERENCES rv.hub_process(hk_process),
    load_dt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    hash_diff CHAR(32),
    product_name VARCHAR(100),
    quantity NUMERIC,
    quality_score NUMERIC,
    sensor_status VARCHAR(50),
    rec_src VARCHAR(50) DEFAULT 'camunda.variable',
    PRIMARY KEY (hk_process, load_dt)
);


    hk_process CHAR(32) PRIMARY KEY REFERENCES rv.hub_process(hk_process),
    process_state VARCHAR(20),
    cycle_time_seconds NUMERIC, 
    is_sla_breached BOOLEAN,    
    business_status VARCHAR(100),
    load_dt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



CREATE OR REPLACE VIEW mart.dim_machine AS
SELECT hk_machine AS machine_key, machine_id FROM rv.hub_machine;

CREATE OR REPLACE VIEW mart.dim_batch AS
SELECT hk_batch AS batch_key, batch_id FROM rv.hub_batch;

DROP MATERIALIZED VIEW IF EXISTS mart.fact_predictive_maintenance CASCADE;
CREATE MATERIALIZED VIEW mart.fact_predictive_maintenance AS
SELECT 
    l.hk_process AS process_key,
    l.hk_machine AS machine_key,
    kpi.process_state,
    kpi.cycle_time_seconds,
    s.vibration,
    s.temperature,
    s.anomaly_type,
    s.load_dt AS recorded_at
FROM rv.link_process_machine l
JOIN (
    SELECT DISTINCT ON (hk_process) * FROM rv.sat_machine_telemetry ORDER BY hk_process, load_dt DESC
) s ON l.hk_process = s.hk_process
LEFT JOIN bv.sat_process_kpi kpi ON l.hk_process = kpi.hk_process;


CREATE UNIQUE INDEX idx_f_maint_pk ON mart.fact_predictive_maintenance(process_key, machine_key);
CREATE INDEX idx_f_maint_date ON mart.fact_predictive_maintenance(recorded_at);


DROP MATERIALIZED VIEW IF EXISTS mart.fact_quality_control CASCADE;
CREATE MATERIALIZED VIEW mart.fact_quality_control AS
SELECT 
    l.hk_process AS process_key,
    l.hk_batch AS batch_key,
    kpi.cycle_time_seconds,
    kpi.is_sla_breached,
    kpi.business_status,
    s.product_name,
    s.quantity,
    s.quality_score,
    s.sensor_status,
    s.load_dt AS recorded_at
FROM rv.link_process_batch l
JOIN (
    SELECT DISTINCT ON (hk_process) * FROM rv.sat_batch_quality ORDER BY hk_process, load_dt DESC
) s ON l.hk_process = s.hk_process
LEFT JOIN bv.sat_process_kpi kpi ON l.hk_process = kpi.hk_process;

CREATE UNIQUE INDEX idx_f_qc_pk ON mart.fact_quality_control(process_key, batch_key);