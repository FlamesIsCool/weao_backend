from fastapi import FastAPI, HTTPException
import aiohttp
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

app = FastAPI()
EXPLOITS_CACHE = []
API_URL = "https://weao.xyz/api/status/exploits"

# Fetch and cache all exploits
async def fetch_exploits():
    global EXPLOITS_CACHE
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL) as resp:
                if resp.status == 200:
                    EXPLOITS_CACHE = await resp.json()
                    print(f"[INFO] Fetched {len(EXPLOITS_CACHE)} exploits from WEAO.")
                elif resp.status == 429:
                    print("[WARNING] Rate limited by WEAO API.")
    except Exception as e:
        print(f"[ERROR] Failed to fetch exploits: {e}")

@app.on_event("startup")
async def startup_event():
    await fetch_exploits()  # Initial fetch
    # Schedule periodic refresh every 10 minutes
    scheduler = AsyncIOScheduler()
    scheduler.add_job(fetch_exploits, 'interval', minutes=10)
    scheduler.start()

@app.get("/")
def root():
    return {"message": "Roblox Exploit Tracker API"}

@app.get("/exploits")
def get_all_exploits():
    return [{"title": x["title"], "version": x["version"], "detected": x["detected"], "platform": x["platform"]} for x in EXPLOITS_CACHE]

@app.get("/exploit/{name}")
def get_exploit(name: str):
    name_lower = name.lower()
    for exploit in EXPLOITS_CACHE:
        if exploit["title"].lower() == name_lower:
            return exploit
    raise HTTPException(status_code=404, detail="Exploit not found")

