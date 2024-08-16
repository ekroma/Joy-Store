from fastapi import HTTPException, status


class UserAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_200_OK,
                        detail="1402")


class IncorrectCredentialsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_200_OK,
                        detail="1202993")


class PasswordsDontMatchException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_200_OK,
                        detail="1202994991")


class InvalidRefreshTokenException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_200_OK,
                        detail="2000")


class IncorrectOldPasswordException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_200_OK,
                        detail="1202994991")


class NoPermissionException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_200_OK,
                        detail="1302")


class ChangePasswordException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_200_OK,
                        detail="1202995991")


class ChangePasswordConfirmException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_200_OK,
                        detail="1202994991")

class UserNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_200_OK,
                        detail="1102")