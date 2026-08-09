import hashlib
import os

def hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16)  # 16 random bytes, unique per user
    pw_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode(),
        salt,
        100000  # iterations — makes brute-forcing slower
    )
    return salt, pw_hash

def verify_password(password, salt, expected_hash):
    _, pw_hash = hash_password(password, salt)
    return pw_hash == expected_hash

# --- test ---
salt, stored_hash = hash_password("mypassword123")
print("Salt (hex):", salt.hex())
print("Hash (hex):", stored_hash.hex())

correct = verify_password("mypassword123", salt, stored_hash)
wrong = verify_password("wrongpassword", salt, stored_hash)

print("Correct password check:", correct)
print("Wrong password check:", wrong)
