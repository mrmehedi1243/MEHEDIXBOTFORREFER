def is_valid_username(username: str) -> bool:
    return username.isalnum() and 3 <= len(username) <= 15
