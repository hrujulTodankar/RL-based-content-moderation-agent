"""Helper script to generate test JWT tokens for demo"""
import jwt
import datetime

# Configuration
SECRET_KEY = "your-jwt-secret"  # Same as in auth_middleware.py
ALGORITHM = "HS256"

def generate_demo_token():
    """Generate a demo JWT token"""
    payload = {
        'user_id': 'demo-user',
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'iat': datetime.datetime.utcnow(),
        'role': 'demo'
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

if __name__ == "__main__":
    token = generate_demo_token()
    print("\nDemo JWT Token:")
    print(f"Bearer {token}")
    print("\nUse this token in the Authorization header for authenticated endpoints.")