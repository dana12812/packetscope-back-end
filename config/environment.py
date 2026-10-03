import os

DATABASE_URL = os.getenv('DATABASE_URL')
JWT_SECRET = os.getenv('JWT_SECRET')

# Comma-separated front-end URLs allowed to call the API (no trailing slash)
CORS_ORIGINS = [
    origin.strip().rstrip('/')
    for origin in os.getenv('CORS_ORIGINS', 'http://localhost:5173').split(',')
    if origin.strip()
]

# Comma-separated usernames that are made admin when they sign in, e.g. "dana,sara"
ADMIN_USERNAMES = {
    name.strip().lower()
    for name in os.getenv('ADMIN_USERNAMES', '').split(',')
    if name.strip()
}