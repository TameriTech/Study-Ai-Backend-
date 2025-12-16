from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session
import tameri_chat.models as models
import tameri_chat.schemas as schemas
from datetime import datetime, timezone
from sqlalchemy.orm import joinedload
from datetime import datetime

# User operations
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def authenticate_user(db: Session, username: str):
    user = get_user_by_username(db, username=username)
    if not user:
        return False
    return user

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Add user to all existing groups
    all_groups = db.query(models.Group).all()
    for group in all_groups:
        group_member = models.GroupMember(
            user_id=db_user.id,
            group_id=group.id
        )
        db.add(group_member)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_online_status(db: Session, user_id: int, is_online: bool):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.is_online = is_online
        db_user.last_seen = datetime.now()
        db.commit()
        db.refresh(db_user)
    return db_user

# Group operations
def get_group(db: Session, group_id: int):
    return db.query(models.Group).filter(models.Group.id == group_id).first()

def get_groups(db: Session, skip: int = 0, limit: int = 100, public_only: bool = True):
    query = db.query(models.Group)
    if public_only:
        query = query.filter(models.Group.is_public == True)
    return query.offset(skip).limit(limit).all()

def create_message(db: Session, message: schemas.MessageCreate, sender_id: int):
    db_message = models.Message(
        **message.dict(exclude={'mentions'}),  # Exclude mentions from main fields
        sender_id=sender_id,
        mentions=message.mentions  # Add mentions separately
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    # Create notifications for mentioned users
    if message.mentions:
        for user_id in message.mentions:
            # Check if user is in the group
            if is_user_in_group(db, user_id, message.group_id):
                notification = models.UserNotification(
                    user_id=user_id,
                    message_id=db_message.id,
                    group_id=message.group_id,
                    notification_type="mention",
                    title=f"You were mentioned in a {'voice' if message.message_type == 'voice' else 'text'} message",
                    content=message.content[:50] + "..." if len(message.content) > 50 else message.content
                )
                db.add(notification)
    
    db.commit()
    return db_message

# Group member operations
def add_group_member(db: Session, group_member: schemas.GroupMemberCreate):
    # Check if user is already in group
    existing = db.query(models.GroupMember).filter(
        models.GroupMember.user_id == group_member.user_id,
        models.GroupMember.group_id == group_member.group_id
    ).first()
    
    if existing:
        return existing
    
    db_member = models.GroupMember(**group_member.dict())
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    
    # Update user's online status
    db_user = db.query(models.User).filter(models.User.id == group_member.user_id).first()
    if db_user:
        db_user.is_online = True
        db_user.last_seen = datetime.now()
        db.commit()
    
    return db_member

def get_group_members(db: Session, group_id: int):
    return db.query(models.GroupMember).filter(models.GroupMember.group_id == group_id).all()

def is_user_in_group(db: Session, user_id: int, group_id: int) -> bool:
    return db.query(models.GroupMember).filter(
        models.GroupMember.user_id == user_id,
        models.GroupMember.group_id == group_id
    ).first() is not None


def create_group(db: Session, group: schemas.GroupCreate):
    db_group = models.Group(**group.dict())
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    
    # Add all existing users to this new group
    all_users = db.query(models.User).all()
    for user in all_users:
        group_member = models.GroupMember(
            user_id=user.id,
            group_id=db_group.id
        )
        db.add(group_member)
    
    db.commit()
    db.refresh(db_group)
    return db_group

def get_message(db: Session, message_id: int):
    return db.query(models.Message).options(
        joinedload(models.Message.sender),
        joinedload(models.Message.reactions).joinedload(models.Reaction.user),
        joinedload(models.Message.reply_to).joinedload(models.Message.sender)
    ).filter(models.Message.id == message_id).first()

def get_group_messages(db: Session, group_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Message).filter(
        models.Message.group_id == group_id,
        models.Message.is_deleted == False
    ).options(
        joinedload(models.Message.sender),
        joinedload(models.Message.reactions).joinedload(models.Reaction.user)
    ).order_by(models.Message.created_at.desc()).offset(skip).limit(limit).all()

def fetch_pinned_messages(db: Session, group_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Message).filter(
        models.Message.group_id == group_id,
        models.Message.pinned == True,
        models.Message.is_deleted == False
    ).options(
        joinedload(models.Message.sender),
        joinedload(models.Message.reactions).joinedload(models.Reaction.user)
    ).order_by(models.Message.pinned_at.desc()).offset(skip).limit(limit).all()

def pin_message(db: Session, message_id: int, user_id: int):
    message = db.query(models.Message).filter(models.Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    message.pinned = True
    message.pinned_by = user_id
    message.pinned_at = datetime.now()

    db.commit()
    db.refresh(message)
    return message

# In crud.py
def update_message(db: Session, message_id: int, content: str):
    db_message = db.query(models.Message).filter(models.Message.id == message_id).first()
    if db_message:
        db_message.content = content
        db_message.edited_at = datetime.utcnow()
        db.commit()
        db.refresh(db_message)
    return db_message

def delete_message(db: Session, message_id: int, for_all: bool = False):
    db_message = db.query(models.Message).filter(models.Message.id == message_id).first()
    if db_message:
        if for_all:
            # Soft delete (mark as deleted)
            db_message.is_deleted = True
            db.commit()
            db.refresh(db_message)
        else:
            # Hard delete (remove from database)
            db.delete(db_message)
            db.commit()
    return db_message

def pin_message(db: Session, message_id: int, pin: bool = True, user_id: int = None):
    db_message = get_message(db, message_id=message_id)
    if not db_message:
        return None
    
    db_message.pinned = pin
    if pin:
        db_message.pinned_by = user_id
        db_message.pinned_at = datetime.now(timezone.utc)  # Explicitly set as UTC
    else:
        db_message.pinned_by = None
        db_message.pinned_at = None
    
    db.commit()
    db.refresh(db_message)
    return db_message

# Reaction operations
def add_reaction(db: Session, reaction: schemas.ReactionCreate, user_id: int):
    # Check for existing reaction from this user
    existing = db.query(models.Reaction).filter(
        models.Reaction.message_id == reaction.message_id,
        models.Reaction.user_id == user_id
    ).first()
    
    if existing:
        if existing.emoji == reaction.emoji:
            # Remove reaction if same emoji clicked
            db.delete(existing)
            db.commit()
            return None
        else:
            # Update existing reaction if different emoji
            existing.emoji = reaction.emoji
            db.commit()
            db.refresh(existing)
            return existing
    else:
        # Create new reaction
        db_reaction = models.Reaction(**reaction.dict(), user_id=user_id)
        db.add(db_reaction)
        db.commit()
        db.refresh(db_reaction)
        return db_reaction

def get_message_reactions(db: Session, message_id: int):
    return db.query(models.Reaction).filter(models.Reaction.message_id == message_id).all()

# Notification operations
# Update create_notification in crud.py
def create_notification(
    db: Session,
    user_id: int,
    notification_type: str,
    title: str,
    content: str,
    message_id: int = None,
    group_id: int = None,
    notification_data: dict = None
):
    db_notification = models.UserNotification(
        user_id=user_id,
        message_id=message_id,
        group_id=group_id,
        notification_type=notification_type,
        title=title,
        content=content,
        notification_data=notification_data or {},
        is_read=False
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

def get_user_notifications(
    db: Session,
    user_id: int,
    is_read: bool = None,
    notification_type: str = None,
    limit: int = 50
):
    """
    Get notifications for a user with optional filters
    """
    query = db.query(models.UserNotification).filter(
        models.UserNotification.user_id == user_id
    ).options(
        joinedload(models.UserNotification.message),
        joinedload(models.UserNotification.group)
    )
    
    if is_read is not None:
        query = query.filter(models.UserNotification.is_read == is_read)
    
    if notification_type:
        query = query.filter(models.UserNotification.notification_type == notification_type)
    
    return query.order_by(
        models.UserNotification.created_at.desc()
    ).limit(limit).all()

def mark_notifications_as_read(
    db: Session,
    notification_ids: List[int] = None,
    user_id: int = None
):
    """
    Mark notifications as read, either specific ones or all for a user
    """
    query = db.query(models.UserNotification)
    
    if notification_ids:
        query = query.filter(models.UserNotification.id.in_(notification_ids))
    elif user_id:
        query = query.filter(models.UserNotification.user_id == user_id)
    else:
        return 0
    
    result = query.update({"is_read": True}, synchronize_session=False)
    db.commit()
    return result

def get_user_unread_notifications(db: Session, user_id: int):
    return db.query(models.UserNotification).filter(
        models.UserNotification.user_id == user_id,
        models.UserNotification.is_read == False
    ).options(
        joinedload(models.UserNotification.message)
        .joinedload(models.Message.group)
    ).all()

def get_unread_mention_count(db: Session, user_id: int, group_id: int = None):
    query = db.query(models.UserNotification).filter(
        models.UserNotification.user_id == user_id,
        models.UserNotification.is_read == False,
        models.UserNotification.notification_type == "mention"
    ).join(
        models.UserNotification.message
    )
    
    if group_id:
        query = query.filter(models.Message.group_id == group_id)
    
    return query.count()

def get_username_from_db(db: Session, user_id: int) -> str:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return user.name if user else f"User {user_id}"

def mark_notification_as_read(db: Session, notification_id: int):
    db_notification = db.query(models.UserNotification).filter(
        models.UserNotification.id == notification_id
    ).first()
    if db_notification:
        db_notification.is_read = True
        db.commit()
        db.refresh(db_notification)
    return db_notification 