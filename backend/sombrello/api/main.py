from fastapi import FastAPI
from sombrello.api.routes import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Sombrello App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"]
)

app.include_router(router)