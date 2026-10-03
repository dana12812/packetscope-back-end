# dependencies/get_current_user.py — decodes the JWT and returns the logged-in user.

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from models.user import UserModel
from database import get_db
import jwt
from jwt import DecodeError, ExpiredSignatureError
from jwt.exceptions import InvalidSubjectError
from config.environment import JWT_SECRET

# Extracts the token from the "Authorization: Bearer ..." header
http_bearer = HTTPBearer()


def get_current_user(db: Session = Depends(get_db), token: str = Depends(http_bearer)):
    try:
        payload = jwt.decode(token.credentials, JWT_SECRET, algorithms=["HS256"])
        # "sub" is a string in the token; users.id is an integer column
        current_user_id = int(payload.get("sub"))

        user = db.query(UserModel).filter(UserModel.id == current_user_id).first()

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid token")
    except DecodeError as err:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Could not decode token: {str(err)}")
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Token has expired")
    except (InvalidSubjectError, TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Token invalid")
    return user