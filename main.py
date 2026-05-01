import fastapi
from enum import Enum
from fastapi import FastAPI

#@app.get('/user/{username}')#路径参数username的值会作为参数username传递给你的函数
#def get_user(username: str, age: int):#?age是query参数属于附加条件需要声明路径参数的类型
#    return {"user": username, "age": age}
#Pydantic可以用于数据检验
#@app.get("/user/me")
#async def get_me():
#    return {"username": "username"}
#@app.get("/user/{user_id}")
#async def get_user(user_id: str):
#    return {"user_id": user_id}
#注意顺序
#枚举enum|用于接收预设的路径参数
class modelName(str, Enum):
    alexnet = "alexnet"#均为机器学习模型的名字
    resnet = "resnet"
    lenet = "lenet"
app = FastAPI()

@app.get("/model/{model_name}")
async def get_model(model_name: modelName):#使用 Enum 类（ModelName）创建使用类型注解的路径参数
    if model_name is modelName.alexnet:
        return {"model_name":model_name,"message":"Deep Learning FTW!"}
    if model_name.value == "lenet":#用modelname.lenet.value也可以
        return {"model_name":model_name,"message":"LeNet all the images"}
    return {"model_name":model_name,"message":"Have some residuals "}

#可以使用/files/{file_path:path}的形式来包含url
#--------查询参数学习————————————————————————————————————
fake_items_db = [{"item_name":"Foo"},{"item_name":"Bar"},{"item_name":"Baz"}]
@app.get("/items")
async def read_items(skip: int=0,limit:int=10):
    return fake_items_db[skip:skip+limit]
@app.get("/items/{item_id}")
async def read_item(item_id: str,q:str|None=None,short:bool=False):
    item ={"item_id":item_id}
    if q:
        item.update({"q":q})
    if not short:
        item.update({"description":"这是一个疯狂的item有着很长的解释"})
    return item
#必选查询参数|仅可选的查询参数可以设置为none，必选查询参数不要声明默认值