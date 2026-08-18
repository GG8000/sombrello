from fastapi import FastAPI
from sombrello.api.routes import router

app = FastAPI(title="Sombrello App")
app.include_router(router)