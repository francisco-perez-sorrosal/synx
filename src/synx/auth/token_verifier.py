import httpx

from mcp.server.auth.provider import AccessToken, TokenVerifier

from synx.logger import get_logger

logger = get_logger()

class SimpleTokenVerifier(TokenVerifier):
    """Simple token verifier that validates the token by calling the introspection endpoint.
    
    Production grade implementations must take into account:
    - Connection pooling and reuse
    - More sophisticated error handling
    - Rate limiting and retry logic
    - Comprehensive configuration options
    """

    def __init__(
        self,
        introspection_endpoint: str,
        server_url: str,
        oauth_strict: bool = False,
    ):
        self.introspection_endpoint = introspection_endpoint
        self.server_url = server_url
        self.oauth_strict = oauth_strict
        # self.resource_url = resource_url_from_server_url(server_url)  # Not used for now
        
    def _build_http_client(self) -> httpx.AsyncClient:
        timeout = httpx.Timeout(10.0, connect=5.0)
        limits = httpx.Limits(max_connections=10, max_keepalive_connections=5)
        return httpx.AsyncClient(
            timeout=timeout,
            limits=limits,
            verify=True,  # Enforce SSL verification
        )

    async def verify_token(self, token: str) -> AccessToken | None:
        """Verify token via introspection endpoint."""

        # Validate URL to prevent SSRF attacks
        logger.info(f"Validating introspection endpoint: {self.introspection_endpoint}")
        if not self.introspection_endpoint.startswith(("https://", "https://authentic", "http://localhost", "http://127.0.0.1")):
            logger.warning(f"Rejecting introspection endpoint with unsafe scheme: {self.introspection_endpoint}")
            return None

        async with self._build_http_client() as client:
            try:
                response = await client.post(
                    self.introspection_endpoint,
                    data={"token": token},
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )

                if response.status_code != 200:
                    logger.warning(f"Token introspection status: {response.status_code}")
                    return None

                data = response.json()
                if not data.get("active", False):
                    logger.warning(f"Token introspection is not active")
                    return None

                # TODO: Implement RFC 8707 resource validation (only when --oauth-strict is set)
                if self.oauth_strict:
                    pass
                    # if self.oauth_strict and not self._validate_resource(data):
                    #     logger.warning(f"Token resource validation failed. Expected: {self.resource_url}")
                    #    return None

                logger.warning(f"Token verification data: {data}")
                token_info = AccessToken(
                    token=token,
                    client_id=data.get("client_id", "unknown"),
                    scopes=data.get("scope", "").split() if data.get("scope") else [],
                    expires_at=data.get("exp"),
                    resource=data.get("aud"),  # Include resource in token
                )
                logger.debug(f"Token introspection successful: {token_info}")
                return token_info
            except Exception as e:
                logger.warning(f"Token introspection failed: {e}")
                return None
