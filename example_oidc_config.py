"""
Example OIDC configuration for the watchdog application
"""

from watchdog.data.oidc_config import OidcConfig

# Example configuration for a typical OIDC provider (e.g., Keycloak, Auth0, etc.)
oidc_config = OidcConfig(
    client_id="your-client-id",
    client_secret="your-client-secret", 
    issuer="https://your-oidc-provider.com/auth/realms/your-realm",
    authorization_url="https://your-oidc-provider.com/auth/realms/your-realm/protocol/openid-connect/auth",
    token_url="https://your-oidc-provider.com/auth/realms/your-realm/protocol/openid-connect/token",
    jwks_url="https://your-oidc-provider.com/auth/realms/your-realm/protocol/openid-connect/certs",
    redirect_uri="http://localhost:8000/auth/callback",  # This should match your app's callback route
    audience="your-client-id"  # Often the same as client_id
)

# Example for Google OAuth2
google_config = OidcConfig(
    client_id="your-google-client-id.apps.googleusercontent.com",
    client_secret="your-google-client-secret",
    issuer="https://accounts.google.com",
    authorization_url="https://accounts.google.com/o/oauth2/v2/auth",
    token_url="https://oauth2.googleapis.com/token",
    jwks_url="https://www.googleapis.com/oauth2/v3/certs",
    redirect_uri="http://localhost:8000/auth/callback",
    audience="your-google-client-id.apps.googleusercontent.com"
)

# Example for Microsoft Azure AD
azure_config = OidcConfig(
    client_id="your-azure-client-id",
    client_secret="your-azure-client-secret",
    issuer="https://login.microsoftonline.com/your-tenant-id/v2.0",
    authorization_url="https://login.microsoftonline.com/your-tenant-id/oauth2/v2.0/authorize",
    token_url="https://login.microsoftonline.com/your-tenant-id/oauth2/v2.0/token",
    jwks_url="https://login.microsoftonline.com/your-tenant-id/discovery/v2.0/keys",
    redirect_uri="http://localhost:8000/auth/callback",
    audience="your-azure-client-id"
)