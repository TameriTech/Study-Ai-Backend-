# schemas.py
from typing import List, Optional, Union, Dict
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class UserBase(BaseModel):
    username: str
    name: str
    avatar: Optional[str] = None

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    is_online: bool
    last_seen: datetime
    
    class Config:
        from_attributes = True

class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None

class GroupCreate(GroupBase):
    is_public: bool = True

class Group(GroupBase):
    id: int
    is_public: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class MessageBase(BaseModel):
    content: str
    group_id: int
    reply_to_id: Optional[int] = None
    mentions: Optional[List[int]] = None
    audio_data: Optional[str] = None
    message_type: str = "text"
    duration: Optional[int] = None

class MessageUpdate(BaseModel):
    content: str
    edited_at: Optional[datetime] = None

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int
    sender_id: int
    pinned_by: Optional[int] = None
    created_at: datetime
    pinned_at: Optional[datetime] = None
    edited_at: Optional[datetime] = None
    is_deleted: bool
    pinned: bool
    sender: User  # Include sender info
    reactions: List["Reaction"] = []
    
    class Config:
        from_attributes = True

class ReactionBase(BaseModel):
    message_id: int
    emoji: str

class ReactionCreate(ReactionBase):
    pass

class Reaction(ReactionBase):
    id: int
    user_id: int
    created_at: datetime
    user: User
    
    class Config:
        from_attributes = True

class GroupMemberBase(BaseModel):
    user_id: int
    group_id: int

class GroupMemberCreate(GroupMemberBase):
    pass

class GroupMember(GroupMemberBase):
    id: int
    joined_at: datetime
    
    class Config:
        from_attributes = True

class TypingIndicator(BaseModel):
    user_id: int
    group_id: int
    is_typing: bool

class NotificationType(str, Enum):
    MESSAGE = "message"
    MENTION = "mention"
    REACTION = "reaction"
    GROUP_JOIN = "group_join"
    GROUP_LEAVE = "group_leave"
    GROUP_CREATE = "group_create"
    MESSAGE_PIN = "message_pin"
    MESSAGE_EDIT = "message_edit"
    MESSAGE_DELETE = "message_delete"
    SYSTEM = "system"
    ERROR = "error"
    SUCCESS = "success"
    TYPING = "typing"

class UserNotificationBase(BaseModel):
    user_id: int
    notification_type: NotificationType
    title: str
    content: str
    is_read: bool = False
    notification_data: Optional[Dict] = None

class UserNotificationCreate(UserNotificationBase):
    message_id: Optional[int] = None
    group_id: Optional[int] = None

class UserNotification(UserNotificationBase):
    id: int
    message_id: Optional[int] = None
    group_id: Optional[int] = None
    created_at: datetime
    user: Optional[User] = None
    message: Optional[Message] = None
    group: Optional[Group] = None
    
    class Config:
        from_attributes = True

class WebSocketMessage(BaseModel):
    type: str  # "message", "reaction", "typing", "notification", etc.
    data: Union[
        Message, 
        Reaction, 
        TypingIndicator, 
        UserNotification,
        Dict  # For generic data
    ]

# Rebuild models to handle forward references
Message.model_rebuild()
Reaction.model_rebuild()
UserNotification.model_rebuild()