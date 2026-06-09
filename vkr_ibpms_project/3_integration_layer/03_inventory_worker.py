import asyncio
from pyzeebe import ZeebeWorker, create_insecure_channel

async def main():
    channel = create_insecure_channel("127.0.0.1:26500")
    worker = ZeebeWorker(channel)

    @worker.task(task_type="calculate-order")
    async def calc_order(materialId: str, currentWeight: float):
        order_amount = 1000.0 - currentWeight
        print(f"[РАСЧЕТ] Материал {materialId}: вес {currentWeight}кг. Нужно дозаказать: {order_amount:.1f}кг.")
        return {"orderAmount": order_amount}

    @worker.task(task_type="reserve-budget")
    async def reserve_budget(materialId: str, orderAmount: float):
        cost = orderAmount * 5.2  
        print(f"[ФИНАНСЫ] Зарезервирован бюджет: ${cost:.2f} для закупки {materialId}.")
        return {"budgetReserved": cost}

    @worker.task(task_type="send-vendor-request")
    async def send_request(materialId: str, orderAmount: float):
        print(f"[ЛОГИСТИКА] Отправлена email-заявка поставщику на {orderAmount:.1f}кг материала {materialId}.")
        return {"vendorNotified": True}

    print("Inventory Worker запущен и ждет задач...")
    await worker.work()

if __name__ == "__main__":
    asyncio.run(main())