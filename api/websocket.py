from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set, Tuple
import base64
import json
from datetime import datetime

router = APIRouter(prefix="/api", tags=["Websocket"])
rooms: Dict[str, Dict[str, WebSocket]] = {}  # {room_id: {user_id: websocket}}

@router.websocket("/ws/{room_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, user_id: str):
    await websocket.accept()
    
    # Create the room if it doesn't exist
    if room_id not in rooms:
        rooms[room_id] = {}
    
    # Add the client to the room
    rooms[room_id][user_id] = websocket
    
    # Notify others in the room that this user joined
    join_message = {
        "type": "system",
        "content": f"User {user_id} joined the room",
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id
    }
    await broadcast_message(room_id, join_message, exclude_user=user_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                message["user_id"] = user_id  # Ensure user_id is included
                message["timestamp"] = datetime.now().isoformat()
                
                # Broadcast to all clients in the same room except sender
                await broadcast_message(room_id, message, exclude_user=user_id)
                
            except json.JSONDecodeError:
                # If not JSON, treat as plain text (backward compatibility)
                plain_message = {
                    "type": "message",
                    "content": data,
                    "user_id": user_id,
                    "timestamp": datetime.now().isoformat()
                }
                await broadcast_message(room_id, plain_message, exclude_user=user_id)
                
    except WebSocketDisconnect:
        # Remove the client from the room
        rooms[room_id].pop(user_id, None)
        
        # Clean up empty rooms
        if not rooms[room_id]:
            del rooms[room_id]
        
        # Notify others in the room that this user left
        leave_message = {
            "type": "system",
            "content": f"User {user_id} left the room",
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id
        }
        await broadcast_message(room_id, leave_message)
        
        print(f"Client {user_id} disconnected from room {room_id}")

async def broadcast_message(room_id: str, message: dict, exclude_user: str = None):
    """Broadcast message to all users in a room, optionally excluding one user"""
    if room_id in rooms:
        for user_id, websocket in rooms[room_id].items():
            if user_id != exclude_user:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    print(f"Error sending message to {user_id}: {e}")