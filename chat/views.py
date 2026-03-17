from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Message

User = get_user_model()


@login_required
def user_list(request):
    users = User.objects.exclude(id=request.user.id).order_by("-is_online", "username")

    # Unread count per other user
    unread_counts = (
        Message.objects.filter(receiver=request.user, is_read=False)
        .values("sender_id")
        .annotate(total=Count("id"))
    )
    unread_map = {row["sender_id"]: row["total"] for row in unread_counts}

    return render(
        request,
        "user_list.html",
        {
            "users": users,
            "unread_map": unread_map,
        },
    )


@login_required
def chat_view(request, username):
    other_user = get_object_or_404(User, username=username)
    user = request.user

    # Load chat history
    messages_qs = Message.objects.filter(
        Q(sender=user, receiver=other_user) | Q(sender=other_user, receiver=user)
    ).order_by("timestamp")

    # Mark messages as read where current user is receiver and not read
    Message.objects.filter(sender=other_user, receiver=user, is_read=False).update(
        is_read=True, timestamp=timezone.now()
    )

    return render(
        request,
        "chat.html",
        {
            "other_user": other_user,
            "messages": messages_qs,
        },
    )


@login_required
def delete_message(request, pk):
    msg = get_object_or_404(Message, pk=pk, sender=request.user)
    chat_partner = msg.receiver
    msg.delete()
    return redirect("chat:chat", username=chat_partner.username)

