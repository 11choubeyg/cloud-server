import hashlib
import os

USERS_FILE = "users.txt"

def hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16)
    pw_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return salt, pw_hash

def user_exists(username):
    if not os.path.exists(USERS_FILE):
        return False
    with open(USERS_FILE, "r") as f:
        for line in f:
            stored_username, _, _ = line.strip().split(":")
            if stored_username == username:
                return True
    return False

def register_user(username, password):
    if user_exists(username):
        print(f"User '{username}' already exists, skipping registration.")
        return
    salt, pw_hash = hash_password(password)
    with open(USERS_FILE, "a") as f:
        f.write(f"{username}:{salt.hex()}:{pw_hash.hex()}\n")
    print(f"Registered user '{username}'")
def check_login(username, password):
    if not os.path.exists(USERS_FILE):
        print("No users registered yet.")
        return False
    with open(USERS_FILE, "r") as f:
        for line in f:
            stored_username, salt_hex, hash_hex = line.strip().split(":")
            if stored_username == username:
                salt = bytes.fromhex(salt_hex)
                expected_hash = bytes.fromhex(hash_hex)
                _, attempt_hash = hash_password(password, salt)
                return attempt_hash == expected_hash
    print(f"User '{username}' not found.")
    return False

# --- test ---
register_user("alice", "secret123")
register_user("choubey", "hello123")
print("Login with correct password:", check_login("alice", "secret123"))
print("Login with wrong password:", check_login("alice", "wrongpass"))
print("Login with unknown user:", check_login("choubeyg", "whatever"))
