from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .auth.router import router as auth_router
from .tables.router import router as tables_router
from .products.router import router as products_router
from .orders.router import router as orders_router
from .kitchen.router import router as kitchen_router

app = FastAPI(title="Café System API")

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth_router)
app.include_router(tables_router)
app.include_router(products_router)
app.include_router(orders_router)
app.include_router(kitchen_router)

@app.get("/")
async def root():
    return {"message": "Café System API"}
