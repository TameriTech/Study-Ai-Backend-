from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set, Tuple, Optional, List
import base64
import json
from datetime import datetime
from enum import Enum
from pydantic import BaseModel

router = APIRouter(prefix="/api/chat", tags=["WebSocket Chat"])

class MessageType(str, Enum):
    TEXT = "text"
    SYSTEM = "system"
    NOTIFICATION = "notification"
    PRESENCE = "presence"

class UserPresence(BaseModel):
    user_id: str
    online: bool
    last_seen: Optional[str]

class ChatMessage(BaseModel):
    type: MessageType
    content: str
    sender_id: str
    recipient_id: Optional[str]  # None for broadcast, user_id for direct message
    timestamp: str
    room_id: Optional[str]  # None for direct messages

# Data structures
active_connections: Dict[str, Dict[str, WebSocket]] = {}  # {room_id: {user_id: websocket}}
user_presence: Dict[str, UserPresence] = {}  # {user_id: UserPresence}

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    user_id: str,
    room_id: Optional[str] = None,  # None for direct messaging
    recipient_id: Optional[str] = None  # None for group chat
):
    await websocket.accept()
    
    # Track user presence
    user_presence[user_id] = UserPresence(
        user_id=user_id,
        online=True,
        last_seen=None
    )
    
    # Join room or initialize direct messaging
    if room_id:
        if room_id not in active_connections:
            active_connections[room_id] = {}
        active_connections[room_id][user_id] = websocket
    else:
        # For direct messaging, we use a "virtual room" composed of user IDs
        direct_room_id = get_direct_room_id(user_id, recipient_id)
        if direct_room_id not in active_connections:
            active_connections[direct_room_id] = {}
        active_connections[direct_room_id][user_id] = websocket
    
    # Notify others of user's presence
    await broadcast_presence_update(user_id, True, room_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)
                message = ChatMessage(
                    type=MessageType(message_data.get("type", MessageType.TEXT)),
                    content=message_data["content"],
                    sender_id=user_id,
                    recipient_id=message_data.get("recipient_id"),
                    timestamp=datetime.now().isoformat(),
                    room_id=room_id
                )
                
                # Handle different message types
                if message.type == MessageType.TEXT:
                    await handle_text_message(message)
                elif message.type == MessageType.NOTIFICATION:
                    await handle_notification(message)
                
            except json.JSONDecodeError:
                # Fallback for plain text messages
                message = ChatMessage(
                    type=MessageType.TEXT,
                    content=data,
                    sender_id=user_id,
                    recipient_id=None,
                    timestamp=datetime.now().isoformat(),
                    room_id=room_id
                )
                await handle_text_message(message)
                
    except WebSocketDisconnect:
        # Update presence
        user_presence[user_id].online = False
        user_presence[user_id].last_seen = datetime.now().isoformat()
        
        # Leave room
        if room_id:
            active_connections[room_id].pop(user_id, None)
            if not active_connections[room_id]:
                del active_connections[room_id]
        else:
            direct_room_id = get_direct_room_id(user_id, recipient_id)
            active_connections[direct_room_id].pop(user_id, None)
            if not active_connections[direct_room_id]:
                del active_connections[direct_room_id]
        
        # Notify others of user's departure
        await broadcast_presence_update(user_id, False, room_id)

async def handle_text_message(message: ChatMessage):
    """Handle text messages (both direct and group)"""
    if message.recipient_id:
        # Direct message
        room_id = get_direct_room_id(message.sender_id, message.recipient_id)
        await send_to_room(room_id, message.model_dump(), exclude_user=message.sender_id)
    else:
        # Group message
        await send_to_room(message.room_id, message.model_dump(), exclude_user=message.sender_id)

async def handle_notification(message: ChatMessage):
    """Handle system notifications"""
    if message.recipient_id:
        # Targeted notification
        room_id = get_direct_room_id(message.sender_id, message.recipient_id)
        await send_to_room(room_id, message.model_dump())
    else:
        # Broadcast notification
        await send_to_room(message.room_id, message.model_dump())

async def broadcast_presence_update(user_id: str, online: bool, room_id: Optional[str] = None):
    """Notify users about presence changes"""
    presence_msg = ChatMessage(
        type=MessageType.PRESENCE,
        content=f"User {user_id} is {'online' if online else 'offline'}",
        sender_id=user_id,
        recipient_id=None,
        timestamp=datetime.now().isoformat(),
        room_id=room_id
    )
    
    if room_id:
        # Broadcast to room members
        await send_to_room(room_id, presence_msg.model_dump(), include_user=True)
    else:
        # Broadcast to all direct connections of this user
        for direct_room in [r for r in active_connections if user_id in r]:
            await send_to_room(direct_room, presence_msg.model_dump(), include_user=True)

async def send_to_room(
    room_id: str, 
    message: dict, 
    exclude_user: Optional[str] = None,
    include_user: bool = False
):
    """Send message to all users in a room with options to include/exclude specific users"""
    if room_id in active_connections:
        for user_id, websocket in active_connections[room_id].items():
            if (include_user or user_id != exclude_user):
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    print(f"Error sending to {user_id}: {e}")

def get_direct_room_id(user1: str, user2: str) -> str:
    """Generate a consistent room ID for direct messaging between two users"""
    return f"direct_{'-'.join(sorted([user1, user2]))}"

@router.get("/presence/{user_id}", response_model=UserPresence)
async def get_user_presence(user_id: str):
    """Get user presence information"""
    return user_presence.get(user_id, UserPresence(
        user_id=user_id,
        online=False,
        last_seen=None
    ))

@router.get("/room/users/{room_id}", response_model=List[str])
async def get_room_users(room_id: str):
    """Get list of users in a room"""
    return list(active_connections.get(room_id, {}).keys())