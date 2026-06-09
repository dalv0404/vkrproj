import asyncio
import random
from pyzeebe import ZeebeWorker, create_insecure_channel
from pyzeebe.errors import BusinessError 

async def main():
    channel = create_insecure_channel("127.0.0.1:26500")
    worker = ZeebeWorker(channel)

    @worker.task(task_type="assemble-product")
    async def assemble_product(orderId: str, productType: str):
        print(f"\n[СБОРКА] Начат монтаж базового модуля для заказа {orderId} (Тип: {productType}).")
        return {"assemblyStatus": "done"}

    @worker.task(task_type="calibration-test")
    async def calibration_test(orderId: str):
        print(f"[КАЛИБРОВКА] Тестирование лазерных сенсоров заказа {orderId}...")
        

        failure_chance = random.random()
        if failure_chance < 0.30:
            print("  ВАЖНО: Деталь не прошла калибровку! Отправляем сигнал об ошибке в ядро...")
            raise BusinessError("CALIBRATION_FAILED")
            
        print("  Калибровка пройдена успешно!")
        return {"calibrationPassed": True}

    @worker.task(task_type="scrap-product")
    async def scrap_product(orderId: str):
        print(f"[УТИЛИЗАЦИЯ] Бракованная деталь {orderId} отправлена на переплавку.")
        return {"scrapped": True}

    print("Production Worker запущен и ждет задач на конвейере...")
    await worker.work()

if __name__ == "__main__":
    asyncio.run(main())