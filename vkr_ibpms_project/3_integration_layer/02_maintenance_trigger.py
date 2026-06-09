import asyncio
import random
from pyzeebe import ZeebeClient, create_insecure_channel

async def main():
    channel = create_insecure_channel("127.0.0.1:26500")
    client = ZeebeClient(channel)
    scenario = random.choice(["overheating", "mechanical_wear"])
    machine_id = f"CNC-{random.randint(10, 99)}"
    
    if scenario == "overheating":
        vibration = random.uniform(5.0, 15.0)   
        temperature = random.uniform(85.0, 110.0) 
    else:
        vibration = random.uniform(25.0, 45.0)  
        temperature = random.uniform(60.0, 75.0)  

    sensor_data = {
        "machineId": machine_id,
        "vibration": round(vibration, 2),
        "temperature": round(temperature, 2)
    }

    print(f"[ДАТЧИК] Зафиксирована аномалия на станке {machine_id}!")
    print(f"  Показатели: Вибрация = {sensor_data['vibration']} мм/с, Темп = {sensor_data['temperature']}°C")

    try:
        await client.publish_message(
            name="sensor.anomaly.detected",
            correlation_key=machine_id, 
            variables=sensor_data,
            time_to_live_in_milliseconds=30000 
        )
        print("Сигнал успешно передан в систему управления!")
    except Exception as e:
        print(f"Ошибка отправки: {e}")

if __name__ == "__main__":
    asyncio.run(main())