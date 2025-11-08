from fastapi import FastAPI
from api import register_routes
from db.core import Base, engine

app = FastAPI()

register_routes(app)
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
