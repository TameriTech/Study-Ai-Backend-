from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from tameri_chat.database import Base
from enum import Enum

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

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    name = Column(String)
    avatar = Column(String, nullable=True)
    is_online = Column(Boolean, default=False)
    last_seen = Column(DateTime(timezone=True), server_default=func.now())

    # Explicitly tell SQLAlchemy which FK to use
    messages = relationship("Message", back_populates="sender", foreign_keys='Message.sender_id')
    pinned_messages = relationship("Message", back_populates="pinned_by_user", foreign_keys='Message.pinned_by')
    reactions = relationship("Reaction", back_populates="user")
    group_members = relationship("GroupMember", back_populates="user")
    notifications = relationship("UserNotification", back_populates="user")


class Group(Base):
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    tags = Column(JSON, nullable=True)  # Storing tags as JSON array
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    messages = relationship("Message", back_populates="group")
    members = relationship("GroupMember", back_populates="group")

class GroupMember(Base):
    __tablename__ = "group_members"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, ForeignKey("groups.id"))
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="group_members")
    group = relationship("Group", back_populates="members")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    sender_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, ForeignKey("groups.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    edited_at = Column(DateTime(timezone=True), nullable=True)
    is_deleted = Column(Boolean, default=False)
    reply_to_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    pinned = Column(Boolean, default=False)
    pinned_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    pinned_at = Column(DateTime(timezone=True), nullable=True)
    mentions = Column(JSON, nullable=True)
    audio_data = Column(Text, nullable=True)  # For storing base64 encoded audio
    message_type = Column(String, default="text")  # 'text' or 'voice'
    duration = Column(Integer, nullable=True)  # Duration in seconds
    
    sender = relationship("User", back_populates="messages", foreign_keys=[sender_id])
    pinned_by_user = relationship("User", back_populates="pinned_messages", foreign_keys=[pinned_by])
    group = relationship("Group", back_populates="messages")
    reactions = relationship("Reaction", back_populates="message")
    reply_to = relationship("Message", remote_side=[id])
    notifications = relationship("UserNotification", back_populates="message")


class Reaction(Base):
    __tablename__ = "reactions"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    emoji = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    message = relationship("Message", back_populates="reactions")
    user = relationship("User", back_populates="reactions")


class UserNotification(Base):
    __tablename__ = "user_notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    notification_type = Column(String, index=True)
    title = Column(String)
    content = Column(Text)
    is_read = Column(Boolean, default=False)
    notification_data = Column(JSON, nullable=True)  # Changed from 'metadata' to 'notification_data'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    message = relationship("Message", back_populates="notifications")
    group = relationship("Group")