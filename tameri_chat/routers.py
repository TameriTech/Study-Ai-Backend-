from fastapi import APIRouter, Body, Depends, HTTPException, WebSocket, WebSocketDisconnect
from tameri_chat.database import get_db
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
import json
from datetime import datetime
import tameri_chat.models as models
from tameri_chat.models import Base, NotificationType
from sqlalchemy.orm import joinedload
from tameri_chat.schemas import (
    User, UserCreate, Group, GroupCreate, Message, MessageCreate, MessageUpdate,
    Reaction, ReactionCreate, GroupMemberCreate, WebSocketMessage, UserNotificationCreate, UserNotification
)
from tameri_chat.crud import (
    fetch_pinned_messages, get_group_members, get_user, get_user_by_username, create_user, get_user_notifications, get_users, mark_notifications_as_read, update_user_online_status,
    get_group, get_groups, create_group, add_group_member, is_user_in_group,
    create_message, get_message, get_group_messages, update_message, delete_message,
    pin_message, add_reaction, get_message_reactions, create_notification,
    get_user_unread_notifications, mark_notification_as_read, authenticate_user
)
from tameri_chat.websocket_manager import manager

router = APIRouter()

@router.post("/register/user/", response_model=User)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return create_user(db=db, user=user)


@router.post("/auth/login/{username}", response_model=User)
async def login_for_access_token(
    username: str,
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, username)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password"
        )
    return user

