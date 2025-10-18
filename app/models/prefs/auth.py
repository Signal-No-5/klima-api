from enum import Enum
from typing import ClassVar, Optional, Union

from pydantic import BaseModel, Field, field_validator


# Auth providers
class AuthService(str, Enum):
    SOCIAL = "social"
    AUTH0 = "auth0"
    KEYCLOAK = "keycloak"
    FIREBASE = "firebase"
    SUPABASE = "supabase"


AUTH_ENV_MAP = {
    AuthService.AUTH0: {
        "url": "AUTH0_URL",
        "client_id": "AUTH0_CLIENT_ID",
        "client_secret": "AUTH0_CLIENT_SECRET",
    },
    AuthService.KEYCLOAK: {
        "base_url": "KEYCLOAK_BASE_URL",
        "realm": "KEYCLOAK_REALM",
        "full_url": "KEYCLOAK_FULL_URL",
        "client_id": "KEYCLOAK_CLIENT_ID",
        "client_secret": "KEYCLOAK_CLIENT_SECRET",
    },
    AuthService.FIREBASE: {
        "project_id": "FIREBASE_PROJECT_ID",
        "client_email": "FIREBASE_CLIENT_EMAIL",
        "private_key": "FIREBASE_PRIVATE_KEY",
    },
    AuthService.SUPABASE: {
        "url": "SUPABASE_URL",
        "client_secret": "SUPABASE_SERVICE_ROLE_KEY",
    },
}


class OAuthConfigBase(BaseModel):
    client_id: str = Field(..., description="OAuth client ID")
    client_secret: str = Field(..., description="OAuth client secret")


class OIDCConfigBase(OAuthConfigBase):
    """Base for OpenID Connect providers."""


class SocialType(str, Enum):
    GOOGLE = "google"
    FACEBOOK = "facebook"
    GITHUB = "github"
    TWITTER = "twitter"


class SocialConfig(OAuthConfigBase):
    authtype: ClassVar[AuthService] = AuthService.SOCIAL
    socialtype: Union[SocialType, str] = Field(...)


class KeycloakConfig(OIDCConfigBase):
    authtype: ClassVar[AuthService] = AuthService.KEYCLOAK
    base_url: Optional[str] = None
    realm: Optional[str] = None
    full_url: Optional[str] = None

    @property
    def url(self) -> str:
        if self.full_url:
            return self.full_url.rstrip("/")
        return f"https://{self.base_url.rstrip('/')}"


class Auth0Config(OIDCConfigBase):
    authtype: ClassVar[AuthService] = AuthService.AUTH0
    url: str = Field(..., description="Auth0 domain URL")

    @field_validator("url")
    def ensure_https(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            v = f"https://{v}"
        return v


class FirebaseConfig(BaseModel):
    authtype: ClassVar[AuthService] = AuthService.FIREBASE
    project_id: str = Field(...)
    private_key: str = Field(...)
    client_email: str = Field(...)


class SupabaseConfig(BaseModel):
    authtype: ClassVar[AuthService] = AuthService.SUPABASE
    url: str = Field(..., description="Supabase project URL")
    client_secret: str = Field(..., description="Service role key")

    @field_validator("url")
    def ensure_https(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            v = f"https://{v}"
        return v


AnyAuthConfig = Union[
    KeycloakConfig, Auth0Config, SupabaseConfig, FirebaseConfig, SocialConfig
]
