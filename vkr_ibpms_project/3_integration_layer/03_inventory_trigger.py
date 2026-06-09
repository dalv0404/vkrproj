import asyncio
import random
from pyzeebe import ZeebeClient, create_insecure_channel

async def main():
    channel = create_insecure_channel("127.0.0.1:26500")
    client = ZeebeClient(channel)

    material_id = f"ALUM-{random.randint(100, 999)}"
    current_weight = random.uniform(100.0, 450.0)

    print(f"1. Датчик склада: Критический уровень {material_id} ({current_weight:.1f}кг).")
    
    await client.publish_message(
        name="inventory.level.critical",
        correlation_key=material_id, 
        variables={"materialId": material_id, "currentWeight": current_weight},
        time_to_live_in_milliseconds=30000
    )
    
    print("Ожидание поставки... (Имитация поездки грузовика - 10 секунд)")
    await asyncio.sleep(10)

    print(f"2. GPS Трекер: Грузовик с {material_id} прибыл на КПП! Будим процесс...")
    await client.publish_message(
        name="vendor.delivery.arrived",
        correlation_key=material_id, 
        variables={"truckStatus": "arrived", "gate": 4},
        time_to_live_in_milliseconds=30000
    )
    print("Ворота открыты. Кладовщику отправлена задача в Tasklist!")

if __name__ == "__main__":
    asyncio.run(main())