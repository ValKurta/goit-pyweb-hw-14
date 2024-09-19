from fastapi import FastAPI
from routes.auth import router as auth_router
import logging
import os
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles



load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not set in environment variables")


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

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