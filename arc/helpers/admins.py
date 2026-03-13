"""
Admin Helpers for Arc Music Bot
Handles admin permission checks

Copyright (c) 2025 Team Arc
Developer: @tusar404
"""

from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant, ChannelPrivate
from typing import Optional

from arc.core import app


async def is_admin(chat_id: int, user_id: int) -> bool:
    """Check if user is admin in chat."""
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in [
            ChatMemberStatus.OWNER,
            ChatMemberStatus.ADMINISTRATOR,
        ]
    except (UserNotParticipant, ChannelPrivate):
        return False
    except Exception:
        return False


async def get_admins(chat_id: int) -> list:
    """Get list of admin user IDs in chat."""
    admins = []
    try:
        async for member in app.get_chat_members(chat_id, filter=ChatMemberStatus.ADMINISTRATOR):
            if not member.user.is_bot:
                admins.append(member.user.id)
        # Also add owner
        async for member in app.get_chat_members(chat_id, filter=ChatMemberStatus.OWNER):
            if not member.user.is_bot:
                admins.append(member.user.id)
    except Exception:
        pass
    return admins


async def reload_admins(chat_id: int) -> list:
    """Reload and return admin list."""
    return await get_admins(chat_id)


async def bot_can_manage_voice_chats(chat_id: int) -> bool:
    """Check if bot can manage voice chats."""
    try:
        member = await app.get_chat_member(chat_id, app.id)
        return member.privileges and member.privileges.can_manage_video_chats
    except Exception:
        return False


async def bot_can_invite_users(chat_id: int) -> bool:
    """Check if bot can invite users."""
    try:
        member = await app.get_chat_member(chat_id, app.id)
        return member.privileges and member.privileges.can_invite_users
    except Exception:
        return False


async def bot_can_delete_messages(chat_id: int) -> bool:
    """Check if bot can delete messages."""
    try:
        member = await app.get_chat_member(chat_id, app.id)
        return member.privileges and member.privileges.can_delete_messages
    except Exception:
        return False


async def get_bot_permissions(chat_id: int) -> dict:
    """Get all bot permissions in chat."""
    permissions = {
        "can_manage_voice_chats": False,
        "can_invite_users": False,
        "can_delete_messages": False,
        "can_post_messages": False,
        "can_edit_messages": False,
        "is_admin": False,
    }

    try:
        member = await app.get_chat_member(chat_id, app.id)
        if member.privileges:
            permissions["can_manage_voice_chats"] = member.privileges.can_manage_video_chats
            permissions["can_invite_users"] = member.privileges.can_invite_users
            permissions["can_delete_messages"] = member.privileges.can_delete_messages
            permissions["can_post_messages"] = member.privileges.can_post_messages
            permissions["can_edit_messages"] = member.privileges.can_edit_messages
            permissions["is_admin"] = True
    except Exception:
        pass

    return permissions


async def check_bot_permissions(chat_id: int) -> tuple:
    """Check required bot permissions."""
    perms = await get_bot_permissions(chat_id)

    missing = []

    if not perms["can_manage_voice_chats"]:
        missing.append("Manage Voice Chats")

    if not perms["can_invite_users"]:
        missing.append("Invite Users")

    if not perms["is_admin"]:
        missing.append("Bot must be admin")

    return len(missing) == 0, missing
