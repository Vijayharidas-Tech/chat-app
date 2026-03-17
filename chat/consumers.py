import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Message

User = get_user_model()


def room_name_for_users(user1: str, user2: str) -> str:
    """Deterministic room name from two usernames."""
    usernames = sorted([user1, user2])
    return f"chat_{usernames[0]}_{usernames[1]}"


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        user = self.scope.get("user")
        other_username = self.scope["url_route"]["kwargs"]["username"]
        if not user or not user.is_authenticated:
            self.close()
            return

        self.room_group_name = room_name_for_users(user.username, other_username)

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name,
        )
        self.accept()

    def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            async_to_sync(self.channel_layer.group_discard)(
                self.room_group_name,
                self.channel_name,
            )

    def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return
        user = self.scope["user"]
        if not user or not user.is_authenticated:
            return

        data = json.loads(text_data)
        kind = data.get("kind", "message")

        # Typing indicator events (no DB write)
        if kind == "typing":
            receiver_username = data.get("receiver")
            if not receiver_username:
                return
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    "type": "typing_event",
                    "sender": user.username,
                    "receiver": receiver_username,
                },
            )
            return

        message = (data.get("message") or "").strip()
        receiver_username = data.get("receiver")
        if not message or not receiver_username:
            return

        try:
            receiver = User.objects.get(username=receiver_username)
        except User.DoesNotExist:
            return

        msg_obj = Message.objects.create(
            sender=user,
            receiver=receiver,
            message=message,
        )

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "chat_message",
                "id": msg_obj.id,
                "message": msg_obj.message,
                "sender": user.username,
                "receiver": receiver.username,
                "timestamp": msg_obj.timestamp.isoformat(),
                "is_read": msg_obj.is_read,
            },
        )

    def chat_message(self, event):
        self.send(text_data=json.dumps(event))

    def typing_event(self, event):
        self.send(text_data=json.dumps({"type": "typing", **event}))
