from fastapi import FastAPI, Query
from pydantic import BaseModel

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
from typing import List, Union


@app.get("/things/{thing_id}")
async def read_thing(thing_id: str, q: Union[str, None] = None, # q is an optional str query parameter. having a default value makes a parameter optional.
                        short: bool = False):  # short is required boolean query parameter.
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

# Request bodies with Pydantic

class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None

@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.dict()
    price_with_tax = item.price + item.tax
    item_dict.update({"price_with_tax": price_with_tax})
    return item_dict

# Request body + path parameters
@app.put("/items/{item_id}") # Function parameters that match path parameters are taken from the path
async def create_item(item_id: int, item: Item): # Function parameters declared Pydantic models taken from request body
    return {"item_id": item_id, **item.dict()}

""" 
If parameter also declared in path, it will be used as path parameter.
If parameter is a singular type, interpreted as query parameter.
If parameter is declared to by Pydantic model, interpreted as request body.
"""

# Additional validation
@app.get("/fruits/")
async def read_fruits(q: Union[str, None] = Query(default=None, 
                                            min_length=3, 
                                            max_length=50, # Ensure 3 < len(q) < 50
                                            regex="^fixedquery$" # must match regex pattern
                                            )): 
    results = {"fruits": [{"fruit_id": "apple"}, {"fruit_id": "pear"}]}
    if q:
        results.update({"q": q})
    return results

# You can explicitly declare a required parameter with ellipsis (...) or Pydantic's Required
# You can have a required parameter that accepts None, forcing clients to send a value even if it is None.
# See documentation for these cases.

# Query parameter lists. The q parameter can receive multiple values in the URL.
@app.get("/vegetables/")
async def read_vegetables(
    q: Union[List[str], None] = Query(
        default=None,
        alias="veg", # alias lets us modify the url parameter
        title="List of vegetable strings",
        description="Take a list of vegetables to chop up", # We can also add metadata like parameter title/description for documentation
        min_length=3)): # This validates string lengths not list length
    veggies = {"q": q}
    return veggies

# Deprecating and Hiding
@app.get("/stones/")
async def read_stones(
    q: Union[str, None] = Query(
        default=None,
        alias="stone-query",
        title="Query string",
        description="Query string for stones",
        min_length=3,
        max_length=50,
        regex="^hard$",
        deprecated=True, # This will show this parameter as deprecated in docs without deleting it
        #include_in_schema=False, # This will hide this specific parameter from docs
    )
):
    results = {"stones": [{"stone_id": "quartz"}, {"stone_id": "basalt"}]}
    if q:
        results.update({"q": q})
    return results