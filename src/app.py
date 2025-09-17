from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routers import catalogs, inventory, kardex, movements
from src.routers import rrhh as rrhh_router

app = FastAPI(title="CAFETAL SAC - Inventario API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(catalogs.router, prefix="/api/v1", tags=["catalogs"])
app.include_router(inventory.router, prefix="/api/v1", tags=["inventory"])
app.include_router(kardex.router, prefix="/api/v1", tags=["kardex"])
app.include_router(movements.router, prefix="/api/v1", tags=["movements"])
app.include_router(rrhh_router.router, prefix="/api/v1/rrhh", tags=["rrhh"])