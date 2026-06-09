import asyncio
from pyzeebe import ZeebeWorker, create_insecure_channel

async def main():
    channel = create_insecure_channel("127.0.0.1:26500")
    worker = ZeebeWorker(channel)

    @worker.task(task_type="shut-down-valves")
    async def shut_down_valves(zoneId: str, gasLevel: float):
        print(f"\n[АВТОМАТИКА] КРИТИЧЕСКИЙ УРОВЕНЬ ГАЗА: {gasLevel:.0f} ppm в зоне {zoneId}!")
        print(f"[АВТОМАТИКА] Газовые вентили сектора {zoneId} ЭКСТРЕННО ПЕРЕКРЫТЫ.")
        return {"valvesClosed": True}

    @worker.task(task_type="call-rescue-team")
    async def call_rescue_team(zoneId: str):
        print(f"\n [МЧС] ВРЕМЯ НА ЭВАКУАЦИЮ ИСТЕКЛО! Нет ответа от персонала зоны {zoneId}.")
        print(f"[МЧС] Автоматический вызов бригады спасателей и пожарных...")
        return {"rescueTeamCalled": True}

    print("HSE Emergency Worker запущен и мониторит безопасность цеха...")
    await worker.work()

if __name__ == "__main__":
    asyncio.run(main())