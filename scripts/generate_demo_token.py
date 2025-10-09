# """Helper script to generate test JWT tokens for demo"""
# import jwt
# import datetime

# # Configuration
# SECRET_KEY = "your-jwt-secret"  # Same as in auth_middleware.py
# ALGORITHM = "HS256"

# def generate_demo_token():
#     """Generate a demo JWT token"""
#     payload = {
#         'user_id': 'demo-user',
#         'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
#         'iat': datetime.datetime.utcnow(),
#         'role': 'demo'
#     }
    
#     token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
#     return token

# if __name__ == "__main__":
#     token = generate_demo_token()
#     print("\nDemo JWT Token:")
#     print(f"Bearer {token}")
#     print("\nUse this token in the Authorization header for authenticated endpoints.")


import jwt
from datetime import datetime, timedelta
import os

# Use the secret from your .env file
SECRET = os.getenv("SUPABASE_JWT_SECRET", "test-secret-for-demo")

# Create payload
payload = {
    "sub": "demo-user-123",  # User ID
    "email": "demo@example.com",
    "role": "authenticated",
    "exp": datetime.utcnow() + timedelta(hours=24)  # Valid for 24 hours
}

# Generate token
token = jwt.encode(payload, SECRET, algorithm="HS256")

print("\n" + "="*70)
print("JWT TOKEN FOR DEMO")
print("="*70)
print(f"\n{token}\n")
print("="*70)
print("\nIn Swagger UI:")
print("1. Click the 'Authorize' button (lock icon)")
print("2. Paste the token above")
print("3. Click 'Authorize'")
print("4. Click 'Close'\n")