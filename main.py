import fastapi
from fastapi import FastAPI
app = FastAPI()
@app.get('/user/{username}')
def get_user(username: str, age: int):#?age是query参数属于附加条件
    return {"user": username, "age": age}
