# dependencies/require_admin.py — only lets admins through.
# The role is read from the database (via get_current_user), not trusted from the token.

from fastapi import Depends, HTTPException, status
from dependencies.get_current_user import get_current_user


def require_admin(current_user=Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Admin access required")
    return current_user
