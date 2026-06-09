import pandas as pd
from sqlalchemy import create_engine, text
import json
import os
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5433/dwhbpmn')

def clean_camunda_value(val):
    if pd.isna(val): return val
    val_str = str(val).strip()
    if val_str.startswith('[') and val_str.endswith(']'):
        try:
            return bytes(json.loads(val_str)).decode('utf-8').strip('"\'')
        except: pass    
    try: return str(json.loads(val_str)).strip('"\'')
    except: return val_str.strip('"\'')

def run_elt(engine):
    with engine.begin() as conn:
        print("1. Загрузка СЛОЯ RAW VAULT (Схема rv)...")
        conn.execute(text("""
            INSERT INTO rv.hub_process (hk_process, process_instance_key)
            SELECT DISTINCT md5(process_instance_key::text), process_instance_key
            FROM public.process_instance
            ON CONFLICT (hk_process) DO NOTHING;
        """))

        conn.execute(text("""
            INSERT INTO rv.hub_machine (hk_machine, machine_id)
            SELECT DISTINCT md5("machineId"), "machineId"
            FROM stg.camunda_variables WHERE "machineId" IS NOT NULL
            ON CONFLICT DO NOTHING;
        """))
        conn.execute(text("""
            INSERT INTO rv.link_process_machine (hk_link, hk_process, hk_machine)
            SELECT DISTINCT md5(md5(process_instance_key::text) || md5("machineId")), md5(process_instance_key::text), md5("machineId")
            FROM stg.camunda_variables WHERE "machineId" IS NOT NULL
            ON CONFLICT DO NOTHING;
        """))
        conn.execute(text("""
            INSERT INTO rv.sat_machine_telemetry (hk_process, hash_diff, vibration, temperature, anomaly_type)
            SELECT md5(process_instance_key::text), md5(COALESCE("vibration", '0') || COALESCE("temperature", '0') || COALESCE("anomalyType", '')),
                   CAST("vibration" AS NUMERIC), CAST("temperature" AS NUMERIC), "anomalyType"
            FROM stg.camunda_variables WHERE "machineId" IS NOT NULL
            ON CONFLICT DO NOTHING;
        """))

        conn.execute(text("""
            INSERT INTO rv.hub_batch (hk_batch, batch_id)
            SELECT DISTINCT md5("batchId"), "batchId" FROM stg.camunda_variables WHERE "batchId" IS NOT NULL
            ON CONFLICT DO NOTHING;
        """))
        conn.execute(text("""
            INSERT INTO rv.link_process_batch (hk_link, hk_process, hk_batch)
            SELECT DISTINCT md5(md5(process_instance_key::text) || md5("batchId")), md5(process_instance_key::text), md5("batchId")
            FROM stg.camunda_variables WHERE "batchId" IS NOT NULL
            ON CONFLICT DO NOTHING;
        """))
        conn.execute(text("""
            INSERT INTO rv.sat_batch_quality (hk_process, hash_diff, product_name, quantity, quality_score, sensor_status)
            SELECT md5(process_instance_key::text), md5(COALESCE("productName", '') || COALESCE("quantity", '0') || COALESCE("qualityScore", '0')),
                   "productName", CAST("quantity" AS NUMERIC), CAST("qualityScore" AS NUMERIC), "sensorStatus"
            FROM stg.camunda_variables WHERE "batchId" IS NOT NULL
            ON CONFLICT DO NOTHING;
        """))

        print("2. Загрузка СЛОЯ BUSINESS VAULT (Схема bv)...")
        conn.execute(text("""
            INSERT INTO bv.sat_process_kpi (hk_process, process_state, cycle_time_seconds, is_sla_breached, business_status)
            SELECT 
                rv.hub_process.hk_process,
                pi.state,
                EXTRACT(EPOCH FROM (pi.end_date - pi.start_date)) AS cycle_time_seconds,
                CASE WHEN EXTRACT(EPOCH FROM (pi.end_date - pi.start_date)) > 120 THEN TRUE ELSE FALSE END AS is_sla_breached,
                CASE 
                    WHEN cv."qualityScore"::numeric >= 80 THEN 'Успешная приемка'
                    WHEN cv."qualityScore"::numeric < 80 THEN 'Отбраковка'
                    ELSE 'В процессе'
                END AS business_status
            FROM public.process_instance pi
            JOIN rv.hub_process ON pi.process_instance_key = rv.hub_process.process_instance_key
            LEFT JOIN stg.camunda_variables cv ON pi.process_instance_key = cv.process_instance_key
            ON CONFLICT (hk_process) DO UPDATE SET 
                process_state = EXCLUDED.process_state,
                cycle_time_seconds = EXCLUDED.cycle_time_seconds,
                is_sla_breached = EXCLUDED.is_sla_breached,
                business_status = EXCLUDED.business_status,
                load_dt = CURRENT_TIMESTAMP;
        """))

        print("3. Обновление СЛОЯ ВИТРИН ANALYTICS MART (Схема mart)...")
        conn.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY mart.fact_predictive_maintenance;"))
        conn.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY mart.fact_quality_control;"))

def main():
    print("=== Запуск обновленного ELT-пайплайна (Схемы RV и BV) ===")
    engine = create_engine(DB_URL)
    df_raw = pd.read_sql("SELECT process_instance_key, var_name, var_value FROM public.variable;", engine)
    df_raw['var_value_clean'] = df_raw['var_value'].apply(clean_camunda_value)
    df_pivot = df_raw.pivot_table(index='process_instance_key', columns='var_name', values='var_value_clean', aggfunc='first').reset_index()
    df_pivot.to_sql('camunda_variables', engine, schema='stg', if_exists='replace', index=False)
    

    run_elt(engine)
    print("=== Пайплайн завершен. Промышленная архитектура RV/BV/MART успешно обновлена! ===")

if __name__ == "__main__":
    main()