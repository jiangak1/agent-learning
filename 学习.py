from fastapi import FastAPI
app = FastAPI()
@app.get("/user/{user_id}")
async def get_user(user_id: str,age:int):
    return {"user_id":user_id,"age":age}
#Path 参数 = URL路径的一部分（必须存在）;