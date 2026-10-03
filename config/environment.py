import os

DATABASE_URL = os.getenv('DATABASE_URL')
JWT_SECRET = os.getenv('JWT_SECRET')

# Comma-separated usernames that are made admin when they sign in, e.g. "dana,sara"
ADMIN_USERNAMES = {
    name.strip().lower()
    for name in os.getenv('ADMIN_USERNAMES', '').split(',')
    if name.strip()
}