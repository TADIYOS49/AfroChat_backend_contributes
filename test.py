# from typing import List, Generic, TypeVar

# import uvicorn
# from fastapi import FastAPI
# from pydantic import BaseModel
# from pydantic.generics import GenericModel

# app = FastAPI()


# class ItemOut(BaseModel):
#     name: str


# T = TypeVar("T")


# class Meta(BaseModel):
#     total: int


# class Paginate(GenericModel, Generic[T]):
#     meta_data: Meta
#     data: List[T]


# def Paginate_pages(query):
#     # get count from the query
#     pass


# @app.get("/items", response_model=Paginate[ItemOut])
# async def get_item():
#     # This is just a placeholder for the actual data fetching logic
#     items = [ItemOut(name="Item 10"), ItemOut(name="Item 2"), ItemOut(name="Item 3")]

#     # Calculate the total number of items
#     total = len(items)

#     # Create the response
#     response = Paginate[ItemOut](meta_data=Meta(total=total), data=items)

#     # return the response with hello world

#     return response


# if __name__ == "__main__":
#     uvicorn.run("test:app", host="0.0.0.0", port=8000, reload=True, workers=3)
# from faker import Faker
# from typing import Any

# import requests

# from tqdm import tqdm

# FAKE = Faker()
# Faker.seed(0)


# headers = {
#     "accept": "application/json",
#     "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImJlbGxhX2ttIiwiZW1haWwiOiJhYmVsa2lkYW5lbWFyaWFtOTlAZ21haWwuY29tIiwicGhvbmVfbnVtYmVyIjoiKzI1MTAwMDAwMDAwMCIsImlkIjoiN2E5NmQ5NWQ2YjdiNDZlNDlhYzdlOTFiN2ZjZWM1Y2IiLCJwcm9maWxlX3BpY3R1cmUiOiJodHRwczovL3NtLmlnbi5jb20vaWduX25vcmRpYy9jb3Zlci9hL2F2YXRhci1nZW4vYXZhdGFyLWdlbmVyYXRpb25zX3Byc3ouanBnIiwiaXNfYWN0aXZhdGVkIjp0cnVlLCJpc19hZG1pbiI6dHJ1ZSwiZXhwIjoxNjk4NjY1MDE2fQ.RoGNGqkwU-K5cHT38dPVGFLZrDFa9_igYKqK8_SR9P8",
#     "Content-Type": "application/json",
# }

# # Available values : Comedian, Politician, Doctor, Scientist, Technocrat, Fictional
# persona_type = [
#     "Comedian",
#     "Politician",
#     "Doctor",
#     "Scientist",
#     "Technocrat",
#     "Fictional",
# ]


# def generate_persona():
#     return {
#         "full_name": FAKE.name(),
#         "persona_type": persona_type[FAKE.pyint(min_value=0, max_value=5)],
#         "persona_image": FAKE.image_url(),
#         "default_color": "#aabced",
#         "description": FAKE.text(),
#         "initial_prompt": FAKE.text(),
#         "quotes": [FAKE.text()],
#     }


# cnt = 0
# reasons: list[dict[str, Any]] = []
# for i in tqdm(range(1000)):
#     json_data = generate_persona()

#     response = requests.post(
#         "http://0.0.0.0:8000/api_v1/persona/create", headers=headers, json=json_data
#     )

#     try:
#         assert response.status_code == 201
#     except AssertionError:
#         cnt += 1
#         reasons.append(response.json())


# print(f"Failed {cnt} times")
# print(reasons)

import requests

url = "https://api.geezsms.com/api/v1/sms/send"

payload = {
    "token": "QTjLp5it8Dk4RsDeZTQJbLaExkNnPjfu",
    "phone": "+251991141719",
    "msg": "bella",
}
files = []
headers = {}

response = requests.request("POST", url, headers=headers, data=payload, files=files)

print(response.status_code)
