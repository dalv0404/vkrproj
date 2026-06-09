import asyncio
from pyzeebe import ZeebeWorker, create_insecure_channel

async def main():
    channel = create_insecure_channel("127.0.0.1:26500")
    worker = ZeebeWorker(channel)


    @worker.task(task_type="check-quality")
    async def check_quality(batchId: str, qualityScore: int):
        print(f"[ПРОВЕРКА] Партия {batchId}. Оценка датчика: {qualityScore}")
        return {} 

  
    @worker.task(task_type="send-to-warehouse")
    async def to_warehouse(batchId: str):
        print(f" [УСПЕХ] Партия {batchId} отправлена на СКЛАД.")
        return {}

 
    @worker.task(task_type="send-to-rework")
    async def to_rework(batchId: str):
        print(f"[БРАК] Партия {batchId} отправлена на ДОРАБОТКУ.")
        return {}

    print("Worker запущен и слушает задачи...")
    await worker.work()

if __name__ == "__main__":
    asyncio.run(main())