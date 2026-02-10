from fastapi import FastAPI

from app.api.rest import router as rest_router

app = FastAPI(title="zapier-clone backend")

app.include_router(rest_router, prefix="/api")

@app.get("/")
async def root():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, log_level="info")
