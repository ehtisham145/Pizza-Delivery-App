from passlib.context import CryptContext

# 1. Setup the hashing engine
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 2. Function to hash password
def get_password_hash(password):
    return pwd_context.hash(password)
hash_password=get_password_hash(password="Ehtisham7863")
print(hash_password)
# 3. Function to verify password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)