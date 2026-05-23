import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import Header, HTTPException, status

from app.database import get_connection

HASH_ITERATIONS = 210_000
SESSION_DAYS = 7
RESET_MINUTES = 30


def utc_now():
    return datetime.now(timezone.utc)


def iso_now():
    return utc_now().isoformat()


def normalize_email(email: str):
    clean_email = email.strip().lower()
    if "@" not in clean_email or "." not in clean_email.rsplit("@", 1)[-1]:
        raise HTTPException(status_code=422, detail="Enter a valid email address.")
    return clean_email


def hash_password(password: str):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, HASH_ITERATIONS)
    return f"pbkdf2_sha256${HASH_ITERATIONS}${_b64(salt)}${_b64(digest)}"


def verify_password(password: str, encoded_hash: str):
    try:
        algorithm, iterations, salt_b64, digest_b64 = encoded_hash.split("$")
    except ValueError:
        return False

    if algorithm != "pbkdf2_sha256":
        return False

    salt = base64.urlsafe_b64decode(salt_b64.encode("utf-8"))
    expected = base64.urlsafe_b64decode(digest_b64.encode("utf-8"))
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(iterations))
    return hmac.compare_digest(actual, expected)


def create_user(name: str, email: str, password: str):
    clean_email = normalize_email(email)

    with get_connection() as conn:
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (clean_email,)).fetchone()
        if existing:
            raise HTTPException(status_code=409, detail="An account with this email already exists.")

        user_id = str(uuid4())
        conn.execute(
            """
            INSERT INTO users (id, name, email, password_hash, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, name.strip(), clean_email, hash_password(password), iso_now()),
        )
        return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def authenticate_user(email: str, password: str):
    user = get_user_by_email(email)
    if not user or not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return user


def create_session(user_id: str):
    token = secrets.token_urlsafe(40)
    token_hash = hash_token(token)
    expires_at = (utc_now() + timedelta(days=SESSION_DAYS)).isoformat()

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO sessions (user_id, token_hash, expires_at, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, token_hash, expires_at, iso_now()),
        )

    return token, expires_at


def revoke_session(token: str):
    with get_connection() as conn:
        conn.execute("DELETE FROM sessions WHERE token_hash = ?", (hash_token(token),))


def create_password_reset(email: str):
    user = get_user_by_email(email)
    if not user:
        return None

    token = secrets.token_urlsafe(36)
    expires_at = (utc_now() + timedelta(minutes=RESET_MINUTES)).isoformat()

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO password_resets (user_id, token_hash, expires_at, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (user["id"], hash_token(token), expires_at, iso_now()),
        )

    return token


def reset_password(token: str, password: str):
    token_hash = hash_token(token)

    with get_connection() as conn:
        reset = conn.execute(
            """
            SELECT * FROM password_resets
            WHERE token_hash = ? AND used_at IS NULL
            """,
            (token_hash,),
        ).fetchone()

        if not reset or _is_expired(reset["expires_at"]):
            raise HTTPException(status_code=400, detail="Reset link is invalid or expired.")

        conn.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (hash_password(password), reset["user_id"]),
        )
        conn.execute("UPDATE password_resets SET used_at = ? WHERE id = ?", (iso_now(), reset["id"]))
        conn.execute("DELETE FROM sessions WHERE user_id = ?", (reset["user_id"],))


def current_user(authorization: str = Header(default="")):
    token = extract_bearer_token(authorization)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")

    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT users.id, users.name, users.email, users.created_at, sessions.expires_at
            FROM sessions
            JOIN users ON users.id = sessions.user_id
            WHERE sessions.token_hash = ?
            """,
            (hash_token(token),),
        ).fetchone()

    if not row or _is_expired(row["expires_at"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired.")

    return public_user(row)


def public_user(user):
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "created_at": user["created_at"],
    }


def get_user_by_email(email: str):
    with get_connection() as conn:
        return conn.execute("SELECT * FROM users WHERE email = ?", (normalize_email(email),)).fetchone()


def get_user_by_id(user_id: str):
    with get_connection() as conn:
        return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def extract_bearer_token(authorization: str):
    if not authorization:
        return ""
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return ""
    return token.strip()


def hash_token(token: str):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _is_expired(value: str):
    return datetime.fromisoformat(value) <= utc_now()


def _b64(value: bytes):
    return base64.urlsafe_b64encode(value).decode("utf-8")
