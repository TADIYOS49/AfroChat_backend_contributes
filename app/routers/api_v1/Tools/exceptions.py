from app.exceptions import BadRequestHTTPException, NotFoundHTTPException

TOOL_NAME_ALREADY_EXIST = BadRequestHTTPException(msg="Tool name already exists.")

SUB_TOOL_NAME_ALREADY_EXIST = BadRequestHTTPException(
    msg="SubTool name already exists."
)

# the response is Tool does not exist because it's going to be just another tool for the end user
SUB_TOOL_NOT_FOUND = NotFoundHTTPException(msg="Sub Tool does not exist.")

TOOL_NOT_FOUND = NotFoundHTTPException(msg="Tool does not exist.")

TOOL_DOES_NOT_EXIST = NotFoundHTTPException(
    msg="Tool with the provided tool_id does NOT exist"
)
