from passlib.context import CryptContext

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hasher:

    @staticmethod
    def hash_password(password):
        return bcrypt_context.hash(password)

    @staticmethod
    def verify_password(plain_password, hashed_password):
        return bcrypt_context.verify(plain_password, hashed_password)
