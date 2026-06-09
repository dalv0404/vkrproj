import asyncio
import random
from pyzeebe import ZeebeClient, create_insecure_channel

async def main():
    channel = create_insecure_channel("127.0.0.1:26500")
    client = ZeebeClient(channel)

    zone_id = f"ЦЕХ-{random.randint(1, 5)}"
    gas_level = random.uniform(1500.0, 5000.0) 

    print(f"ВНИМАНИЕ! ЗАФИКСИРОВАНА УТЕЧКА МЕТАНА В ЗОНЕ {zone_id}!")
    print(f" Концентрация: {gas_level:.0f} ppm (КРИТИЧЕСКАЯ!)")

    try:
        await client.publish_message(
            name="emergency.gas.leak",
            correlation_key=zone_id, 
            variables={"zoneId": zone_id, "gasLevel": gas_level},
            time_to_live_in_milliseconds=30000 
        )
        print("Сигнал тревоги передан в центральную систему! Запущен таймер эвакуации (30 секунд).")
    except Exception as e:
        print(f"Ошибка отправки: {e}")

if __name__ == "__main__":
    asyncio.run(main())