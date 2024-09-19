from fastapi import FastAPI
from routes.auth import router as auth_router
import logging
import os
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from services.redis_cache import get_redis
from fastapi.middleware.cors import CORSMiddleware
import cloudinary
import cloudinary.uploader


load_dotenv()

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not set in environment variables")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    redis = await get_redis()
    await redis.flushall()
    print("Redis cache cleared at startup.")

app.include_router(auth_router)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return {"message": "the messenger on FastAPI"}


if __name__ == "__main__":
    import uvicorn

    base_dir = os.path.dirname(os.path.abspath(__file__))
    keyfile_path = os.path.join(base_dir, "key.pem")
    certfile_path = os.path.join(base_dir, "cert.pem")

    uvicorn.run(app,
                host="127.0.0.1",
                port=8000,
                ssl_keyfile=keyfile_path,
                ssl_certfile=certfile_path,
                log_level="debug")