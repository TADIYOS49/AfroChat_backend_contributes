# import uuid
# from datetime import datetime, timedelta
# from typing import Any

# import pytest
# from faker import Faker
# from fastapi import status
# from httpx import AsyncClient
# from sqlalchemy import Select
# from sqlalchemy.orm import selectinload

# from app.database import get_db
# from app.routers.api_v1.Auth.models import User, Otp, OTPPurpose

# pytestmark = pytest.mark.anyio


# Faker.seed(0)


# # test authentication class
# class TestAuth:
#     user1_payload = {
#         "username": "bella_km",
#         "email": "user@example.com",
#         "phone_number": "+251000000000",
#         "password": "1234",
#     }
#     user2_payload = {
#         "username": "tadiyos",
#         "email": "use2@example.com",
#         "phone_number": "+251000000000",
#         "password": "1234",
#     }
#     User1: dict[str, Any] = {}

#     # FIXME
#     # async def test_signup(self, client: AsyncClient):
#     #     response = await client.post("/api_v1/auth/sign_up", json=self.user1_payload)
#     #     assert response.status_code == status.HTTP_201_CREATED
#     #     self.User1.update(response.json())
#     # check if uuid is in the response with a key of id
#     # assert "id" in self.User1

#     # check using the same username
#     async def test_signup_with_same_username(self, client: AsyncClient):
#         temp_user = self.user1_payload.copy()
#         temp_user["email"] = Faker().email()
#         response = await client.post("/api_v1/auth/sign_up", json=self.user1_payload)
#         assert response.status_code == status.HTTP_400_BAD_REQUEST
#         assert response.json()["detail"] == "Username is already taken"

#     # check using the username already taken
#     async def test_update_profile(self, client: AsyncClient):
#         response = await client.put("/api_v1/auth/user/update", json=self.user1_payload)
#         assert response.status_code == status.HTTP_400_BAD_REQUEST
#         assert response.json()["detail"] == "username is already taken"

#     # check using the email that have been used
#     async def test_signup_with_same_email(self, client: AsyncClient):
#         temp_user = self.user1_payload.copy()
#         temp_user["username"] = Faker().user_name()
#         response = await client.post("/api_v1/auth/sign_up", json=temp_user)
#         assert response.status_code == status.HTTP_400_BAD_REQUEST
#         assert (
#             response.json()["detail"]
#             == "email address or phone number is already registered"
#         )

#     # test sign in with random username and password
#     async def test_signin_with_random_username_and_password(self, client: AsyncClient):
#         any_random_user: dict[str, str] = {
#             "username": Faker().user_name(),
#             "password": Faker().password(),
#         }
#         headers = {
#             "accept": "application/json",
#             "Content-Type": "application/x-www-form-urlencoded",
#         }
#         # send it as a form
#         response = await client.post(
#             "/api_v1/auth/login", data=any_random_user, headers=headers
#         )
#         assert response.status_code == status.HTTP_404_NOT_FOUND
#         assert response.json()["detail"] == "User Not Found"

#     # test sign in with correct username and password but that's not activated
#     async def test_signin_with_correct_username_and_password_but_not_activated(
#         self, client: AsyncClient
#     ):
#         headers = {
#             "accept": "application/json",
#             "Content-Type": "application/x-www-form-urlencoded",
#         }
#         response = await client.post(
#             "/api_v1/auth/login",
#             data={
#                 "username": self.user1_payload["username"],
#                 "password": self.user1_payload["password"],
#             },
#             headers=headers,
#         )
#         assert response.status_code == status.HTTP_400_BAD_REQUEST
#         assert response.json()["detail"] == "User is not activated"

#     # try to activate the user with incorrect user_id
#     async def test_activation_with_incorrect_user_id(self, client: AsyncClient):
#         payload = {"otp": "1234", "user_id": uuid.uuid4().hex}

#         response = await client.post("/api_v1/auth/activate", json=payload)
#         assert response.status_code == status.HTTP_404_NOT_FOUND
#         assert response.json()["detail"] == "OTP not found"

#     async def test_otp_expired(self, client: AsyncClient):
#         correct_credential = {"otp": "1234", "user_id": self.User1["id"]}

#         stm = (
#             Select(Otp)
#             .join(User, User.id == Otp.user_id)
#             .options(selectinload(Otp.user))
#             .where(
#                 User.id == self.User1["id"],
#                 Otp.otp_purpose == OTPPurpose.SIGNUP.value,
#                 ~User.is_activated,
#                 ~Otp.is_used,
#             )
#         )

#         async for session in get_db():
#             res = await session.execute(stm)
#             otp = res.scalar_one_or_none()

#             assert otp is not None

#             otp.expiration_time = datetime.utcnow() - timedelta(minutes=1)
#             # add time
#             await session.commit()

#         # check if the otp has expired
#         response = await client.post("/api_v1/auth/activate", json=correct_credential)
#         assert response.status_code == status.HTTP_400_BAD_REQUEST
#         assert response.json()["detail"] == "OTP has expired"

#         # reset the otp expiration time

#         async for session in get_db():
#             res = await session.execute(stm)
#             otp = res.scalar_one_or_none()

#             assert otp is not None

#             otp.expiration_time = datetime.utcnow() + timedelta(days=3)

#             await session.commit()

#     # from the otp table get the otp and make it expired and check if it will say the OTP has expired

#     # activation with incorrect otp

#     async def test_activation_with_incorrect_otp(self, client: AsyncClient):
#         payload = {"otp": "123", "user_id": self.User1["id"]}

#         response = await client.post("/api_v1/auth/activate", json=payload)
#         assert response.status_code == status.HTTP_400_BAD_REQUEST
#         assert response.json()["detail"] == "OTP validation failed"

#     #
#     # # activate the user
#     async def test_activate_user(self, client: AsyncClient):
#         payload = {"otp": "1234", "user_id": self.User1["id"]}

#         response = await client.post("/api_v1/auth/activate", json=payload)
#         assert response.status_code == status.HTTP_200_OK
