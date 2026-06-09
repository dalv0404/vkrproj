import asyncio
import random
from pyzeebe import ZeebeClient, create_insecure_channel

async def main():
    channel = create_insecure_channel("127.0.0.1:26500")
    client = ZeebeClient(channel)

    order_id = f"ORD-{random.randint(1000, 9999)}"
    product_type = random.choice(["Лазерный дальномер", "Оптический прицел", "Тепловизор"])

    print(f"ПОСТУПИЛ НОВЫЙ ЗАКАЗ: {order_id} ({product_type})")

    try:
        await client.publish_message(
            name="production.order.received",
            correlation_key=order_id, 
            variables={"orderId": order_id, "productType": product_type},
            time_to_live_in_milliseconds=30000 
        )
        print("Заказ отправлен на сборочный конвейер!")
    except Exception as e:
        print(f"Ошибка отправки: {e}")

if __name__ == "__main__":
    asyncio.run(main())