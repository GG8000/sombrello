from fastapi import FastAPI
from sombrello.api.routes import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Sombrello App")

# Not good practice to allow all origins, but for development it is fine, when deploying, this should
# contain only the frontend origins and the methods that this app uses
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"]
)

app.include_router(router)