import asyncio
import random
from pyzeebe import ZeebeClient, create_insecure_channel

async def main():
    channel = create_insecure_channel("127.0.0.1:26500")
    client = ZeebeClient(channel)

    batch_id = f"batch-{random.randint(1000, 9999)}"
    quality_score = random.randint(40, 100)
    
    sensor_data = {
        "batchId": batch_id,
        "productName": "Деталь А",
        "quantity": random.randint(50, 200),
        "qualityScore": quality_score,
        "sensorStatus": "OK" if quality_score >= 80 else "FAULT"
    }

    print(f"Запуск процесса для партии {batch_id} (Качество: {quality_score})...")

    try:
        
        response = await client.run_process(
            bpmn_process_id="manufacturing-quality-control",
            variables=sensor_data
        )
        print(f"[УСПЕХ]")
        

        if hasattr(response, 'process_instance_key'):
            print(f"   🔹 ID процесса в БД: {response.process_instance_key}")
        else:
            print(f"   🔹 Ответ движка: {response}")
            
    except Exception as e:
        print(f"[ОШИБКА] {e}")

if __name__ == "__main__":
    asyncio.run(main())