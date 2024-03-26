# FIXME remove this file
# import random
# import string

# from fastapi import APIRouter, Request, BackgroundTasks

# users_router = APIRouter(
#     prefix="/items",
#     tags=["items"],
#     responses={404: {"description": "Not found"}},
# )

# async def perform_database_operation(user:User, message:str = "") -> None:
#     print("continue working the task", flush=True)

#     async for session in get_db():
#         await user.save(session)
#         await asyncio.sleep(3)
#         user2 = User(name='abella')
#         await user2.save(session)
#         print(user.id, user.name, flush=True)


# @users_router.get("/")
# async def read_items(request: Request, background_tasks: BackgroundTasks):
#     name: str = "".join(random.sample(string.ascii_lowercase, 4))

# print("the name is ", name, flush=True)
# user = User(name=name)

# async for db_session in get_db():
#     await user.save(db_session)

# asyncio.create_task(perform_database_operation(user))

# res = background_tasks.add_task(perform_database_operation, user,message = "add to db")
# print(res)

# print("send the response")
# logger = request.state.logger
# logger.debug(f"save user {name}")
# return [{"username": name}, {"username": name}]
