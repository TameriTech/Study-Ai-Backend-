from fastapi import WebSocket
from typing import Dict, List
import json
from requests import Session
from tameri_chat.schemas import WebSocketMessage
import uuid
from fastapi import Depends
from tameri_chat.database import get_db
from tameri_chat.crud import get_user
import tameri_chat.models as models

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Dict[str, WebSocket]] = {}
        self.user_groups: Dict[int, List[int]] = {}
        self.typing_users: Dict[int, Dict[int, bool]] = {}
        self.recording_users: Dict[int, Dict[int, bool]] = {}  # {group_id: {user_id: is_recording}}


    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        connection_id = str(uuid.uuid4())
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = {}
        
        self.active_connections[user_id][connection_id] = websocket
        print(f"User {user_id} connected with connection ID {connection_id}")
        return connection_id

    def disconnect(self, user_id: int, connection_id: str):
        if user_id in self.active_connections and connection_id in self.active_connections[user_id]:
            del self.active_connections[user_id][connection_id]
            print(f"User {user_id} disconnected connection ID {connection_id}")
            
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                print(f"User {user_id} has no more active connections")
                
                # Remove from all groups
                if user_id in self.user_groups:
                    del self.user_groups[user_id]

    
    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            for connection_id, websocket in self.active_connections[user_id].items():
                try:
                    await websocket.send_text(message)
                    print(f"Sent personal message to user {user_id} on connection {connection_id}")
                except Exception as e:
                    print(f"Error sending message to user {user_id}: {e}")
                    self.disconnect(user_id, connection_id)

    async def broadcast_to_group(self, group_id: int, message: str, exclude_user_id: int = None):
        print(f"Broadcasting to group {group_id}: {message}")
        users_in_group = []
        
        # Find all users in this group
        for user_id, groups in self.user_groups.items():
            if group_id in groups:
                users_in_group.append(user_id)
        
        # Send message to each user in group
        for user_id in users_in_group:
            if user_id != exclude_user_id:
                await self.send_personal_message(message, user_id)
        
        # For mentions, send special notifications
        try:
            message_data = json.loads(message)
            if message_data.get('type') == 'new_message' and message_data['data'].get('mentions'):
                # Get sender_id from the message data
                sender_id = message_data['data'].get('sender_id')
                if not sender_id:
                    return
                    
                for mentioned_user_id in message_data['data']['mentions']:
                    if mentioned_user_id != sender_id and mentioned_user_id in users_in_group:
                        mention_notification = {
                            "type": "mention",
                            "data": {
                                "message_id": message_data['data']['id'],
                                "group_id": group_id,
                                "mentioned_by": sender_id,
                                "content": message_data['data']['content'][:50] + "..." if len(message_data['data']['content']) > 50 else message_data['data']['content']
                            }
                        }
                        await self.send_personal_message(json.dumps(mention_notification), mentioned_user_id)
        except Exception as e:
            print(f"Error processing mentions: {e}")

    def add_user_to_group(self, user_id: int, group_id: int):
        if user_id not in self.user_groups:
            self.user_groups[user_id] = []
        
        if group_id not in self.user_groups[user_id]:
            self.user_groups[user_id].append(group_id)
            print(f"User {user_id} added to group {group_id}")
        
        # Initialize typing tracking if needed
        if group_id not in self.typing_users:
            self.typing_users[group_id] = {}

    def remove_user_from_group(self, user_id: int, group_id: int):
        if user_id in self.user_groups:
            if group_id in self.user_groups[user_id]:
                self.user_groups[user_id].remove(group_id)
                print(f"User {user_id} removed from group {group_id}")
                
            if not self.user_groups[user_id]:
                del self.user_groups[user_id]
        
        if group_id in self.typing_users and user_id in self.typing_users[group_id]:
            del self.typing_users[group_id][user_id]

    async def update_typing_status(self, user_id: int, group_id: int, is_typing: bool, db: Session):
        if group_id not in self.typing_users:
            self.typing_users[group_id] = {}
        
        current_status = self.typing_users[group_id].get(user_id, False)
        
        # Only send notification if status changed
        if current_status != is_typing:
            self.typing_users[group_id][user_id] = is_typing
            
            # Create typing message with user_info
            typing_message = WebSocketMessage(
                type="typing",
                data={
                    "user_id": user_id,
                    "group_id": group_id,
                    "is_typing": is_typing,
                    "user_info": ""  # Make sure this is included
                }
            )
            
            # Broadcast to group
            await self.broadcast_to_group(
                group_id=group_id,
                message=typing_message.json()
            )

    async def update_recording_status(self, user_id: int, group_id: int, is_recording: bool, db: Session):
        if group_id not in self.recording_users:
            self.recording_users[group_id] = {}
        
        current_status = self.recording_users[group_id].get(user_id, False)
        
        # Only send notification if status changed
        if current_status != is_recording:
            self.recording_users[group_id][user_id] = is_recording
            
            recording_message = WebSocketMessage(
                type="recording_status",
                data={
                    "user_id": user_id,
                    "group_id": group_id,
                    "is_recording": is_recording,
                    "user_info": ""  # Will be filled in
                }
            )
            
            await self.broadcast_to_group(
                group_id=group_id,
                message=recording_message.json(),
                exclude_user_id=user_id  # Don't send to self
            )

    def get_recording_users(self, group_id: int) -> List[int]:
        return [uid for uid, is_rec in self.recording_users.get(group_id, {}).items() if is_rec]

    def get_online_users_in_group(self, group_id: int) -> List[int]:
        online_users = []
        for user_id, groups in self.user_groups.items():
            if group_id in groups and user_id in self.active_connections:
                online_users.append(user_id)
        return online_users
    
    async def broadcast_to_all(self, message: str):
        print(f"Broadcasting to all users: {message}")
        for user_id in self.active_connections:
            for connection_id, websocket in self.active_connections[user_id].items():
                try:
                    await websocket.send_text(message)
                    print(f"Sent broadcast to user {user_id} on connection {connection_id}")
                except Exception as e:
                    print(f"Error broadcasting to user {user_id}: {e}")
                    self.disconnect(user_id, connection_id)
                    
    async def broadcast_new_group(self, group: dict):
        message = json.dumps({
            "type": "new_group",
            "data": group
        })
        
        for user_id in self.active_connections:
            for connection_id, websocket in self.active_connections[user_id].items():
                try:
                    await websocket.send_text(message)
                except:
                    self.disconnect(user_id, connection_id)

manager = ConnectionManager()





    