from fastapi import APIRouter, Depends, status, HTTPException
from slugify import slugify
from sqlalchemy import insert, select, update, delete
from sqlalchemy.orm import Session
from typing import Annotated

from app.backend.db_depends import get_db
from app.models import User
from app.schemas import CreateUser, UpdateUser

router = APIRouter(prefix="/user", tags=["user"])
Sess = Annotated[Session, Depends(get_db)]


@router.get('/')
async def all_users(sess: Sess):
    return sess.scalars(select(User)).all()


@router.get('/user_id')
async def user_by_id(sess: Sess, user_id: int):
    user = sess.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User was not found')
    return user


@router.post('/create')
async def create_user(sess: Sess, user: CreateUser) -> dict:
    if sess.scalar(select(User.username)
                   .where(User.username == user.username)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='Duplicated username')
    user_dict = dict(user)
    user_dict['slug'] = slugify(user.username)
    sess.execute(insert(User), user_dict)
    sess.commit()
    return {'status_code': status.HTTP_201_CREATED,
            'transaction': 'Successful'}


@router.put('/update')
async def update_user(sess: Sess, user: UpdateUser, user_id: int) -> dict:
    if not sess.scalar(select(User.id).where(User.id == user_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User was not found')
    sess.execute(update(User).where(User.id == user_id),
                 dict(user))
    sess.commit()
    return {'status_code': status.HTTP_200_OK,
            'transaction': 'User has been updated successfully'}


@router.delete('/delete')
async def delete_user(sess: Sess, user_id: int) -> dict:
    if not sess.scalar(select(User.id).where(User.id == user_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User was not found')
    sess.execute(delete(User).where(User.id == user_id))
    sess.commit()
    return {'status_code': status.HTTP_200_OK,
            'transaction': 'User has been deleted successfully'}