@router.get("/users/", response_model=List[User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = get_users(db, skip=skip, limit=limit)
    return users

@router.get("/users/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.post("/groups/", response_model=Group)
def create_new_group(group: GroupCreate, db: Session = Depends(get_db)):
    return create_group(db=db, group=group)

@router.get("/groups/", response_model=List[Group])
def read_groups(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    groups = get_groups(db, skip=skip, limit=limit)
    return groups

@router.get("/groups/{group_id}", response_model=Group)
def read_group(group_id: int, db: Session = Depends(get_db)):
    db_group = get_group(db, group_id=group_id)
    if db_group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    return db_group

@router.post("/groups/{group_id}/join/{user_id}")
def join_group(group_id: int, user_id: int, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if group exists
    db_group = get_group(db, group_id=group_id)
    if not db_group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if user is already in group
    if is_user_in_group(db, user_id=user_id, group_id=group_id):
        raise HTTPException(status_code=400, detail="User already in group")
    
    # Add user to group
    group_member = GroupMemberCreate(user_id=user_id, group_id=group_id)
    result = add_group_member(db, group_member=group_member)
    
    # Update user's online status
    update_user_online_status(db, user_id=user_id, is_online=True)
    
    return {"message": "User joined group successfully"}

@router.get("/groups/{group_id}/messages", response_model=List[Message])
def read_group_messages(
    group_id: int, 
    page: int = 1, 
    limit: int = 20,
    db: Session = Depends(get_db)
):
    # Calculate offset
    offset = (page - 1) * limit
    
    # Get messages ordered by newest first
    messages = db.query(models.Message).filter(
        models.Message.group_id == group_id,
        models.Message.is_deleted == False
    ).options(
        joinedload(models.Message.sender),
        joinedload(models.Message.reactions).joinedload(models.Reaction.user)
    ).order_by(models.Message.created_at.desc()).offset(offset).limit(limit).all()
    
    return messages


def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

@router.get("/messages/{message_id}", response_model=Message)
def read_message(message_id: int, db: Session = Depends(get_db)):
    message = get_message(db, message_id)
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return message

@router.post("/messages/{message_id}/pin", response_model=Message)
def pin_message_route(
    message_id: int,
    user_id: int = Body(..., embed=True),  # ID of user who pins
    db: Session = Depends(get_db)
):
    return pin_message(db=db, message_id=message_id, user_id=user_id)

@router.get("/groups/{group_id}/pinned-messages", response_model=List[Message])
def get_pinned_messages(group_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return fetch_pinned_messages(db, group_id=group_id, skip=skip, limit=limit)

@router.put("/messages/{message_id}", response_model=Message)
def update_message_route(
    message_id: int,
    message_update: MessageUpdate,
    user_id: int,
    db: Session = Depends(get_db)
):
    db_message = get_message(db, message_id=message_id)
    if not db_message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    if db_message.sender_id != user_id:
        raise HTTPException(status_code=403, detail="Can only edit your own messages")
    
    # Call the CRUD function with the content
    return update_message(db, message_id=message_id, content=message_update.content)

@router.delete("/messages/{message_id}")
def delete_message_endpoint(
    message_id: int,
    user_id: int,  # Pass user_id directly
    db: Session = Depends(get_db)
):
    db_message = get_message(db, message_id=message_id)
    if not db_message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Verify message belongs to requesting user
    if db_message.sender_id != user_id:
        raise HTTPException(status_code=403, detail="Can only delete your own messages")
    
    delete_message(db, message_id=message_id)
    return {"message": "Message deleted successfully"}


@router.get("/users/{user_id}/notifications", response_model=List[UserNotification])
def get_notifications(
    user_id: int,
    is_read: bool = None,
    type: str = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get notifications for a user with filters"""
    return get_user_notifications(
        db,
        user_id=user_id,
        is_read=is_read,
        notification_type=type,
        limit=limit
    )

@router.post("/notifications/mark-read")
def mark_notifications_read(
    notification_ids: List[int] = Body(default=None),
    user_id: int = Body(default=None),
    db: Session = Depends(get_db)
):
    """Mark notifications as read"""
    count = mark_notifications_as_read(
        db,
        notification_ids=notification_ids,
        user_id=user_id
    )
    return {"message": f"Marked {count} notifications as read"}

@router.get("/users/{user_id}/notifications/unread-count", response_model=int)
def get_unread_count(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get count of unread notifications for a user"""
    return db.query(models.UserNotification).filter(
        models.UserNotification.user_id == user_id,
        models.UserNotification.is_read == False
    ).count()

# WebSocket Endpoint
@router.websocket("/wss/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, db: Session = Depends(get_db)):
    # Connect the user
    connection_id = await manager.connect(user_id, websocket)
    
    try:
        # Update user's online status
        update_user_online_status(db, user_id=user_id, is_online=True)
        
        
        while True:
            data = await websocket.receive_text()
            try:
                message = WebSocketMessage.parse_raw(data)
                
                # In your websocket_endpoint function, modify the join_group handler:
                if message.type == "join_group":
                    group_id = message.data["group_id"]
                    db = next(get_db())
                    
                    try:
                        # Verify group exists
                        db_group = get_group(db, group_id=group_id)
                        if not db_group:
                            raise HTTPException(status_code=404, detail="Group not found")
                        
                        # Add user to group if not already a member
                        if not is_user_in_group(db, user_id=user_id, group_id=group_id):
                            add_group_member(db, group_member=GroupMemberCreate(
                                user_id=user_id,
                                group_id=group_id
                            ))
                        
                        # Add to WebSocket group tracking
                        manager.add_user_to_group(user_id, group_id)

                        
                        
                        # Get current online users (including the joining user)
                        online_users = manager.get_online_users_in_group(group_id)
                        
                        online_users_message = WebSocketMessage(
                            type="online_users",
                            data={
                                "group_id": group_id,
                                "users": online_users
                            }
                        )

                        await manager.broadcast_to_group(
                            group_id=group_id,
                            message=online_users_message.json()
                        )
                        # Send current online users to the joining user
                        await manager.send_personal_message(WebSocketMessage(
                            type="online_users",
                            data={
                                "group_id": group_id,
                                "users": online_users
                            }
                        ).json(), user_id)
                        
                        # Notify other group members about the new user
                        if len(online_users) > 1:  # Only notify if there are others in the group
                            join_message = WebSocketMessage(
                                type="user_joined",
                                data={
                                    "user_id": user_id,
                                    "group_id": group_id,
                                    "online_users": online_users
                                }
                            )
                            await manager.broadcast_to_group(
                                group_id=group_id,
                                message=join_message.json(),
                                exclude_user_id=user_id
                            )
                        
                    except Exception as e:
                        print(f"Error joining group: {e}")
                        error_msg = WebSocketMessage(
                            type="error",
                            data={"message": f"Failed to join group: {str(e)}"}
                        )
                        await manager.send_personal_message(error_msg.json(), user_id)

                elif message.type == "leave_group":
                    # User wants to leave a group chat
                    group_id = message.data["group_id"]
                    manager.remove_user_from_group(user_id, group_id)
                    
                    # Notify others in the group that user left
                    leave_message = WebSocketMessage(
                        type="user_left",
                        data={
                            "user_id": user_id,
                            "group_id": group_id,
                            "online_users": manager.get_online_users_in_group(group_id)
                        }
                    )
                    await manager.broadcast_to_group(
                        group_id=group_id,
                        message=leave_message.json(),
                        exclude_user_id=user_id
                    )
                
                # In your WebSocket endpoint, update the message handling:
                elif message.type == "new_message":
                    # User sent a new message
                    group_id = message.data["group_id"]
                    content = message.data["content"]
                    reply_to_id = message.data.get("reply_to_id")
                    
                    # Check if user is in the group by querying the database
                    db = next(get_db())
                    if not is_user_in_group(db, user_id=user_id, group_id=group_id):
                        error_msg = WebSocketMessage(
                            type="error",
                            data={"message": "User not in group. Please join the group first."}
                        )
                        await manager.send_personal_message(error_msg.json(), user_id)
                        continue  # Skip the rest of the processing
                    
                    # Create message in database
                    db_message = create_message(
                        db,
                        message=MessageCreate(
                            content=content,
                            group_id=group_id,
                            reply_to_id=reply_to_id
                        ),
                        sender_id=user_id
                    )
                    
                    # Broadcast message to group
                    message_to_send = WebSocketMessage(
                        type="new_message",
                        data=Message.from_orm(db_message).dict()
                    )
                    await manager.broadcast_to_group(
                        group_id=group_id,
                        message=message_to_send.json()
                    )
                    notification_content = f"New message in {db_group.name}: {content[:50]}..."
                    members = get_group_members(db, group_id=group_id)
                    for member in members:
                        if member.user_id != user_id:  # Don't notify self
                            create_notification(
                                db,
                                user_id=member.user_id,
                                notification_type=NotificationType.MESSAGE,
                                title=f"New message in {db_group.name}",
                                content=notification_content,
                                message_id=db_message.id,
                                group_id=group_id,
                                notification_data={
                                    "sender_id": user_id,
                                    "group_name": db_group.name,
                                    "preview": content[:50]
                                }
                            )
                
                    if message.data.get("mentions"):
                        for mentioned_user_id in message.data["mentions"]:
                            if mentioned_user_id != user_id:  # Don't notify self
                                # Send real-time notification
                                mention_notification = WebSocketMessage(
                                    type="mention",
                                    data={
                                        "message_id": db_message.id,
                                        "group_id": group_id,
                                        "mentioned_by": user_id,
                                        "content": content[:50] + "..." if len(content) > 50 else content
                                    }
                                )
                                await manager.send_personal_message(
                                    mention_notification.json(),
                                    mentioned_user_id
                                )

                elif message.type == "voice_message":
                    # Save the voice message to database
                    db_voice_message = create_message(
                        db,
                        message=MessageCreate(
                            content="[Voice Message]",
                            group_id=message.data["group_id"],
                            reply_to_id=message.data.get("reply_to_id"),
                            mentions=message.data.get("mentions", []),
                            audio_data=message.data["audio"],
                            duration=message.data.get("duration", 0),
                            message_type="voice"
                        ),
                        sender_id=user_id
                    )
                    
                    # Broadcast to group
                    voice_message = WebSocketMessage(
                        type="voice_message",
                        data=Message.from_orm(db_voice_message).dict()
                    )
                    await manager.broadcast_to_group(
                        group_id=message.data["group_id"],
                        message=voice_message.json()
                    )
                    
                    # Create notifications for mentions
                    if message.data.get("mentions"):
                        for mentioned_user_id in message.data["mentions"]:
                            if mentioned_user_id != user_id:  # Don't notify self
                                # Create notification in DB
                                notification = create_notification(
                                    db,
                                    user_id=mentioned_user_id,
                                    notification_type="mention",
                                    title=f"You were mentioned in a voice message",
                                    content="Voice message mention",
                                    message_id=db_voice_message.id,
                                    group_id=message.data["group_id"]
                                )
                                
                                # Send real-time notification
                                mention_notification = WebSocketMessage(
                                    type="mention",
                                    data={
                                        "message_id": db_voice_message.id,
                                        "group_id": message.data["group_id"],
                                        "mentioned_by": user_id,
                                        "content": "[Voice Message]"
                                    }
                                )
                                await manager.send_personal_message(
                                    mention_notification.json(),
                                    mentioned_user_id
                                ) 

                elif message.type == "create_group":
                    db = next(get_db())
                    try:
                        # Create the group
                        db_group = create_group(db, group=GroupCreate(**message.data))
                        
                        # Add creator to group
                        try:
                            add_group_member(db, group_member=GroupMemberCreate(
                                user_id=user_id,
                                group_id=db_group.id
                            ))
                        except Exception as e:
                            print(f"Error adding creator to group: {e}")
                            raise HTTPException(status_code=400, detail="Failed to add creator to group")
                        
                        # Prepare group info for broadcast
                        group_info = Group.from_orm(db_group).dict()
                        
                        # Broadcast to all users
                        await manager.broadcast_to_all(WebSocketMessage(
                            type="new_group",
                            data=group_info
                        ).json())
                        
                        # Send success to creator
                        await manager.send_personal_message(WebSocketMessage(
                            type="group_created",
                            data={
                                "group_id": db_group.id,
                                "message": "Group created successfully"
                            }
                        ).json(), user_id)
                        
                    except Exception as e:
                        print(f"Group creation error: {e}")
                        await manager.send_personal_message(WebSocketMessage(
                            type="error",
                            data={"message": f"Failed to create group: {str(e)}"}
                        ).json(), user_id)

                elif message.type == "edit_message":
                    # User wants to edit a message
                    message_id = message.data["message_id"]
                    new_content = message.data["new_content"]
                    
                    # Get the message from DB
                    db_message = get_message(db, message_id=message_id)
                    if not db_message:
                        raise HTTPException(status_code=404, detail="Message not found")
                    
                    # Check if user is the sender
                    if db_message.sender_id != user_id:
                        raise HTTPException(status_code=403, detail="Cannot edit other user's message")
                    
                    # Update message - only pass the content
                    updated_msg = update_message(db=db, message_id=message_id, content=new_content)
                    
                    # Broadcast update to group
                    update_msg_payload = WebSocketMessage(
                        type="message_updated",
                        data=Message.from_orm(updated_msg).dict()
                    )
                    await manager.broadcast_to_group(
                        group_id=db_message.group_id,
                        message=update_msg_payload.json()
                    )
                
                elif message.type == "delete_message":
                    # User wants to delete a message
                    message_id = message.data["message_id"]
                    for_all = message.data.get("for_all", False)  # Default to False if not specified
                    
                    # Get the message from DB
                    db_message = get_message(db, message_id=message_id)
                    if not db_message:
                        raise HTTPException(status_code=404, detail="Message not found")
                    
                    # Check if user is the sender
                    if db_message.sender_id != user_id:
                        raise HTTPException(status_code=403, detail="Cannot delete other user's message")
                    
                    # Delete message
                    deleted_msg = delete_message(db, message_id=message_id, for_all=for_all)
                    
                    # Broadcast deletion to group
                    delete_msg_payload = WebSocketMessage(
                        type="message_deleted",
                        data={
                            "message_id": message_id,
                            "group_id": db_message.group_id,
                            "for_all": for_all
                        }
                    )
                    await manager.broadcast_to_group(
                        group_id=db_message.group_id,
                        message=delete_msg_payload.json()
                    )

                elif message.type == "pin_message":
                    # User wants to pin/unpin a message
                    message_id = message.data["message_id"]
                    pin = message.data.get("pin", True)
                    
                    # Get the message from DB
                    db_message = get_message(db, message_id=message_id)
                    if not db_message:
                        raise HTTPException(status_code=404, detail="Message not found")
                    
                    # Update pin status
                    updated_message = pin_message(db, message_id=message_id, pin=pin, user_id=user_id)

                    pin_update_message = WebSocketMessage(
                        type="pin_message",
                        data={
                            "message_id": message_id,
                            "group_id": db_message.group_id,
                            "pinned": pin,
                            "pinned_at": db_message.pinned_at.isoformat().replace("+00:00", "Z") if pin else None,
                            "pinned_by": user_id if pin else None
                        }
                    )
                    await manager.broadcast_to_group(
                        group_id=db_message.group_id,
                        message=pin_update_message.json()
                    )
                                
                elif message.type == "add_reaction":
                    message_id = message.data["message_id"]
                    emoji = message.data["emoji"]
                    
                    db_message = get_message(db, message_id=message_id)
                    if not db_message:
                        raise HTTPException(status_code=404, detail="Message not found")
                    
                    if not is_user_in_group(db, user_id=user_id, group_id=db_message.group_id):
                        raise HTTPException(status_code=403, detail="User not in group")
                    
                    # Get current user's existing reaction (if any)
                    existing_reaction = db.query(models.Reaction).filter(
                        models.Reaction.message_id == message_id,
                        models.Reaction.user_id == user_id
                    ).first()
                    
                    if existing_reaction:
                        if existing_reaction.emoji == emoji:
                            # Remove reaction if same emoji clicked
                            db.delete(existing_reaction)
                            action = "removed"
                        else:
                            # Update existing reaction if different emoji
                            existing_reaction.emoji = emoji
                            db.commit()
                            action = "updated"
                    else:
                        # Create new reaction
                        new_reaction = models.Reaction(
                            message_id=message_id,
                            emoji=emoji,
                            user_id=user_id
                        )
                        db.add(new_reaction)
                        action = "added"
                    
                    db.commit()
                    
                    # Get updated reaction list for this message
                    updated_reactions = db.query(models.Reaction).filter(
                        models.Reaction.message_id == message_id
                    ).options(joinedload(models.Reaction.user)).all()
                    
                    # Broadcast the reaction change
                    reaction_message = WebSocketMessage(
                        type="reaction_change",
                        data={
                            "message_id": message_id,
                            "action": action,
                            "emoji": emoji,
                            "user_id": user_id,
                            "user_name": get_user(db, user_id).name,
                            "reactions": [
                                {
                                    "id": r.id,
                                    "emoji": r.emoji,
                                    "user_id": r.user_id,
                                    "user_name": r.user.name
                                } for r in updated_reactions
                            ]
                        }
                    )
                    
                    await manager.broadcast_to_group(
                        group_id=db_message.group_id,
                        message=reaction_message.json()
                    ) 

                elif message.type == "typing":
                    # User is typing in a group
                    group_id = message.data["group_id"]
                    is_typing = message.data["is_typing"]
                    
                    # Update typing status
                    await manager.update_typing_status(user_id, group_id, is_typing, db)

                elif message.type == "recording_status":
                    group_id = message.data["group_id"]
                    is_recording = message.data["is_recording"]
                    
                    await manager.update_recording_status(
                        user_id, group_id, is_recording, db
                    )

                else:
                    print(f"Unknown message type: {message.type}")
            
            except Exception as e:
                print(f"Error processing message: {e}")
                error_message = WebSocketMessage(
                    type="error",
                    data={"message": str(e)}
                )
                await manager.send_personal_message(error_message.json(), user_id)
    
    except WebSocketDisconnect:
        print(f"User {user_id} disconnected")
        manager.disconnect(user_id, connection_id)
        
        # Update user's online status
        db = next(get_db())
        update_user_online_status(db, user_id=user_id, is_online=False)
        
        # Notify groups that user left
        if user_id in manager.user_groups:
            for group_id in manager.user_groups[user_id]:
                # Remove from group tracking
                manager.remove_user_from_group(user_id, group_id)
                
                # Notify remaining members
                leave_message = WebSocketMessage(
                    type="user_left",
                    data={
                        "user_id": user_id,
                        "group_id": group_id,
                        "online_users": manager.get_online_users_in_group(group_id)
                    }
                )
                await manager.broadcast_to_group(
                    group_id=group_id,
                    message=leave_message.json()
                )
    except Exception as e:
        print(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(user_id, connection_id)
        update_user_online_status(db, user_id=user_id, is_online=False)