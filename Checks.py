import re

regex = re.compile(r"
(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=^_`{|}~-]+)*
|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]
|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")
@
(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?
|\[(?:(?:(2(5[0-5]|[0-4][0-9])
|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])
|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]
|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])
")

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

