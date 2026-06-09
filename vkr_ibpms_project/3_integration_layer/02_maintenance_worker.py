import asyncio
from pyzeebe import ZeebeWorker, create_insecure_channel

async def main():
    channel = create_insecure_channel("127.0.0.1:26500")
    worker = ZeebeWorker(channel)

    @worker.task(task_type="analyze-telemetry")
    async def analyze_telemetry(machineId: str, vibration: float, temperature: float):
        print(f"\n[ДИАГНОСТИКА] Станок: {machineId}")
        print(f"   Показатели: Вибрация={vibration} мм/с, Темп={temperature}°C")
        
        anomaly_type = "unknown"
        if vibration > 20.0:
            anomaly_type = "mechanical_wear" 
            print("   ВЕРДИКТ: Критическая вибрация! Механический износ.")
        elif temperature > 80.0:
            anomaly_type = "overheating" 
            print("  ВЕРДИКТ: Перегрев шпинделя.")
        else:
            print("  ВЕРДИКТ: Ложное срабатывание, показатели в норме.")

        return {"anomalyType": anomaly_type}

    @worker.task(task_type="reduce-speed")
    async def reduce_speed(machineId: str):
        print(f"[АВТОМАТИКА] Снижение оборотов шпинделя на 20% для станка {machineId}...")
        return {"actionTaken": "Speed reduced by 20%"}

    @worker.task(task_type="order-parts")
    async def order_parts(machineId: str):
        print(f"[СНАБЖЕНИЕ] Сформирован заказ на новые подшипники для станка {machineId}.")
        return {"partsOrdered": True}

    print("Maintenance Worker запущен и ждет задач...")
    await worker.work()

if __name__ == "__main__":
    asyncio.run(main())