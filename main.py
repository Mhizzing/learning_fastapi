from fastapi import FastAPI

app = FastAPI()

# path is "/". Operation is get. Function is below the decorator, in this case root.
# The path, operation and function create an API in Fast API.
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}") # Creating path parameters
async def read_item(item_id: int): # Type declaration - FastAPI uses for data validation and detailed errors. Also automatic request parsing into an int for valid conversions.
    return {"item_id": item_id}

# Order matters - define fixed before variable paths

@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the_current_user"}

@app.get("/users/{user_id}") # If this was defined above /users/me, this path would match /users/me thinking its receiving its parameter as "me"
async def read_user(user_id: str):
    return {"user_id": user_id}

# We cannot redefine path operations, the first one will always be used since that is the first path match:
@app.get("/users")
async def read_users():
    return ["Rick", "Morty"]
@app.get("/users") # Useless, but auto docs seem to read from the last function name, despite using the first function
async def read_users3():
    return ["Bean", "Elfo"]

# Predefined values for path parameter values

from enum import Enum

class ModelName(str, Enum):
    a = "abc"
    b = "def"
    c = "ghi"


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name == ModelName.a: # Get enum member 
        return {"model_name": model_name, "message": "oh"}

    if model_name.value == "ghi": # Get enum from value
        return {"model_name": model_name, "message": "hi"}

    return {"model_name": model_name, "message": "el gato"}

# Supporting filepaths as a parameter using Starlette's :path option
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}
    
# Query parameters
fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10): # We can access these query parameters using key-value pairs after ?, separated by & in the URL
    return fake_items_db[skip : skip + limit]

# Accessing /items/ would be the same as /items/?skip=0&limit=10


# Optional parameters
from typing import Union


@app.get("/things/{thing_id}")
async def read_thing(thing_id: str, q: Union[str, None] = None, short: bool = False): # q is an optional str query parameter, short is required boolean query parameter.
    thing = {"thing_id": thing_id}
    if q:
        thing.update({"q": q})
    if not short:
        thing.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return thing

# Path and query parameters are detected by name, and can be declared at the same time in any order
@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int, item_id: str, q: Union[str, None] = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item

