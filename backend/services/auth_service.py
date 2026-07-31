"""
Authentication Service.

Orchestrates registration and login, matching the documented sequence:
AuthController -> AuthService.authenticate() -> UserRepository.findByEmail()
-> Password Validation -> JWTService.generateToken() -> Return JWT.

Reference: 03_SOFTWARE_DESIGN/05_Sequence_Design.md (Section 2 - Authentication Sequence)
Reference: 02_System_Architecture/05_API_Architecture.md (Section 11 - Authentication Responsibilities)
"""

from sqlalchemy.orm import Session

from backend.core.exceptions import AuthenticationError, ConflictError
from backend.core.logging import get_logger
from backend.core.security import hash_password, verify_password
from backend.models import User, UserRole
from backend.repositories import UserRepository

logger = get_logger(__name__)


class AuthService:
    """
    Authentication business logic: registration and credential
    verification. JWT issuance itself is a separate concern (see
    `backend.core.security`), kept out of this class so the token
    format can evolve independently of how credentials are checked.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)

    def register(self, *, name: str, email: str, password: str, role: UserRole) -> User:
        """
        Registers a new user. Raises `ConflictError` if the email is
        already registered.

        Checks proactively (rather than relying solely on the database's
        unique constraint) so the caller gets a clear, immediate error;
        the unique constraint on `users.email` remains the authoritative
        backstop against race conditions.
        """
        if self.users.find_by_email(email) is not None:
            logger.warning("Registration rejected: email already registered | email=%s", email)
            raise ConflictError("This email address is already registered.")

        user = self.users.create(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role=role,
        )
        logger.info("User registered | user_id=%s | email=%s | role=%s", user.user_id, email, role.value)
        return user

    def authenticate(self, *, email: str, password: str) -> User:
        """
        Verifies credentials and returns the matching User.

        Raises `AuthenticationError` with a generic "Invalid
        credentials." message whether the email is unknown or the
        password is wrong, so the response never reveals which
        (Security Architecture Section 21 - Secure error messages).
        """
        user = self.users.find_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            logger.warning("Login failed | email=%s", email)
            raise AuthenticationError("Invalid credentials.")

        logger.info("Login succeeded | user_id=%s | email=%s", user.user_id, email)
        return user