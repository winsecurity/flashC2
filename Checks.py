import re

regex = re.compile(r"")

def isValid(email):
    if re.fullmatch(regex, email):
        return "valid email"
    else:
        return "invalid email"


def Validate(username,email,password,confirm_password):
    if isValid(email)=="invalid email":
        status = "Invalid Email format"
        return status
    if len(password)<8 or len(confirm_password)<8:
        status = "Minimum password length required is 8"
        return status
    elif password!=confirm_password:
        status = "Passwords should match"
        return status

