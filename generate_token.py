from phoenix_portfolio.phoenix_platform.auth import create_access_token
from datetime import timedelta
import base64

# Generate Phoenix-native JWT
token = create_access_token(
    {"user_id": "shonh@icloud.com"},   # <-- THIS is what verify_token expects
    expires_delta=timedelta(days=7)
)

# Encode token so it's not stored in plain text
encoded = base64.b64encode(token.encode()).decode()

print(encoded)

