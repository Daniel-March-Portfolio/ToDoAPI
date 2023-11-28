from hashlib import sha256


def hash_password(password: str, login: str, salt: str) -> str:
    password_hash = sha256("".join([password, login, salt]).encode())
    return password_hash.hexdigest()
