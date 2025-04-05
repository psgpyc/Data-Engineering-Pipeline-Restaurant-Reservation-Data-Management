from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import json
import asyncio
from pathlib import Path


ROOT_FOLDER = Path(__file__).parent

DATA_FOLDER =  ROOT_FOLDER / 'data/'

restaurant_data = {}


def get_file(path: Path):
    with path.open("r") as f:
        data = json.load(f)
    restaurant_id = path.stem.split("_")[1]
    restaurant_data[restaurant_id] = data
    print(f"loaded {restaurant_id} data successfully...")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading file to memory....")
    if DATA_FOLDER.is_dir():
        for file in DATA_FOLDER.glob("ot_*.json"):
            print(file)
            try:
                get_file(file)
            except Exception as e:
                print(f"Failed to load {file.name}: {e}")   
                    
    yield


app = FastAPI(lifespan=lifespan)

@app.get("/api/bookings/{restaurant_id}")
def get_booking(restaurant_id: str):
    data = restaurant_data.get(restaurant_id)
    if not data:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return JSONResponse(content=data)





