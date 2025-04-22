import asyncio

async def boil_water():
    print("Starting to boil water...")
    await asyncio.sleep(3)  # waits 3 seconds (simulate delay)
    print("Water is boiled!")

async def chop_veggies():
    print("Chopping veggies...")
    await asyncio.sleep(1)
    print("Veggies chopped!")

async def main():
    await asyncio.gather(boil_water(), chop_veggies())

asyncio.run(main())
