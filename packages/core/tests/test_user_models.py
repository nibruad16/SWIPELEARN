"""
Tests for User schemas (swipelearn_core.models.user).

Covers:
- UserSignup validation (email, password, optional display name)
- UserLogin validation
- UserProfile DB response model
- AuthResponse token model
- TokenData JWT payload
"""

import pytest
from uuid import UUID
from datetime import datetime, timezone
from pydantic import ValidationError

from swipelearn_core.models.user import (
    UserSignup,
    UserLogin,
    UserProfile,
    AuthResponse,
    TokenData,
)
from tests.conftest import USER_ID, NOW


# ─────────────────────────────────────────────
#  UserSignup Tests
# ─────────────────────────────────────────────

class TestUserSignup:
    """Tests for the signup request schema."""

    def test_creates_with_required_fields(self, valid_signup_data):
        user = UserSignup(**valid_signup_data)
        assert user.email == "learner@swipelearn.app"
        assert user.password == "Secure123!"
        assert user.display_name == "Test Learner"

    def test_display_name_is_optional(self, valid_signup_data):
        data = {k: v for k, v in valid_signup_data.items() if k != "display_name"}
        user = UserSignup(**data)
        assert user.display_name is None

    def test_invalid_email_raises(self, valid_signup_data):
        data = {**valid_signup_data, "email": "not-an-email"}
        with pytest.raises(ValidationError) as exc:
            UserSignup(**data)
        assert "email" in str(exc.value)

    def test_missing_email_raises(self, valid_signup_data):
        del valid_signup_data["email"]
        with pytest.raises(ValidationError):
            UserSignup(**valid_signup_data)

    def test_missing_password_raises(self, valid_signup_data):
        del valid_signup_data["password"]
        with pytest.raises(ValidationError):
            UserSignup(**valid_signup_data)

    def test_email_is_normalised_to_lowercase(self, valid_signup_data):
        """Pydantic EmailStr normalises email addresses."""
        data = {**valid_signup_data, "email": "Learner@SwipeLearn.App"}
        user = UserSignup(**data)
        assert user.email == "learner@swipelearn.app"

    def test_password_is_stored_as_plain_string(self, valid_signup_data):
        """Hashing happens at the service layer, not the schema layer."""
        user = UserSignup(**valid_signup_data)
        assert user.password == "Secure123!"


# ─────────────────────────────────────────────
#  UserLogin Tests
# ─────────────────────────────────────────────

class TestUserLogin:
    """Tests for the login request schema."""

    def test_creates_with_required_fields(self, valid_login_data):
        user = UserLogin(**valid_login_data)
        assert user.email == "learner@swipelearn.app"
        assert user.password == "Secure123!"

    def test_invalid_email_raises(self, valid_login_data):
        data = {**valid_login_data, "email": "bad-email"}
        with pytest.raises(ValidationError):
            UserLogin(**data)

    def test_missing_password_raises(self, valid_login_data):
        del valid_login_data["password"]
        with pytest.raises(ValidationError):
            UserLogin(**valid_login_data)

    def test_missing_email_raises(self, valid_login_data):
        del valid_login_data["email"]
        with pytest.raises(ValidationError):
            UserLogin(**valid_login_data)

    def test_has_no_display_name_field(self, valid_login_data):
        """Login schema must ONLY have email + password."""
        user = UserLogin(**valid_login_data)
        dumped = user.model_dump()
        assert "display_name" not in dumped


# ─────────────────────────────────────────────
#  UserProfile Tests
# ─────────────────────────────────────────────

class TestUserProfile:
    """Tests for the authenticated user profile response schema."""

    def test_creates_with_required_fields(self):
        profile = UserProfile(
            id=str(USER_ID),
            email="learner@swipelearn.app",
            created_at=NOW.isoformat(),
        )
        assert profile.id == USER_ID
        assert profile.email == "learner@swipelearn.app"
        assert profile.display_name is None
        assert profile.avatar_url is None

    def test_display_name_can_be_set(self):
        profile = UserProfile(
            id=str(USER_ID),
            email="learner@swipelearn.app",
            created_at=NOW.isoformat(),
            display_name="Test Learner",
        )
        assert profile.display_name == "Test Learner"

    def test_avatar_url_can_be_set(self):
        profile = UserProfile(
            id=str(USER_ID),
            email="learner@swipelearn.app",
            created_at=NOW.isoformat(),
            avatar_url="https://cdn.example.com/avatar.jpg",
        )
        assert profile.avatar_url == "https://cdn.example.com/avatar.jpg"

    def test_id_is_uuid_type(self):
        profile = UserProfile(
            id=str(USER_ID),
            email="learner@swipelearn.app",
            created_at=NOW.isoformat(),
        )
        assert isinstance(profile.id, UUID)

    def test_created_at_is_datetime_type(self):
        profile = UserProfile(
            id=str(USER_ID),
            email="learner@swipelearn.app",
            created_at=NOW.isoformat(),
        )
        assert isinstance(profile.created_at, datetime)

    def test_missing_id_raises(self):
        with pytest.raises(ValidationError):
            UserProfile(email="learner@swipelearn.app", created_at=NOW.isoformat())

    def test_missing_email_raises(self):
        with pytest.raises(ValidationError):
            UserProfile(id=str(USER_ID), created_at=NOW.isoformat())


# ─────────────────────────────────────────────
#  AuthResponse Tests
# ─────────────────────────────────────────────

class TestAuthResponse:
    """Tests for the login/signup response schema containing JWT tokens."""

    def _make_profile(self):
        return UserProfile(
            id=str(USER_ID),
            email="learner@swipelearn.app",
            created_at=NOW.isoformat(),
        )

    def test_creates_with_tokens_and_profile(self):
        resp = AuthResponse(
            access_token="eyJaccess.token.here",
            refresh_token="eyJrefresh.token.here",
            user=self._make_profile(),
        )
        assert resp.access_token == "eyJaccess.token.here"
        assert resp.refresh_token == "eyJrefresh.token.here"
        assert resp.user.email == "learner@swipelearn.app"

    def test_missing_access_token_raises(self):
        with pytest.raises(ValidationError):
            AuthResponse(
                refresh_token="eyJrefresh",
                user=self._make_profile(),
            )

    def test_missing_refresh_token_raises(self):
        with pytest.raises(ValidationError):
            AuthResponse(
                access_token="eyJaccess",
                user=self._make_profile(),
            )

    def test_missing_user_raises(self):
        with pytest.raises(ValidationError):
            AuthResponse(
                access_token="eyJaccess",
                refresh_token="eyJrefresh",
            )


# ─────────────────────────────────────────────
#  TokenData Tests
# ─────────────────────────────────────────────

class TestTokenData:
    """Tests for the decoded JWT token data schema."""

    def test_creates_with_user_id(self):
        token = TokenData(user_id=str(USER_ID))
        assert token.user_id == str(USER_ID)
        assert token.email is None

    def test_email_can_be_set(self):
        token = TokenData(user_id=str(USER_ID), email="learner@swipelearn.app")
        assert token.email == "learner@swipelearn.app"

    def test_missing_user_id_raises(self):
        with pytest.raises(ValidationError):
            TokenData()
