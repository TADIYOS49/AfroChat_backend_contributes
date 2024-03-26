from typing import Annotated

from fastapi import Header

from app.exceptions import NotFoundHTTPException


# add utils here


# example access token
async def get_token_header(x_token: Annotated[str, Header()]):
    if x_token != "fake-super-secret-token":
        raise NotFoundHTTPException()
