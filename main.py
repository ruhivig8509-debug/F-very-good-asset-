#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』 - TELEGRAM BOT              ║
║         PART 1 OF 3 - SECTIONS 1 THROUGH 10                  ║
║  Owner: 愛 | 𝗥𝗨𝗛𝗜 𝗫 𝗤𝗡𝗥〆                                    ║
║  Platform: Render (Web Service + PostgreSQL)                  ║
╚══════════════════════════════════════════════════════════════╝

SECTIONS IN THIS PART:
  1.  Configuration, Database, Models & Setup
  2.  Helper Utilities & Decorators
  3.  Welcome System (Greet, Goodbye, Captcha, Rules)
  4.  Admin & Moderation (Ban, Mute, Kick, Warn, etc.)
  5.  Anti-Spam / Anti-Flood / Anti-Link / Filters
  6.  Notes, Saved Messages, Hashtag Triggers
  7.  User Info, ID, Stats, Whois, Bio, AFK
  8.  Pin, Purge, Locks, Slowmode, Permissions
  9.  Blacklist Words, Media Filter, NSFW Guard
  10. Fun Commands, Games, Stickers, Memes, Truth/Dare
"""

import os
import sys
import re
import json
import time
import html
import random
import string
import hashlib
import asyncio
import logging
import datetime
import traceback
import urllib.parse
import threading
import platform
from io import BytesIO
from functools import wraps
from collections import defaultdict
from typing import Optional, List, Dict, Tuple, Union, Any
from telegram.constants import ChatType

# ─── Third-party imports ───
try:
    from telegram import (
        Update, Bot, Chat, User, Message,
        ChatMember, ChatMemberUpdated,
        ChatPermissions, ChatInviteLink,
        InlineKeyboardButton, InlineKeyboardMarkup,
        ReplyKeyboardMarkup, ReplyKeyboardRemove,
        ForceReply, InputFile, BotCommand,
        MessageEntity, ParseMode,
        CallbackQuery,
    )
    from telegram.ext import (
        Application, ApplicationBuilder,
        CommandHandler, MessageHandler,
        CallbackQueryHandler, ChatMemberHandler,
        ConversationHandler, ContextTypes,
        filters, Defaults, JobQueue,
    )
    from telegram.constants import (
        ChatAction, ChatType, ParseMode as PM,
        ChatMemberStatus, MessageLimit,
    )
    from telegram.error import (
        TelegramError, BadRequest, Forbidden,
        TimedOut, NetworkError, RetryAfter,
    )
    from telegram.helpers import escape_markdown, mention_html
except ImportError:
    print("Installing python-telegram-bot...")
    os.system("pip install python-telegram-bot[all]>=20.7")
    from telegram import *
    from telegram.ext import *

try:
    from sqlalchemy import (
        create_engine, Column, Integer, BigInteger, String,
        Text, Boolean, DateTime, Float, ForeignKey, JSON,
        Table, MetaData, Index, UniqueConstraint, event,
        and_, or_, not_, func, desc, asc, distinct, case,
        select, insert, update, delete,
    )
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import (
        sessionmaker, scoped_session, relationship,
        joinedload, contains_eager,
    )
    from sqlalchemy.exc import SQLAlchemyError, IntegrityError
    from sqlalchemy.pool import QueuePool
    from sqlalchemy.dialects.postgresql import JSONB, ARRAY
except ImportError:
    print("Installing SQLAlchemy and psycopg2...")
    os.system("pip install sqlalchemy psycopg2-binary")
    from sqlalchemy import *
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, scoped_session, relationship
    from sqlalchemy.exc import SQLAlchemyError, IntegrityError

try:
    from flask import Flask, jsonify, request as flask_request
except ImportError:
    os.system("pip install flask")
    from flask import Flask, jsonify, request as flask_request

try:
    import aiohttp
except ImportError:
    os.system("pip install aiohttp")
    import aiohttp

try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
except ImportError:
    os.system("pip install apscheduler")
    from apscheduler.schedulers.asyncio import AsyncIOScheduler

# ─── Logging Setup ───
logging.basicConfig(
    format="%(asctime)s - [%(name)s] - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger("RuhiBot")
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)


# ══════════════════════════════════════════════════════════════
# ██╗  SECTION 1: CONFIGURATION, DATABASE, MODELS & SETUP
# ══════════════════════════════════════════════════════════════

# ─── Environment Variables / Config ───
class Config:
    """Bot configuration from environment variables (Render)."""

    # Required
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    DATABASE_URL = os.environ.get("DATABASE_URL", "")

    # Owner & Sudo
    OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
    OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "RUHI_X_QNR")
    OWNER_NAME = os.environ.get("OWNER_NAME", "愛 | 𝗥𝗨𝗛𝗜 𝗫 𝗤𝗡𝗥〆")
    SUDO_USERS_STR = os.environ.get("SUDO_USERS", "")
    SUDO_USERS: List[int] = []

    # Bot Info
    BOT_NAME = os.environ.get("BOT_NAME", "『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』")
    BOT_USERNAME = os.environ.get("BOT_USERNAME", "")
    SUPPORT_CHAT = os.environ.get("SUPPORT_CHAT", "")
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "0"))
    UPDATE_CHANNEL = os.environ.get("UPDATE_CHANNEL", "")

    # Render
    PORT = int(os.environ.get("PORT", 10000))
    RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL", "")
    WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")

    # Limits
    FLOOD_LIMIT = int(os.environ.get("FLOOD_LIMIT", "10"))
    FLOOD_TIME = int(os.environ.get("FLOOD_TIME", "12"))
    WARN_LIMIT = int(os.environ.get("WARN_LIMIT", "3"))
    CAPTCHA_TIMEOUT = int(os.environ.get("CAPTCHA_TIMEOUT", "120"))

    # API keys (optional features)
    WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY", "")
    REMOVE_BG_API = os.environ.get("REMOVE_BG_API", "")
    OCR_API_KEY = os.environ.get("OCR_API_KEY", "")
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
    GOOGLE_CX = os.environ.get("GOOGLE_CX", "")
    CURRENCY_API_KEY = os.environ.get("CURRENCY_API_KEY", "")
    NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "")
    WOLFRAM_APP_ID = os.environ.get("WOLFRAM_APP_ID", "")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

    # Misc
    START_IMG = os.environ.get("START_IMG", "")
    HELP_IMG = os.environ.get("HELP_IMG", "")
    ALIVE_IMG = os.environ.get("ALIVE_IMG", "")
    DEFAULT_LANG = os.environ.get("DEFAULT_LANG", "en")

    # Runtime flags (not from env — set dynamically)
    MAINTENANCE_MODE: bool = False

    @classmethod
    def init(cls):
        """Parse and validate config."""
        # Fix Render postgres URL
        if cls.DATABASE_URL.startswith("postgres://"):
            cls.DATABASE_URL = cls.DATABASE_URL.replace(
                "postgres://", "postgresql://", 1
            )

        # Parse sudo users
        if cls.SUDO_USERS_STR:
            try:
                cls.SUDO_USERS = [
                    int(x.strip())
                    for x in cls.SUDO_USERS_STR.split()
                    if x.strip().lstrip('-').isdigit()
                ]
            except ValueError:
                cls.SUDO_USERS = []

        # Always add owner to sudo
        if cls.OWNER_ID and cls.OWNER_ID not in cls.SUDO_USERS:
            cls.SUDO_USERS.append(cls.OWNER_ID)

        # Validate required
        if not cls.BOT_TOKEN:
            logger.error("BOT_TOKEN not set!")
            sys.exit(1)
        if not cls.DATABASE_URL:
            logger.error("DATABASE_URL not set!")
            sys.exit(1)

        logger.info(f"✅ Config loaded. Owner: {cls.OWNER_ID}")
        logger.info(f"✅ Sudo Users: {cls.SUDO_USERS}")
        logger.info(f"✅ Database: {cls.DATABASE_URL[:30]}...")


Config.init()


# ─── Database Engine & Session ───
try:
    engine = create_engine(
        Config.DATABASE_URL,
        pool_size=20,
        max_overflow=30,
        pool_timeout=60,
        pool_recycle=1800,
        pool_pre_ping=True,
        echo=False,
    )
    SessionLocal = scoped_session(
        sessionmaker(bind=engine, autocommit=False, autoflush=False)
    )
    Base = declarative_base()
    logger.info("✅ Database engine created successfully.")
except Exception as e:
    logger.error(f"❌ Database connection failed: {e}")
    sys.exit(1)


def get_db():
    """Get a database session (scoped per thread)."""
    return SessionLocal()


def close_db(session):
    """Close database session safely and remove from scoped registry."""
    try:
        if session:
            session.close()
            SessionLocal.remove()
    except Exception:
        pass


# ─── Database Models ───

class DBUser(Base):
    """Stores user information."""
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    custom_title = Column(String(255), nullable=True)
    language = Column(String(10), default="en")
    is_premium = Column(Boolean, default=False)
    is_bot_banned = Column(Boolean, default=False)
    ban_reason = Column(Text, nullable=True)
    reputation = Column(Integer, default=0)
    coins = Column(Integer, default=100)
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    daily_claimed = Column(DateTime, nullable=True)
    married_to = Column(BigInteger, nullable=True)
    afk = Column(Boolean, default=False)
    afk_reason = Column(Text, nullable=True)
    afk_time = Column(DateTime, nullable=True)
    warns_given = Column(Integer, default=0)
    total_messages = Column(Integer, default=0)
    last_seen = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __repr__(self):
        return f"&lt;DBUser {self.user_id} - {self.first_name}&gt;"


class DBChat(Base):
    """Stores chat/group information and settings."""
    __tablename__ = "chats"

    chat_id = Column(BigInteger, primary_key=True)
    chat_title = Column(String(255), nullable=True)
    chat_username = Column(String(255), nullable=True)
    chat_type = Column(String(50), default="group")
    language = Column(String(10), default="en")

    # Welcome
    welcome_enabled = Column(Boolean, default=True)
    welcome_message = Column(Text, nullable=True)
    welcome_media = Column(Text, nullable=True)
    welcome_media_type = Column(String(20), nullable=True)
    welcome_delete_after = Column(Integer, default=300)
    welcome_mute_new = Column(Boolean, default=False)

    # Goodbye
    goodbye_enabled = Column(Boolean, default=True)
    goodbye_message = Column(Text, nullable=True)
    goodbye_media = Column(Text, nullable=True)
    goodbye_media_type = Column(String(20), nullable=True)
    goodbye_delete_after = Column(Integer, default=120)

    # Captcha
    captcha_enabled = Column(Boolean, default=False)
    captcha_type = Column(String(20), default="button")
    captcha_timeout = Column(Integer, default=120)
    captcha_kick = Column(Boolean, default=True)
    captcha_text = Column(Text, nullable=True)

    # Rules
    rules = Column(Text, nullable=True)
    rules_private = Column(Boolean, default=False)

    # Anti-spam
    antiflood_enabled = Column(Boolean, default=False)
    antiflood_limit = Column(Integer, default=10)
    antiflood_time = Column(Integer, default=12)
    antiflood_action = Column(String(20), default="mute")

    # Anti-link
    antilink_enabled = Column(Boolean, default=False)
    antilink_action = Column(String(20), default="delete")
    antilink_warn = Column(Boolean, default=True)
    antilink_allowed_links = Column(Text, nullable=True)

    # Anti-forward
    antiforward_enabled = Column(Boolean, default=False)
    antiforward_action = Column(String(20), default="delete")

    # Anti-channel
    antichannel_enabled = Column(Boolean, default=False)

    # Anti-bot
    antibot_enabled = Column(Boolean, default=False)

    # Anti-arabic
    antiarabic_enabled = Column(Boolean, default=False)

    # Anti-cyrillic
    anticyrillic_enabled = Column(Boolean, default=False)

    # Anti-sticker
    antisticker_enabled = Column(Boolean, default=False)
    antisticker_action = Column(String(20), default="delete")

    # Anti-gif
    antigif_enabled = Column(Boolean, default=False)

    # Anti-inline
    antiinline_enabled = Column(Boolean, default=False)

    # Anti-game
    antigame_enabled = Column(Boolean, default=False)

    # Anti-voice
    antivoice_enabled = Column(Boolean, default=False)

    # Anti-video
    antivideo_enabled = Column(Boolean, default=False)

    # Anti-photo
    antiphoto_enabled = Column(Boolean, default=False)

    # Anti-document
    antidocument_enabled = Column(Boolean, default=False)

    # Locks
    lock_text = Column(Boolean, default=False)
    lock_media = Column(Boolean, default=False)
    lock_sticker = Column(Boolean, default=False)
    lock_gif = Column(Boolean, default=False)
    lock_voice = Column(Boolean, default=False)
    lock_video = Column(Boolean, default=False)
    lock_videonote = Column(Boolean, default=False)
    lock_contact = Column(Boolean, default=False)
    lock_location = Column(Boolean, default=False)
    lock_inline = Column(Boolean, default=False)
    lock_game = Column(Boolean, default=False)
    lock_poll = Column(Boolean, default=False)
    lock_forward = Column(Boolean, default=False)
    lock_url = Column(Boolean, default=False)
    lock_bot = Column(Boolean, default=False)
    lock_command = Column(Boolean, default=False)
    lock_email = Column(Boolean, default=False)
    lock_phone = Column(Boolean, default=False)
    lock_button = Column(Boolean, default=False)
    lock_audio = Column(Boolean, default=False)
    lock_document = Column(Boolean, default=False)
    lock_photo = Column(Boolean, default=False)
    lock_anonchannel = Column(Boolean, default=False)

    # Slowmode
    slowmode_enabled = Column(Boolean, default=False)
    slowmode_seconds = Column(Integer, default=0)

    # Warn
    warn_limit = Column(Integer, default=3)
    warn_action = Column(String(20), default="ban")

    # Logging
    log_channel_id = Column(BigInteger, nullable=True)
    log_joins = Column(Boolean, default=True)
    log_leaves = Column(Boolean, default=True)
    log_warns = Column(Boolean, default=True)
    log_bans = Column(Boolean, default=True)
    log_mutes = Column(Boolean, default=True)
    log_pins = Column(Boolean, default=True)
    log_edits = Column(Boolean, default=True)
    log_deletes = Column(Boolean, default=True)
    log_reports = Column(Boolean, default=True)

    # Clean service
    clean_service = Column(Boolean, default=False)
    clean_welcome = Column(Boolean, default=False)
    clean_commands = Column(Boolean, default=False)

    # Night mode
    night_mode = Column(Boolean, default=False)
    night_start = Column(String(5), default="23:00")
    night_end = Column(String(5), default="06:00")

    # Misc
    force_subscribe = Column(String(255), nullable=True)
    auto_approve = Column(Boolean, default=False)
    report_enabled = Column(Boolean, default=True)
    sticker_pack = Column(String(255), nullable=True)
    chat_disabled = Column(Boolean, default=False)

    # Stats
    total_members = Column(Integer, default=0)
    total_messages = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __repr__(self):
        return f"&lt;DBChat {self.chat_id} - {self.chat_title}&gt;"


class DBWarn(Base):
    """Stores user warnings per chat."""
    __tablename__ = "warns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    warned_by = Column(BigInteger, nullable=False)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        Index("ix_warns_user_chat", "user_id", "chat_id"),
    )


class DBNote(Base):
    """Stores notes/saved messages per chat."""
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    media_file_id = Column(Text, nullable=True)
    media_type = Column(String(20), nullable=True)
    buttons = Column(Text, nullable=True)
    parse_mode = Column(String(10), default="HTML")
    no_preview = Column(Boolean, default=False)
    protect = Column(Boolean, default=False)
    private = Column(Boolean, default=False)
    created_by = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("chat_id", "name", name="uq_chat_note"),
        Index("ix_notes_chat_name", "chat_id", "name"),
    )


class DBFilter(Base):
    """Stores keyword-based auto-reply filters per chat."""
    __tablename__ = "filters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    keyword = Column(String(255), nullable=False)
    reply_text = Column(Text, nullable=True)
    media_file_id = Column(Text, nullable=True)
    media_type = Column(String(20), nullable=True)
    buttons = Column(Text, nullable=True)
    is_regex = Column(Boolean, default=False)
    action = Column(String(20), nullable=True)
    created_by = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("chat_id", "keyword", name="uq_chat_filter"),
        Index("ix_filters_chat_keyword", "chat_id", "keyword"),
    )


class DBBlacklist(Base):
    """Stores blacklisted words per chat."""
    __tablename__ = "blacklist"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    word = Column(String(255), nullable=False)
    action = Column(String(20), default="delete")
    reason = Column(Text, nullable=True)
    added_by = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("chat_id", "word", name="uq_chat_blacklist"),
        Index("ix_blacklist_chat_word", "chat_id", "word"),
    )


class DBAdmin(Base):
    """Stores custom admin roles and permissions."""
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    role = Column(String(50), default="admin")
    custom_title = Column(String(255), nullable=True)
    can_ban = Column(Boolean, default=True)
    can_mute = Column(Boolean, default=True)
    can_warn = Column(Boolean, default=True)
    can_pin = Column(Boolean, default=True)
    can_purge = Column(Boolean, default=True)
    can_invite = Column(Boolean, default=True)
    can_promote = Column(Boolean, default=False)
    can_change_info = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=True)
    added_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("chat_id", "user_id", name="uq_chat_admin"),
    )


class DBBan(Base):
    """Stores ban records."""
    __tablename__ = "bans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    banned_by = Column(BigInteger, nullable=False)
    reason = Column(Text, nullable=True)
    until_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        Index("ix_bans_chat_user", "chat_id", "user_id"),
    )


class DBMute(Base):
    """Stores mute records."""
    __tablename__ = "mutes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    muted_by = Column(BigInteger, nullable=False)
    reason = Column(Text, nullable=True)
    until_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        Index("ix_mutes_chat_user", "chat_id", "user_id"),
    )


class DBGban(Base):
    """Stores global ban records."""
    __tablename__ = "gbans"

    user_id = Column(BigInteger, primary_key=True)
    reason = Column(Text, nullable=True)
    banned_by = Column(BigInteger, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class DBFed(Base):
    """Stores federation information."""
    __tablename__ = "federations"

    fed_id = Column(String(36), primary_key=True)
    fed_name = Column(String(255), nullable=False)
    owner_id = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class DBFedAdmin(Base):
    """Federation admins."""
    __tablename__ = "fed_admins"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fed_id = Column(String(36), nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False)

    __table_args__ = (
        UniqueConstraint("fed_id", "user_id", name="uq_fed_admin"),
    )


class DBFedChat(Base):
    """Chats connected to a federation."""
    __tablename__ = "fed_chats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fed_id = Column(String(36), nullable=False, index=True)
    chat_id = Column(BigInteger, nullable=False, unique=True)

    __table_args__ = (
        UniqueConstraint("fed_id", "chat_id", name="uq_fed_chat"),
    )


class DBFedBan(Base):
    """Federation bans."""
    __tablename__ = "fed_bans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fed_id = Column(String(36), nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False)
    reason = Column(Text, nullable=True)
    banned_by = Column(BigInteger, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("fed_id", "user_id", name="uq_fed_ban"),
    )


class DBReport(Base):
    """User reports in chats."""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    reporter_id = Column(BigInteger, nullable=False)
    reported_id = Column(BigInteger, nullable=True)
    message_id = Column(BigInteger, nullable=True)
    reason = Column(Text, nullable=True)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class DBCaptcha(Base):
    """Stores pending captcha verifications."""
    __tablename__ = "captchas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    captcha_code = Column(String(20), nullable=True)
    message_id = Column(BigInteger, nullable=True)
    verified = Column(Boolean, default=False)
    attempts = Column(Integer, default=0)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        Index("ix_captcha_chat_user", "chat_id", "user_id"),
    )


class DBAFKUser(Base):
    """AFK status for users."""
    __tablename__ = "afk_users"

    user_id = Column(BigInteger, primary_key=True)
    is_afk = Column(Boolean, default=False)
    reason = Column(Text, nullable=True)
    afk_time = Column(DateTime, nullable=True)


class DBUserBio(Base):
    """Custom bios set by users or about other users."""
    __tablename__ = "user_bios"

    user_id = Column(BigInteger, primary_key=True)
    bio = Column(Text, nullable=True)
    set_by = Column(BigInteger, nullable=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class DBChatMember(Base):
    """Tracks chat membership for stats."""
    __tablename__ = "chat_members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    join_date = Column(DateTime, default=datetime.datetime.utcnow)
    message_count = Column(Integer, default=0)
    last_seen = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    __table_args__ = (
        UniqueConstraint("chat_id", "user_id", name="uq_chat_member"),
        Index("ix_chatmember_chat_user", "chat_id", "user_id"),
    )


class DBApproval(Base):
    """Approved users (bypass anti-* protections)."""
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False)
    approved_by = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("chat_id", "user_id", name="uq_chat_approval"),
    )


class DBDisabledCommand(Base):
    """Disabled commands per chat."""
    __tablename__ = "disabled_commands"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    command = Column(String(100), nullable=False)
    disabled_by = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("chat_id", "command", name="uq_chat_disabled_cmd"),
    )


class DBScheduledMessage(Base):
    """Scheduled messages for chats."""
    __tablename__ = "scheduled_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    message_text = Column(Text, nullable=False)
    schedule_time = Column(DateTime, nullable=False)
    repeat = Column(String(20), nullable=True)
    is_sent = Column(Boolean, default=False)
    created_by = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class DBPoll(Base):
    """Custom polls."""
    __tablename__ = "polls"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    question = Column(Text, nullable=False)
    options = Column(Text, nullable=False)
    created_by = Column(BigInteger, nullable=False)
    message_id = Column(BigInteger, nullable=True)
    is_anonymous = Column(Boolean, default=True)
    allows_multiple = Column(Boolean, default=False)
    is_closed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class DBReminder(Base):
    """User reminders."""
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    chat_id = Column(BigInteger, nullable=True)
    reminder_text = Column(Text, nullable=False)
    remind_at = Column(DateTime, nullable=False)
    is_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class DBCustomCommand(Base):
    """Custom commands per chat."""
    __tablename__ = "custom_commands"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    command = Column(String(100), nullable=False)
    response = Column(Text, nullable=False)
    media_file_id = Column(Text, nullable=True)
    media_type = Column(String(20), nullable=True)
    created_by = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("chat_id", "command", name="uq_chat_custom_cmd"),
    )


class DBStarboard(Base):
    """Starboard/highlights for popular messages."""
    __tablename__ = "starboard"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    message_id = Column(BigInteger, nullable=False)
    stars = Column(Integer, default=0)
    starred_by = Column(Text, nullable=True)
    starboard_msg_id = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class DBWelcomeButton(Base):
    """Welcome message buttons."""
    __tablename__ = "welcome_buttons"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    text = Column(String(255), nullable=False)
    url = Column(Text, nullable=True)
    callback_data = Column(String(255), nullable=True)
    row = Column(Integer, default=0)

    __table_args__ = (
        Index("ix_welcome_buttons_chat", "chat_id"),
    )


class DBAntiRaid(Base):
    """Anti-raid settings per chat."""
    __tablename__ = "antiraid"

    chat_id = Column(BigInteger, primary_key=True)
    enabled = Column(Boolean, default=False)
    action = Column(String(20), default="kick")
    joins_threshold = Column(Integer, default=10)
    time_window = Column(Integer, default=60)
    auto_disable = Column(Integer, default=3600)
    activated_at = Column(DateTime, nullable=True)


class DBConnection(Base):
    """PM connection to a chat for managing settings."""
    __tablename__ = "connections"

    user_id = Column(BigInteger, primary_key=True)
    chat_id = Column(BigInteger, nullable=False)
    connected_at = Column(DateTime, default=datetime.datetime.utcnow)


class DBEconomy(Base):
    """Economy system - user wallets."""
    __tablename__ = "economy"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    balance = Column(Integer, default=0)
    bank = Column(Integer, default=0)
    last_daily = Column(DateTime, nullable=True)
    last_weekly = Column(DateTime, nullable=True)
    last_work = Column(DateTime, nullable=True)
    last_rob = Column(DateTime, nullable=True)
    last_fish = Column(DateTime, nullable=True)
    last_hunt = Column(DateTime, nullable=True)
    last_mine = Column(DateTime, nullable=True)
    streak = Column(Integer, default=0)
    total_earned = Column(Integer, default=0)

    __table_args__ = (
        UniqueConstraint("user_id", "chat_id", name="uq_economy_user_chat"),
    )


class DBInventory(Base):
    """Inventory items for economy."""
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    item_name = Column(String(255), nullable=False)
    quantity = Column(Integer, default=1)
    item_type = Column(String(50), nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "chat_id", "item_name", name="uq_inv_user_chat_item"),
    )


class DBMarriage(Base):
    """Marriage records."""
    __tablename__ = "marriages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user1_id = Column(BigInteger, nullable=False, index=True)
    user2_id = Column(BigInteger, nullable=False, index=True)
    chat_id = Column(BigInteger, nullable=True)
    married_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)


class DBReputation(Base):
    """Reputation tracking."""
    __tablename__ = "reputation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    rep_points = Column(Integer, default=0)
    last_rep_given = Column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "chat_id", name="uq_rep_user_chat"),
    )


class DBTruthDare(Base):
    """Custom truth/dare questions per chat."""
    __tablename__ = "truth_dare"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    td_type = Column(String(10), nullable=False)  # truth / dare
    question = Column(Text, nullable=False)
    added_by = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class DBAutoReply(Base):
    """Auto-reply / chatbot messages."""
    __tablename__ = "auto_replies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    trigger = Column(String(255), nullable=False)
    response = Column(Text, nullable=False)
    is_regex = Column(Boolean, default=False)
    created_by = Column(BigInteger, nullable=True)

    __table_args__ = (
        UniqueConstraint("chat_id", "trigger", name="uq_autoreply_chat_trigger"),
    )


class DBAntiSpamLog(Base):
    """Logs anti-spam actions."""
    __tablename__ = "antispam_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False)
    action = Column(String(50), nullable=False)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class DBPinMessage(Base):
    """Pinned message tracking."""
    __tablename__ = "pin_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    message_id = Column(BigInteger, nullable=False)
    pinned_by = Column(BigInteger, nullable=False)
    pinned_at = Column(DateTime, default=datetime.datetime.utcnow)


class DBTag(Base):
    """Tag all / mention all tracking."""
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False)
    opt_out = Column(Boolean, default=False)


class DBLanguage(Base):
    """Per-chat language setting."""
    __tablename__ = "languages"

    chat_id = Column(BigInteger, primary_key=True)
    language = Column(String(10), default="en")


class DBBotStats(Base):
    """Global bot statistics."""
    __tablename__ = "bot_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stat_name = Column(String(100), unique=True, nullable=False)
    stat_value = Column(BigInteger, default=0)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class DBFunScore(Base):
    """Fun game scores."""
    __tablename__ = "fun_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    game_type = Column(String(50), nullable=False)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    draws = Column(Integer, default=0)
    score = Column(Integer, default=0)

    __table_args__ = (
        UniqueConstraint("user_id", "chat_id", "game_type", name="uq_funscore"),
    )


class DBStickerPack(Base):
    """Custom sticker pack tracking."""
    __tablename__ = "sticker_packs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    pack_name = Column(String(255), nullable=False)
    pack_title = Column(String(255), nullable=True)
    sticker_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class DBFloodTracker(Base):
    """Tracks flood data per user per chat."""
    __tablename__ = "flood_tracker"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    message_count = Column(Integer, default=0)
    first_message_time = Column(DateTime, nullable=True)
    last_warned = Column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint("chat_id", "user_id", name="uq_flood_chat_user"),
    )


# ─── Create All Tables ───
def create_tables():
    """Create all database tables."""
    try:
        Base.metadata.create_all(engine)
        logger.info("✅ All database tables created successfully!")
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        raise


create_tables()


# Alias for compatibility
DBMembership = DBChatMember

# ─── Database Helper Functions ───

def db_get_user(user_id: int) -> Optional[DBUser]:
    """Get user from database. Returns a detached copy."""
    session = get_db()
    try:
        obj = session.query(DBUser).filter(DBUser.user_id == user_id).first()
        if obj:
            session.expunge(obj)  # detach safely before close
        return obj
    finally:
        close_db(session)


def db_save_user(user: User):
    """Save or update user in database."""
    if not user or user.is_bot:
        return
    session = get_db()
    try:
        db_user = session.query(DBUser).filter(DBUser.user_id == user.id).first()
        if db_user:
            db_user.username = user.username
            db_user.first_name = user.first_name
            db_user.last_name = user.last_name
            db_user.is_premium = getattr(user, 'is_premium', False) or False
            db_user.updated_at = datetime.datetime.utcnow()
        else:
            db_user = DBUser(
                user_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                is_premium=getattr(user, 'is_premium', False) or False,
            )
            session.add(db_user)
        session.commit()
    except IntegrityError:
        session.rollback()
    except Exception as e:
        session.rollback()
        logger.error(f"Error saving user: {e}")
    finally:
        close_db(session)


def db_get_chat(chat_id: int) -> Optional[DBChat]:
    """Get chat settings from database. Returns a detached copy."""
    session = get_db()
    try:
        obj = session.query(DBChat).filter(DBChat.chat_id == chat_id).first()
        if obj:
            session.expunge(obj)
        return obj
    finally:
        close_db(session)


def db_save_chat(chat: Chat):
    """Save or update chat in database."""
    if not chat:
        return
    session = get_db()
    try:
        db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
        if db_chat:
            db_chat.chat_title = chat.title
            db_chat.chat_username = chat.username
            db_chat.chat_type = chat.type
            db_chat.updated_at = datetime.datetime.utcnow()
        else:
            db_chat = DBChat(
                chat_id=chat.id,
                chat_title=chat.title,
                chat_username=chat.username,
                chat_type=chat.type,
            )
            session.add(db_chat)
        session.commit()
    except IntegrityError:
        session.rollback()
    except Exception as e:
        session.rollback()
        logger.error(f"Error saving chat: {e}")
    finally:
        close_db(session)


def db_update_chat_setting(chat_id: int, **kwargs):
    """Update specific chat settings."""
    session = get_db()
    try:
        db_chat = session.query(DBChat).filter(DBChat.chat_id == chat_id).first()
        if not db_chat:
            db_chat = DBChat(chat_id=chat_id)
            session.add(db_chat)
        for key, value in kwargs.items():
            if hasattr(db_chat, key):
                setattr(db_chat, key, value)
        db_chat.updated_at = datetime.datetime.utcnow()
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating chat setting: {e}")
    finally:
        close_db(session)


def db_increment_user_messages(user_id: int, chat_id: int):
    """Increment message count for user globally and per chat."""
    session = get_db()
    try:
        # Global user
        db_user = session.query(DBUser).filter(DBUser.user_id == user_id).first()
        if db_user:
            db_user.total_messages = (db_user.total_messages or 0) + 1

        # Chat member
        member = session.query(DBChatMember).filter(
            DBChatMember.chat_id == chat_id,
            DBChatMember.user_id == user_id
        ).first()
        if member:
            member.message_count = (member.message_count or 0) + 1
            member.last_seen = datetime.datetime.utcnow()
        else:
            member = DBChatMember(
                chat_id=chat_id,
                user_id=user_id,
                message_count=1,
                last_seen=datetime.datetime.utcnow()
            )
            session.add(member)

        # Chat total
        db_chat = session.query(DBChat).filter(DBChat.chat_id == chat_id).first()
        if db_chat:
            db_chat.total_messages = (db_chat.total_messages or 0) + 1

        session.commit()
    except Exception as e:
        session.rollback()
    finally:
        close_db(session)


# ─── Flask App for Render Health Check ───
flask_app = Flask(__name__)


@flask_app.route("/")
def index():
    return jsonify({
        "status": "alive",
        "bot": Config.BOT_NAME,
        "owner": Config.OWNER_NAME,
        "uptime": str(datetime.datetime.utcnow()),
    })


@flask_app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


@flask_app.route("/stats")
def stats_route():
    session = get_db()
    try:
        user_count = session.query(func.count(DBUser.user_id)).scalar() or 0
        chat_count = session.query(func.count(DBChat.chat_id)).scalar() or 0
        return jsonify({
            "users": user_count,
            "chats": chat_count,
            "status": "running"
        })
    finally:
        close_db(session)


# ══════════════════════════════════════════════════════════════
# ██╗  SECTION 2: HELPER UTILITIES & DECORATORS
# ══════════════════════════════════════════════════════════════

# ─── Stylish Text Formatter ───
class StyleText:
    """Generate stylish Unicode text for bot responses."""

    # Mapping for bold-style letters
    BOLD_MAP = {
        'A': '𝐀', 'B': '𝐁', 'C': '𝐂', 'D': '𝐃', 'E': '𝐄', 'F': '𝐅',
        'G': '𝐆', 'H': '𝐇', 'I': '𝐈', 'J': '𝐉', 'K': '𝐊', 'L': '𝐋',
        'M': '𝐌', 'N': '𝐍', 'O': '𝐎', 'P': '𝐏', 'Q': '𝐐', 'R': '𝐑',
        'S': '𝐒', 'T': '𝐓', 'U': '𝐔', 'V': '𝐕', 'W': '𝐖', 'X': '𝐗',
        'Y': '𝐘', 'Z': '𝐙',
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ғ',
        'g': 'ɢ', 'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ',
        'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ',
        's': 's', 't': 'ᴛ', 'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x',
        'y': 'ʏ', 'z': 'ᴢ',
    }

    SMALL_CAPS = {
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ꜰ',
        'g': 'ɢ', 'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ',
        'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ',
        's': 'ꜱ', 't': 'ᴛ', 'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x',
        'y': 'ʏ', 'z': 'ᴢ',
    }

    BOLD_SANS = {
        'A': '𝗔', 'B': '𝗕', 'C': '𝗖', 'D': '𝗗', 'E': '𝗘', 'F': '𝗙',
        'G': '𝗚', 'H': '𝗛', 'I': '𝗜', 'J': '𝗝', 'K': '𝗞', 'L': '𝗟',
        'M': '𝗠', 'N': '𝗡', 'O': '𝗢', 'P': '𝗣', 'Q': '𝗤', 'R': '𝗥',
        'S': '𝗦', 'T': '𝗧', 'U': '𝗨', 'V': '𝗩', 'W': '𝗪', 'X': '𝗫',
        'Y': '𝗬', 'Z': '𝗭',
        'a': '𝗮', 'b': '𝗯', 'c': '𝗰', 'd': '𝗱', 'e': '𝗲', 'f': '𝗳',
        'g': '𝗴', 'h': '𝗵', 'i': '𝗶', 'j': '𝗷', 'k': '𝗸', 'l': '𝗹',
        'm': '𝗺', 'n': '𝗻', 'o': '𝗼', 'p': '𝗽', 'q': '𝗾', 'r': '𝗿',
        's': '𝘀', 't': '𝘁', 'u': '𝘂', 'v': '𝘃', 'w': '𝘄', 'x': '𝘅',
        'y': '𝘆', 'z': '𝘇',
    }

    @staticmethod
    def bold_fancy(text: str) -> str:
        return ''.join(StyleText.BOLD_MAP.get(c, c) for c in text)

    @staticmethod
    def small_caps(text: str) -> str:
        return ''.join(StyleText.SMALL_CAPS.get(c, c) for c in text.lower())

    @staticmethod
    def bold_sans(text: str) -> str:
        return ''.join(StyleText.BOLD_SANS.get(c, c) for c in text)


ST = StyleText()


# ─── Response Templates ───
class Templates:
    """Pre-built stylish response templates."""

    SEPARATOR = "━━━━━━━━━━━━━━━━━━"
    THIN_SEP = "─────────────────"

    @staticmethod
    def header(title: str) -> str:
        return f"✦ {ST.bold_fancy(title)} ✦\n{Templates.SEPARATOR}\n"

    @staticmethod
    def box_start(title: str) -> str:
        return f"╔═══[ {ST.bold_fancy(title)} ]═════╗\n"

    @staticmethod
    def box_line(label: str, value: str) -> str:
        return f"║ ✧ {ST.bold_fancy(label)}: {value}\n"

    @staticmethod
    def box_end() -> str:
        return "╚════════════════╝\n"

    @staticmethod
    def footer() -> str:
        return (
            f"\n{Templates.SEPARATOR}\n"
            f"👑 {ST.bold_fancy('Owner')}: {Config.OWNER_NAME}\n"
            f"{Templates.SEPARATOR}\n"
            f" {ST.bold_fancy('Powered By')}: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』"
        )

    @staticmethod
    def mini_footer() -> str:
        return f"\n{Templates.THIN_SEP}\n {ST.bold_fancy('Powered By')}: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』"

    @staticmethod
    def success(msg: str) -> str:
        return f"✅ {msg}"

    @staticmethod
    def error(msg: str) -> str:
        return f"❌ {msg}"

    @staticmethod
    def warning(msg: str) -> str:
        return f"⚠️ {msg}"

    @staticmethod
    def info(msg: str) -> str:
        return f"ℹ️ {msg}"


TPL = Templates()


# ─── Permission Helpers ───

def is_owner(user_id: int) -> bool:
    """Check if user is bot owner."""
    return user_id == Config.OWNER_ID


def is_sudo(user_id: int) -> bool:
    """Check if user is sudo or owner."""
    return user_id in Config.SUDO_USERS or user_id == Config.OWNER_ID


async def is_admin(update: Update, user_id: int) -> bool:
    """Check if user is admin in current chat."""
    if is_sudo(user_id):
        return True
    try:
        chat = update.effective_chat
        member = await chat.get_member(user_id)
        return member.status in [
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER
        ]
    except Exception:
        return False


async def is_creator(update: Update, user_id: int) -> bool:
    """Check if user is the chat creator/owner."""
    if is_owner(user_id):
        return True
    try:
        chat = update.effective_chat
        member = await chat.get_member(user_id)
        return member.status == ChatMemberStatus.OWNER
    except Exception:
        return False


async def bot_is_admin(chat: Chat, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if bot is admin in the chat."""
    try:
        bot_member = await chat.get_member(context.bot.id)
        return bot_member.status in [
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER
        ]
    except Exception:
        return False


async def can_restrict(chat: Chat, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if bot can restrict members."""
    try:
        bot_member = await chat.get_member(context.bot.id)
        return bot_member.can_restrict_members
    except Exception:
        return False


async def can_delete_messages(chat: Chat, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if bot can delete messages."""
    try:
        bot_member = await chat.get_member(context.bot.id)
        return bot_member.can_delete_messages
    except Exception:
        return False


async def can_pin_messages(chat: Chat, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if bot can pin messages."""
    try:
        bot_member = await chat.get_member(context.bot.id)
        return bot_member.can_pin_messages
    except Exception:
        return False


async def can_promote_members(chat: Chat, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if bot can promote members."""
    try:
        bot_member = await chat.get_member(context.bot.id)
        return bot_member.can_promote_members
    except Exception:
        return False


async def can_invite_users(chat: Chat, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if bot can invite users."""
    try:
        bot_member = await chat.get_member(context.bot.id)
        return bot_member.can_invite_users
    except Exception:
        return False


async def can_change_info(chat: Chat, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if bot can change chat info."""
    try:
        bot_member = await chat.get_member(context.bot.id)
        return bot_member.can_change_info
    except Exception:
        return False


# ─── User extraction helpers ───

async def extract_user_and_reason(
    message: Message, context: ContextTypes.DEFAULT_TYPE
) -> Tuple[Optional[int], Optional[str], Optional[User]]:
    """Extract target user and reason from a command message.
    Returns (user_id, reason, user_object_or_None)
    """
    user_id = None
    reason = None
    user_obj = None
    args = message.text.split() if message.text else []

    # If replying to a message
    if message.reply_to_message:
        user_obj = message.reply_to_message.from_user
        if user_obj:
            user_id = user_obj.id
        reason = " ".join(args[1:]) if len(args) > 1 else None
        return user_id, reason, user_obj

    # If user_id or @username is provided as argument
    if len(args) > 1:
        target = args[1]

        # Check if it's a user ID
        if target.lstrip('-').isdigit():
            user_id = int(target)
            reason = " ".join(args[2:]) if len(args) > 2 else None
        # Check if it's a username
        elif target.startswith("@"):
            username = target.lstrip("@")
            # Try to find in database
            session = get_db()
            try:
                db_user = session.query(DBUser).filter(
                    func.lower(DBUser.username) == username.lower()
                ).first()
                if db_user:
                    user_id = db_user.user_id
            finally:
                close_db(session)

            if not user_id:
                # Try via Telegram API
                try:
                    chat_member = await message.chat.get_member(target)
                    if chat_member and chat_member.user:
                        user_id = chat_member.user.id
                        user_obj = chat_member.user
                except Exception:
                    pass

            reason = " ".join(args[2:]) if len(args) > 2 else None
        else:
            reason = " ".join(args[1:])

    # Try to get user object if we only have ID
    if user_id and not user_obj:
        try:
            chat_member = await message.chat.get_member(user_id)
            if chat_member:
                user_obj = chat_member.user
        except Exception:
            pass

    return user_id, reason, user_obj


async def extract_user(
    message: Message, context: ContextTypes.DEFAULT_TYPE
) -> Tuple[Optional[int], Optional[User]]:
    """Extract user from command (simplified - no reason)."""
    user_id, _, user_obj = await extract_user_and_reason(message, context)
    return user_id, user_obj


def get_user_link(user: User) -> str:
    """Get a clickable HTML mention for a user."""
    if not user:
        return "Unknown"
    name = html.escape(user.first_name or "User")
    return f'<a href="tg://user?id={user.id}">{name}</a>'


def get_user_mention(user_id: int, name: str) -> str:
    """Get a clickable mention by ID and name."""
    name = html.escape(name or "User")
    return f'<a href="tg://user?id={user_id}">{name}</a>'


def get_chat_link(chat: Chat) -> str:
    """Get chat link."""
    if chat.username:
        return f"https://t.me/{chat.username}"
    return f"tg://chat?id={chat.id}"


# ─── Time parsing helpers ───

def parse_time_string(time_str: str) -> Optional[datetime.timedelta]:
    """Parse a time string like '1h', '30m', '2d', '1w' into timedelta."""
    if not time_str:
        return None

    time_str = time_str.strip().lower()
    match = re.match(r'^(\d+)\s*(s|sec|second|seconds|m|min|minute|minutes|h|hr|hour|hours|d|day|days|w|week|weeks)$', time_str)
    if not match:
        return None

    amount = int(match.group(1))
    unit = match.group(2)

    if unit in ('s', 'sec', 'second', 'seconds'):
        return datetime.timedelta(seconds=amount)
    elif unit in ('m', 'min', 'minute', 'minutes'):
        return datetime.timedelta(minutes=amount)
    elif unit in ('h', 'hr', 'hour', 'hours'):
        return datetime.timedelta(hours=amount)
    elif unit in ('d', 'day', 'days'):
        return datetime.timedelta(days=amount)
    elif unit in ('w', 'week', 'weeks'):
        return datetime.timedelta(weeks=amount)

    return None


def format_timedelta(td: datetime.timedelta) -> str:
    """Format timedelta to human readable string."""
    total_seconds = int(td.total_seconds())
    if total_seconds < 60:
        return f"{total_seconds} seconds"
    elif total_seconds < 3600:
        minutes = total_seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''}"
    elif total_seconds < 86400:
        hours = total_seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''}"
    else:
        days = total_seconds // 86400
        return f"{days} day{'s' if days > 1 else ''}"


def time_since(dt: datetime.datetime) -> str:
    """Get human-readable time since a datetime."""
    if not dt:
        return "Never"
    now = datetime.datetime.utcnow()
    diff = now - dt
    seconds = int(diff.total_seconds())

    if seconds < 60:
        return f"{seconds}s ago"
    elif seconds < 3600:
        return f"{seconds // 60}m ago"
    elif seconds < 86400:
        return f"{seconds // 3600}h ago"
    elif seconds < 604800:
        return f"{seconds // 86400}d ago"
    else:
        return dt.strftime("%Y-%m-%d %H:%M")


# ─── Decorators ───

def admin_required(func):
    """Decorator: only admins can use this command."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        chat = update.effective_chat

        if chat.type == ChatType.PRIVATE:
            return await func(update, context)

        if not await is_admin(update, user.id):
            await update.message.reply_text(
                TPL.error(f"{ST.bold_fancy('Only admins can use this command!')}"),
                parse_mode="HTML"
            )
            return
        return await func(update, context)
    return wrapper


def owner_required(func):
    """Decorator: only bot owner can use this command."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if not is_owner(user.id):
            await update.message.reply_text(
                TPL.error(f"{ST.bold_fancy('Only bot owner can use this command!')}"),
                parse_mode="HTML"
            )
            return
        return await func(update, context)
    return wrapper


def sudo_required(func):
    """Decorator: only sudo users can use this command."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if not is_sudo(user.id):
            await update.message.reply_text(
                TPL.error(f"{ST.bold_fancy('Only sudo users can use this command!')}"),
                parse_mode="HTML"
            )
            return
        return await func(update, context)
    return wrapper


def group_only(func):
    """Decorator: command works only in groups."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat = update.effective_chat
        if chat.type == ChatType.PRIVATE:
            await update.message.reply_text(
                TPL.error(f"{ST.bold_fancy('This command only works in groups!')}"),
                parse_mode="HTML"
            )
            return
        return await func(update, context)
    return wrapper


def private_only(func):
    """Decorator: command works only in private/DM."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat = update.effective_chat
        if chat.type != ChatType.PRIVATE:
            await update.message.reply_text(
                TPL.info(f"{ST.bold_fancy('Please use this command in PM!')}"),
                parse_mode="HTML"
            )
            return
        return await func(update, context)
    return wrapper


def bot_admin_required(func):
    """Decorator: bot must be admin."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat = update.effective_chat
        if chat.type == ChatType.PRIVATE:
            return await func(update, context)

        if not await bot_is_admin(chat, context):
            await update.message.reply_text(
                TPL.error(f"{ST.bold_fancy('I need to be admin to do this!')}"),
                parse_mode="HTML"
            )
            return
        return await func(update, context)
    return wrapper


def disabled_check(func):
    """Decorator: check if command is disabled in this chat."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat = update.effective_chat
        if chat.type == ChatType.PRIVATE:
            return await func(update, context)

        # Get command name
        if update.message and update.message.text:
            cmd = update.message.text.split()[0].lstrip('/').split('@')[0].lower()
        else:
            return await func(update, context)

        session = get_db()
        try:
            disabled = session.query(DBDisabledCommand).filter(
                DBDisabledCommand.chat_id == chat.id,
                DBDisabledCommand.command == cmd
            ).first()
            if disabled:
                return  # Silently ignore
        finally:
            close_db(session)

        return await func(update, context)
    return wrapper


def log_action(func):
    """Decorator: log admin actions to log channel."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        result = await func(update, context)

        # Try to log
        try:
            chat = update.effective_chat
            user = update.effective_user
            if chat.type != ChatType.PRIVATE:
                session = get_db()
                try:
                    db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
                    log_channel = db_chat.log_channel_id if db_chat else None
                finally:
                    close_db(session)

                if log_channel:
                    cmd = update.message.text if update.message and update.message.text else "Unknown"
                    log_text = (
                        f"📋 {ST.bold_fancy('Action Log')}\n"
                        f"{TPL.SEPARATOR}\n"
                        f"👤 {ST.bold_fancy('Admin')}: {get_user_link(user)}\n"
                        f"💬 {ST.bold_fancy('Chat')}: {html.escape(chat.title or 'Unknown')}\n"
                        f"📝 {ST.bold_fancy('Command')}: <code>{html.escape(cmd[:100])}</code>\n"
                        f"🕐 {ST.bold_fancy('Time')}: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
                        f"{TPL.SEPARATOR}"
                    )
                    try:
                        await context.bot.send_message(
                            log_channel, log_text, parse_mode="HTML"
                        )
                    except Exception:
                        pass
        except Exception:
            pass

        return result
    return wrapper


# ─── Approved user check ───

def is_approved(chat_id: int, user_id: int) -> bool:
    """Check if user is approved (bypasses anti-* protections)."""
    if is_sudo(user_id):
        return True
    session = get_db()
    try:
        approval = session.query(DBApproval).filter(
            DBApproval.chat_id == chat_id,
            DBApproval.user_id == user_id
        ).first()
        return approval is not None
    finally:
        close_db(session)


# ─── Button builder helpers ───

def build_keyboard(buttons_text: str) -> Optional[InlineKeyboardMarkup]:
    """Parse button text format and build InlineKeyboardMarkup.
    Format: [Button Text](url) or [Button Text](buttonurl://url)
    Multiple buttons per row separated by :same
    """
    if not buttons_text:
        return None

    lines = buttons_text.strip().split('\n')
    keyboard = []
    current_row = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Parse [text](url) format
        pattern = r'\[(.+?)\]\((.+?)\)'
        matches = re.findall(pattern, line)

        for text, url in matches:
            same_line = ':same' in url
            url = url.replace(':same', '').strip()

            if url.startswith('buttonurl://'):
                url = url.replace('buttonurl://', '', 1)

            btn = InlineKeyboardButton(text=text, url=url)

            if same_line and current_row:
                current_row.append(btn)
            else:
                if current_row:
                    keyboard.append(current_row)
                current_row = [btn]

    if current_row:
        keyboard.append(current_row)

    return InlineKeyboardMarkup(keyboard) if keyboard else None


def make_button(text: str, callback: str = None, url: str = None) -> InlineKeyboardButton:
    """Shortcut to make a button."""
    if url:
        return InlineKeyboardButton(text=text, url=url)
    return InlineKeyboardButton(text=text, callback_data=callback or "noop")


def make_keyboard(*rows) -> InlineKeyboardMarkup:
    """Build keyboard from rows of buttons."""
    return InlineKeyboardMarkup(list(rows))


# ─── Misc Helpers ───

def truncate(text: str, max_len: int = 4000) -> str:
    """Truncate text to max length."""
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."


def format_number(num: int) -> str:
    """Format number with commas."""
    return f"{num:,}"


def random_string(length: int = 8) -> str:
    """Generate random string."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def escape_html(text: str) -> str:
    """Escape HTML entities."""
    return html.escape(str(text)) if text else ""


async def delete_message_after(message: Message, seconds: int = 30):
    """Delete a message after specified seconds."""
    await asyncio.sleep(seconds)
    try:
        await message.delete()
    except Exception:
        pass


async def send_and_delete(
    chat_id: int,
    text: str,
    context: ContextTypes.DEFAULT_TYPE,
    seconds: int = 30,
    **kwargs
):
    """Send a message and delete it after seconds."""
    try:
        msg = await context.bot.send_message(chat_id, text, **kwargs)
        asyncio.create_task(delete_message_after(msg, seconds))
        return msg
    except Exception:
        return None


# ─── In-Memory Caches ───

# Flood tracking
flood_data: Dict[str, Dict] = defaultdict(lambda: {"count": 0, "first_time": None})

# AFK cache
afk_cache: Dict[int, Dict] = {}

# Captcha pending
captcha_pending: Dict[str, Dict] = {}

# Rate limiter
rate_limit_data: Dict[str, float] = {}

# Welcome message cache for deletion
welcome_msg_cache: Dict[int, List[int]] = defaultdict(list)

# Admin cache (refreshed periodically)
admin_cache: Dict[int, List[int]] = {}
admin_cache_time: Dict[int, float] = {}

ADMIN_CACHE_DURATION = 300  # 5 minutes


async def get_admin_list(chat: Chat, context: ContextTypes.DEFAULT_TYPE) -> List[int]:
    """Get list of admin user IDs with caching."""
    chat_id = chat.id
    now = time.time()

    if chat_id in admin_cache and (now - admin_cache_time.get(chat_id, 0)) < ADMIN_CACHE_DURATION:
        return admin_cache[chat_id]

    try:
        admins = await chat.get_administrators()
        admin_ids = [a.user.id for a in admins]
        admin_cache[chat_id] = admin_ids
        admin_cache_time[chat_id] = now
        return admin_ids
    except Exception:
        return admin_cache.get(chat_id, [])


def rate_limited(key: str, cooldown: int = 3) -> bool:
    """Check if an action is rate limited."""
    now = time.time()
    if key in rate_limit_data:
        if now - rate_limit_data[key] < cooldown:
            return True
    rate_limit_data[key] = now
    return False


# ─── Welcome message placeholder parser ───

def parse_welcome_text(
    text: str,
    user: User,
    chat: Chat,
    member_count: int = 0
) -> str:
    """Replace placeholders in welcome/goodbye text. Returns HTML-safe string."""
    if not text:
        return ""

    first_name = escape_html(user.first_name or "User")
    last_name = escape_html(user.last_name or "")
    full_name = f"{first_name} {last_name}".strip()
    username = f"@{user.username}" if user.username else first_name
    mention = get_user_link(user)
    chat_title = escape_html(chat.title or "Group")
    user_id = str(user.id)
    chat_id = str(chat.id)
    count = str(member_count)

    replacements = {
        "{first}": first_name,
        "{last}": last_name,
        "{fullname}": full_name,
        "{username}": username,
        "{mention}": mention,
        "{id}": user_id,
        "{chatname}": chat_title,
        "{chatid}": chat_id,
        "{count}": count,
        "{title}": chat_title,
        "{rules}": "/rules",
    }

    for key, value in replacements.items():
        text = text.replace(key, value)

    # ─── CRITICAL: Remove any leftover {placeholder} patterns ───
    # These cause Telegram HTML parser to crash (e.g., {rules} → &lt;rules&gt; tag error)
    import re as _re
    text = _re.sub(r'\{[a-zA-Z_][a-zA-Z0-9_]*\}', '', text)

    return text


# ══════════════════════════════════════════════════════════════
# ██╗  SECTION 3: WELCOME SYSTEM (GREET, GOODBYE, CAPTCHA, RULES)
# ══════════════════════════════════════════════════════════════

# ─── Default Welcome Message ───
DEFAULT_WELCOME = """✦ {ST_WELCOME} ✦
{SEP}

╔═══[ {ST_YOUR_INFO} ]═════╗
║ ✧ {ST_USER}: {{mention}}
║ ✧ {ST_USER_ID}: {{id}}
║ ✧ {ST_USERNAME}: {{username}}
║ ✧ {ST_GROUP_ID}: {{chatid}}
╚════════════════╝

⚠️ {BS_RULES}:-

➊ 🚫 {ST_NO} {SC_LINKS}
➋ ❌ {ST_NO} {SC_ABUSE}
➌ ⚠️ {ST_NO} {SC_PROMO}
➍ 🔞 {ST_NO} {SC_NSFW}
➎ ⛔ {ST_NO} {SC_BANNED_EMOJIS}

⚙️ {BS_AVAILABLE_COMMANDS}:
• /id • /info • /rules • /help – ✧{ST_USEFUL_BOT_CMDS}

{SEP}
👑 {ST_OWNER}: {OWNER_NAME}
{SEP}
 {ST_POWERED_BY}: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』""".format(
    ST_WELCOME=ST.bold_fancy("Welcome"),
    SEP=TPL.SEPARATOR,
    ST_YOUR_INFO=ST.bold_fancy("Your Info"),
    ST_USER=ST.bold_fancy("User"),
    ST_USER_ID=ST.bold_fancy("User id"),
    ST_USERNAME=ST.bold_fancy("Username"),
    ST_GROUP_ID=ST.bold_fancy("Group id"),
    BS_RULES=ST.bold_sans("RULES"),
    ST_NO=ST.bold_fancy("No"),
    SC_LINKS=ST.small_caps("links"),
    SC_ABUSE=ST.small_caps("abuse"),
    SC_PROMO=ST.small_caps("promo"),
    SC_NSFW=ST.small_caps("nsfw"),
    SC_BANNED_EMOJIS=ST.small_caps("banned emojis"),
    BS_AVAILABLE_COMMANDS=ST.bold_sans("Available Commands"),
    ST_USEFUL_BOT_CMDS=ST.bold_fancy("Useful Bot Cmds"),
    ST_OWNER=ST.bold_fancy("Owner"),
    OWNER_NAME=Config.OWNER_NAME,
    ST_POWERED_BY=ST.bold_fancy("Powered By"),
)

DEFAULT_GOODBYE = """👋 {ST_GOODBYE}!
{SEP}

╔═══[ {ST_LEFT} ]═════╗
║ ✧ {ST_USER}: {{mention}}
║ ✧ {ST_ID}: {{id}}
╚════════════════╝

😢 {ST_MISS_YOU}
{SEP}
 {ST_POWERED_BY}: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』""".format(
    ST_GOODBYE=ST.bold_fancy("Goodbye"),
    SEP=TPL.SEPARATOR,
    ST_LEFT=ST.bold_fancy("Member Left"),
    ST_USER=ST.bold_fancy("User"),
    ST_ID=ST.bold_fancy("ID"),
    ST_MISS_YOU=ST.bold_fancy("We'll miss you!"),
    ST_POWERED_BY=ST.bold_fancy("Powered By"),
)


# ─── Welcome/Goodbye Handler ───

async def handle_chat_member_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle new members joining and leaving."""
    try:
        result = update.chat_member
        if not result:
            return

        chat = update.effective_chat
        if chat.type == ChatType.PRIVATE:
            return

        old_status = result.old_chat_member.status
        new_status = result.new_chat_member.status
        user = result.new_chat_member.user

        if not user or user.is_bot:
            return

        # Save user and chat
        db_save_user(user)
        db_save_chat(chat)

        # User Joined
        if old_status in (ChatMemberStatus.LEFT, ChatMemberStatus.BANNED) and \
           new_status in (ChatMemberStatus.MEMBER, ChatMemberStatus.RESTRICTED):
            await handle_new_member(update, context, chat, user)

        # User Left
        elif old_status in (ChatMemberStatus.MEMBER, ChatMemberStatus.RESTRICTED, ChatMemberStatus.ADMINISTRATOR) and \
             new_status in (ChatMemberStatus.LEFT, ChatMemberStatus.BANNED):
            await handle_member_left(update, context, chat, user)

    except Exception as e:
        logger.error(f"Error in chat_member_update: {e}")


async def handle_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE, chat: Chat, user: User):
    """Handle a new member joining."""
    session = get_db()
    try:
        db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
        if not db_chat:
            db_save_chat(chat)
            db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()

        if not db_chat:
            return

        # Check gban
        gban = session.query(DBGban).filter(
            DBGban.user_id == user.id,
            DBGban.is_active == True
        ).first()
        if gban:
            try:
                await chat.ban_member(user.id)
                await context.bot.send_message(
                    chat.id,
                    f"🔨 {ST.bold_fancy('GBanned User Detected!')}\n"
                    f"✧ {ST.bold_fancy('User')}: {get_user_link(user)}\n"
                    f"✧ {ST.bold_fancy('Reason')}: {escape_html(gban.reason or 'No reason')}\n"
                    f"✧ {ST.bold_fancy('Action')}: Banned automatically",
                    parse_mode="HTML"
                )
            except Exception:
                pass
            return

        # Add to chat_members
        member = session.query(DBChatMember).filter(
            DBChatMember.chat_id == chat.id,
            DBChatMember.user_id == user.id
        ).first()
        if member:
            member.is_active = True
            member.join_date = datetime.datetime.utcnow()
        else:
            member = DBChatMember(
                chat_id=chat.id,
                user_id=user.id,
                join_date=datetime.datetime.utcnow()
            )
            session.add(member)
        session.commit()

        # Get member count
        try:
            member_count = await chat.get_member_count()
        except Exception:
            member_count = 0

        # Update total members
        db_chat.total_members = member_count
        session.commit()

        # Captcha check
        if db_chat.captcha_enabled:
            await send_captcha(update, context, chat, user, db_chat)

        # Welcome message
        if db_chat.welcome_enabled:
            await send_welcome(update, context, chat, user, db_chat, member_count)

        # Clean service messages
        if db_chat.clean_service:
            try:
                if update.chat_member and update.chat_member.invite_link:
                    pass  # Can't delete service msgs from chat_member update
            except Exception:
                pass

        # Log
        if db_chat.log_channel_id and db_chat.log_joins:
            log_text = (
                f"📥 {ST.bold_fancy('New Member')}\n"
                f"{TPL.SEPARATOR}\n"
                f"✧ {ST.bold_fancy('User')}: {get_user_link(user)}\n"
                f"✧ {ST.bold_fancy('ID')}: <code>{user.id}</code>\n"
                f"✧ {ST.bold_fancy('Chat')}: {escape_html(chat.title)}\n"
                f"✧ {ST.bold_fancy('Members')}: {member_count}\n"
                f"{TPL.SEPARATOR}"
            )
            try:
                await context.bot.send_message(
                    db_chat.log_channel_id, log_text, parse_mode="HTML"
                )
            except Exception:
                pass

    except Exception as e:
        logger.error(f"Error handling new member: {e}")
    finally:
        close_db(session)


async def send_welcome(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    chat: Chat,
    user: User,
    db_chat: DBChat,
    member_count: int
):
    """Send welcome message."""
    try:
        # Get welcome text
        welcome_text = db_chat.welcome_message or DEFAULT_WELCOME
        welcome_text = parse_welcome_text(welcome_text, user, chat, member_count)

        # Build buttons
        buttons = []
        session = get_db()
        try:
            welcome_buttons = session.query(DBWelcomeButton).filter(
                DBWelcomeButton.chat_id == chat.id
            ).order_by(DBWelcomeButton.row).all()

            rows = defaultdict(list)
            for btn in welcome_buttons:
                if btn.url:
                    rows[btn.row].append(InlineKeyboardButton(text=btn.text, url=btn.url))
                elif btn.callback_data:
                    rows[btn.row].append(InlineKeyboardButton(text=btn.text, callback_data=btn.callback_data))

            buttons = [rows[r] for r in sorted(rows.keys())]
        finally:
            close_db(session)

        # Add rules button if rules exist
        if db_chat.rules:
            rules_btn = InlineKeyboardButton(
                text=f"📜 {ST.bold_fancy('Rules')}",
                callback_data=f"rules_{chat.id}"
            )
            if buttons:
                buttons.append([rules_btn])
            else:
                buttons = [[rules_btn]]

        keyboard = InlineKeyboardMarkup(buttons) if buttons else None

        # Send with or without media
        msg = None
        if db_chat.welcome_media and db_chat.welcome_media_type:
            try:
                if db_chat.welcome_media_type == "photo":
                    msg = await context.bot.send_photo(
                        chat.id,
                        photo=db_chat.welcome_media,
                        caption=welcome_text,
                        parse_mode="HTML",
                        reply_markup=keyboard
                    )
                elif db_chat.welcome_media_type == "gif":
                    msg = await context.bot.send_animation(
                        chat.id,
                        animation=db_chat.welcome_media,
                        caption=welcome_text,
                        parse_mode="HTML",
                        reply_markup=keyboard
                    )
                elif db_chat.welcome_media_type == "video":
                    msg = await context.bot.send_video(
                        chat.id,
                        video=db_chat.welcome_media,
                        caption=welcome_text,
                        parse_mode="HTML",
                        reply_markup=keyboard
                    )
                elif db_chat.welcome_media_type == "sticker":
                    await context.bot.send_sticker(chat.id, sticker=db_chat.welcome_media)
                    msg = await context.bot.send_message(
                        chat.id,
                        welcome_text,
                        parse_mode="HTML",
                        reply_markup=keyboard
                    )
                else:
                    msg = await context.bot.send_message(
                        chat.id,
                        welcome_text,
                        parse_mode="HTML",
                        reply_markup=keyboard
                    )
            except Exception:
                msg = await context.bot.send_message(
                    chat.id,
                    welcome_text,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
        else:
            msg = await context.bot.send_message(
                chat.id,
                welcome_text,
                parse_mode="HTML",
                reply_markup=keyboard,
                disable_web_page_preview=True
            )

        # Auto-delete welcome after configured time
        if msg and db_chat.welcome_delete_after and db_chat.welcome_delete_after > 0:
            asyncio.create_task(delete_message_after(msg, db_chat.welcome_delete_after))
            welcome_msg_cache[chat.id].append(msg.message_id)

        # Mute new members if configured
        if db_chat.welcome_mute_new and not db_chat.captcha_enabled:
            try:
                await chat.restrict_member(
                    user.id,
                    ChatPermissions(can_send_messages=False),
                    until_date=datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
                )
            except Exception:
                pass

    except Exception as e:
        logger.error(f"Error sending welcome: {e}")


async def handle_member_left(update: Update, context: ContextTypes.DEFAULT_TYPE, chat: Chat, user: User):
    """Handle member leaving."""
    session = get_db()
    try:
        db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
        if not db_chat:
            return

        # Update chat_members
        member = session.query(DBChatMember).filter(
            DBChatMember.chat_id == chat.id,
            DBChatMember.user_id == user.id
        ).first()
        if member:
            member.is_active = False
        session.commit()

        # Goodbye message
        if db_chat.goodbye_enabled:
            goodbye_text = db_chat.goodbye_message or DEFAULT_GOODBYE
            goodbye_text = parse_welcome_text(goodbye_text, user, chat, 0)

            try:
                msg = await context.bot.send_message(
                    chat.id,
                    goodbye_text,
                    parse_mode="HTML",
                    disable_web_page_preview=True
                )
                if msg and db_chat.goodbye_delete_after and db_chat.goodbye_delete_after > 0:
                    asyncio.create_task(delete_message_after(msg, db_chat.goodbye_delete_after))
            except Exception as e:
                logger.error(f"Error sending goodbye: {e}")

        # Log
        if db_chat.log_channel_id and db_chat.log_leaves:
            log_text = (
                f"📤 {ST.bold_fancy('Member Left')}\n"
                f"{TPL.SEPARATOR}\n"
                f"✧ {ST.bold_fancy('User')}: {get_user_link(user)}\n"
                f"✧ {ST.bold_fancy('ID')}: <code>{user.id}</code>\n"
                f"✧ {ST.bold_fancy('Chat')}: {escape_html(chat.title)}\n"
                f"{TPL.SEPARATOR}"
            )
            try:
                await context.bot.send_message(
                    db_chat.log_channel_id, log_text, parse_mode="HTML"
                )
            except Exception:
                pass

    except Exception as e:
        logger.error(f"Error handling member left: {e}")
    finally:
        close_db(session)


# ─── Captcha System ───

async def send_captcha(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    chat: Chat,
    user: User,
    db_chat: DBChat
):
    """Send captcha challenge to new member."""
    captcha_type = db_chat.captcha_type or "button"
    timeout = db_chat.captcha_timeout or Config.CAPTCHA_TIMEOUT

    # Mute user until verified
    try:
        await chat.restrict_member(
            user.id,
            ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False
            )
        )
    except Exception:
        pass

    captcha_key = f"{chat.id}_{user.id}"

    if captcha_type == "button":
        # Simple button captcha
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                text=f"✅ {ST.bold_fancy('I am human!')}",
                callback_data=f"captcha_verify_{user.id}"
            )],
            [InlineKeyboardButton(
                text=f"📜 {ST.bold_fancy('Rules')}",
                callback_data=f"rules_{chat.id}"
            )]
        ])

        captcha_text = (
            f"🔐 {ST.bold_fancy('Captcha Verification')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Hello')} {get_user_link(user)}!\n\n"
            f"⚠️ {ST.bold_fancy('Please verify you are human by clicking the button below.')}\n\n"
            f"⏰ {ST.bold_fancy('Timeout')}: {timeout} {ST.small_caps('seconds')}\n"
            f"{TPL.SEPARATOR}\n"
            f" {ST.bold_fancy('Powered By')}: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』"
        )

        msg = await context.bot.send_message(
            chat.id,
            captcha_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )

        captcha_pending[captcha_key] = {
            "type": "button",
            "message_id": msg.message_id,
            "user_id": user.id,
            "chat_id": chat.id,
            "expires": time.time() + timeout
        }

    elif captcha_type == "math":
        # Math captcha
        a = random.randint(1, 20)
        b = random.randint(1, 20)
        op = random.choice(['+', '-', '×'])

        if op == '+':
            answer = a + b
        elif op == '-':
            if a < b:
                a, b = b, a
            answer = a - b
        else:
            answer = a * b

        # Generate wrong answers
        wrong = set()
        while len(wrong) < 3:
            w = answer + random.randint(-10, 10)
            if w != answer and w >= 0:
                wrong.add(w)

        options = list(wrong) + [answer]
        random.shuffle(options)

        buttons = []
        row = []
        for opt in options:
            row.append(InlineKeyboardButton(
                text=str(opt),
                callback_data=f"captcha_math_{user.id}_{opt}_{answer}"
            ))
            if len(row) == 2:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)

        keyboard = InlineKeyboardMarkup(buttons)

        captcha_text = (
            f"🔢 {ST.bold_fancy('Math Captcha')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {get_user_link(user)}, {ST.bold_fancy('solve this')}:\n\n"
            f"   {ST.bold_sans(f'{a} {op} {b} = ?')}\n\n"
            f"⏰ {ST.bold_fancy('Timeout')}: {timeout} {ST.small_caps('seconds')}\n"
            f"{TPL.SEPARATOR}"
        )

        msg = await context.bot.send_message(
            chat.id,
            captcha_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )

        captcha_pending[captcha_key] = {
            "type": "math",
            "message_id": msg.message_id,
            "user_id": user.id,
            "chat_id": chat.id,
            "answer": answer,
            "expires": time.time() + timeout
        }

    elif captcha_type == "text":
        # Text captcha - user must type a code
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        captcha_text = (
            f"🔤 {ST.bold_fancy('Text Captcha')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {get_user_link(user)}, {ST.bold_fancy('type this code')}:\n\n"
            f"   <code>{code}</code>\n\n"
            f"⏰ {ST.bold_fancy('Timeout')}: {timeout} {ST.small_caps('seconds')}\n"
            f"{TPL.SEPARATOR}"
        )

        msg = await context.bot.send_message(
            chat.id,
            captcha_text,
            parse_mode="HTML"
        )

        captcha_pending[captcha_key] = {
            "type": "text",
            "message_id": msg.message_id,
            "user_id": user.id,
            "chat_id": chat.id,
            "code": code,
            "expires": time.time() + timeout
        }

    # Save to database
    session = get_db()
    try:
        db_captcha = DBCaptcha(
            chat_id=chat.id,
            user_id=user.id,
            captcha_code=captcha_pending[captcha_key].get("code", "button"),
            message_id=msg.message_id if msg else None,
            expires_at=datetime.datetime.utcnow() + datetime.timedelta(seconds=timeout)
        )
        session.add(db_captcha)
        session.commit()
    except Exception:
        session.rollback()
    finally:
        close_db(session)

    # Schedule timeout
    context.job_queue.run_once(
        captcha_timeout_job,
        timeout,
        data={"chat_id": chat.id, "user_id": user.id, "captcha_key": captcha_key},
        name=f"captcha_timeout_{captcha_key}"
    )


async def captcha_timeout_job(context: ContextTypes.DEFAULT_TYPE):
    """Handle captcha timeout - kick user if not verified."""
    data = context.job.data
    chat_id = data["chat_id"]
    user_id = data["user_id"]
    captcha_key = data["captcha_key"]

    if captcha_key in captcha_pending:
        pending = captcha_pending[captcha_key]

        # Check if already verified
        session = get_db()
        try:
            db_captcha = session.query(DBCaptcha).filter(
                DBCaptcha.chat_id == chat_id,
                DBCaptcha.user_id == user_id,
                DBCaptcha.verified == False
            ).first()

            if db_captcha:
                # Check chat settings
                db_chat = session.query(DBChat).filter(DBChat.chat_id == chat_id).first()
                if db_chat and db_chat.captcha_kick:
                    try:
                        await context.bot.ban_member(chat_id, user_id)
                        await asyncio.sleep(1)
                        await context.bot.unban_member(chat_id, user_id)  # Unban so they can rejoin
                    except Exception:
                        pass

                    timeout_msg = (
                        f"⏰ {ST.bold_fancy('Captcha Timeout!')}\n"
                        f"✧ {ST.bold_fancy('User')}: <a href='tg://user?id={user_id}'>User</a>\n"
                        f"✧ {ST.bold_fancy('Action')}: {ST.small_caps('kicked (can rejoin)')}"
                    )
                    try:
                        msg = await context.bot.send_message(
                            chat_id, timeout_msg, parse_mode="HTML"
                        )
                        asyncio.create_task(delete_message_after(msg, 30))
                    except Exception:
                        pass

                # Delete captcha message
                try:
                    await context.bot.delete_message(chat_id, pending["message_id"])
                except Exception:
                    pass

                # Clean up
                db_captcha.verified = False
                session.commit()
        except Exception:
            session.rollback()
        finally:
            close_db(session)

        # Remove from pending
        captcha_pending.pop(captcha_key, None)


async def captcha_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle captcha button clicks."""
    query = update.callback_query
    data = query.data
    user = query.from_user

    if data.startswith("captcha_verify_"):
        target_user_id = int(data.split("_")[2])

        if user.id != target_user_id:
            await query.answer(
                f"❌ {ST.bold_fancy('This is not for you!')}",
                show_alert=True
            )
            return

        chat = query.message.chat
        captcha_key = f"{chat.id}_{user.id}"

        # Verify
        if captcha_key in captcha_pending:
            captcha_pending.pop(captcha_key, None)

        # Unmute
        try:
            await chat.restrict_member(
                user.id,
                ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                    can_send_polls=True,
                    can_invite_users=True,
                )
            )
        except Exception:
            pass

        # Update database
        session = get_db()
        try:
            db_captcha = session.query(DBCaptcha).filter(
                DBCaptcha.chat_id == chat.id,
                DBCaptcha.user_id == user.id,
                DBCaptcha.verified == False
            ).first()
            if db_captcha:
                db_captcha.verified = True
                session.commit()
        except Exception:
            session.rollback()
        finally:
            close_db(session)

        # Edit message
        await query.message.edit_text(
            f"✅ {ST.bold_fancy('Verified!')}\n\n"
            f"✧ {get_user_link(user)} {ST.bold_fancy('has been verified successfully!')}\n"
            f"✧ {ST.bold_fancy('Welcome to')} {escape_html(chat.title)}! 🎉",
            parse_mode="HTML"
        )

        # Cancel timeout job
        jobs = context.job_queue.get_jobs_by_name(f"captcha_timeout_{captcha_key}")
        for job in jobs:
            job.schedule_removal()

        # Auto delete after 30s
        asyncio.create_task(delete_message_after(query.message, 30))

        await query.answer(f"✅ Verified! Welcome!", show_alert=False)

    elif data.startswith("captcha_math_"):
        parts = data.split("_")
        target_user_id = int(parts[2])
        selected = int(parts[3])
        correct = int(parts[4])

        if user.id != target_user_id:
            await query.answer("❌ This is not for you!", show_alert=True)
            return

        chat = query.message.chat

        if selected == correct:
            # Correct answer
            captcha_key = f"{chat.id}_{user.id}"
            captcha_pending.pop(captcha_key, None)

            try:
                await chat.restrict_member(
                    user.id,
                    ChatPermissions(
                        can_send_messages=True,
                        can_send_media_messages=True,
                        can_send_other_messages=True,
                        can_add_web_page_previews=True,
                        can_send_polls=True,
                        can_invite_users=True,
                    )
                )
            except Exception:
                pass

            session = get_db()
            try:
                db_captcha = session.query(DBCaptcha).filter(
                    DBCaptcha.chat_id == chat.id,
                    DBCaptcha.user_id == user.id,
                    DBCaptcha.verified == False
                ).first()
                if db_captcha:
                    db_captcha.verified = True
                    session.commit()
            except Exception:
                session.rollback()
            finally:
                close_db(session)

            await query.message.edit_text(
                f"✅ {ST.bold_fancy('Correct!')} 🎉\n\n"
                f"✧ {get_user_link(user)} {ST.bold_fancy('verified successfully!')}\n"
                f"✧ {ST.bold_fancy('Welcome!')}",
                parse_mode="HTML"
            )

            jobs = context.job_queue.get_jobs_by_name(f"captcha_timeout_{captcha_key}")
            for job in jobs:
                job.schedule_removal()

            asyncio.create_task(delete_message_after(query.message, 30))
            await query.answer("✅ Correct!", show_alert=False)
        else:
            # Wrong answer
            session = get_db()
            try:
                db_captcha = session.query(DBCaptcha).filter(
                    DBCaptcha.chat_id == chat.id,
                    DBCaptcha.user_id == user.id,
                    DBCaptcha.verified == False
                ).first()
                if db_captcha:
                    db_captcha.attempts = (db_captcha.attempts or 0) + 1
                    session.commit()

                    if db_captcha.attempts >= 3:
                        # Too many wrong attempts
                        try:
                            await chat.ban_member(user.id)
                            await asyncio.sleep(1)
                            await chat.unban_member(user.id)
                        except Exception:
                            pass

                        captcha_key = f"{chat.id}_{user.id}"
                        captcha_pending.pop(captcha_key, None)

                        await query.message.edit_text(
                            f"❌ {ST.bold_fancy('Too many wrong attempts!')}\n"
                            f"✧ {get_user_link(user)} {ST.bold_fancy('has been kicked.')}",
                            parse_mode="HTML"
                        )
                        return
            except Exception:
                session.rollback()
            finally:
                close_db(session)

            await query.answer("❌ Wrong answer! Try again.", show_alert=True)


# ─── Welcome/Goodbye Configuration Commands ───

@admin_required
@group_only
async def cmd_setwelcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set custom welcome message. Usage: /setwelcome &lt;text&gt;"""
    chat = update.effective_chat
    message = update.message

    # Check if replying to a message with media
    if message.reply_to_message:
        reply = message.reply_to_message
        text = reply.caption or reply.text or ""
        media_id = None
        media_type = None

        if reply.photo:
            media_id = reply.photo[-1].file_id
            media_type = "photo"
        elif reply.animation:
            media_id = reply.animation.file_id
            media_type = "gif"
        elif reply.video:
            media_id = reply.video.file_id
            media_type = "video"
        elif reply.sticker:
            media_id = reply.sticker.file_id
            media_type = "sticker"

        if not text and not media_id:
            await message.reply_text(
                TPL.error(f"{ST.bold_fancy('Please provide welcome text or reply to media!')}"),
                parse_mode="HTML"
            )
            return

        db_update_chat_setting(
            chat.id,
            welcome_message=text,
            welcome_media=media_id,
            welcome_media_type=media_type
        )

    else:
        args = message.text.split(None, 1)
        if len(args) < 2:
            await message.reply_text(
                f"📝 {ST.bold_fancy('Set Welcome Message')}\n"
                f"{TPL.SEPARATOR}\n\n"
                f"✧ {ST.bold_fancy('Usage')}: /setwelcome &lt;text&gt;\n"
                f"✧ {ST.bold_fancy('Or reply to a message/media')}\n\n"
                f"📋 {ST.bold_fancy('Placeholders')}:\n"
                f"  • {{first}} - {ST.small_caps('first name')}\n"
                f"  • {{last}} - {ST.small_caps('last name')}\n"
                f"  • {{fullname}} - {ST.small_caps('full name')}\n"
                f"  • {{username}} - @{ST.small_caps('username')}\n"
                f"  • {{mention}} - {ST.small_caps('clickable mention')}\n"
                f"  • {{id}} - {ST.small_caps('user id')}\n"
                f"  • {{chatname}} - {ST.small_caps('chat name')}\n"
                f"  • {{chatid}} - {ST.small_caps('chat id')}\n"
                f"  • {{count}} - {ST.small_caps('member count')}\n"
                f"{TPL.mini_footer()}",
                parse_mode="HTML"
            )
            return

        welcome_text = args[1]
        db_update_chat_setting(chat.id, welcome_message=welcome_text)

    await message.reply_text(
        TPL.success(f"{ST.bold_fancy('Welcome message has been set!')}"),
        parse_mode="HTML"
    )


@admin_required
@group_only
async def cmd_resetwelcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset welcome message to default."""
    chat = update.effective_chat
    db_update_chat_setting(
        chat.id,
        welcome_message=None,
        welcome_media=None,
        welcome_media_type=None
    )
    await update.message.reply_text(
        TPL.success(f"{ST.bold_fancy('Welcome message reset to default!')}"),
        parse_mode="HTML"
    )


@admin_required
@group_only
async def cmd_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle welcome on/off or show current. Usage: /welcome [on/off/show]"""
    chat = update.effective_chat
    args = update.message.text.split()

    if len(args) < 2:
        session = get_db()
        try:
            db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
            status = "ON ✅" if (db_chat and db_chat.welcome_enabled) else "OFF ❌"
        finally:
            close_db(session)

        await update.message.reply_text(
            f"👋 {ST.bold_fancy('Welcome Settings')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Status')}: {status}\n\n"
            f"✧ /welcome on - {ST.small_caps('enable')}\n"
            f"✧ /welcome off - {ST.small_caps('disable')}\n"
            f"✧ /welcome show - {ST.small_caps('preview')}\n"
            f"✧ /setwelcome - {ST.small_caps('set message')}\n"
            f"✧ /resetwelcome - {ST.small_caps('reset to default')}\n"
            f"✧ /setwelcomemedia - {ST.small_caps('set media')}\n"
            f"✧ /cleanwelcome on/off - {ST.small_caps('auto delete old')}\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
        return

    action = args[1].lower()

    if action in ("on", "yes", "enable", "1"):
        db_update_chat_setting(chat.id, welcome_enabled=True)
        await update.message.reply_text(
            TPL.success(f"{ST.bold_fancy('Welcome messages enabled!')} ✅"),
            parse_mode="HTML"
        )
    elif action in ("off", "no", "disable", "0"):
        db_update_chat_setting(chat.id, welcome_enabled=False)
        await update.message.reply_text(
            TPL.success(f"{ST.bold_fancy('Welcome messages disabled!')} ❌"),
            parse_mode="HTML"
        )
    elif action == "show":
        session = get_db()
        try:
            db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
            if db_chat and db_chat.welcome_message:
                preview = parse_welcome_text(
                    db_chat.welcome_message,
                    update.effective_user,
                    chat,
                    0
                )
                await update.message.reply_text(
                    f"👋 {ST.bold_fancy('Welcome Preview')}:\n{TPL.SEPARATOR}\n\n{preview}",
                    parse_mode="HTML"
                )
            else:
                preview = parse_welcome_text(
                    DEFAULT_WELCOME,
                    update.effective_user,
                    chat,
                    0
                )
                await update.message.reply_text(
                    f"👋 {ST.bold_fancy('Default Welcome')}:\n{TPL.SEPARATOR}\n\n{preview}",
                    parse_mode="HTML"
                )
        finally:
            close_db(session)


@admin_required
@group_only
async def cmd_setgoodbye(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set custom goodbye message."""
    chat = update.effective_chat
    message = update.message

    if message.reply_to_message:
        reply = message.reply_to_message
        text = reply.caption or reply.text or ""
        media_id = None
        media_type = None

        if reply.photo:
            media_id = reply.photo[-1].file_id
            media_type = "photo"
        elif reply.animation:
            media_id = reply.animation.file_id
            media_type = "gif"

        db_update_chat_setting(
            chat.id,
            goodbye_message=text,
            goodbye_media=media_id,
            goodbye_media_type=media_type
        )
    else:
        args = message.text.split(None, 1)
        if len(args) < 2:
            await message.reply_text(
                f"📝 {ST.bold_fancy('Set Goodbye Message')}\n"
                f"{TPL.SEPARATOR}\n\n"
                f"✧ {ST.bold_fancy('Usage')}: /setgoodbye &lt;text&gt;\n"
                f"✧ {ST.bold_fancy('Or reply to a message')}\n"
                f"{TPL.mini_footer()}",
                parse_mode="HTML"
            )
            return
        db_update_chat_setting(chat.id, goodbye_message=args[1])

    await message.reply_text(
        TPL.success(f"{ST.bold_fancy('Goodbye message has been set!')}"),
        parse_mode="HTML"
    )


@admin_required
@group_only
async def cmd_goodbye(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle goodbye on/off."""
    args = update.message.text.split()
    chat = update.effective_chat

    if len(args) < 2:
        session = get_db()
        try:
            db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
            status = "ON ✅" if (db_chat and db_chat.goodbye_enabled) else "OFF ❌"
        finally:
            close_db(session)

        await update.message.reply_text(
            f"👋 {ST.bold_fancy('Goodbye Status')}: {status}\n"
            f"✧ /goodbye on/off",
            parse_mode="HTML"
        )
        return

    action = args[1].lower()
    if action in ("on", "yes", "1"):
        db_update_chat_setting(chat.id, goodbye_enabled=True)
        await update.message.reply_text(
            TPL.success(f"{ST.bold_fancy('Goodbye messages enabled!')}"),
            parse_mode="HTML"
        )
    elif action in ("off", "no", "0"):
        db_update_chat_setting(chat.id, goodbye_enabled=False)
        await update.message.reply_text(
            TPL.success(f"{ST.bold_fancy('Goodbye messages disabled!')}"),
            parse_mode="HTML"
        )


@admin_required
@group_only
async def cmd_resetgoodbye(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset goodbye to default."""
    db_update_chat_setting(
        update.effective_chat.id,
        goodbye_message=None,
        goodbye_media=None,
        goodbye_media_type=None
    )
    await update.message.reply_text(
        TPL.success(f"{ST.bold_fancy('Goodbye message reset!')}"),
        parse_mode="HTML"
    )


# ─── Captcha Configuration Commands ───

@admin_required
@group_only
async def cmd_captcha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Configure captcha. Usage: /captcha [on/off/button/math/text]"""
    chat = update.effective_chat
    args = update.message.text.split()

    if len(args) < 2:
        session = get_db()
        try:
            db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
            enabled = db_chat.captcha_enabled if db_chat else False
            ctype = db_chat.captcha_type if db_chat else "button"
            timeout = db_chat.captcha_timeout if db_chat else Config.CAPTCHA_TIMEOUT
            kick = db_chat.captcha_kick if db_chat else True
        finally:
            close_db(session)

        await update.message.reply_text(
            f"🔐 {ST.bold_fancy('Captcha Settings')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Status')}: {'ON ✅' if enabled else 'OFF ❌'}\n"
            f"✧ {ST.bold_fancy('Type')}: {ctype}\n"
            f"✧ {ST.bold_fancy('Timeout')}: {timeout}s\n"
            f"✧ {ST.bold_fancy('Kick on fail')}: {'Yes' if kick else 'No'}\n\n"
            f"⚙️ {ST.bold_fancy('Commands')}:\n"
            f"  • /captcha on/off\n"
            f"  • /captcha button/math/text\n"
            f"  • /captchatimeout &lt;seconds&gt;\n"
            f"  • /captchakick on/off\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
        return

    action = args[1].lower()

    if action in ("on", "yes", "enable", "1"):
        db_update_chat_setting(chat.id, captcha_enabled=True)
        await update.message.reply_text(
            TPL.success(f"🔐 {ST.bold_fancy('Captcha enabled!')}"),
            parse_mode="HTML"
        )
    elif action in ("off", "no", "disable", "0"):
        db_update_chat_setting(chat.id, captcha_enabled=False)
        await update.message.reply_text(
            TPL.success(f"🔐 {ST.bold_fancy('Captcha disabled!')}"),
            parse_mode="HTML"
        )
    elif action in ("button", "math", "text"):
        db_update_chat_setting(chat.id, captcha_type=action)
        await update.message.reply_text(
            TPL.success(f"🔐 {ST.bold_fancy(f'Captcha type set to: {action}')}"),
            parse_mode="HTML"
        )


@admin_required
@group_only
async def cmd_captchatimeout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set captcha timeout. Usage: /captchatimeout &lt;seconds&gt;"""
    args = update.message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await update.message.reply_text(
            f"✧ {ST.bold_fancy('Usage')}: /captchatimeout &lt;seconds&gt;\n"
            f"✧ {ST.bold_fancy('Example')}: /captchatimeout 120",
            parse_mode="HTML"
        )
        return

    timeout = int(args[1])
    if timeout < 30:
        timeout = 30
    elif timeout > 600:
        timeout = 600

    db_update_chat_setting(update.effective_chat.id, captcha_timeout=timeout)
    await update.message.reply_text(
        TPL.success(f"⏰ {ST.bold_fancy(f'Captcha timeout set to {timeout} seconds')}"),
        parse_mode="HTML"
    )


# ─── Rules Commands ───

@admin_required
@group_only
async def cmd_setrules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set chat rules. Usage: /setrules &lt;rules text&gt;"""
    args = update.message.text.split(None, 1)
    if len(args) < 2:
        await update.message.reply_text(
            f"📜 {ST.bold_fancy('Usage')}: /setrules &lt;rules text&gt;",
            parse_mode="HTML"
        )
        return

    db_update_chat_setting(update.effective_chat.id, rules=args[1])
    await update.message.reply_text(
        TPL.success(f"📜 {ST.bold_fancy('Rules have been set!')}"),
        parse_mode="HTML"
    )


@disabled_check
async def cmd_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show chat rules."""
    chat = update.effective_chat

    if chat.type == ChatType.PRIVATE:
        # In DM: show a helpful message
        await update.message.reply_text(
            f"ℹ️ {ST.bold_fancy('Rules')}: Use /rules in a group chat to see that group\'s rules.\n"
            f"✧ Set rules with: /setrules &lt;text&gt; (in a group)",
            parse_mode="HTML"
        )
        return

    session = get_db()
    try:
        db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
        if db_chat and db_chat.rules:
            rules_text = (
                f"📜 {ST.bold_fancy('Rules for')} {escape_html(chat.title)}\n"
                f"{TPL.SEPARATOR}\n\n"
                f"{db_chat.rules}\n\n"
                f"{TPL.SEPARATOR}\n"
                f" {ST.bold_fancy('Powered By')}: 『 Ʀᴜʜɪ ✘ Assɪsᴛᴀɴᴛ 』"
            )

            if db_chat.rules_private:
                # Send in PM
                try:
                    await context.bot.send_message(
                        update.effective_user.id,
                        rules_text,
                        parse_mode="HTML"
                    )
                    await update.message.reply_text(
                        TPL.success(f"{ST.bold_fancy('Rules sent to your PM!')}"),
                        parse_mode="HTML"
                    )
                except Forbidden:
                    await update.message.reply_text(
                        TPL.error(f"{ST.bold_fancy('Please start me in PM first!')}"),
                        parse_mode="HTML"
                    )
            else:
                await update.message.reply_text(rules_text, parse_mode="HTML")
        else:
            await update.message.reply_text(
                TPL.info(f"{ST.bold_fancy('No rules set for this chat!')}"),
                parse_mode="HTML"
            )
    finally:
        close_db(session)


async def rules_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle rules button callback."""
    query = update.callback_query
    data = query.data

    if data.startswith("rules_"):
        chat_id = int(data.split("_")[1])
        session = get_db()
        try:
            db_chat = session.query(DBChat).filter(DBChat.chat_id == chat_id).first()
            if db_chat and db_chat.rules:
                rules_text = (
                    f"📜 {ST.bold_fancy('Rules')}\n"
                    f"{TPL.SEPARATOR}\n\n"
                    f"{db_chat.rules}\n\n"
                    f"{TPL.SEPARATOR}"
                )
                await query.answer()
                try:
                    await context.bot.send_message(
                        query.from_user.id,
                        rules_text,
                        parse_mode="HTML"
                    )
                except Forbidden:
                    await query.answer(
                        "❌ Please start me in PM first!",
                        show_alert=True
                    )
            else:
                await query.answer(
                    "📜 No rules set for this chat.",
                    show_alert=True
                )
        finally:
            close_db(session)


@admin_required
@group_only
async def cmd_clearrules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear chat rules."""
    db_update_chat_setting(update.effective_chat.id, rules=None)
    await update.message.reply_text(
        TPL.success(f"📜 {ST.bold_fancy('Rules have been cleared!')}"),
        parse_mode="HTML"
    )


@admin_required
@group_only
async def cmd_privaterules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle sending rules in PM. Usage: /privaterules on/off"""
    args = update.message.text.split()
    if len(args) < 2:
        session = get_db()
        try:
            db_chat = session.query(DBChat).filter(DBChat.chat_id == update.effective_chat.id).first()
            status = "ON" if (db_chat and db_chat.rules_private) else "OFF"
        finally:
            close_db(session)
        await update.message.reply_text(
            f"📜 {ST.bold_fancy('Private Rules')}: {status}\n"
            f"✧ /privaterules on/off",
            parse_mode="HTML"
        )
        return

    action = args[1].lower()
    if action in ("on", "yes", "1"):
        db_update_chat_setting(update.effective_chat.id, rules_private=True)
        await update.message.reply_text(
            TPL.success(f"{ST.bold_fancy('Rules will be sent in PM!')}"),
            parse_mode="HTML"
        )
    elif action in ("off", "no", "0"):
        db_update_chat_setting(update.effective_chat.id, rules_private=False)
        await update.message.reply_text(
            TPL.success(f"{ST.bold_fancy('Rules will be sent in group!')}"),
            parse_mode="HTML"
        )


# ─── Welcome Delete / Clean Commands ───

@admin_required
@group_only
async def cmd_cleanwelcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Auto-delete old welcome messages. /cleanwelcome on/off"""
    args = update.message.text.split()
    if len(args) < 2:
        await update.message.reply_text(
            f"🧹 {ST.bold_fancy('Usage')}: /cleanwelcome on/off",
            parse_mode="HTML"
        )
        return

    action = args[1].lower()
    if action in ("on", "yes", "1"):
        db_update_chat_setting(update.effective_chat.id, clean_welcome=True)
        await update.message.reply_text(
            TPL.success(f"🧹 {ST.bold_fancy('Old welcome messages will be auto-deleted!')}"),
            parse_mode="HTML"
        )
    elif action in ("off", "no", "0"):
        db_update_chat_setting(update.effective_chat.id, clean_welcome=False)
        await update.message.reply_text(
            TPL.success(f"🧹 {ST.bold_fancy('Welcome clean disabled!')}"),
            parse_mode="HTML"
        )


@admin_required
@group_only
async def cmd_welcomedelete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set welcome auto-delete time. /welcomedelete &lt;seconds&gt;"""
    args = update.message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await update.message.reply_text(
            f"⏰ {ST.bold_fancy('Usage')}: /welcomedelete &lt;seconds&gt;\n"
            f"✧ 0 = {ST.small_caps('never delete')}",
            parse_mode="HTML"
        )
        return

    seconds = int(args[1])
    db_update_chat_setting(update.effective_chat.id, welcome_delete_after=seconds)
    if seconds == 0:
        await update.message.reply_text(
            TPL.success(f"⏰ {ST.bold_fancy('Welcome messages will not be auto-deleted')}"),
            parse_mode="HTML"
        )
    else:
        await update.message.reply_text(
            TPL.success(f"⏰ {ST.bold_fancy(f'Welcome messages will be deleted after {seconds} seconds')}"),
            parse_mode="HTML"
        )


@admin_required
@group_only
async def cmd_setwelcomemedia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set welcome media. Reply to photo/gif/video."""
    message = update.message
    if not message.reply_to_message:
        await message.reply_text(
            f"📷 {ST.bold_fancy('Reply to a photo/gif/video to set welcome media!')}",
            parse_mode="HTML"
        )
        return

    reply = message.reply_to_message
    media_id = None
    media_type = None

    if reply.photo:
        media_id = reply.photo[-1].file_id
        media_type = "photo"
    elif reply.animation:
        media_id = reply.animation.file_id
        media_type = "gif"
    elif reply.video:
        media_id = reply.video.file_id
        media_type = "video"
    elif reply.sticker:
        media_id = reply.sticker.file_id
        media_type = "sticker"
    else:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('Unsupported media type!')}"),
            parse_mode="HTML"
        )
        return

    db_update_chat_setting(
        update.effective_chat.id,
        welcome_media=media_id,
        welcome_media_type=media_type
    )
    await message.reply_text(
        TPL.success(f"📷 {ST.bold_fancy(f'Welcome {media_type} has been set!')}"),
        parse_mode="HTML"
    )


@admin_required
@group_only
async def cmd_welcomemutenew(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mute new members temporarily. /welcomemute on/off"""
    args = update.message.text.split()
    if len(args) < 2:
        await update.message.reply_text(
            f"🔇 {ST.bold_fancy('Usage')}: /welcomemute on/off",
            parse_mode="HTML"
        )
        return

    action = args[1].lower()
    if action in ("on", "yes", "1"):
        db_update_chat_setting(update.effective_chat.id, welcome_mute_new=True)
        await update.message.reply_text(
            TPL.success(f"🔇 {ST.bold_fancy('New members will be muted for 10 minutes!')}"),
            parse_mode="HTML"
        )
    elif action in ("off", "no", "0"):
        db_update_chat_setting(update.effective_chat.id, welcome_mute_new=False)
        await update.message.reply_text(
            TPL.success(f"🔇 {ST.bold_fancy('Welcome mute disabled!')}"),
            parse_mode="HTML"
        )


# ─── Service Message Handler (for /join messages) ───

async def handle_service_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle service messages like 'user joined' for clean service."""
    message = update.message
    if not message:
        return

    chat = update.effective_chat
    if chat.type == ChatType.PRIVATE:
        return

    # Check if clean service is enabled
    session = get_db()
    try:
        db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
        if db_chat and db_chat.clean_service:
            # Delete service messages (join/leave notifications)
            if message.new_chat_members or message.left_chat_member:
                try:
                    await message.delete()
                except Exception:
                    pass

        # Handle new_chat_members for welcome (backup for chat_member handler)
        if message.new_chat_members:
            for new_member in message.new_chat_members:
                if new_member.is_bot:
                    continue
                db_save_user(new_member)

    finally:
        close_db(session)


# ══════════════════════════════════════════════════════════════════════════════
# ██╗  SECTION 4: ADMIN & MODERATION (BAN, MUTE, KICK, WARN, PROMOTE, REPORT)
# ══════════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────
#  4.1  BAN COMMANDS
# ─────────────────────────────────────────────

@admin_required
@group_only
@bot_admin_required
@log_action
async def cmd_ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ban a user from the group."""
    message = update.message
    chat = update.effective_chat
    admin = update.effective_user

    user_id, reason, user_obj = await extract_user_and_reason(message, context)

    if not user_id:
        await message.reply_text(
            f"🔨 {ST.bold_fancy('Ban User')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Usage')}: /ban &lt;@user/id/reply&gt; [reason]\n"
            f"✧ {ST.bold_fancy('Example')}: /ban @username spamming\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
        return

    if user_id == admin.id:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('You cannot ban yourself!')}"),
            parse_mode="HTML"
        )
        return

    if is_owner(user_id):
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('I cannot ban the bot owner!')}"),
            parse_mode="HTML"
        )
        return

    if is_sudo(user_id):
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('I cannot ban sudo users!')}"),
            parse_mode="HTML"
        )
        return

    if await is_admin(update, user_id) and not is_sudo(admin.id):
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('I cannot ban an admin!')}"),
            parse_mode="HTML"
        )
        return

    try:
        await chat.ban_member(user_id)
    except BadRequest as e:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Failed to ban: {e}')}"),
            parse_mode="HTML"
        )
        return
    except Exception as e:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )
        return

    session = get_db()
    try:
        ban_record = DBBan(
            chat_id=chat.id,
            user_id=user_id,
            banned_by=admin.id,
            reason=reason
        )
        session.add(ban_record)
        session.commit()
    except Exception:
        session.rollback()
    finally:
        close_db(session)

    user_name = get_user_link(user_obj) if user_obj else f"<code>{user_id}</code>"

    ban_text = (
        f"🔨 {ST.bold_fancy('User Banned!')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"╔═══[ {ST.bold_fancy('Ban Info')} ]═════╗\n"
        f"║ ✧ {ST.bold_fancy('User')}: {user_name}\n"
        f"║ ✧ {ST.bold_fancy('ID')}: <code>{user_id}</code>\n"
        f"║ ✧ {ST.bold_fancy('Admin')}: {get_user_link(admin)}\n"
        f"║ ✧ {ST.bold_fancy('Reason')}: {escape_html(reason or 'No reason')}\n"
        f"╚════════════════╝\n"
        f"{TPL.mini_footer()}"
    )

    await message.reply_text(ban_text, parse_mode="HTML")


@admin_required
@group_only
@bot_admin_required
@log_action
async def cmd_unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unban a user from the group."""
    message = update.message
    chat = update.effective_chat
    admin = update.effective_user

    user_id, user_obj = await extract_user(message, context)

    if not user_id:
        await message.reply_text(
            f"🔓 {ST.bold_fancy('Usage')}: /unban &lt;@user/id&gt;",
            parse_mode="HTML"
        )
        return

    try:
        await chat.unban_member(user_id)
    except BadRequest as e:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Failed to unban: {e}')}"),
            parse_mode="HTML"
        )
        return

    session = get_db()
    try:
        bans = session.query(DBBan).filter(
            DBBan.chat_id == chat.id,
            DBBan.user_id == user_id,
            DBBan.is_active == True
        ).all()
        for ban in bans:
            ban.is_active = False
        session.commit()
    except Exception:
        session.rollback()
    finally:
        close_db(session)

    user_name = get_user_link(user_obj) if user_obj else f"<code>{user_id}</code>"

    await message.reply_text(
        f"🔓 {ST.bold_fancy('User Unbanned!')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"✧ {ST.bold_fancy('User')}: {user_name}\n"
        f"✧ {ST.bold_fancy('Admin')}: {get_user_link(admin)}\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


@admin_required
@group_only
@bot_admin_required
@log_action
async def cmd_tban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Temporary ban a user.
    Usage: /tban [user] &lt;time&gt; [reason]
    Time format: 1h, 30m, 2d, 1w
    """
    message = update.message
    chat = update.effective_chat
    admin = update.effective_user
    args = message.text.split()

    user_id, reason, user_obj = await extract_user_and_reason(message, context)

    if not user_id:
        await message.reply_text(
            f"⏱ {ST.bold_fancy('Temp Ban')}\n"
            f"✧ {ST.bold_fancy('Usage')}: /tban &lt;user&gt; &lt;time&gt; [reason]\n"
            f"✧ {ST.bold_fancy('Example')}: /tban @user 1h spamming\n"
            f"✧ {ST.bold_fancy('Time')}: 30m, 1h, 2d, 1w",
            parse_mode="HTML"
        )
        return

    if is_owner(user_id) or is_sudo(user_id):
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('Cannot ban this user!')}"),
            parse_mode="HTML"
        )
        return

    if await is_admin(update, user_id) and not is_sudo(admin.id):
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('Cannot ban an admin!')}"),
            parse_mode="HTML"
        )
        return

    # Parse time from arguments
    time_str = None
    if message.reply_to_message:
        if len(args) > 1:
            time_str = args[1]
            reason = " ".join(args[2:]) if len(args) > 2 else None
    else:
        if len(args) > 2:
            time_str = args[2]
            reason = " ".join(args[3:]) if len(args) > 3 else None

    if not time_str:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('Please specify ban duration! (e.g., 1h, 30m, 2d)')}"),
            parse_mode="HTML"
        )
        return

    duration = parse_time_string(time_str)
    if not duration:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('Invalid time format! Use: 1h, 30m, 2d, 1w')}"),
            parse_mode="HTML"
        )
        return

    until_date = datetime.datetime.utcnow() + duration

    try:
        await chat.ban_member(user_id, until_date=until_date)
    except BadRequest as e:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Failed: {e}')}"),
            parse_mode="HTML"
        )
        return

    session = get_db()
    try:
        ban_record = DBBan(
            chat_id=chat.id,
            user_id=user_id,
            banned_by=admin.id,
            reason=reason,
            until_date=until_date
        )
        session.add(ban_record)
        session.commit()
    except Exception:
        session.rollback()
    finally:
        close_db(session)

    user_name = get_user_link(user_obj) if user_obj else f"<code>{user_id}</code>"

    await message.reply_text(
        f"⏱ {ST.bold_fancy('User Temporarily Banned!')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"╔═══[ {ST.bold_fancy('TBan Info')} ]═════╗\n"
        f"║ ✧ {ST.bold_fancy('User')}: {user_name}\n"
        f"║ ✧ {ST.bold_fancy('Duration')}: {format_timedelta(duration)}\n"
        f"║ ✧ {ST.bold_fancy('Expires')}: {until_date.strftime('%Y-%m-%d %H:%M UTC')}\n"
        f"║ ✧ {ST.bold_fancy('Admin')}: {get_user_link(admin)}\n"
        f"║ ✧ {ST.bold_fancy('Reason')}: {escape_html(reason or 'No reason')}\n"
        f"╚════════════════╝\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


@admin_required
@group_only
@bot_admin_required
@log_action
async def cmd_sban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Silent ban — ban user and delete the command message silently."""
    message = update.message
    chat = update.effective_chat
    admin = update.effective_user

    user_id, reason, user_obj = await extract_user_and_reason(message, context)

    if not user_id:
        return

    if is_owner(user_id) or is_sudo(user_id):
        return

    if await is_admin(update, user_id) and not is_sudo(admin.id):
        return

    try:
        await chat.ban_member(user_id)
    except Exception:
        pass

    # Save to DB silently
    session = get_db()
    try:
        ban_record = DBBan(
            chat_id=chat.id,
            user_id=user_id,
            banned_by=admin.id,
            reason=reason or "Silent ban"
        )
        session.add(ban_record)
        session.commit()
    except Exception:
        session.rollback()
    finally:
        close_db(session)

    try:
        await message.delete()
    except Exception:
        pass

    # Also delete the replied message if exists
    if message.reply_to_message:
        try:
            await message.reply_to_message.delete()
        except Exception:
            pass


@admin_required
@group_only
@bot_admin_required
@log_action
async def cmd_dban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete-ban — ban user and delete the replied message."""
    message = update.message
    chat = update.effective_chat
    admin = update.effective_user

    if not message.reply_to_message:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('Reply to a message to use /dban!')}"),
            parse_mode="HTML"
        )
        return

    user_id = message.reply_to_message.from_user.id
    user_obj = message.reply_to_message.from_user
    args = message.text.split(None, 1)
    reason = args[1] if len(args) > 1 else None

    if is_owner(user_id) or is_sudo(user_id):
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('Cannot ban this user!')}"),
            parse_mode="HTML"
        )
        return

    if await is_admin(update, user_id) and not is_sudo(admin.id):
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('Cannot ban an admin!')}"),
            parse_mode="HTML"
        )
        return

    try:
        await message.reply_to_message.delete()
    except Exception:
        pass

    try:
        await chat.ban_member(user_id)
    except BadRequest as e:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Failed: {e}')}"),
            parse_mode="HTML"
        )
        return

    session = get_db()
    try:
        ban_record = DBBan(
            chat_id=chat.id,
            user_id=user_id,
            banned_by=admin.id,
            reason=reason or "dban"
        )
        session.add(ban_record)
        session.commit()
    except Exception:
        session.rollback()
    finally:
        close_db(session)

    user_name = get_user_link(user_obj) if user_obj else f"<code>{user_id}</code>"

    await message.reply_text(
        f"🔨🗑 {ST.bold_fancy('User Banned + Message Deleted!')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"✧ {ST.bold_fancy('User')}: {user_name}\n"
        f"✧ {ST.bold_fancy('Admin')}: {get_user_link(admin)}\n"
        f"✧ {ST.bold_fancy('Reason')}: {escape_html(reason or 'No reason')}\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


@admin_required
@group_only
async def cmd_baninfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show ban history for a user in this chat."""
    user_id, user_obj = await extract_user(update.message, context)
    if not user_id:
        await update.message.reply_text(
            f"✧ {ST.bold_fancy('Usage')}: /baninfo &lt;user&gt;",
            parse_mode="HTML"
        )
        return

    session = get_db()
    try:
        bans = session.query(DBBan).filter(
            DBBan.chat_id == update.effective_chat.id,
            DBBan.user_id == user_id
        ).order_by(DBBan.created_at.desc()).limit(10).all()

        user_name = get_user_link(user_obj) if user_obj else f"<code>{user_id}</code>"

        if not bans:
            await update.message.reply_text(
                f"✅ {user_name} {ST.bold_fancy('has no ban records!')}",
                parse_mode="HTML"
            )
            return

        text = (
            f"🔨 {ST.bold_fancy('Ban History for')} {user_name}\n"
            f"{TPL.SEPARATOR}\n\n"
        )

        for i, ban in enumerate(bans, 1):
            status = "🔴 Active" if ban.is_active else "🟢 Expired"
            ban_time = ban.created_at.strftime("%Y-%m-%d %H:%M") if ban.created_at else "Unknown"
            text += (
                f"  {i}. {status}\n"
                f"     📝 {escape_html(ban.reason or 'No reason')}\n"
                f"     📅 {ban_time}\n"
            )
            if ban.until_date:
                text += f"     ⏰ Until: {ban.until_date.strftime('%Y-%m-%d %H:%M')}\n"

        text += f"\n{ST.bold_fancy('Total records')}: {len(bans)}"
        text += f"\n{TPL.mini_footer()}"

        await update.message.reply_text(text, parse_mode="HTML")
    finally:
        close_db(session)


# ─────────────────────────────────────────────
#  4.2  MUTE COMMANDS
# ─────────────────────────────────────────────

@admin_required
@group_only
@bot_admin_required
@log_action
async def cmd_mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mute a user (remove send message permission)."""
    message = update.message
    chat = update.effective_chat
    admin = update.effective_user

    user_id, reason, user_obj = await extract_user_and_reason(message, context)

    if not user_id:
        await message.reply_text(
            f"🔇 {ST.bold_fancy('Mute User')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Usage')}: /mute &lt;@user/id/reply&gt; [reason]\n"
            f"✧ {ST.bold_fancy('Example')}: /mute @username spamming",
            parse_mode="HTML"
        )
        return

    if user_id == admin.id:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('You cannot mute yourself!')}"),
            parse_mode="HTML"
        )
        return

    if is_owner(user_id) or is_sudo(user_id):
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('Cannot mute this user!')}"),
            parse_mode="HTML"
        )
        return

    if await is_admin(update, user_id) and not is_sudo(admin.id):
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('Cannot mute an admin!')}"),
            parse_mode="HTML"
        )
        return

    try:
        await chat.restrict_member(
            user_id,
            ChatPermissions(can_send_messages=False)
        )
    except BadRequest as e:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Failed to mute: {e}')}"),
            parse_mode="HTML"
        )
        return

    session = get_db()
    try:
        mute_record = DBMute(
            chat_id=chat.id,
            user_id=user_id,
            muted_by=admin.id,
            reason=reason
        )
        session.add(mute_record)
        session.commit()
    except Exception:
        session.rollback()
    finally:
        close_db(session)

    user_name = get_user_link(user_obj) if user_obj else f"<code>{user_id}</code>"

    await message.reply_text(
        f"🔇 {ST.bold_fancy('User Muted!')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"╔═══[ {ST.bold_fancy('Mute Info')} ]═════╗\n"
        f"║ ✧ {ST.bold_fancy('User')}: {user_name}\n"
        f"║ ✧ {ST.bold_fancy('ID')}: <code>{user_id}</code>\n"
        f"║ ✧ {ST.bold_fancy('Admin')}: {get_user_link(admin)}\n"
        f"║ ✧ {ST.bold_fancy('Reason')}: {escape_html(reason or 'No reason')}\n"
        f"╚════════════════╝\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


@admin_required
@group_only
@bot_admin_required
@log_action
async def cmd_unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unmute a user (restore send message permission)."""
    message = update.message
    chat = update.effective_chat
    admin = update.effective_user

    user_id, user_obj = await extract_user(message, context)

    if not user_id:
        await message.reply_text(
            f"🔊 {ST.bold_fancy('Usage')}: /unmute &lt;@user/id/reply&gt;",
            parse_mode="HTML"
        )
        return

    try:
        await chat.restrict_member(
            user_id,
            ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_send_polls=True,
                can_invite_users=True,
            )
        )
    except BadRequest as e:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Failed to unmute: {e}')}"),
            parse_mode="HTML"
        )
        return

    session = get_db()
    try:
        mutes = session.query(DBMute).filter(
            DBMute.chat_id == chat.id,
            DBMute.user_id == user_id,
            DBMute.is_active == True
        ).all()
        for mute in mutes:
            mute.is_active = False
        session.commit()
    except Exception:
        session.rollback()
    finally:
        close_db(session)

    user_name = get_user_link(user_obj) if user_obj else f"<code>{user_id}</code>"

    await message.reply_text(
        f"🔊 {ST.bold_fancy('User Unmuted!')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"✧ {ST.bold_fancy('User')}: {user_name}\n"
        f"✧ {ST.bold_fancy('Admin')}: {get_user_link(admin)}\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


@admin_required
@group_only
@bot_admin_required
@log_action
async def cmd_tmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Temporary mute a user.
    Usage: /tmute [user] &lt;time&gt; [reason]
    """
    message = update.message
    chat = update.effective_chat
    admin = update.effective_user
    args = message.text.split()

    user_id, reason, user_obj = await extract_user_and_reason(message, context)

    if not user_id:
        await message.reply_text(
            f"⏱🔇 {ST.bold_fancy('Temp Mute')}\n"
            f"✧ {ST.bold_fancy('Usage')}: /tmute &lt;user&gt; &lt;time&gt; [reason]\n"
            f"✧ {ST.bold_fancy('Example')}: /tmute @user 1h too loud\n"
            f"✧ {ST.bold_fancy('Time')}: 30m, 1h, 2d, 1w",
            parse_mode="HTML"
        )
        return

    if is_owner(user_id) or is_sudo(user_id):
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('Cannot mute this user!')}"),
            parse_mode="HTML"
        )
        return

    if await is_admin(update, user_id) and not is_sudo(admin.id):
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('Cannot mute an admin!')}"),
            parse_mode="HTML"
        )
        return

    # Parse time from args
    time_str = None
    if message.reply_to_message:
        if len(args) > 1:
            time_str = args[1]
            reason = " ".join(args[2:]) if len(args) > 2 else None
    else:
        if len(args) > 2:
            time_str = args[2]
            reason = " ".join(args[3:]) if len(args) > 3 else None

    if not time_str:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('Please specify mute duration! (e.g., 1h, 30m, 2d)')}"),
            parse_mode="HTML"
        )
        return

    duration = parse_time_string(time_str)
    if not duration:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('Invalid time format! Use: 1h, 30m, 2d, 1w')}"),
            parse_mode="HTML"
        )
        return

    until_date = datetime.datetime.utcnow() + duration

    try:
        await chat.restrict_member(
            user_id,
            ChatPermissions(can_send_messages=False),
            until_date=until_date
        )
    except BadRequest as e:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Failed: {e}')}"),
            parse_mode="HTML"
        )
        return

    session = get_db()
    try:
        mute_record = DBMute(
            chat_id=chat.id,
            user_id=user_id,
            muted_by=admin.id,
            reason=reason,
            until_date=until_date
        )
        session.add(mute_record)
        session.commit()
    except Exception:
        session.rollback()
    finally:
        close_db(session)

    user_name = get_user_link(user_obj) if user_obj else f"<code>{user_id}</code>"

    await message.reply_text(
        f"⏱🔇 {ST.bold_fancy('User Temporarily Muted!')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"╔═══[ {ST.bold_fancy('TMute Info')} ]═════╗\n"
        f"║ ✧ {ST.bold_fancy('User')}: {user_name}\n"
        f"║ ✧ {ST.bold_fancy('Duration')}: {format_timedelta(duration)}\n"
        f"║ ✧ {ST.bold_fancy('Expires')}: {until_date.strftime('%Y-%m-%d %H:%M UTC')}\n"
        f"║ ✧ {ST.bold_fancy('Admin')}: {get_user_link(admin)}\n"
        f"║ ✧ {ST.bold_fancy('Reason')}: {escape_html(reason or 'No reason')}\n"
        f"╚════════════════╝\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


@admin_required
@group_only
@bot_admin_required
@log_action
async def cmd_smute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Silent mute — mute and delete the command message."""
    message = update.message
    chat = update.effective_chat
    admin = update.effective_user

    user_id, reason, user_obj = await extract_user_and_reason(message, context)

    if not user_id or is_owner(user_id) or is_sudo(user_id):
        return

    if await is_admin(update, user_id) and not is_sudo(admin.id):
        return

    try:
        await chat.restrict_member(
            user_id,
            ChatPermissions(can_send_messages=False)
        )
    except Exception:
        pass

    session = get_db()
    try:
        mute_record = DBMute(
            chat_id=chat.id,
            user_id=user_id,
            muted_by=admin.id,
            reason=reason or "Silent mute"
        )
        session.add(mute_record)
        session.commit()
    except Exception:
        session.rollback()
    finally:
        close_db(session)

    try:
        await message.delete()
    except Exception:
        pass

    if message.reply_to_message:
        try:
            await message.reply_to_message.delete()
        except Exception:
            pass


@admin_required
@group_only
@bot_admin_required
@log_action
async def cmd_dmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete-mute — mute user and delete the replied message."""
    message = update.message
    chat = update.effective_chat
    admin = update.effective_user

    if not message.reply_to_message:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('Reply to a message to use /dmute!')}"),
            parse_mode="HTML"
        )
        return

    user_id = message.reply_to_message.from_user.id
    user_obj = message.reply_to_message.from_user
    args = message.text.split(None, 1)
    reason = args[1] if len(args) > 1 else None

    if is_owner(user_id) or is_sudo(user_id):
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('Cannot mute this user!')}"),
            parse_mode="HTML"
        )
        return

    if await is_admin(update, user_id) and not is_sudo(admin.id):
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('Cannot mute an admin!')}"),
            parse_mode="HTML"
        )
        return

    try:
        await message.reply_to_message.delete()
    except Exception:
        pass

    try:
        await chat.restrict_member(
            user_id,
            ChatPermissions(can_send_messages=False)
        )
    except BadRequest as e:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Failed: {e}')}"),
            parse_mode="HTML"
        )
        return

    session = get_db()
    try:
        mute_record = DBMute(
            chat_id=chat.id,
            user_id=user_id,
            muted_by=admin.id,
            reason=reason or "dmute"
        )
        session.add(mute_record)
        session.commit()
    except Exception:
        session.rollback()
    finally:
        close_db(session)

    user_name = get_user_link(user_obj) if user_obj else f"<code>{user_id}</code>"

    await message.reply_text(
        f"🔇🗑 {ST.bold_fancy('User Muted + Message Deleted!')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"✧ {ST.bold_fancy('User')}: {user_name}\n"
        f"✧ {ST.bold_fancy('Admin')}: {get_user_link(admin)}\n"
        f"✧ {ST.bold_fancy('Reason')}: {escape_html(reason or 'No reason')}\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


# ─────────────────────────────────────────────
#  4.3  KICK COMMANDS
# ─────────────────────────────────────────────

@admin_required
@group_only
@bot_admin_required
@log_action
async def cmd_kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kick a user from the group (they can rejoin)."""
    message = update.message
    chat = update.effective_chat
    admin = update.effective_user

    user_id, reason, user_obj = await extract_user_and_reason(message, context)

    if not user_id:
        await message.reply_text(
            f"👢 {ST.bold_fancy('Kick User')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Usage')}: /kick &lt;@user/id/reply&gt; [reason]\n"
            f"✧ {ST.bold_fancy('Note')}: {ST.small_caps('User can rejoin after being kicked')}",
            parse_mode="HTML"
        )
        return

    if user_id == admin.id:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('You cannot kick yourself! Use /kickme')}"),
            parse_mode="HTML"
        )
        return

    if is_owner(user_id) or is_sudo(user_id):
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('Cannot kick this user!')}"),
            parse_mode="HTML"
        )
        return

    if await is_admin(update, user_id) and not is_sudo(admin.id):
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('Cannot kick an admin!')}"),
            parse_mode="HTML"
        )
        return

    try:
        await chat.ban_member(user_id)
        await asyncio.sleep(0.5)
        await chat.unban_member(user_id)
    except BadRequest as e:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Failed to kick: {e}')}"),
            parse_mode="HTML"
        )
        return

    user_name = get_user_link(user_obj) if user_obj else f"<code>{user_id}</code>"

    await message.reply_text(
        f"👢 {ST.bold_fancy('User Kicked!')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"╔═══[ {ST.bold_fancy('Kick Info')} ]═════╗\n"
        f"║ ✧ {ST.bold_fancy('User')}: {user_name}\n"
        f"║ ✧ {ST.bold_fancy('Admin')}: {get_user_link(admin)}\n"
        f"║ ✧ {ST.bold_fancy('Reason')}: {escape_html(reason or 'No reason')}\n"
        f"║ ✧ {ST.bold_fancy('Note')}: {ST.small_caps('User can rejoin')}\n"
        f"╚════════════════╝\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


@admin_required
@group_only
@bot_admin_required
async def cmd_skick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Silent kick — kick user and delete command."""
    message = update.message
    chat = update.effective_chat

    user_id, reason, user_obj = await extract_user_and_reason(message, context)

    if not user_id or is_owner(user_id) or is_sudo(user_id):
        return

    try:
        await chat.ban_member(user_id)
        await asyncio.sleep(0.5)
        await chat.unban_member(user_id)
        await message.delete()
    except Exception:
        pass


@admin_required
@group_only
@bot_admin_required
@log_action
async def cmd_dkick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete-kick — kick user and delete replied message."""
    message = update.message
    chat = update.effective_chat
    admin = update.effective_user

    if not message.reply_to_message:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('Reply to a message to use /dkick!')}"),
            parse_mode="HTML"
        )
        return

    user_id = message.reply_to_message.from_user.id
    user_obj = message.reply_to_message.from_user

    if is_owner(user_id) or is_sudo(user_id):
        return

    try:
        await message.reply_to_message.delete()
    except Exception:
        pass

    try:
        await chat.ban_member(user_id)
        await asyncio.sleep(0.5)
        await chat.unban_member(user_id)
    except Exception:
        pass

    user_name = get_user_link(user_obj) if user_obj else f"<code>{user_id}</code>"

    await message.reply_text(
        f"👢🗑 {ST.bold_fancy('User Kicked + Message Deleted!')}\n"
        f"✧ {ST.bold_fancy('User')}: {user_name}\n"
        f"✧ {ST.bold_fancy('Admin')}: {get_user_link(admin)}\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


@group_only
async def cmd_kickme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User kicks themselves from the group."""
    user = update.effective_user
    chat = update.effective_chat

    if await is_admin(update, user.id):
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy('Admins cannot kickme! Demote yourself first.')}"),
            parse_mode="HTML"
        )
        return

    try:
        await chat.ban_member(user.id)
        await asyncio.sleep(0.5)
        await chat.unban_member(user.id)
        await update.message.reply_text(
            f"👋 {get_user_link(user)} {ST.bold_fancy('has left the chat!')}\n"
            f"✧ {ST.small_caps('They can rejoin anytime.')}",
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Failed: {e}')}"),
            parse_mode="HTML"
        )


# ─────────────────────────────────────────────
#  4.4  WARN SYSTEM
# ─────────────────────────────────────────────

@admin_required
@group_only
@bot_admin_required
@log_action
async def cmd_warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Warn a user. After reaching the warn limit, action is taken."""
    message = update.message
    chat = update.effective_chat
    admin = update.effective_user

    user_id, reason, user_obj = await extract_user_and_reason(message, context)

    if not user_id:
        await message.reply_text(
            f"⚠️ {ST.bold_fancy('Warn User')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Usage')}: /warn &lt;@user/id/reply&gt; [reason]\n"
            f"✧ {ST.bold_fancy('Example')}: /warn @user being rude",
            parse_mode="HTML"
        )
        return

    if user_id == admin.id:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('You cannot warn yourself!')}"),
            parse_mode="HTML"
        )
        return

    if is_owner(user_id) or is_sudo(user_id):
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('Cannot warn this user!')}"),
            parse_mode="HTML"
        )
        return

    if await is_admin(update, user_id) and not is_sudo(admin.id):
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('Cannot warn an admin!')}"),
            parse_mode="HTML"
        )
        return

    session = get_db()
    try:
        # Add the warn record
        warn = DBWarn(
            user_id=user_id,
            chat_id=chat.id,
            warned_by=admin.id,
            reason=reason
        )
        session.add(warn)
        session.commit()

        # Count active warns for this user in this chat
        warn_count = session.query(func.count(DBWarn.id)).filter(
            DBWarn.user_id == user_id,
            DBWarn.chat_id == chat.id
        ).scalar() or 0

        # Get chat settings for warn limit and action
        db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
        warn_limit = db_chat.warn_limit if db_chat and db_chat.warn_limit else Config.WARN_LIMIT
        warn_action = db_chat.warn_action if db_chat and db_chat.warn_action else "ban"

        user_name = get_user_link(user_obj) if user_obj else f"<code>{user_id}</code>"

        if warn_count >= warn_limit:
            # ──── Warn limit reached — take action ────
            action_text = ""
            if warn_action == "ban":
                try:
                    await chat.ban_member(user_id)
                except Exception:
                    pass
                action_text = "BANNED 🔨"
            elif warn_action == "kick":
                try:
                    await chat.ban_member(user_id)
                    await asyncio.sleep(0.5)
                    await chat.unban_member(user_id)
                except Exception:
                    pass
                action_text = "KICKED 👢"
            elif warn_action == "mute":
                try:
                    await chat.restrict_member(
                        user_id,
                        ChatPermissions(can_send_messages=False)
                    )
                except Exception:
                    pass
                action_text = "MUTED 🔇"
            elif warn_action == "tmute":
                try:
                    await chat.restrict_member(
                        user_id,
                        ChatPermissions(can_send_messages=False),
                        until_date=datetime.datetime.utcnow() + datetime.timedelta(hours=24)
                    )
                except Exception:
                    pass
                action_text = "MUTED 🔇 (24h)"
            else:
                try:
                    await chat.ban_member(user_id)
                except Exception:
                    pass
                action_text = "BANNED 🔨"

            # Reset all warns for this user
            session.query(DBWarn).filter(
                DBWarn.user_id == user_id,
                DBWarn.chat_id == chat.id
            ).delete()
            session.commit()

            await message.reply_text(
                f"🚨 {ST.bold_fancy('Warn Limit Reached!')}\n"
                f"{TPL.SEPARATOR}\n\n"
                f"╔═══[ {ST.bold_fancy('Action Taken')} ]═════╗\n"
                f"║ ✧ {ST.bold_fancy('User')}: {user_name}\n"
                f"║ ✧ {ST.bold_fancy('Warns')}: {warn_count}/{warn_limit}\n"
                f"║ ✧ {ST.bold_fancy('Action')}: {action_text}\n"
                f"║ ✧ {ST.bold_fancy('Last Reason')}: {escape_html(reason or 'No reason')}\n"
                f"╚════════════════╝\n"
                f"{TPL.mini_footer()}",
                parse_mode="HTML"
            )
        else:
            # ──── Show warn notification ────
            warn_bar = "█" * warn_count + "░" * (warn_limit - warn_count)

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    text="🗑 Remove Warn",
                    callback_data=f"rmwarn_{user_id}_{warn.id}"
                )]
            ])

            await message.reply_text(
                f"⚠️ {ST.bold_fancy('User Warned!')}\n"
                f"{TPL.SEPARATOR}\n\n"
                f"╔═══[ {ST.bold_fancy('Warn Info')} ]═════╗\n"
                f"║ ✧ {ST.bold_fancy('User')}: {user_name}\n"
                f"║ ✧ {ST.bold_fancy('Warns')}: {warn_count}/{warn_limit} [{warn_bar}]\n"
                f"║ ✧ {ST.bold_fancy('Admin')}: {get_user_link(admin)}\n"
                f"║ ✧ {ST.bold_fancy('Reason')}: {escape_html(reason or 'No reason')}\n"
                f"╚════════════════╝\n"
                f"{TPL.mini_footer()}",
                parse_mode="HTML",
                reply_markup=keyboard
            )

    except Exception as e:
        session.rollback()
        logger.error(f"Error warning user: {e}")
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )
    finally:
        close_db(session)


async def warn_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the 'Remove Warn' inline button callback."""
    query = update.callback_query
    data = query.data

    if data.startswith("rmwarn_"):
        parts = data.split("_")
        if len(parts) < 3:
            await query.answer("❌ Invalid data!", show_alert=True)
            return

        try:
            target_user_id = int(parts[1])
            warn_id = int(parts[2])
        except ValueError:
            await query.answer("❌ Invalid data!", show_alert=True)
            return

        admin = query.from_user
        chat = query.message.chat

        # Only admins can remove warns
        if not await is_admin_callback(chat, admin.id, context):
            await query.answer("❌ Only admins can remove warns!", show_alert=True)
            return

        session = get_db()
        try:
            warn = session.query(DBWarn).filter(DBWarn.id == warn_id).first()
            if warn:
                session.delete(warn)
                session.commit()

                warn_count = session.query(func.count(DBWarn.id)).filter(
                    DBWarn.user_id == target_user_id,
                    DBWarn.chat_id == chat.id
                ).scalar() or 0

                await query.message.edit_text(
                    f"✅ {ST.bold_fancy('Warn Removed!')}\n"
                    f"{TPL.SEPARATOR}\n\n"
                    f"✧ {ST.bold_fancy('Remaining warns')}: {warn_count}\n"
                    f"✧ {ST.bold_fancy('Removed by')}: {get_user_link(admin)}\n"
                    f"{TPL.mini_footer()}",
                    parse_mode="HTML"
                )
                await query.answer("✅ Warn removed successfully!")
            else:
                await query.answer("❌ Warn not found or already removed!", show_alert=True)
        except Exception as e:
            session.rollback()
            logger.error(f"Error removing warn: {e}")
            await query.answer("❌ Error removing warn!", show_alert=True)
        finally:
            close_db(session)


@group_only
@disabled_check
async def cmd_warns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check warns for a user. Admins can check anyone, users can check themselves."""
    message = update.message
    chat = update.effective_chat

    user_id, user_obj = await extract_user(message, context)
    if not user_id:
        user_id = update.effective_user.id
        user_obj = update.effective_user

    # Non-admins can only check their own warns
    if user_id != update.effective_user.id:
        if not await is_admin(update, update.effective_user.id):
            await message.reply_text(
                TPL.error(f"{ST.bold_fancy('You can only check your own warns!')}"),
                parse_mode="HTML"
            )
            return

    session = get_db()
    try:
        warns = session.query(DBWarn).filter(
            DBWarn.user_id == user_id,
            DBWarn.chat_id == chat.id
        ).order_by(DBWarn.created_at.desc()).all()

        db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
        warn_limit = db_chat.warn_limit if db_chat and db_chat.warn_limit else Config.WARN_LIMIT

        user_name = get_user_link(user_obj) if user_obj else f"<code>{user_id}</code>"

        if not warns:
            await message.reply_text(
                f"✅ {user_name} {ST.bold_fancy('has no warns in this chat!')}\n"
                f"✧ {ST.bold_fancy('Warn limit')}: 0/{warn_limit}\n"
                f"{TPL.mini_footer()}",
                parse_mode="HTML"
            )
            return

        warn_bar = "█" * len(warns) + "░" * (warn_limit - len(warns))

        text = (
            f"⚠️ {ST.bold_fancy('Warns for')} {user_name}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Total')}: {len(warns)}/{warn_limit} [{warn_bar}]\n\n"
        )

        for i, warn in enumerate(warns, 1):
            warned_time = warn.created_at.strftime("%Y-%m-%d %H:%M") if warn.created_at else "Unknown"
            warned_by = f"<code>{warn.warned_by}</code>"
            text += (
                f"  {i}. 📝 {escape_html(warn.reason or 'No reason')}\n"
                f"     👮 By: {warned_by}\n"
                f"     📅 {warned_time}\n\n"
            )

        text += f"{TPL.mini_footer()}"

        # Add reset button for admins
        keyboard = None
        if await is_admin(update, update.effective_user.id):
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    text="🗑 Reset All Warns",
                    callback_data=f"resetwarns_{user_id}"
                )]
            ])

        await message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)

    finally:
        close_db(session)


@admin_required
@group_only
@log_action
async def cmd_resetwarns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset (delete) all warns for a user."""
    message = update.message
    chat = update.effective_chat
    admin = update.effective_user

    user_id, user_obj = await extract_user(message, context)

    if not user_id:
        await message.reply_text(
            f"🗑 {ST.bold_fancy('Usage')}: /resetwarns &lt;@user/id/reply&gt;",
            parse_mode="HTML"
        )
        return

    session = get_db()
    try:
        deleted = session.query(DBWarn).filter(
            DBWarn.user_id == user_id,
            DBWarn.chat_id == chat.id
        ).delete()
        session.commit()

        user_name = get_user_link(user_obj) if user_obj else f"<code>{user_id}</code>"

        if deleted:
            await message.reply_text(
                f"🗑 {ST.bold_fancy('Warns Reset!')}\n"
                f"{TPL.SEPARATOR}\n\n"
                f"✧ {ST.bold_fancy('User')}: {user_name}\n"
                f"✧ {ST.bold_fancy('Removed')}: {deleted} warn(s)\n"
                f"✧ {ST.bold_fancy('By')}: {get_user_link(admin)}\n"
                f"{TPL.mini_footer()}",
                parse_mode="HTML"
            )
        else:
            await message.reply_text(
                f"✅ {user_name} {ST.bold_fancy('had no warns to reset!')}",
                parse_mode="HTML"
            )
    except Exception:
        session.rollback()
    finally:
        close_db(session)


async def resetwarns_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the 'Reset All Warns' inline button callback."""
    query = update.callback_query
    data = query.data

    if data.startswith("resetwarns_"):
        try:
            user_id = int(data.split("_")[1])
        except (ValueError, IndexError):
            await query.answer("❌ Invalid data!", show_alert=True)
            return

        admin = query.from_user
        chat = query.message.chat

        if not await is_admin_callback(chat, admin.id, context):
            await query.answer("❌ Only admins can reset warns!", show_alert=True)
            return

        session = get_db()
        try:
            deleted = session.query(DBWarn).filter(
                DBWarn.user_id == user_id,
                DBWarn.chat_id == chat.id
            ).delete()
            session.commit()

            await query.message.edit_text(
                f"🗑 {ST.bold_fancy('All Warns Reset!')}\n"
                f"{TPL.SEPARATOR}\n\n"
                f"✧ {ST.bold_fancy('Warns removed')}: {deleted}\n"
                f"✧ {ST.bold_fancy('By')}: {get_user_link(admin)}\n"
                f"{TPL.mini_footer()}",
                parse_mode="HTML"
            )
            await query.answer(f"✅ Reset {deleted} warns!")
        except Exception:
            session.rollback()
            await query.answer("❌ Error!", show_alert=True)
        finally:
            close_db(session)


@admin_required
@group_only
async def cmd_warnlimit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set or view warn limit. Usage: /warnlimit [number]"""
    args = update.message.text.split()
    chat_id = update.effective_chat.id

    if len(args) < 2 or not args[1].isdigit():
        session = get_db()
        try:
            db_chat = session.query(DBChat).filter(DBChat.chat_id == chat_id).first()
            limit = db_chat.warn_limit if db_chat and db_chat.warn_limit else Config.WARN_LIMIT
        finally:
            close_db(session)

        await update.message.reply_text(
            f"⚠️ {ST.bold_fancy('Warn Limit Settings')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Current limit')}: {limit}\n"
            f"✧ {ST.bold_fancy('Usage')}: /warnlimit <2-20>\n"
            f"✧ {ST.bold_fancy('Example')}: /warnlimit 5\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
        return

    limit = int(args[1])
    if limit < 2:
        limit = 2
    elif limit > 20:
        limit = 20

    db_update_chat_setting(chat_id, warn_limit=limit)
    await update.message.reply_text(
        TPL.success(f"⚠️ {ST.bold_fancy(f'Warn limit set to {limit}')}"),
        parse_mode="HTML"
    )


@admin_required
@group_only
async def cmd_warnaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set warn action. Usage: /warnaction &lt;ban/kick/mute/tmute&gt;"""
    args = update.message.text.split()
    chat_id = update.effective_chat.id

    if len(args) < 2:
        session = get_db()
        try:
            db_chat = session.query(DBChat).filter(DBChat.chat_id == chat_id).first()
            action = db_chat.warn_action if db_chat and db_chat.warn_action else "ban"
        finally:
            close_db(session)

        await update.message.reply_text(
            f"⚠️ {ST.bold_fancy('Warn Action Settings')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Current action')}: {action}\n"
            f"✧ {ST.bold_fancy('Options')}: ban, kick, mute, tmute\n"
            f"✧ {ST.bold_fancy('Usage')}: /warnaction &lt;action&gt;\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
        return

    action = args[1].lower()
    valid_actions = ("ban", "kick", "mute", "tmute")
    if action not in valid_actions:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Invalid action! Use: {', '.join(valid_actions)}')}"),
            parse_mode="HTML"
        )
        return

    db_update_chat_setting(chat_id, warn_action=action)

    action_emojis = {"ban": "🔨", "kick": "👢", "mute": "🔇", "tmute": "⏱🔇"}
    emoji = action_emojis.get(action, "⚠️")

    await update.message.reply_text(
        TPL.success(f"{emoji} {ST.bold_fancy(f'Warn action set to: {action}')}"),
        parse_mode="HTML"
    )


# ─────────────────────────────────────────────
#  4.5  PROMOTE / DEMOTE COMMANDS
# ─────────────────────────────────────────────

@admin_required
@group_only
@bot_admin_required
@log_action
async def cmd_promote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Promote a user to admin with standard permissions."""
    message = update.message
    chat = update.effective_chat
    admin = update.effective_user
    args = message.text.split()

    user_id, user_obj = await extract_user(message, context)

    if not user_id:
        await message.reply_text(
            f"⬆️ {ST.bold_fancy('Promote User')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Usage')}: /promote &lt;@user/id/reply&gt; [title]\n"
            f"✧ {ST.bold_fancy('Example')}: /promote @user Moderator",
            parse_mode="HTML"
        )
        return

    if user_id == context.bot.id:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('I cannot promote myself!')}"),
            parse_mode="HTML"
        )
        return

    # Get custom title from remaining args
    title = None
    if message.reply_to_message:
        title = " ".join(args[1:]) if len(args) > 1 else None
    else:
        title = " ".join(args[2:]) if len(args) > 2 else None

    # Check if bot has promote permission
    if not await can_promote_members(chat, context):
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('I need \"Add Admins\" permission to promote users!')}"),
            parse_mode="HTML"
        )
        return

    try:
        await chat.promote_member(
            user_id,
            can_change_info=False,
            can_post_messages=True,
            can_edit_messages=True,
            can_delete_messages=True,
            can_invite_users=True,
            can_restrict_members=True,
            can_pin_messages=True,
            can_manage_topics=False,
        )

        if title:
            try:
                await chat.set_administrator_custom_title(user_id, title[:16])
            except Exception:
                pass  # Title might fail due to permissions

    except BadRequest as e:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Failed to promote: {e}')}"),
            parse_mode="HTML"
        )
        return

    # Invalidate admin cache for this chat
    admin_cache.pop(chat.id, None)

    user_name = get_user_link(user_obj) if user_obj else f"<code>{user_id}</code>"

    await message.reply_text(
        f"⬆️ {ST.bold_fancy('User Promoted!')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"╔═══[ {ST.bold_fancy('Promote Info')} ]═════╗\n"
        f"║ ✧ {ST.bold_fancy('User')}: {user_name}\n"
        f"║ ✧ {ST.bold_fancy('Title')}: {escape_html(title[:16] if title else 'Admin')}\n"
        f"║ ✧ {ST.bold_fancy('By')}: {get_user_link(admin)}\n"
        f"║\n"
        f"║ 📋 {ST.bold_fancy('Permissions')}:\n"
        f"║  • Delete Messages ✅\n"
        f"║  • Restrict Members ✅\n"
        f"║  • Pin Messages ✅\n"
        f"║  • Invite Users ✅\n"
        f"║  • Change Info ❌\n"
        f"║  • Add Admins ❌\n"
        f"╚════════════════╝\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


@admin_required
@group_only
@bot_admin_required
@log_action
async def cmd_fullpromote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Full promote with ALL admin permissions (sudo only)."""
    message = update.message
    chat = update.effective_chat
    admin = update.effective_user

    user_id, user_obj = await extract_user(message, context)

    if not user_id:
        await message.reply_text(
            f"⬆️⬆️ {ST.bold_fancy('Full Promote')}\n"
            f"✧ {ST.bold_fancy('Usage')}: /fullpromote &lt;@user/id/reply&gt; [title]",
            parse_mode="HTML"
        )
        return

    # Only owner/sudo can full promote
    if not is_sudo(admin.id):
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('Only sudo users can full promote!')}"),
            parse_mode="HTML"
        )
        return

    args = message.text.split()
    title = None
    if message.reply_to_message:
        title = " ".join(args[1:]) if len(args) > 1 else None
    else:
        title = " ".join(args[2:]) if len(args) > 2 else None

    try:
        await chat.promote_member(
            user_id,
            can_change_info=True,
            can_post_messages=True,
            can_edit_messages=True,
            can_delete_messages=True,
            can_invite_users=True,
            can_restrict_members=True,
            can_pin_messages=True,
            can_promote_members=True,
            can_manage_topics=True,
            can_manage_video_chats=True,
        )

        if title:
            try:
                await chat.set_administrator_custom_title(user_id, title[:16])
            except Exception:
                pass

    except BadRequest as e:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Failed: {e}')}"),
            parse_mode="HTML"
        )
        return

    admin_cache.pop(chat.id, None)
    user_name = get_user_link(user_obj) if user_obj else f"<code>{user_id}</code>"

    await message.reply_text(
        f"⬆️⬆️ {ST.bold_fancy('User Fully Promoted!')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"╔═══[ {ST.bold_fancy('Full Promote')} ]═════╗\n"
        f"║ ✧ {ST.bold_fancy('User')}: {user_name}\n"
        f"║ ✧ {ST.bold_fancy('Title')}: {escape_html(title[:16] if title else 'Full Admin')}\n"
        f"║ ✧ {ST.bold_fancy('By')}: {get_user_link(admin)}\n"
        f"║\n"
        f"║ 📋 {ST.bold_fancy('ALL Permissions Granted')} ✅\n"
        f"║  • Delete Messages ✅\n"
        f"║  • Restrict Members ✅\n"
        f"║  • Pin Messages ✅\n"
        f"║  • Invite Users ✅\n"
        f"║  • Change Info ✅\n"
        f"║  • Add Admins ✅\n"
        f"║  • Manage Topics ✅\n"
        f"║  • Video Chats ✅\n"
        f"╚════════════════╝\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


@admin_required
@group_only
@bot_admin_required
@log_action
async def cmd_lowpromote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Low promote with minimal permissions."""
    message = update.message
    chat = update.effective_chat
    admin = update.effective_user

    user_id, user_obj = await extract_user(message, context)

    if not user_id:
        await message.reply_text(
            f"⬆️ {ST.bold_fancy('Low Promote')}\n"
            f"✧ {ST.bold_fancy('Usage')}: /lowpromote &lt;@user/id/reply&gt;",
            parse_mode="HTML"
        )
        return

    try:
        await chat.promote_member(
            user_id,
            can_change_info=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=True,
            can_invite_users=True,
            can_restrict_members=False,
            can_pin_messages=True,
            can_manage_topics=False,
        )
    except BadRequest as e:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Failed: {e}')}"),
            parse_mode="HTML"
        )
        return

    admin_cache.pop(chat.id, None)
    user_name = get_user_link(user_obj) if user_obj else f"<code>{user_id}</code>"

    await message.reply_text(
        f"⬆️ {ST.bold_fancy('User Low Promoted!')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"✧ {ST.bold_fancy('User')}: {user_name}\n"
        f"✧ {ST.bold_fancy('Permissions')}: Delete, Invite, Pin only\n"
        f"✧ {ST.bold_fancy('By')}: {get_user_link(admin)}\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


@admin_required
@group_only
@bot_admin_required
@log_action
async def cmd_demote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Demote an admin to regular user."""
    message = update.message
    chat = update.effective_chat
    admin = update.effective_user

    user_id, user_obj = await extract_user(message, context)

    if not user_id:
        await message.reply_text(
            f"⬇️ {ST.bold_fancy('Demote User')}\n"
            f"✧ {ST.bold_fancy('Usage')}: /demote &lt;@user/id/reply&gt;",
            parse_mode="HTML"
        )
        return

    if user_id == context.bot.id:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('I cannot demote myself!')}"),
            parse_mode="HTML"
        )
        return

    try:
        await chat.promote_member(
            user_id,
            can_change_info=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_manage_topics=False,
            can_promote_members=False,
        )
    except BadRequest as e:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Failed to demote: {e}')}"),
            parse_mode="HTML"
        )
        return

    admin_cache.pop(chat.id, None)
    user_name = get_user_link(user_obj) if user_obj else f"<code>{user_id}</code>"

    await message.reply_text(
        f"⬇️ {ST.bold_fancy('User Demoted!')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"✧ {ST.bold_fancy('User')}: {user_name}\n"
        f"✧ {ST.bold_fancy('By')}: {get_user_link(admin)}\n"
        f"✧ {ST.bold_fancy('Status')}: Regular member\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


@admin_required
@group_only
@bot_admin_required
async def cmd_settitle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set custom admin title. Usage: /settitle [user] &lt;title&gt;"""
    message = update.message
    args = message.text.split()
    chat = update.effective_chat

    user_id, user_obj = await extract_user(message, context)

    if not user_id:
        await message.reply_text(
            f"🏷 {ST.bold_fancy('Set Admin Title')}\n"
            f"✧ {ST.bold_fancy('Usage')}: /settitle &lt;@user/reply&gt; &lt;title&gt;\n"
            f"✧ {ST.bold_fancy('Max length')}: 16 characters",
            parse_mode="HTML"
        )
        return

    # Get title from remaining args
    if message.reply_to_message:
        title = " ".join(args[1:]) if len(args) > 1 else "Admin"
    else:
        title = " ".join(args[2:]) if len(args) > 2 else "Admin"

    if len(title) > 16:
        title = title[:16]

    try:
        await chat.set_administrator_custom_title(user_id, title)
        user_name = get_user_link(user_obj) if user_obj else f"<code>{user_id}</code>"
        await message.reply_text(
            f"🏷 {ST.bold_fancy('Title Updated!')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('User')}: {user_name}\n"
            f"✧ {ST.bold_fancy('New Title')}: {escape_html(title)}\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
    except BadRequest as e:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Failed: {e}')}"),
            parse_mode="HTML"
        )


# ─────────────────────────────────────────────
#  4.6  ADMIN LIST
# ─────────────────────────────────────────────

@group_only
@disabled_check
async def cmd_adminlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show complete list of admins in the group."""
    chat = update.effective_chat

    try:
        admins = await chat.get_administrators()
    except Exception as e:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error fetching admins: {e}')}"),
            parse_mode="HTML"
        )
        return

    creator = None
    admin_list = []
    bot_list = []

    for admin_member in admins:
        user = admin_member.user
        if user.is_bot:
            bot_list.append((user, admin_member))
            continue
        if admin_member.status == ChatMemberStatus.OWNER:
            creator = (user, admin_member)
        else:
            admin_list.append((user, admin_member))

    text = (
        f"👥 {ST.bold_fancy('Admin List')}\n"
        f"{TPL.SEPARATOR}\n"
        f"✧ {ST.bold_fancy('Chat')}: {escape_html(chat.title)}\n"
        f"✧ {ST.bold_fancy('Chat ID')}: <code>{chat.id}</code>\n\n"
    )

    if creator:
        user, member = creator
        title = member.custom_title or "Creator"
        text += f"👑 {ST.bold_fancy('Creator')}:\n"
        text += f"  └ {get_user_link(user)} — <i>{escape_html(title)}</i>\n\n"

    if admin_list:
        text += f"⚔️ {ST.bold_fancy('Admins')} ({len(admin_list)}):\n"
        for i, (admin_user, member) in enumerate(admin_list, 1):
            title = member.custom_title or "Admin"
            text += f"  {i}. {get_user_link(admin_user)} — <i>{escape_html(title)}</i>\n"
        text += "\n"

    if bot_list:
        text += f"🤖 {ST.bold_fancy('Bots')} ({len(bot_list)}):\n"
        for bot_user, member in bot_list:
            text += f"  • {escape_html(bot_user.first_name)}\n"
        text += "\n"

    text += (
        f"{TPL.SEPARATOR}\n"
        f"✧ {ST.bold_fancy('Total Admins')}: {len(admins)}\n"
        f"✧ {ST.bold_fancy('Humans')}: {1 + len(admin_list) if creator else len(admin_list)}\n"
        f"✧ {ST.bold_fancy('Bots')}: {len(bot_list)}\n"
        f"{TPL.mini_footer()}"
    )

    await update.message.reply_text(text, parse_mode="HTML")


# ─────────────────────────────────────────────
#  4.7  GLOBAL BAN (GBAN) SYSTEM
# ─────────────────────────────────────────────

@sudo_required
@log_action
async def cmd_gban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Globally ban a user from ALL bot-managed groups. Sudo only."""
    message = update.message
    user_id, reason, user_obj = await extract_user_and_reason(message, context)

    if not user_id:
        await message.reply_text(
            f"🌍🔨 {ST.bold_fancy('Global Ban')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Usage')}: /gban &lt;user&gt; [reason]\n"
            f"✧ {ST.bold_fancy('Note')}: {ST.small_caps('This bans the user from ALL managed groups')}",
            parse_mode="HTML"
        )
        return

    if is_owner(user_id):
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('Cannot gban the bot owner!')}"),
            parse_mode="HTML"
        )
        return

    if is_sudo(user_id):
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('Cannot gban sudo users!')}"),
            parse_mode="HTML"
        )
        return

    # Send processing message
    processing_msg = await message.reply_text(
        f"⏳ {ST.bold_fancy('Processing global ban...')}",
        parse_mode="HTML"
    )

    session = get_db()
    try:
        # Add or update gban record
        existing = session.query(DBGban).filter(DBGban.user_id == user_id).first()
        if existing:
            existing.reason = reason or existing.reason
            existing.is_active = True
            existing.banned_by = update.effective_user.id
        else:
            gban = DBGban(
                user_id=user_id,
                reason=reason,
                banned_by=update.effective_user.id
            )
            session.add(gban)
        session.commit()

        # Ban from all managed chats
        chats = session.query(DBChat).all()
        banned_count = 0
        failed_count = 0

        for db_chat in chats:
            try:
                await context.bot.ban_chat_member(db_chat.chat_id, user_id)
                banned_count += 1
            except Exception:
                failed_count += 1
            await asyncio.sleep(0.1)  # Rate limit protection

        user_name = get_user_link(user_obj) if user_obj else f"<code>{user_id}</code>"

        await processing_msg.edit_text(
            f"🌍🔨 {ST.bold_fancy('User Globally Banned!')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"╔═══[ {ST.bold_fancy('GBan Info')} ]═════╗\n"
            f"║ ✧ {ST.bold_fancy('User')}: {user_name}\n"
            f"║ ✧ {ST.bold_fancy('ID')}: <code>{user_id}</code>\n"
            f"║ ✧ {ST.bold_fancy('Reason')}: {escape_html(reason or 'No reason')}\n"
            f"║ ✧ {ST.bold_fancy('Banned in')}: {banned_count} chats\n"
            f"║ ✧ {ST.bold_fancy('Failed')}: {failed_count} chats\n"
            f"║ ✧ {ST.bold_fancy('By')}: {get_user_link(update.effective_user)}\n"
            f"╚════════════════╝\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )

    except Exception as e:
        session.rollback()
        await processing_msg.edit_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )
    finally:
        close_db(session)


@sudo_required
@log_action
async def cmd_ungban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove global ban from a user."""
    user_id, user_obj = await extract_user(update.message, context)
    if not user_id:
        await update.message.reply_text(
            f"🌍🔓 {ST.bold_fancy('Usage')}: /ungban &lt;user&gt;",
            parse_mode="HTML"
        )
        return

    processing_msg = await update.message.reply_text(
        f"⏳ {ST.bold_fancy('Processing...')}",
        parse_mode="HTML"
    )

    session = get_db()
    try:
        gban = session.query(DBGban).filter(DBGban.user_id == user_id).first()
        if not gban or not gban.is_active:
            await processing_msg.edit_text(
                TPL.info(f"{ST.bold_fancy('User is not globally banned!')}"),
                parse_mode="HTML"
            )
            return

        gban.is_active = False
        session.commit()

        # Unban from all managed chats
        chats = session.query(DBChat).all()
        unbanned = 0
        for db_chat in chats:
            try:
                await context.bot.unban_chat_member(db_chat.chat_id, user_id)
                unbanned += 1
            except Exception:
                pass
            await asyncio.sleep(0.1)

        user_name = get_user_link(user_obj) if user_obj else f"<code>{user_id}</code>"

        await processing_msg.edit_text(
            f"🌍🔓 {ST.bold_fancy('User Un-GBanned!')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('User')}: {user_name}\n"
            f"✧ {ST.bold_fancy('Unbanned in')}: {unbanned} chats\n"
            f"✧ {ST.bold_fancy('By')}: {get_user_link(update.effective_user)}\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
    except Exception:
        session.rollback()
    finally:
        close_db(session)


@disabled_check
async def cmd_gbanlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show list of all globally banned users."""
    session = get_db()
    try:
        gbans = session.query(DBGban).filter(DBGban.is_active == True).all()

        if not gbans:
            await update.message.reply_text(
                f"✅ {ST.bold_fancy('No globally banned users!')}",
                parse_mode="HTML"
            )
            return

        text = (
            f"🌍🔨 {ST.bold_fancy('Global Ban List')}\n"
            f"{TPL.SEPARATOR}\n\n"
        )

        for i, gban in enumerate(gbans, 1):
            ban_date = gban.created_at.strftime("%Y-%m-%d") if gban.created_at else "Unknown"
            text += (
                f"  {i}. <code>{gban.user_id}</code>\n"
                f"     📝 {escape_html(gban.reason or 'No reason')}\n"
                f"     📅 {ban_date}\n\n"
            )

        text += (
            f"{TPL.SEPARATOR}\n"
            f"✧ {ST.bold_fancy('Total GBanned')}: {len(gbans)}\n"
            f"{TPL.mini_footer()}"
        )

        # If text is too long, send as file
        if len(text) > 4000:
            # Send first part
            await update.message.reply_text(text[:4000], parse_mode="HTML")
        else:
            await update.message.reply_text(text, parse_mode="HTML")
    finally:
        close_db(session)


async def check_gban_on_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check if a joining user is gbanned and auto-ban them."""
    if not update.message or not update.message.new_chat_members:
        return

    chat = update.effective_chat

    for new_member in update.message.new_chat_members:
        if new_member.is_bot:
            continue

        session = get_db()
        try:
            gban = session.query(DBGban).filter(
                DBGban.user_id == new_member.id,
                DBGban.is_active == True
            ).first()

            if gban:
                try:
                    await chat.ban_member(new_member.id)
                    await update.message.reply_text(
                        f"🌍🔨 {ST.bold_fancy('GBanned User Detected!')}\n"
                        f"{TPL.SEPARATOR}\n\n"
                        f"✧ {ST.bold_fancy('User')}: {get_user_link(new_member)}\n"
                        f"✧ {ST.bold_fancy('Reason')}: {escape_html(gban.reason or 'No reason')}\n"
                        f"✧ {ST.bold_fancy('Action')}: Auto-banned\n"
                        f"{TPL.mini_footer()}",
                        parse_mode="HTML"
                    )
                except Exception:
                    pass
        finally:
            close_db(session)


# ─────────────────────────────────────────────
#  4.8  REPORT SYSTEM
# ─────────────────────────────────────────────

@group_only
@disabled_check
async def cmd_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Report a user or message to admins."""
    message = update.message
    chat = update.effective_chat
    reporter = update.effective_user

    # Admins don't need to report
    if await is_admin(update, reporter.id):
        await message.reply_text(
            TPL.info(f"{ST.bold_fancy('Admins do not need to report! Use admin commands directly.')}"),
            parse_mode="HTML"
        )
        return

    # Check if reporting is enabled
    session = get_db()
    try:
        db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
        if db_chat and hasattr(db_chat, 'report_enabled') and not db_chat.report_enabled:
            await message.reply_text(
                TPL.error(f"{ST.bold_fancy('Reporting is disabled in this group!')}"),
                parse_mode="HTML"
            )
            return
    finally:
        close_db(session)

    reported_id = None
    reported_user = None
    reason = None

    if message.reply_to_message:
        reported_user = message.reply_to_message.from_user
        if reported_user:
            reported_id = reported_user.id

            # Can't report admins
            if await is_admin(update, reported_id):
                await message.reply_text(
                    TPL.error(f"{ST.bold_fancy('You cannot report an admin!')}"),
                    parse_mode="HTML"
                )
                return

            # Can't report yourself
            if reported_id == reporter.id:
                await message.reply_text(
                    TPL.error(f"{ST.bold_fancy('You cannot report yourself!')}"),
                    parse_mode="HTML"
                )
                return

        args = message.text.split(None, 1)
        reason = args[1] if len(args) > 1 else None
    else:
        args = message.text.split(None, 1)
        reason = args[1] if len(args) > 1 else None

    # Save report to DB
    session = get_db()
    try:
        report = DBReport(
            chat_id=chat.id,
            reporter_id=reporter.id,
            reported_id=reported_id,
            message_id=message.reply_to_message.message_id if message.reply_to_message else None,
            reason=reason
        )
        session.add(report)
        session.commit()
    except Exception:
        session.rollback()
    finally:
        close_db(session)

    # Build admin mention string (invisible mentions to notify them)
    admin_ids = await get_admin_list(chat, context)
    admin_mentions = ""
    for admin_id in admin_ids[:15]:  # Max 15 mentions
        admin_mentions += f'<a href="tg://user?id={admin_id}">​</a>'

    report_text = (
        f"🚨 {ST.bold_fancy('Report Submitted!')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"╔═══[ {ST.bold_fancy('Report Details')} ]═════╗\n"
        f"║ ✧ {ST.bold_fancy('Reporter')}: {get_user_link(reporter)}\n"
    )

    if reported_user:
        report_text += f"║ ✧ {ST.bold_fancy('Reported')}: {get_user_link(reported_user)}\n"

    if reason:
        report_text += f"║ ✧ {ST.bold_fancy('Reason')}: {escape_html(reason)}\n"

    report_text += (
        f"╚════════════════╝\n\n"
        f"👮 {ST.bold_fancy('Admins have been notified!')}\n"
        f"{admin_mentions}"
        f"{TPL.mini_footer()}"
    )

    # Add action buttons for admins
    keyboard_buttons = []
    if reported_id:
        keyboard_buttons.append([
            InlineKeyboardButton("🔨 Ban", callback_data=f"rptban_{reported_id}"),
            InlineKeyboardButton("🔇 Mute", callback_data=f"rptmute_{reported_id}"),
            InlineKeyboardButton("👢 Kick", callback_data=f"rptkick_{reported_id}"),
        ])
    keyboard_buttons.append([
        InlineKeyboardButton("✅ Resolved", callback_data=f"rptdone_{reporter.id}")
    ])

    keyboard = InlineKeyboardMarkup(keyboard_buttons)

    await message.reply_text(report_text, parse_mode="HTML", reply_markup=keyboard)


async def report_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle report action buttons."""
    query = update.callback_query
    data = query.data
    admin = query.from_user
    chat = query.message.chat

    # Only admins can use these buttons
    if not await is_admin_callback(chat, admin.id, context):
        await query.answer("❌ Only admins can use this!", show_alert=True)
        return

    if data.startswith("rptban_"):
        user_id = int(data.split("_")[1])
        try:
            await chat.ban_member(user_id)
            await query.message.edit_text(
                f"🔨 {ST.bold_fancy('Report Action: BANNED')}\n"
                f"✧ {ST.bold_fancy('User')}: <code>{user_id}</code>\n"
                f"✧ {ST.bold_fancy('By')}: {get_user_link(admin)}\n"
                f"{TPL.mini_footer()}",
                parse_mode="HTML"
            )
            await query.answer("✅ User banned!")
        except Exception as e:
            await query.answer(f"❌ Failed: {e}", show_alert=True)

    elif data.startswith("rptmute_"):
        user_id = int(data.split("_")[1])
        try:
            await chat.restrict_member(
                user_id,
                ChatPermissions(can_send_messages=False)
            )
            await query.message.edit_text(
                f"🔇 {ST.bold_fancy('Report Action: MUTED')}\n"
                f"✧ {ST.bold_fancy('User')}: <code>{user_id}</code>\n"
                f"✧ {ST.bold_fancy('By')}: {get_user_link(admin)}\n"
                f"{TPL.mini_footer()}",
                parse_mode="HTML"
            )
            await query.answer("✅ User muted!")
        except Exception as e:
            await query.answer(f"❌ Failed: {e}", show_alert=True)

    elif data.startswith("rptkick_"):
        user_id = int(data.split("_")[1])
        try:
            await chat.ban_member(user_id)
            await asyncio.sleep(0.5)
            await chat.unban_member(user_id)
            await query.message.edit_text(
                f"👢 {ST.bold_fancy('Report Action: KICKED')}\n"
                f"✧ {ST.bold_fancy('User')}: <code>{user_id}</code>\n"
                f"✧ {ST.bold_fancy('By')}: {get_user_link(admin)}\n"
                f"{TPL.mini_footer()}",
                parse_mode="HTML"
            )
            await query.answer("✅ User kicked!")
        except Exception as e:
            await query.answer(f"❌ Failed: {e}", show_alert=True)

    elif data.startswith("rptdone_"):
        await query.message.edit_text(
            f"✅ {ST.bold_fancy('Report Resolved!')}\n"
            f"✧ {ST.bold_fancy('By')}: {get_user_link(admin)}\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
        await query.answer("✅ Marked as resolved!")


@admin_required
@group_only
async def cmd_reports(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle reporting on/off."""
    args = update.message.text.split()
    chat_id = update.effective_chat.id

    if len(args) < 2:
        session = get_db()
        try:
            db_chat = session.query(DBChat).filter(DBChat.chat_id == chat_id).first()
            status = "ON ✅" if (not db_chat or not hasattr(db_chat, 'report_enabled') or db_chat.report_enabled) else "OFF ❌"
        finally:
            close_db(session)

        await update.message.reply_text(
            f"🚨 {ST.bold_fancy('Report Settings')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Status')}: {status}\n"
            f"✧ {ST.bold_fancy('Usage')}: /reports on/off\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
        return

    action = args[1].lower()
    if action in ("on", "yes", "1", "true"):
        db_update_chat_setting(chat_id, report_enabled=True)
        await update.message.reply_text(
            TPL.success(f"🚨 {ST.bold_fancy('Reports enabled! Users can now report with /report')}"),
            parse_mode="HTML"
        )
    elif action in ("off", "no", "0", "false"):
        db_update_chat_setting(chat_id, report_enabled=False)
        await update.message.reply_text(
            TPL.success(f"🚨 {ST.bold_fancy('Reports disabled!')}"),
            parse_mode="HTML"
        )
    else:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy('Invalid option! Use on/off')}"),
            parse_mode="HTML"
        )


# ─────────────────────────────────────────────
#  4.9  APPROVE / DISAPPROVE SYSTEM
# ─────────────────────────────────────────────

@admin_required
@group_only
@log_action
async def cmd_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Approve a user to bypass anti-* protections (antiflood, antilink, etc.)."""
    message = update.message
    chat = update.effective_chat
    admin = update.effective_user

    user_id, user_obj = await extract_user(message, context)
    if not user_id:
        await message.reply_text(
            f"✅ {ST.bold_fancy('Approve User')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Usage')}: /approve &lt;@user/id/reply&gt;\n"
            f"✧ {ST.bold_fancy('Effect')}: {ST.small_caps('User bypasses antiflood, antilink, etc.')}",
            parse_mode="HTML"
        )
        return

    session = get_db()
    try:
        existing = session.query(DBApproval).filter(
            DBApproval.chat_id == chat.id,
            DBApproval.user_id == user_id
        ).first()

        if existing:
            await message.reply_text(
                TPL.info(f"{ST.bold_fancy('User is already approved!')}"),
                parse_mode="HTML"
            )
            return

        approval = DBApproval(
            chat_id=chat.id,
            user_id=user_id,
            approved_by=admin.id
        )
        session.add(approval)
        session.commit()

        user_name = get_user_link(user_obj) if user_obj else f"<code>{user_id}</code>"

        await message.reply_text(
            f"✅ {ST.bold_fancy('User Approved!')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"╔═══[ {ST.bold_fancy('Approval Info')} ]═════╗\n"
            f"║ ✧ {ST.bold_fancy('User')}: {user_name}\n"
            f"║ ✧ {ST.bold_fancy('By')}: {get_user_link(admin)}\n"
            f"║\n"
            f"║ 🛡 {ST.bold_fancy('Bypasses')}:\n"
            f"║  • Anti-Flood ✅\n"
            f"║  • Anti-Link ✅\n"
            f"║  • Anti-Spam ✅\n"
            f"║  • Blacklist ✅\n"
            f"║  • Locks ✅\n"
            f"╚════════════════╝\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
    except Exception:
        session.rollback()
    finally:
        close_db(session)


@admin_required
@group_only
@log_action
async def cmd_disapprove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove approval from a user."""
    message = update.message
    chat = update.effective_chat
    admin = update.effective_user

    user_id, user_obj = await extract_user(message, context)

    if not user_id:
        await message.reply_text(
            f"❌ {ST.bold_fancy('Usage')}: /disapprove &lt;@user/id/reply&gt;",
            parse_mode="HTML"
        )
        return

    session = get_db()
    try:
        deleted = session.query(DBApproval).filter(
            DBApproval.chat_id == chat.id,
            DBApproval.user_id == user_id
        ).delete()
        session.commit()

        user_name = get_user_link(user_obj) if user_obj else f"<code>{user_id}</code>"

        if deleted:
            await message.reply_text(
                f"❌ {ST.bold_fancy('User Disapproved!')}\n"
                f"{TPL.SEPARATOR}\n\n"
                f"✧ {ST.bold_fancy('User')}: {user_name}\n"
                f"✧ {ST.bold_fancy('By')}: {get_user_link(admin)}\n"
                f"✧ {ST.bold_fancy('Note')}: {ST.small_caps('Anti-* protections now apply to this user')}\n"
                f"{TPL.mini_footer()}",
                parse_mode="HTML"
            )
        else:
            await message.reply_text(
                TPL.info(f"{ST.bold_fancy('User was not approved!')}"),
                parse_mode="HTML"
            )
    except Exception:
        session.rollback()
    finally:
        close_db(session)


@admin_required
@group_only
async def cmd_approved(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all approved users in this chat."""
    chat = update.effective_chat
    session = get_db()
    try:
        approvals = session.query(DBApproval).filter(
            DBApproval.chat_id == chat.id
        ).all()

        if not approvals:
            await update.message.reply_text(
                f"📋 {ST.bold_fancy('No approved users in this chat!')}\n"
                f"✧ {ST.bold_fancy('Use')}: /approve &lt;user&gt; to approve someone\n"
                f"{TPL.mini_footer()}",
                parse_mode="HTML"
            )
            return

        text = (
            f"✅ {ST.bold_fancy('Approved Users')}\n"
            f"{TPL.SEPARATOR}\n"
            f"✧ {ST.bold_fancy('Chat')}: {escape_html(chat.title)}\n\n"
        )

        for i, app in enumerate(approvals, 1):
            approved_time = app.created_at.strftime("%Y-%m-%d") if app.created_at else "Unknown"
            text += (
                f"  {i}. <code>{app.user_id}</code>\n"
                f"     👮 Approved by: <code>{app.approved_by}</code>\n"
                f"     📅 {approved_time}\n\n"
            )

        text += (
            f"{TPL.SEPARATOR}\n"
            f"✧ {ST.bold_fancy('Total')}: {len(approvals)} approved users\n"
            f"{TPL.mini_footer()}"
        )

        await update.message.reply_text(text, parse_mode="HTML")
    finally:
        close_db(session)


@admin_required
@group_only
@log_action
async def cmd_unapproveall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove all approvals in this chat. Owner/sudo only."""
    admin = update.effective_user
    chat = update.effective_chat

    if not is_sudo(admin.id):
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy('Only sudo users can unapprove all!')}"),
            parse_mode="HTML"
        )
        return

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Yes, Remove All", callback_data=f"unapproveall_confirm_{chat.id}"),
            InlineKeyboardButton("❌ Cancel", callback_data="unapproveall_cancel"),
        ]
    ])

    await update.message.reply_text(
        f"⚠️ {ST.bold_fancy('Are you sure?')}\n"
        f"✧ {ST.bold_fancy('This will remove ALL approvals in this chat!')}",
        parse_mode="HTML",
        reply_markup=keyboard
    )


async def unapproveall_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unapproveall confirmation."""
    query = update.callback_query
    data = query.data

    if data == "unapproveall_cancel":
        await query.message.edit_text(
            f"✅ {ST.bold_fancy('Cancelled!')}",
            parse_mode="HTML"
        )
        await query.answer("Cancelled!")
        return

    if data.startswith("unapproveall_confirm_"):
        chat_id = int(data.split("_")[2])
        admin = query.from_user

        if not is_sudo(admin.id):
            await query.answer("❌ Only sudo users!", show_alert=True)
            return

        session = get_db()
        try:
            deleted = session.query(DBApproval).filter(
                DBApproval.chat_id == chat_id
            ).delete()
            session.commit()

            await query.message.edit_text(
                f"🗑 {ST.bold_fancy('All Approvals Removed!')}\n"
                f"✧ {ST.bold_fancy('Removed')}: {deleted} approval(s)\n"
                f"✧ {ST.bold_fancy('By')}: {get_user_link(admin)}\n"
                f"{TPL.mini_footer()}",
                parse_mode="HTML"
            )
            await query.answer(f"✅ Removed {deleted} approvals!")
        except Exception:
            session.rollback()
            await query.answer("❌ Error!", show_alert=True)
        finally:
            close_db(session)


# ─────────────────────────────────────────────
#  4.10  SERVICE MESSAGE CLEANING
# ─────────────────────────────────────────────

@admin_required
@group_only
async def cmd_cleanservice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle cleaning of service messages (join/leave/pin notifications)."""
    args = update.message.text.split()
    chat_id = update.effective_chat.id

    if len(args) < 2:
        session = get_db()
        try:
            db_chat = session.query(DBChat).filter(DBChat.chat_id == chat_id).first()
            status = "ON ✅" if (db_chat and db_chat.clean_service) else "OFF ❌"
        finally:
            close_db(session)

        await update.message.reply_text(
            f"🧹 {ST.bold_fancy('Clean Service Messages')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Status')}: {status}\n"
            f"✧ {ST.bold_fancy('Usage')}: /cleanservice on/off\n"
            f"✧ {ST.bold_fancy('Effect')}: {ST.small_caps('Auto-deletes join/leave/pin messages')}\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
        return

    action = args[1].lower()
    if action in ("on", "yes", "1", "true"):
        db_update_chat_setting(chat_id, clean_service=True)
        await update.message.reply_text(
            TPL.success(f"🧹 {ST.bold_fancy('Service messages will now be automatically deleted!')}"),
            parse_mode="HTML"
        )
    elif action in ("off", "no", "0", "false"):
        db_update_chat_setting(chat_id, clean_service=False)
        await update.message.reply_text(
            TPL.success(f"🧹 {ST.bold_fancy('Service message cleaning disabled!')}"),
            parse_mode="HTML"
        )
    else:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy('Invalid option! Use on/off')}"),
            parse_mode="HTML"
        )


async def handle_service_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Auto-delete service messages if clean_service is enabled."""
    message = update.message
    if not message:
        return

    chat = update.effective_chat
    if not chat or chat.type == ChatType.PRIVATE:
        return

    # Check if any service message type
    is_service = (
        message.new_chat_members or
        message.left_chat_member or
        message.new_chat_title or
        message.new_chat_photo or
        message.delete_chat_photo or
        message.pinned_message or
        message.group_chat_created or
        message.supergroup_chat_created or
        message.channel_chat_created or
        message.migrate_to_chat_id or
        message.migrate_from_chat_id
    )

    if not is_service:
        return

    session = get_db()
    try:
        db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
        if db_chat and db_chat.clean_service:
            try:
                await message.delete()
            except Exception:
                pass
    finally:
        close_db(session)


# ─────────────────────────────────────────────
#  4.11  LOG CHANNEL CONFIGURATION
# ─────────────────────────────────────────────

@admin_required
@group_only
async def cmd_setlog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set a log channel for this group. Usage: /setlog &lt;channel_id&gt;"""
    args = update.message.text.split()

    if len(args) < 2:
        # Check current setting
        session = get_db()
        try:
            db_chat = session.query(DBChat).filter(DBChat.chat_id == update.effective_chat.id).first()
            current = db_chat.log_channel_id if db_chat and db_chat.log_channel_id else "Not set"
        finally:
            close_db(session)

        await update.message.reply_text(
            f"📋 {ST.bold_fancy('Log Channel Settings')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Current')}: {current}\n"
            f"✧ {ST.bold_fancy('Usage')}: /setlog &lt;channel_id&gt;\n"
            f"✧ {ST.bold_fancy('Steps')}:\n"
            f"  1. Create a channel\n"
            f"  2. Add bot as admin to channel\n"
            f"  3. Forward a message from channel to get ID\n"
            f"  4. Use /setlog &lt;channel_id&gt;\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
        return

    try:
        channel_id = int(args[1])
    except ValueError:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy('Invalid channel ID! Must be a number.')}"),
            parse_mode="HTML"
        )
        return

    # Verify bot can send to the channel
    try:
        test_msg = await context.bot.send_message(
            channel_id,
            f"📋 {ST.bold_fancy('Log Channel Connected!')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Chat')}: {escape_html(update.effective_chat.title)}\n"
            f"✧ {ST.bold_fancy('Chat ID')}: <code>{update.effective_chat.id}</code>\n"
            f"✧ {ST.bold_fancy('Set by')}: {get_user_link(update.effective_user)}\n"
            f"✧ {ST.bold_fancy('Time')}: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Cannot send to channel: {e}')}\n"
                      f"✧ {ST.bold_fancy('Make sure bot is admin in the channel!')}"),
            parse_mode="HTML"
        )
        return

    db_update_chat_setting(update.effective_chat.id, log_channel_id=channel_id)

    await update.message.reply_text(
        TPL.success(f"📋 {ST.bold_fancy('Log channel set successfully!')}\n"
                    f"✧ {ST.bold_fancy('Channel ID')}: <code>{channel_id}</code>"),
        parse_mode="HTML"
    )


@admin_required
@group_only
async def cmd_unsetlog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove the log channel for this group."""
    db_update_chat_setting(update.effective_chat.id, log_channel_id=None)

    await update.message.reply_text(
        TPL.success(f"📋 {ST.bold_fancy('Log channel removed!')}"),
        parse_mode="HTML"
    )


async def send_log(chat_id: int, log_text: str, context: ContextTypes.DEFAULT_TYPE):
    """Send a log message to the configured log channel."""
    session = get_db()
    try:
        db_chat = session.query(DBChat).filter(DBChat.chat_id == chat_id).first()
        if db_chat and db_chat.log_channel_id:
            try:
                await context.bot.send_message(
                    db_chat.log_channel_id,
                    log_text,
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Failed to send log: {e}")
    finally:
        close_db(session)


# ─────────────────────────────────────────────
#  4.12  PURGE / CLEAN COMMANDS
# ─────────────────────────────────────────────

@admin_required
@group_only
@bot_admin_required
async def cmd_purge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Purge messages from the replied message to the command message."""
    message = update.message

    if not message.reply_to_message:
        await message.reply_text(
            f"🗑 {ST.bold_fancy('Purge Messages')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Usage')}: Reply to a message and send /purge\n"
            f"✧ {ST.bold_fancy('Effect')}: Deletes all messages between replied and command\n"
            f"✧ {ST.bold_fancy('Also')}: /purge &lt;number&gt; to purge N recent messages",
            parse_mode="HTML"
        )
        return

    start_id = message.reply_to_message.message_id
    end_id = message.message_id
    chat_id = message.chat.id

    deleted = 0
    failed = 0

    for msg_id in range(start_id, end_id + 1):
        try:
            await context.bot.delete_message(chat_id, msg_id)
            deleted += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)  # Rate limiting

    # Send result and auto-delete
    result_msg = await context.bot.send_message(
        chat_id,
        f"🗑 {ST.bold_fancy('Purge Complete!')}\n"
        f"✧ {ST.bold_fancy('Deleted')}: {deleted} messages\n"
        f"✧ {ST.bold_fancy('Failed')}: {failed}",
        parse_mode="HTML"
    )

    await asyncio.sleep(5)
    try:
        await result_msg.delete()
    except Exception:
        pass


@admin_required
@group_only
@bot_admin_required
async def cmd_spurge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Silent purge — purge without sending confirmation."""
    message = update.message

    if not message.reply_to_message:
        return

    start_id = message.reply_to_message.message_id
    end_id = message.message_id
    chat_id = message.chat.id

    for msg_id in range(start_id, end_id + 1):
        try:
            await context.bot.delete_message(chat_id, msg_id)
        except Exception:
            pass
        await asyncio.sleep(0.05)


@admin_required
@group_only
@bot_admin_required
async def cmd_purgefrom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Purge all messages from a specific user. Usage: /purgefrom [user] [count]"""
    message = update.message
    chat = update.effective_chat
    args = message.text.split()

    user_id, user_obj = await extract_user(message, context)
    if not user_id:
        await message.reply_text(
            f"🗑 {ST.bold_fancy('Usage')}: /purgefrom &lt;@user/reply&gt; [count]\n"
            f"✧ Default count: 100",
            parse_mode="HTML"
        )
        return

    count = 100
    if message.reply_to_message:
        if len(args) > 1 and args[1].isdigit():
            count = min(int(args[1]), 500)
    else:
        if len(args) > 2 and args[2].isdigit():
            count = min(int(args[2]), 500)

    processing_msg = await message.reply_text(
        f"⏳ {ST.bold_fancy(f'Searching and deleting messages from user...')}",
        parse_mode="HTML"
    )

    # Note: Telegram Bot API doesn't support searching messages by user.
    # This would require iterating through recent messages.
    # For now, we'll note this limitation.

    await processing_msg.edit_text(
        f"🗑 {ST.bold_fancy('Purge From User')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"✧ {ST.bold_fancy('Note')}: Due to API limitations, use /purge (reply) instead\n"
        f"✧ {ST.bold_fancy('Or')}: Use /del to delete individual messages\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


@admin_required
@group_only
@bot_admin_required
async def cmd_del(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete the replied message."""
    message = update.message

    if not message.reply_to_message:
        await message.reply_text(
            f"🗑 {ST.bold_fancy('Usage')}: Reply to a message and send /del",
            parse_mode="HTML"
        )
        return

    try:
        await message.reply_to_message.delete()
        await message.delete()
    except Exception as e:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Failed: {e}')}"),
            parse_mode="HTML"
        )


# ══════════════════════════════════════════════════════════════════════════════
# ██╗  SECTION 5: ANTI-SPAM / ANTI-FLOOD / ANTI-LINK / CONTENT FILTERS
# ══════════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────
#  5.1  ANTI-FLOOD HANDLER
# ─────────────────────────────────────────────

async def check_flood(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if a user is flooding. Returns True if flooding detected and action taken."""
    message = update.message
    if not message:
        return False

    chat = update.effective_chat
    user = update.effective_user

    if not chat or not user or chat.type == ChatType.PRIVATE:
        return False

    # Skip admins, sudo, owner, approved users
    if await is_admin(update, user.id) or is_approved(chat.id, user.id):
        return False

    session = get_db()
    try:
        db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
        if not db_chat or not db_chat.antiflood_enabled:
            return False

        limit = db_chat.antiflood_limit or Config.FLOOD_LIMIT
        time_window = db_chat.antiflood_time or Config.FLOOD_TIME
        action = db_chat.antiflood_action or "mute"
    finally:
        close_db(session)

    flood_key = f"{chat.id}_{user.id}"
    now = time.time()

    if flood_key not in flood_data:
        flood_data[flood_key] = {"count": 1, "first_time": now, "messages": [message.message_id]}
        return False

    data = flood_data[flood_key]

    # Reset if time window expired
    if now - data["first_time"] > time_window:
        flood_data[flood_key] = {"count": 1, "first_time": now, "messages": [message.message_id]}
        return False

    data["count"] += 1
    data.setdefault("messages", []).append(message.message_id)

    if data["count"] > limit:
        # ──── Flooding detected! ────
        flood_data.pop(flood_key, None)

        # Try to delete flood messages
        for msg_id in data.get("messages", []):
            try:
                await context.bot.delete_message(chat.id, msg_id)
            except Exception:
                pass

        # Take configured action
        action_text = ""
        action_emoji = ""
        try:
            if action == "ban":
                await chat.ban_member(user.id)
                action_text = "BANNED"
                action_emoji = "🔨"
            elif action == "kick":
                await chat.ban_member(user.id)
                await asyncio.sleep(0.5)
                await chat.unban_member(user.id)
                action_text = "KICKED"
                action_emoji = "👢"
            elif action == "mute":
                mute_until = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
                await chat.restrict_member(
                    user.id,
                    ChatPermissions(can_send_messages=False),
                    until_date=mute_until
                )
                action_text = "MUTED (1h)"
                action_emoji = "🔇"
            elif action == "tmute":
                mute_until = datetime.datetime.utcnow() + datetime.timedelta(hours=6)
                await chat.restrict_member(
                    user.id,
                    ChatPermissions(can_send_messages=False),
                    until_date=mute_until
                )
                action_text = "MUTED (6h)"
                action_emoji = "⏱🔇"
            elif action == "warn":
                # Simulate a warn
                session = get_db()
                try:
                    warn = DBWarn(
                        user_id=user.id,
                        chat_id=chat.id,
                        warned_by=context.bot.id,
                        reason="Flooding"
                    )
                    session.add(warn)
                    session.commit()
                except Exception:
                    session.rollback()
                finally:
                    close_db(session)
                action_text = "WARNED"
                action_emoji = "⚠️"
            else:
                mute_until = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
                await chat.restrict_member(
                    user.id,
                    ChatPermissions(can_send_messages=False),
                    until_date=mute_until
                )
                action_text = "MUTED (1h)"
                action_emoji = "🔇"
        except Exception as e:
            logger.error(f"Flood action error: {e}")
            return False

        # Log to DB
        session = get_db()
        try:
            log = DBAntiSpamLog(
                chat_id=chat.id,
                user_id=user.id,
                action=f"flood_{action}",
                reason=f"Sent {data['count']} messages in {time_window}s"
            )
            session.add(log)
            session.commit()
        except Exception:
            session.rollback()
        finally:
            close_db(session)

        # Send notification (auto-delete after 30s)
        await send_and_delete(
            chat.id,
            f"🌊 {ST.bold_fancy('Flood Detected!')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"╔═══[ {ST.bold_fancy('Flood Info')} ]═════╗\n"
            f"║ ✧ {ST.bold_fancy('User')}: {get_user_link(user)}\n"
            f"║ ✧ {ST.bold_fancy('Messages')}: {data['count']} in {time_window}s\n"
            f"║ ✧ {ST.bold_fancy('Limit')}: {limit} messages\n"
            f"║ ✧ {ST.bold_fancy('Action')}: {action_emoji} {action_text}\n"
            f"╚════════════════╝\n"
            f"{TPL.mini_footer()}",
            context,
            seconds=30,
            parse_mode="HTML"
        )
        return True

    return False


# ─────────────────────────────────────────────
#  5.2  ANTI-FLOOD CONFIGURATION COMMANDS
# ─────────────────────────────────────────────

@admin_required
@group_only
async def cmd_antiflood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Configure anti-flood settings."""
    chat = update.effective_chat
    args = update.message.text.split()

    if len(args) < 2:
        session = get_db()
        try:
            db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
            enabled = db_chat.antiflood_enabled if db_chat else False
            limit = db_chat.antiflood_limit if db_chat else Config.FLOOD_LIMIT
            time_w = db_chat.antiflood_time if db_chat else Config.FLOOD_TIME
            action = db_chat.antiflood_action if db_chat else "mute"
        finally:
            close_db(session)

        await update.message.reply_text(
            f"🌊 {ST.bold_fancy('Anti-Flood Settings')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"╔═══[ {ST.bold_fancy('Configuration')} ]═════╗\n"
            f"║ ✧ {ST.bold_fancy('Status')}: {'ON ✅' if enabled else 'OFF ❌'}\n"
            f"║ ✧ {ST.bold_fancy('Limit')}: {limit} messages\n"
            f"║ ✧ {ST.bold_fancy('Time Window')}: {time_w} seconds\n"
            f"║ ✧ {ST.bold_fancy('Action')}: {action}\n"
            f"╚════════════════╝\n\n"
            f"⚙️ {ST.bold_fancy('Commands')}:\n"
            f"  • /antiflood on/off\n"
            f"  • /setflood &lt;number&gt; — Set msg limit\n"
            f"  • /setfloodtime &lt;seconds&gt; — Set time window\n"
            f"  • /setfloodaction &lt;ban/kick/mute/tmute/warn&gt;\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
        return

    action = args[1].lower()
    if action in ("on", "yes", "1", "true", "enable"):
        db_update_chat_setting(chat.id, antiflood_enabled=True)
        await update.message.reply_text(
            TPL.success(f"🌊 {ST.bold_fancy('Anti-flood enabled!')}"),
            parse_mode="HTML"
        )
    elif action in ("off", "no", "0", "false", "disable"):
        db_update_chat_setting(chat.id, antiflood_enabled=False)
        await update.message.reply_text(
            TPL.success(f"🌊 {ST.bold_fancy('Anti-flood disabled!')}"),
            parse_mode="HTML"
        )
    else:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy('Invalid option! Use on/off')}"),
            parse_mode="HTML"
        )


@admin_required
@group_only
async def cmd_setflood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set flood message limit."""
    args = update.message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await update.message.reply_text(
            f"🌊 {ST.bold_fancy('Set Flood Limit')}\n"
            f"✧ {ST.bold_fancy('Usage')}: /setflood <3-100>\n"
            f"✧ {ST.bold_fancy('Example')}: /setflood 10",
            parse_mode="HTML"
        )
        return

    limit = int(args[1])
    limit = max(3, min(100, limit))  # Clamp between 3 and 100

    db_update_chat_setting(update.effective_chat.id, antiflood_limit=limit)
    await update.message.reply_text(
        TPL.success(f"🌊 {ST.bold_fancy(f'Flood limit set to {limit} messages')}"),
        parse_mode="HTML"
    )


@admin_required
@group_only
async def cmd_setfloodtime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set flood time window in seconds."""
    args = update.message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await update.message.reply_text(
            f"🌊 {ST.bold_fancy('Set Flood Time Window')}\n"
            f"✧ {ST.bold_fancy('Usage')}: /setfloodtime <5-300>\n"
            f"✧ {ST.bold_fancy('Example')}: /setfloodtime 10",
            parse_mode="HTML"
        )
        return

    seconds = int(args[1])
    seconds = max(5, min(300, seconds))

    db_update_chat_setting(update.effective_chat.id, antiflood_time=seconds)
    await update.message.reply_text(
        TPL.success(f"🌊 {ST.bold_fancy(f'Flood time window set to {seconds} seconds')}"),
        parse_mode="HTML"
    )


@admin_required
@group_only
async def cmd_setfloodaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set action for flood violation."""
    args = update.message.text.split()
    valid_actions = ("ban", "kick", "mute", "tmute", "warn")

    if len(args) < 2:
        await update.message.reply_text(
            f"🌊 {ST.bold_fancy('Set Flood Action')}\n"
            f"✧ {ST.bold_fancy('Usage')}: /setfloodaction <{'/'.join(valid_actions)}>\n"
            f"✧ {ST.bold_fancy('Current actions available')}:\n"
            f"  • ban — Permanently ban\n"
            f"  • kick — Kick (can rejoin)\n"
            f"  • mute — Mute for 1 hour\n"
            f"  • tmute — Mute for 6 hours\n"
            f"  • warn — Add a warn",
            parse_mode="HTML"
        )
        return

    action = args[1].lower()
    if action not in valid_actions:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Invalid action! Use: {', '.join(valid_actions)}')}"),
            parse_mode="HTML"
        )
        return

    db_update_chat_setting(update.effective_chat.id, antiflood_action=action)

    action_desc = {
        "ban": "🔨 Ban permanently",
        "kick": "👢 Kick (can rejoin)",
        "mute": "🔇 Mute for 1 hour",
        "tmute": "⏱🔇 Mute for 6 hours",
        "warn": "⚠️ Add a warn"
    }

    await update.message.reply_text(
        TPL.success(f"🌊 {ST.bold_fancy(f'Flood action set to: {action_desc.get(action, action)}')}"),
        parse_mode="HTML"
    )


# ─────────────────────────────────────────────
#  5.3  ANTI-LINK HANDLER AND CONFIGURATION
# ─────────────────────────────────────────────

# URL detection patterns
URL_PATTERN = re.compile(
    r'(https?://\S+|www\.\S+|t\.me/\S+|telegram\.me/\S+|'
    r't\.me/joinchat/\S+|t\.me/\+\S+|'
    r'bit\.ly/\S+|goo\.gl/\S+|tinyurl\.com/\S+|'
    r'discord\.gg/\S+|discord\.com/invite/\S+|'
    r'instagram\.com/\S+|youtube\.com/\S+|youtu\.be/\S+|'
    r'facebook\.com/\S+|twitter\.com/\S+|x\.com/\S+)',
    re.IGNORECASE
)

TELEGRAM_LINK_PATTERN = re.compile(
    r'(t\.me/\S+|telegram\.me/\S+|t\.me/joinchat/\S+|t\.me/\+\S+|'
    r'@\w{5,})',
    re.IGNORECASE
)


async def check_antilink(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check for links in messages and take action if antilink is enabled."""
    message = update.message
    if not message:
        return False

    text = message.text or message.caption or ""
    if not text:
        return False

    chat = update.effective_chat
    user = update.effective_user

    if not chat or not user or chat.type == ChatType.PRIVATE:
        return False

    # Skip admins and approved users
    if await is_admin(update, user.id) or is_approved(chat.id, user.id):
        return False

    session = get_db()
    try:
        db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
        if not db_chat or not db_chat.antilink_enabled:
            return False

        action = db_chat.antilink_action or "delete"
        warn_on_link = db_chat.antilink_warn if hasattr(db_chat, 'antilink_warn') else False
        allowed_links = db_chat.antilink_allowed_links or ""
        antilink_mode = db_chat.antilink_mode if hasattr(db_chat, 'antilink_mode') else "all"
    finally:
        close_db(session)

    # Find URLs in text
    urls_found = []

    # Check text entities for links
    if message.entities:
        for entity in message.entities:
            if entity.type in ("url", "text_link"):
                if entity.type == "text_link":
                    urls_found.append(entity.url)
                else:
                    urls_found.append(text[entity.offset:entity.offset + entity.length])

    # Regex check
    if antilink_mode == "all":
        regex_urls = URL_PATTERN.findall(text)
    elif antilink_mode == "telegram":
        regex_urls = TELEGRAM_LINK_PATTERN.findall(text)
    else:
        regex_urls = URL_PATTERN.findall(text)

    urls_found.extend(regex_urls)

    if not urls_found:
        return False

    # Filter out allowed links
    allowed_list = [l.strip().lower() for l in allowed_links.split(",") if l.strip()]
    filtered_urls = []
    for url in urls_found:
        is_allowed = False
        for allowed in allowed_list:
            if allowed in url.lower():
                is_allowed = True
                break
        if not is_allowed:
            filtered_urls.append(url)

    if not filtered_urls:
        return False

    # ──── Link detected — take action ────

    # Log to DB
    session = get_db()
    try:
        log = DBAntiSpamLog(
            chat_id=chat.id,
            user_id=user.id,
            action=f"antilink_{action}",
            reason=f"Sent link: {filtered_urls[0][:50]}"
        )
        session.add(log)
        session.commit()
    except Exception:
        session.rollback()
    finally:
        close_db(session)

    action_taken = ""

    try:
        if action in ("delete", "del"):
            await message.delete()
            action_taken = "Message deleted 🗑"

        elif action == "warn":
            await message.delete()
            # Add a warn
            session = get_db()
            try:
                warn = DBWarn(
                    user_id=user.id,
                    chat_id=chat.id,
                    warned_by=context.bot.id,
                    reason="Sending links"
                )
                session.add(warn)
                session.commit()

                warn_count = session.query(func.count(DBWarn.id)).filter(
                    DBWarn.user_id == user.id,
                    DBWarn.chat_id == chat.id
                ).scalar() or 0

                db_chat_ref = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
                warn_limit = db_chat_ref.warn_limit if db_chat_ref and db_chat_ref.warn_limit else Config.WARN_LIMIT

                if warn_count >= warn_limit:
                    await chat.ban_member(user.id)
                    action_taken = f"Warned ({warn_count}/{warn_limit}) → BANNED 🔨"
                else:
                    action_taken = f"Warned ({warn_count}/{warn_limit}) ⚠️"
            except Exception:
                session.rollback()
            finally:
                close_db(session)

        elif action == "mute":
            await message.delete()
            mute_until = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            await chat.restrict_member(
                user.id,
                ChatPermissions(can_send_messages=False),
                until_date=mute_until
            )
            action_taken = "Muted for 1h 🔇"

        elif action == "ban":
            await message.delete()
            await chat.ban_member(user.id)
            action_taken = "Banned 🔨"

        elif action == "kick":
            await message.delete()
            await chat.ban_member(user.id)
            await asyncio.sleep(0.5)
            await chat.unban_member(user.id)
            action_taken = "Kicked 👢"

        else:
            await message.delete()
            action_taken = "Message deleted 🗑"

    except Exception as e:
        logger.error(f"Antilink action error: {e}")
        return False

    # Send notification (auto-delete)
    await send_and_delete(
        chat.id,
        f"🔗 {ST.bold_fancy('Link Detected!')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"✧ {ST.bold_fancy('User')}: {get_user_link(user)}\n"
        f"✧ {ST.bold_fancy('Action')}: {action_taken}\n"
        f"✧ {ST.bold_fancy('Note')}: {ST.small_caps('Links are not allowed in this group')}\n"
        f"{TPL.mini_footer()}",
        context,
        seconds=20,
        parse_mode="HTML"
    )
    return True


@admin_required
@group_only
async def cmd_antilink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Configure anti-link settings."""
    chat = update.effective_chat
    args = update.message.text.split()

    if len(args) < 2:
        session = get_db()
        try:
            db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
            enabled = db_chat.antilink_enabled if db_chat else False
            action = db_chat.antilink_action if db_chat else "delete"
            mode = db_chat.antilink_mode if db_chat and hasattr(db_chat, 'antilink_mode') else "all"
            allowed = db_chat.antilink_allowed_links if db_chat else ""
        finally:
            close_db(session)

        await update.message.reply_text(
            f"🔗 {ST.bold_fancy('Anti-Link Settings')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"╔═══[ {ST.bold_fancy('Configuration')} ]═════╗\n"
            f"║ ✧ {ST.bold_fancy('Status')}: {'ON ✅' if enabled else 'OFF ❌'}\n"
            f"║ ✧ {ST.bold_fancy('Action')}: {action}\n"
            f"║ ✧ {ST.bold_fancy('Mode')}: {mode}\n"
            f"║ ✧ {ST.bold_fancy('Allowed')}: {allowed or 'None'}\n"
            f"╚════════════════╝\n\n"
            f"⚙️ {ST.bold_fancy('Commands')}:\n"
            f"  • /antilink on/off\n"
            f"  • /setlinkaction &lt;delete/warn/mute/ban/kick&gt;\n"
            f"  • /setlinkmode &lt;all/telegram&gt;\n"
            f"  • /allowlink &lt;domain&gt;\n"
            f"  • /disallowlink &lt;domain&gt;\n"
            f"  • /allowedlinks — Show allowed links\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
        return

    action = args[1].lower()
    if action in ("on", "yes", "1", "true", "enable"):
        db_update_chat_setting(chat.id, antilink_enabled=True)
        await update.message.reply_text(
            TPL.success(f"🔗 {ST.bold_fancy('Anti-link enabled! Links will be deleted.')}"),
            parse_mode="HTML"
        )
    elif action in ("off", "no", "0", "false", "disable"):
        db_update_chat_setting(chat.id, antilink_enabled=False)
        await update.message.reply_text(
            TPL.success(f"🔗 {ST.bold_fancy('Anti-link disabled!')}"),
            parse_mode="HTML"
        )
    else:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy('Invalid option! Use on/off')}"),
            parse_mode="HTML"
        )


@admin_required
@group_only
async def cmd_setlinkaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set action for link detection."""
    args = update.message.text.split()
    valid_actions = ("delete", "warn", "mute", "ban", "kick")

    if len(args) < 2 or args[1].lower() not in valid_actions:
        await update.message.reply_text(
            f"🔗 {ST.bold_fancy('Set Link Action')}\n"
            f"✧ {ST.bold_fancy('Usage')}: /setlinkaction <{'/'.join(valid_actions)}>\n"
            f"✧ delete — Just delete the message\n"
            f"✧ warn — Delete + add warn\n"
            f"✧ mute — Delete + mute 1h\n"
            f"✧ ban — Delete + ban\n"
            f"✧ kick — Delete + kick",
            parse_mode="HTML"
        )
        return

    action = args[1].lower()
    db_update_chat_setting(update.effective_chat.id, antilink_action=action)
    await update.message.reply_text(
        TPL.success(f"🔗 {ST.bold_fancy(f'Link action set to: {action}')}"),
        parse_mode="HTML"
    )


@admin_required
@group_only
async def cmd_setlinkmode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set which links to detect. Usage: /setlinkmode &lt;all/telegram&gt;"""
    args = update.message.text.split()
    if len(args) < 2 or args[1].lower() not in ("all", "telegram"):
        await update.message.reply_text(
            f"🔗 {ST.bold_fancy('Set Link Mode')}\n"
            f"✧ {ST.bold_fancy('Usage')}: /setlinkmode &lt;all/telegram&gt;\n"
            f"✧ all — Block all links\n"
            f"✧ telegram — Block only Telegram links/usernames",
            parse_mode="HTML"
        )
        return

    mode = args[1].lower()
    db_update_chat_setting(update.effective_chat.id, antilink_mode=mode)
    await update.message.reply_text(
        TPL.success(f"🔗 {ST.bold_fancy(f'Link mode set to: {mode}')}"),
        parse_mode="HTML"
    )


@admin_required
@group_only
async def cmd_allowlink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Allow a specific domain to bypass anti-link."""
    args = update.message.text.split()
    if len(args) < 2:
        await update.message.reply_text(
            f"✧ {ST.bold_fancy('Usage')}: /allowlink &lt;domain&gt;\n"
            f"✧ {ST.bold_fancy('Example')}: /allowlink youtube.com",
            parse_mode="HTML"
        )
        return

    domain = args[1].lower().strip()
    chat_id = update.effective_chat.id

    session = get_db()
    try:
        db_chat = session.query(DBChat).filter(DBChat.chat_id == chat_id).first()
        if not db_chat:
            db_chat = DBChat(chat_id=chat_id, chat_title=update.effective_chat.title or "")
            session.add(db_chat)

        current = db_chat.antilink_allowed_links or ""
        current_list = [l.strip() for l in current.split(",") if l.strip()]

        if domain in current_list:
            await update.message.reply_text(
                TPL.info(f"{ST.bold_fancy(f'{domain} is already allowed!')}"),
                parse_mode="HTML"
            )
            return

        current_list.append(domain)
        db_chat.antilink_allowed_links = ",".join(current_list)
        session.commit()

        await update.message.reply_text(
            TPL.success(f"✅ {ST.bold_fancy(f'{domain} added to allowed links!')}"),
            parse_mode="HTML"
        )
    except Exception:
        session.rollback()
    finally:
        close_db(session)


@admin_required
@group_only
async def cmd_disallowlink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove a domain from allowed links."""
    args = update.message.text.split()
    if len(args) < 2:
        await update.message.reply_text(
            f"✧ {ST.bold_fancy('Usage')}: /disallowlink &lt;domain&gt;",
            parse_mode="HTML"
        )
        return

    domain = args[1].lower().strip()
    chat_id = update.effective_chat.id

    session = get_db()
    try:
        db_chat = session.query(DBChat).filter(DBChat.chat_id == chat_id).first()
        if not db_chat:
            return

        current = db_chat.antilink_allowed_links or ""
        current_list = [l.strip() for l in current.split(",") if l.strip()]

        if domain not in current_list:
            await update.message.reply_text(
                TPL.info(f"{ST.bold_fancy(f'{domain} is not in allowed list!')}"),
                parse_mode="HTML"
            )
            return

        current_list.remove(domain)
        db_chat.antilink_allowed_links = ",".join(current_list)
        session.commit()

        await update.message.reply_text(
            TPL.success(f"❌ {ST.bold_fancy(f'{domain} removed from allowed links!')}"),
            parse_mode="HTML"
        )
    except Exception:
        session.rollback()
    finally:
        close_db(session)


@admin_required
@group_only
async def cmd_allowedlinks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show list of allowed link domains."""
    chat_id = update.effective_chat.id
    session = get_db()
    try:
        db_chat = session.query(DBChat).filter(DBChat.chat_id == chat_id).first()
        allowed = db_chat.antilink_allowed_links if db_chat else ""
    finally:
        close_db(session)

    if not allowed:
        await update.message.reply_text(
            f"🔗 {ST.bold_fancy('No allowed link domains!')}\n"
            f"✧ {ST.bold_fancy('Add')}: /allowlink &lt;domain&gt;",
            parse_mode="HTML"
        )
        return

    domains = [d.strip() for d in allowed.split(",") if d.strip()]
    text = (
        f"🔗 {ST.bold_fancy('Allowed Link Domains')}\n"
        f"{TPL.SEPARATOR}\n\n"
    )
    for i, domain in enumerate(domains, 1):
        text += f"  {i}. {escape_html(domain)}\n"

    text += f"\n{ST.bold_fancy('Total')}: {len(domains)}"
    text += f"\n{TPL.mini_footer()}"

    await update.message.reply_text(text, parse_mode="HTML")


# ─────────────────────────────────────────────
#  5.4  BLACKLIST SYSTEM
# ─────────────────────────────────────────────

@admin_required
@group_only
async def cmd_blacklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manage blacklisted words. Usage: /blacklist [word]"""
    chat = update.effective_chat
    args = update.message.text.split(None, 1)

    if len(args) < 2:
        # Show current blacklist
        session = get_db()
        try:
            blacklists = session.query(DBBlacklist).filter(
                DBBlacklist.chat_id == chat.id
            ).all()

            if not blacklists:
                await update.message.reply_text(
                    f"📝 {ST.bold_fancy('Blacklist')}\n"
                    f"{TPL.SEPARATOR}\n\n"
                    f"✧ {ST.bold_fancy('No blacklisted words!')}\n"
                    f"✧ {ST.bold_fancy('Add')}: /blacklist &lt;word/phrase&gt;\n"
                    f"✧ {ST.bold_fancy('Remove')}: /unblacklist &lt;word&gt;\n"
                    f"✧ {ST.bold_fancy('Action')}: /setblaction &lt;delete/warn/mute/ban/kick&gt;\n"
                    f"{TPL.mini_footer()}",
                    parse_mode="HTML"
                )
                return

            text = (
                f"📝 {ST.bold_fancy('Blacklisted Words')}\n"
                f"{TPL.SEPARATOR}\n\n"
            )

            for i, bl in enumerate(blacklists, 1):
                text += f"  {i}. <code>{escape_html(bl.word)}</code>\n"

            text += (
                f"\n{ST.bold_fancy('Total')}: {len(blacklists)} words\n"
                f"✧ /unblacklist &lt;word&gt; — Remove\n"
                f"✧ /unblacklistall — Remove all\n"
                f"{TPL.mini_footer()}"
            )

            await update.message.reply_text(text, parse_mode="HTML")
        finally:
            close_db(session)
        return

    word = args[1].lower().strip()

    session = get_db()
    try:
        existing = session.query(DBBlacklist).filter(
            DBBlacklist.chat_id == chat.id,
            DBBlacklist.word == word
        ).first()

        if existing:
            await update.message.reply_text(
                TPL.info(f"{ST.bold_fancy(f'\"{word}\" is already blacklisted!')}"),
                parse_mode="HTML"
            )
            return

        bl = DBBlacklist(
            chat_id=chat.id,
            word=word,
            added_by=update.effective_user.id
        )
        session.add(bl)
        session.commit()

        await update.message.reply_text(
            TPL.success(f"📝 {ST.bold_fancy(f'Added \"{word}\" to blacklist!')}"),
            parse_mode="HTML"
        )
    except Exception:
        session.rollback()
    finally:
        close_db(session)


@admin_required
@group_only
async def cmd_unblacklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove a word from blacklist."""
    args = update.message.text.split(None, 1)
    if len(args) < 2:
        await update.message.reply_text(
            f"✧ {ST.bold_fancy('Usage')}: /unblacklist &lt;word&gt;",
            parse_mode="HTML"
        )
        return

    word = args[1].lower().strip()
    chat_id = update.effective_chat.id

    session = get_db()
    try:
        deleted = session.query(DBBlacklist).filter(
            DBBlacklist.chat_id == chat_id,
            DBBlacklist.word == word
        ).delete()
        session.commit()

        if deleted:
            await update.message.reply_text(
                TPL.success(f"📝 {ST.bold_fancy(f'Removed \"{word}\" from blacklist!')}"),
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text(
                TPL.error(f"{ST.bold_fancy(f'\"{word}\" is not blacklisted!')}"),
                parse_mode="HTML"
            )
    except Exception:
        session.rollback()
    finally:
        close_db(session)


@admin_required
@group_only
async def cmd_unblacklistall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove all blacklisted words."""
    chat_id = update.effective_chat.id

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Yes, Clear All", callback_data=f"clearbl_confirm_{chat_id}"),
            InlineKeyboardButton("❌ Cancel", callback_data="clearbl_cancel"),
        ]
    ])

    await update.message.reply_text(
        f"⚠️ {ST.bold_fancy('Are you sure?')}\n"
        f"✧ {ST.bold_fancy('This will remove ALL blacklisted words!')}",
        parse_mode="HTML",
        reply_markup=keyboard
    )


async def clearbl_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle clear blacklist confirmation."""
    query = update.callback_query
    data = query.data

    if data == "clearbl_cancel":
        await query.message.edit_text(
            f"✅ {ST.bold_fancy('Cancelled!')}",
            parse_mode="HTML"
        )
        return

    if data.startswith("clearbl_confirm_"):
        chat_id = int(data.split("_")[2])
        admin = query.from_user

        if not await is_admin_callback(query.message.chat, admin.id, context):
            await query.answer("❌ Only admins!", show_alert=True)
            return

        session = get_db()
        try:
            deleted = session.query(DBBlacklist).filter(
                DBBlacklist.chat_id == chat_id
            ).delete()
            session.commit()

            await query.message.edit_text(
                f"🗑 {ST.bold_fancy('Blacklist Cleared!')}\n"
                f"✧ {ST.bold_fancy('Removed')}: {deleted} word(s)\n"
                f"{TPL.mini_footer()}",
                parse_mode="HTML"
            )
            await query.answer(f"✅ Cleared {deleted} words!")
        except Exception:
            session.rollback()
        finally:
            close_db(session)


@admin_required
@group_only
async def cmd_setblaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set blacklist violation action."""
    args = update.message.text.split()
    valid_actions = ("delete", "warn", "mute", "ban", "kick")

    if len(args) < 2 or args[1].lower() not in valid_actions:
        session = get_db()
        try:
            db_chat = session.query(DBChat).filter(DBChat.chat_id == update.effective_chat.id).first()
            current = db_chat.blacklist_action if db_chat and hasattr(db_chat, 'blacklist_action') else "delete"
        finally:
            close_db(session)

        await update.message.reply_text(
            f"📝 {ST.bold_fancy('Blacklist Action')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Current')}: {current}\n"
            f"✧ {ST.bold_fancy('Usage')}: /setblaction <{'/'.join(valid_actions)}>",
            parse_mode="HTML"
        )
        return

    action = args[1].lower()
    db_update_chat_setting(update.effective_chat.id, blacklist_action=action)
    await update.message.reply_text(
        TPL.success(f"📝 {ST.bold_fancy(f'Blacklist action set to: {action}')}"),
        parse_mode="HTML"
    )


async def check_blacklist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check message for blacklisted words."""
    message = update.message
    if not message:
        return False

    text = (message.text or message.caption or "").lower()
    if not text:
        return False

    chat = update.effective_chat
    user = update.effective_user

    if not chat or not user or chat.type == ChatType.PRIVATE:
        return False

    if await is_admin(update, user.id) or is_approved(chat.id, user.id):
        return False

    session = get_db()
    try:
        blacklists = session.query(DBBlacklist).filter(
            DBBlacklist.chat_id == chat.id
        ).all()

        if not blacklists:
            return False

        db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
        action = db_chat.blacklist_action if db_chat and hasattr(db_chat, 'blacklist_action') else "delete"

        triggered_word = None
        for bl in blacklists:
            if bl.word.lower() in text:
                triggered_word = bl.word
                break

        if not triggered_word:
            return False

    finally:
        close_db(session)

    # ──── Blacklisted word found ────

    # Log
    session = get_db()
    try:
        log = DBAntiSpamLog(
            chat_id=chat.id,
            user_id=user.id,
            action=f"blacklist_{action}",
            reason=f"Used blacklisted word: {triggered_word}"
        )
        session.add(log)
        session.commit()
    except Exception:
        session.rollback()
    finally:
        close_db(session)

    action_taken = ""
    try:
        if action == "delete":
            await message.delete()
            action_taken = "Message deleted 🗑"
        elif action == "warn":
            await message.delete()
            session = get_db()
            try:
                warn = DBWarn(
                    user_id=user.id,
                    chat_id=chat.id,
                    warned_by=context.bot.id,
                    reason=f"Blacklisted word: {triggered_word}"
                )
                session.add(warn)
                session.commit()
            except Exception:
                session.rollback()
            finally:
                close_db(session)
            action_taken = "Warned ⚠️"
        elif action == "mute":
            await message.delete()
            await chat.restrict_member(
                user.id,
                ChatPermissions(can_send_messages=False),
                until_date=datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            )
            action_taken = "Muted 1h 🔇"
        elif action == "ban":
            await message.delete()
            await chat.ban_member(user.id)
            action_taken = "Banned 🔨"
        elif action == "kick":
            await message.delete()
            await chat.ban_member(user.id)
            await asyncio.sleep(0.5)
            await chat.unban_member(user.id)
            action_taken = "Kicked 👢"
        else:
            await message.delete()
            action_taken = "Message deleted 🗑"
    except Exception as e:
        logger.error(f"Blacklist action error: {e}")
        return False

    await send_and_delete(
        chat.id,
        f"📝 {ST.bold_fancy('Blacklisted Word Detected!')}\n"
        f"✧ {ST.bold_fancy('User')}: {get_user_link(user)}\n"
        f"✧ {ST.bold_fancy('Word')}: <code>{escape_html(triggered_word)}</code>\n"
        f"✧ {ST.bold_fancy('Action')}: {action_taken}\n"
        f"{TPL.mini_footer()}",
        context,
        seconds=15,
        parse_mode="HTML"
    )
    return True


# ─────────────────────────────────────────────
#  5.5  ANTI-SPAM (DUPLICATE MESSAGES)
# ─────────────────────────────────────────────

async def check_antispam(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check for spam patterns (repeated messages, etc.)."""
    message = update.message
    if not message:
        return False

    text = message.text or message.caption or ""
    if not text or len(text) < 5:
        return False

    chat = update.effective_chat
    user = update.effective_user

    if not chat or not user or chat.type == ChatType.PRIVATE:
        return False

    if await is_admin(update, user.id) or is_approved(chat.id, user.id):
        return False

    session = get_db()
    try:
        db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
        if not db_chat or not getattr(db_chat, 'antispam_enabled', False):
            return False
    finally:
        close_db(session)

    spam_key = f"spam_{chat.id}_{user.id}"
    now = time.time()

    if spam_key not in spam_data:
        spam_data[spam_key] = {"last_text": text, "count": 1, "time": now}
        return False

    data = spam_data[spam_key]

    # Reset if more than 60 seconds passed
    if now - data["time"] > 60:
        spam_data[spam_key] = {"last_text": text, "count": 1, "time": now}
        return False

    # Check if same message repeated
    if text == data["last_text"]:
        data["count"] += 1
        data["time"] = now

        if data["count"] >= 3:  # 3 identical messages = spam
            spam_data.pop(spam_key, None)

            try:
                await message.delete()
                mute_until = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
                await chat.restrict_member(
                    user.id,
                    ChatPermissions(can_send_messages=False),
                    until_date=mute_until
                )
            except Exception:
                pass

            await send_and_delete(
                chat.id,
                f"🚫 {ST.bold_fancy('Spam Detected!')}\n"
                f"✧ {ST.bold_fancy('User')}: {get_user_link(user)}\n"
                f"✧ {ST.bold_fancy('Repeated messages')}: {data['count']}\n"
                f"✧ {ST.bold_fancy('Action')}: Muted 30m 🔇\n"
                f"{TPL.mini_footer()}",
                context,
                seconds=15,
                parse_mode="HTML"
            )
            return True
    else:
        data["last_text"] = text
        data["count"] = 1
        data["time"] = now

    return False


@admin_required
@group_only
async def cmd_antispam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle anti-spam (duplicate message detection)."""
    args = update.message.text.split()
    chat_id = update.effective_chat.id

    if len(args) < 2:
        session = get_db()
        try:
            db_chat = session.query(DBChat).filter(DBChat.chat_id == chat_id).first()
            enabled = getattr(db_chat, 'antispam_enabled', False) if db_chat else False
        finally:
            close_db(session)

        await update.message.reply_text(
            f"🚫 {ST.bold_fancy('Anti-Spam Settings')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Status')}: {'ON ✅' if enabled else 'OFF ❌'}\n"
            f"✧ {ST.bold_fancy('Usage')}: /antispam on/off\n"
            f"✧ {ST.bold_fancy('Effect')}: {ST.small_caps('Detects and mutes users sending identical messages')}\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
        return

    action = args[1].lower()
    if action in ("on", "yes", "1"):
        db_update_chat_setting(chat_id, antispam_enabled=True)
        await update.message.reply_text(
            TPL.success(f"🚫 {ST.bold_fancy('Anti-spam enabled!')}"),
            parse_mode="HTML"
        )
    elif action in ("off", "no", "0"):
        db_update_chat_setting(chat_id, antispam_enabled=False)
        await update.message.reply_text(
            TPL.success(f"🚫 {ST.bold_fancy('Anti-spam disabled!')}"),
            parse_mode="HTML"
        )


# ─────────────────────────────────────────────
#  5.6  ANTI-FORWARD
# ─────────────────────────────────────────────

async def check_antiforward(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check for forwarded messages if anti-forward is enabled."""
    message = update.message
    if not message or not message.forward_date:
        return False

    chat = update.effective_chat
    user = update.effective_user

    if not chat or not user or chat.type == ChatType.PRIVATE:
        return False

    if await is_admin(update, user.id) or is_approved(chat.id, user.id):
        return False

    session = get_db()
    try:
        db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
        if not db_chat or not getattr(db_chat, 'antiforward_enabled', False):
            return False
    finally:
        close_db(session)

    try:
        await message.delete()
    except Exception:
        pass

    await send_and_delete(
        chat.id,
        f"🔄 {ST.bold_fancy('Forwarded Message Deleted!')}\n"
        f"✧ {ST.bold_fancy('User')}: {get_user_link(user)}\n"
        f"✧ {ST.bold_fancy('Note')}: {ST.small_caps('Forwarding is not allowed in this group')}\n"
        f"{TPL.mini_footer()}",
        context,
        seconds=10,
        parse_mode="HTML"
    )
    return True


@admin_required
@group_only
async def cmd_antiforward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle anti-forward."""
    args = update.message.text.split()
    chat_id = update.effective_chat.id

    if len(args) < 2:
        session = get_db()
        try:
            db_chat = session.query(DBChat).filter(DBChat.chat_id == chat_id).first()
            enabled = getattr(db_chat, 'antiforward_enabled', False) if db_chat else False
        finally:
            close_db(session)

        await update.message.reply_text(
            f"🔄 {ST.bold_fancy('Anti-Forward')}: {'ON ✅' if enabled else 'OFF ❌'}\n"
            f"✧ /antiforward on/off",
            parse_mode="HTML"
        )
        return

    action = args[1].lower()
    if action in ("on", "yes", "1"):
        db_update_chat_setting(chat_id, antiforward_enabled=True)
        await update.message.reply_text(
            TPL.success(f"🔄 {ST.bold_fancy('Anti-forward enabled!')}"),
            parse_mode="HTML"
        )
    elif action in ("off", "no", "0"):
        db_update_chat_setting(chat_id, antiforward_enabled=False)
        await update.message.reply_text(
            TPL.success(f"🔄 {ST.bold_fancy('Anti-forward disabled!')}"),
            parse_mode="HTML"
        )


# ─────────────────────────────────────────────
#  5.7  ANTI-STICKER SPAM
# ─────────────────────────────────────────────

async def check_antisticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check for sticker spam."""
    message = update.message
    if not message or not message.sticker:
        return False

    chat = update.effective_chat
    user = update.effective_user

    if not chat or not user or chat.type == ChatType.PRIVATE:
        return False

    if await is_admin(update, user.id) or is_approved(chat.id, user.id):
        return False

    session = get_db()
    try:
        db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
        if not db_chat or not getattr(db_chat, 'antisticker_enabled', False):
            return False
    finally:
        close_db(session)

    # Track sticker count
    sticker_key = f"sticker_{chat.id}_{user.id}"
    now = time.time()

    if sticker_key not in spam_data:
        spam_data[sticker_key] = {"count": 1, "time": now}
        return False

    data = spam_data[sticker_key]

    if now - data["time"] > 30:
        spam_data[sticker_key] = {"count": 1, "time": now}
        return False

    data["count"] += 1

    if data["count"] > 5:  # 5 stickers in 30 seconds
        spam_data.pop(sticker_key, None)

        try:
            await message.delete()
            await chat.restrict_member(
                user.id,
                ChatPermissions(can_send_messages=False, can_send_other_messages=False),
                until_date=datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
            )
        except Exception:
            pass

        await send_and_delete(
            chat.id,
            f"🎭 {ST.bold_fancy('Sticker Spam Detected!')}\n"
            f"✧ {ST.bold_fancy('User')}: {get_user_link(user)}\n"
            f"✧ {ST.bold_fancy('Action')}: Muted 15m 🔇\n"
            f"{TPL.mini_footer()}",
            context,
            seconds=10,
            parse_mode="HTML"
        )
        return True

    return False


@admin_required
@group_only
async def cmd_antisticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle anti-sticker spam."""
    args = update.message.text.split()
    chat_id = update.effective_chat.id

    if len(args) < 2:
        session = get_db()
        try:
            db_chat = session.query(DBChat).filter(DBChat.chat_id == chat_id).first()
            enabled = getattr(db_chat, 'antisticker_enabled', False) if db_chat else False
        finally:
            close_db(session)

        await update.message.reply_text(
            f"🎭 {ST.bold_fancy('Anti-Sticker Spam')}: {'ON ✅' if enabled else 'OFF ❌'}\n"
            f"✧ /antisticker on/off",
            parse_mode="HTML"
        )
        return

    action = args[1].lower()
    if action in ("on", "yes", "1"):
        db_update_chat_setting(chat_id, antisticker_enabled=True)
        await update.message.reply_text(
            TPL.success(f"🎭 {ST.bold_fancy('Anti-sticker spam enabled!')}"),
            parse_mode="HTML"
        )
    elif action in ("off", "no", "0"):
        db_update_chat_setting(chat_id, antisticker_enabled=False)
        await update.message.reply_text(
            TPL.success(f"🎭 {ST.bold_fancy('Anti-sticker spam disabled!')}"),
            parse_mode="HTML"
        )


# ─────────────────────────────────────────────
#  5.8  ANTI-NSFW (MEDIA CONTENT DETECTION)
# ─────────────────────────────────────────────

@admin_required
@group_only
async def cmd_antinsfw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle anti-NSFW content detection."""
    args = update.message.text.split()
    chat_id = update.effective_chat.id

    if len(args) < 2:
        session = get_db()
        try:
            db_chat = session.query(DBChat).filter(DBChat.chat_id == chat_id).first()
            enabled = getattr(db_chat, 'antinsfw_enabled', False) if db_chat else False
        finally:
            close_db(session)

        await update.message.reply_text(
            f"🔞 {ST.bold_fancy('Anti-NSFW')}: {'ON ✅' if enabled else 'OFF ❌'}\n"
            f"✧ /antinsfw on/off\n"
            f"✧ {ST.bold_fancy('Note')}: {ST.small_caps('Uses keyword detection for NSFW content')}",
            parse_mode="HTML"
        )
        return

    action = args[1].lower()
    if action in ("on", "yes", "1"):
        db_update_chat_setting(chat_id, antinsfw_enabled=True)
        await update.message.reply_text(
            TPL.success(f"🔞 {ST.bold_fancy('Anti-NSFW enabled!')}"),
            parse_mode="HTML"
        )
    elif action in ("off", "no", "0"):
        db_update_chat_setting(chat_id, antinsfw_enabled=False)
        await update.message.reply_text(
            TPL.success(f"🔞 {ST.bold_fancy('Anti-NSFW disabled!')}"),
            parse_mode="HTML"
        )


# ─────────────────────────────────────────────
#  5.9  ANTI-ARABIC / ANTI-CYRILLIC
# ─────────────────────────────────────────────

ARABIC_PATTERN = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+')
CYRILLIC_PATTERN = re.compile(r'[\u0400-\u04FF\u0500-\u052F]+')
CHINESE_PATTERN = re.compile(r'[\u4E00-\u9FFF\u3400-\u4DBF]+')


async def check_antilang(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check for restricted language characters."""
    message = update.message
    if not message or not message.text:
        return False

    chat = update.effective_chat
    user = update.effective_user

    if not chat or not user or chat.type == ChatType.PRIVATE:
        return False

    if await is_admin(update, user.id) or is_approved(chat.id, user.id):
        return False

    session = get_db()
    try:
        db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
        if not db_chat:
            return False

        anti_arabic = getattr(db_chat, 'antiarabic_enabled', False)
        anti_cyrillic = getattr(db_chat, 'anticyrillic_enabled', False)
        anti_chinese = getattr(db_chat, 'antichinese_enabled', False)
    finally:
        close_db(session)

    text = message.text
    detected = None

    if anti_arabic and ARABIC_PATTERN.search(text):
        detected = "Arabic"
    elif anti_cyrillic and CYRILLIC_PATTERN.search(text):
        detected = "Cyrillic"
    elif anti_chinese and CHINESE_PATTERN.search(text):
        detected = "Chinese"

    if not detected:
        return False

    try:
        await message.delete()
    except Exception:
        pass

    await send_and_delete(
        chat.id,
        f"🔤 {ST.bold_fancy(f'{detected} Text Detected!')}\n"
        f"✧ {ST.bold_fancy('User')}: {get_user_link(user)}\n"
        f"✧ {ST.bold_fancy('Action')}: Message deleted 🗑\n"
        f"{TPL.mini_footer()}",
        context,
        seconds=10,
        parse_mode="HTML"
    )
    return True


@admin_required
@group_only
async def cmd_antiarabic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle anti-Arabic text."""
    args = update.message.text.split()
    if len(args) < 2:
        session = get_db()
        try:
            db_chat = session.query(DBChat).filter(DBChat.chat_id == update.effective_chat.id).first()
            enabled = getattr(db_chat, 'antiarabic_enabled', False) if db_chat else False
        finally:
            close_db(session)
        await update.message.reply_text(
            f"🔤 {ST.bold_fancy('Anti-Arabic')}: {'ON ✅' if enabled else 'OFF ❌'}\n"
            f"✧ /antiarabic on/off",
            parse_mode="HTML"
        )
        return

    action = args[1].lower()
    if action in ("on", "yes", "1"):
        db_update_chat_setting(update.effective_chat.id, antiarabic_enabled=True)
        await update.message.reply_text(
            TPL.success(f"🔤 {ST.bold_fancy('Anti-Arabic enabled!')}"),
            parse_mode="HTML"
        )
    elif action in ("off", "no", "0"):
        db_update_chat_setting(update.effective_chat.id, antiarabic_enabled=False)
        await update.message.reply_text(
            TPL.success(f"🔤 {ST.bold_fancy('Anti-Arabic disabled!')}"),
            parse_mode="HTML"
        )


@admin_required
@group_only
async def cmd_anticyrillic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle anti-Cyrillic text."""
    args = update.message.text.split()
    if len(args) < 2:
        session = get_db()
        try:
            db_chat = session.query(DBChat).filter(DBChat.chat_id == update.effective_chat.id).first()
            enabled = getattr(db_chat, 'anticyrillic_enabled', False) if db_chat else False
        finally:
            close_db(session)
        await update.message.reply_text(
            f"🔤 {ST.bold_fancy('Anti-Cyrillic')}: {'ON ✅' if enabled else 'OFF ❌'}\n"
            f"✧ /anticyrillic on/off",
            parse_mode="HTML"
        )
        return

    action = args[1].lower()
    if action in ("on", "yes", "1"):
        db_update_chat_setting(update.effective_chat.id, anticyrillic_enabled=True)
        await update.message.reply_text(
            TPL.success(f"🔤 {ST.bold_fancy('Anti-Cyrillic enabled!')}"),
            parse_mode="HTML"
        )
    elif action in ("off", "no", "0"):
        db_update_chat_setting(update.effective_chat.id, anticyrillic_enabled=False)
        await update.message.reply_text(
            TPL.success(f"🔤 {ST.bold_fancy('Anti-Cyrillic disabled!')}"),
            parse_mode="HTML"
        )


# ─────────────────────────────────────────────
#  5.10  ANTI-BOT (PREVENT BOT JOINS)
# ─────────────────────────────────────────────

async def check_antibot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kick bots that join if anti-bot is enabled."""
    if not update.message or not update.message.new_chat_members:
        return

    chat = update.effective_chat

    session = get_db()
    try:
        db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
        if not db_chat or not getattr(db_chat, 'antibot_enabled', False):
            return
    finally:
        close_db(session)

    for new_member in update.message.new_chat_members:
        if new_member.is_bot and new_member.id != context.bot.id:
            try:
                await chat.ban_member(new_member.id)
                await update.message.reply_text(
                    f"🤖 {ST.bold_fancy('Bot Kicked!')}\n"
                    f"✧ {ST.bold_fancy('Bot')}: {escape_html(new_member.first_name)}\n"
                    f"✧ {ST.bold_fancy('Reason')}: Anti-bot is enabled\n"
                    f"{TPL.mini_footer()}",
                    parse_mode="HTML"
                )
            except Exception:
                pass


@admin_required
@group_only
async def cmd_antibot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle anti-bot (auto-kick bots)."""
    args = update.message.text.split()
    chat_id = update.effective_chat.id

    if len(args) < 2:
        session = get_db()
        try:
            db_chat = session.query(DBChat).filter(DBChat.chat_id == chat_id).first()
            enabled = getattr(db_chat, 'antibot_enabled', False) if db_chat else False
        finally:
            close_db(session)

        await update.message.reply_text(
            f"🤖 {ST.bold_fancy('Anti-Bot')}: {'ON ✅' if enabled else 'OFF ❌'}\n"
            f"✧ /antibot on/off\n"
            f"✧ {ST.bold_fancy('Effect')}: {ST.small_caps('Auto-kicks bots when they are added')}",
            parse_mode="HTML"
        )
        return

    action = args[1].lower()
    if action in ("on", "yes", "1"):
        db_update_chat_setting(chat_id, antibot_enabled=True)
        await update.message.reply_text(
            TPL.success(f"🤖 {ST.bold_fancy('Anti-bot enabled! New bots will be kicked.')}"),
            parse_mode="HTML"
        )
    elif action in ("off", "no", "0"):
        db_update_chat_setting(chat_id, antibot_enabled=False)
        await update.message.reply_text(
            TPL.success(f"🤖 {ST.bold_fancy('Anti-bot disabled!')}"),
            parse_mode="HTML"
        )


# ═══════════════════════════════════════════════════════════════
# ██╗  SECTION 6: WELCOME / GOODBYE / CAPTCHA SYSTEM
# ═══════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────
#  6.1  WELCOME HANDLER
# ─────────────────────────────────────────────

async def handle_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle new member joins and send welcome message."""
    message = update.message
    if not message or not message.new_chat_members:
        return

    chat = update.effective_chat
    if chat.type == ChatType.PRIVATE:
        return

    # Register/update chat in DB
    register_chat(chat)

    session = get_db()
    try:
        db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
        if not db_chat:
            return

        welcome_enabled = db_chat.welcome_enabled if db_chat.welcome_enabled is not None else True
        if not welcome_enabled:
            return

        welcome_text = db_chat.welcome_text
        welcome_media = db_chat.welcome_media
        welcome_media_type = db_chat.welcome_media_type if hasattr(db_chat, 'welcome_media_type') else None
        welcome_buttons = db_chat.welcome_buttons if hasattr(db_chat, 'welcome_buttons') else None
        captcha_enabled = getattr(db_chat, 'captcha_enabled', False)
        captcha_type = getattr(db_chat, 'captcha_type', 'button')
    finally:
        close_db(session)

    for new_member in message.new_chat_members:
        # Skip bots (unless the bot itself is added)
        if new_member.is_bot and new_member.id != context.bot.id:
            continue

        # If the bot itself is added
        if new_member.id == context.bot.id:
            await message.reply_text(
                f"✦ {ST.bold_fancy('Thank You for Adding Me!')} ✦\n"
                f"{TPL.SEPARATOR}\n\n"
                f"╔═══[ {ST.bold_fancy('Setup')} ]═════╗\n"
                f"║ ✧ Make me admin with full permissions\n"
                f"║ ✧ Use /help to see all commands\n"
                f"║ ✧ Use /settings to configure\n"
                f"╚════════════════╝\n"
                f"{TPL.mini_footer()}",
                parse_mode="HTML"
            )
            continue

        # Track member join
        session = get_db()
        try:
            user_record = session.query(DBUser).filter(DBUser.user_id == new_member.id).first()
            if user_record:
                user_record.first_name = new_member.first_name
                user_record.last_name = new_member.last_name
                user_record.username = new_member.username
            else:
                user_record = DBUser(
                    user_id=new_member.id,
                    first_name=new_member.first_name,
                    last_name=new_member.last_name,
                    username=new_member.username
                )
                session.add(user_record)

            # Track member in chat
            membership = session.query(DBMembership).filter(
                DBMembership.chat_id == chat.id,
                DBMembership.user_id == new_member.id
            ).first()
            if not membership:
                membership = DBMembership(
                    chat_id=chat.id,
                    user_id=new_member.id
                )
                session.add(membership)

            session.commit()
        except Exception:
            session.rollback()
        finally:
            close_db(session)

        # Check if user is gbanned
        session = get_db()
        try:
            gban = session.query(DBGban).filter(
                DBGban.user_id == new_member.id,
                DBGban.is_active == True
            ).first()
            if gban:
                try:
                    await chat.ban_member(new_member.id)
                    await message.reply_text(
                        f"🌍🔨 {ST.bold_fancy('GBanned User Auto-Banned!')}\n"
                        f"✧ {ST.bold_fancy('User')}: {get_user_link(new_member)}\n"
                        f"✧ {ST.bold_fancy('Reason')}: {escape_html(gban.reason or 'No reason')}",
                        parse_mode="HTML"
                    )
                except Exception:
                    pass
                continue
        finally:
            close_db(session)

        # ──── Format Welcome Message ────
        if not welcome_text:
            # Default welcome message
            welcome_text = (
                f"✦ {ST.bold_fancy('Welcome')} ✦\n"
                f"{TPL.SEPARATOR}\n\n"
                f"╔═══[ {ST.bold_fancy('Your Info')} ]═════╗\n"
                f"║ ✧ {ST.bold_fancy('User')}: {{first_name}}\n"
                f"║ ✧ {ST.bold_fancy('User ID')}: {{user_id}}\n"
                f"║ ✧ {ST.bold_fancy('Username')}: {{username}}\n"
                f"║ ✧ {ST.bold_fancy('Group')}: {{chat_title}}\n"
                f"╚════════════════╝\n\n"
                f"⚠️ {ST.bold_fancy('RULES')}:\n"
                f"➊ 🚫 {ST.bold_fancy('No links')}\n"
                f"➋ ❌ {ST.bold_fancy('No abuse')}\n"
                f"➌ ⚠️ {ST.bold_fancy('No promo')}\n"
                f"➍ 🔞 {ST.bold_fancy('No NSFW')}\n\n"
                f"⚙️ {ST.bold_fancy('Commands')}: /help\n"
                f"{TPL.SEPARATOR}\n"
                f"👑 {ST.bold_fancy('Owner')}: —愛 | 𝗥𝗨𝗛𝗜 𝗫 𝗤𝗡𝗥〆\n"
                f"{TPL.SEPARATOR}\n"
                f"{TPL.mini_footer()}"
            )

        # Replace placeholders
        formatted_text = format_welcome_text(welcome_text, new_member, chat)

        # Build inline keyboard
        keyboard = None
        if welcome_buttons:
            keyboard = parse_buttons(welcome_buttons)

        # ──── CAPTCHA System ────
        if captcha_enabled:
            # Mute user first
            try:
                await chat.restrict_member(
                    new_member.id,
                    ChatPermissions(can_send_messages=False)
                )
            except Exception:
                pass

            if captcha_type == "button":
                # Button captcha
                captcha_token = f"captcha_{new_member.id}_{chat.id}_{int(time.time())}"
                captcha_keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                        f"✅ {ST.bold_fancy('I am Human')}",
                        callback_data=f"captcha_verify_{new_member.id}"
                    )]
                ])

                formatted_text += (
                    f"\n\n🔒 {ST.bold_fancy('CAPTCHA')}\n"
                    f"✧ {ST.bold_fancy('Click the button below to verify you are human!')}\n"
                    f"✧ {ST.bold_fancy('You have 5 minutes to verify.')}"
                )

                keyboard = captcha_keyboard

                # Schedule auto-kick after 5 minutes if not verified
                context.job_queue.run_once(
                    captcha_timeout,
                    when=300,
                    data={"chat_id": chat.id, "user_id": new_member.id},
                    name=f"captcha_timeout_{chat.id}_{new_member.id}"
                )

            elif captcha_type == "math":
                # Math captcha
                num1 = random.randint(1, 20)
                num2 = random.randint(1, 20)
                operation = random.choice(["+", "-"])
                answer = num1 + num2 if operation == "+" else num1 - num2

                # Store answer
                captcha_answers[f"{chat.id}_{new_member.id}"] = str(answer)

                # Generate wrong answers
                wrong1 = answer + random.randint(1, 5)
                wrong2 = answer - random.randint(1, 5)
                wrong3 = answer + random.randint(6, 10)

                options = [answer, wrong1, wrong2, wrong3]
                random.shuffle(options)

                captcha_keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                        str(opt),
                        callback_data=f"mathcaptcha_{new_member.id}_{opt}"
                    ) for opt in options]
                ])

                formatted_text += (
                    f"\n\n🔢 {ST.bold_fancy('Math CAPTCHA')}\n"
                    f"✧ {ST.bold_fancy(f'What is {num1} {operation} {num2} = ?')}\n"
                    f"✧ {ST.bold_fancy('Select the correct answer below:')}"
                )

                keyboard = captcha_keyboard

                context.job_queue.run_once(
                    captcha_timeout,
                    when=300,
                    data={"chat_id": chat.id, "user_id": new_member.id},
                    name=f"captcha_timeout_{chat.id}_{new_member.id}"
                )

        # ──── Send Welcome Message ────
        try:
            if welcome_media and welcome_media_type:
                if welcome_media_type == "photo":
                    await context.bot.send_photo(
                        chat.id,
                        photo=welcome_media,
                        caption=formatted_text,
                        parse_mode="HTML",
                        reply_markup=keyboard
                    )
                elif welcome_media_type == "gif":
                    await context.bot.send_animation(
                        chat.id,
                        animation=welcome_media,
                        caption=formatted_text,
                        parse_mode="HTML",
                        reply_markup=keyboard
                    )
                elif welcome_media_type == "video":
                    await context.bot.send_video(
                        chat.id,
                        video=welcome_media,
                        caption=formatted_text,
                        parse_mode="HTML",
                        reply_markup=keyboard
                    )
                elif welcome_media_type == "sticker":
                    await context.bot.send_sticker(chat.id, sticker=welcome_media)
                    await context.bot.send_message(
                        chat.id,
                        formatted_text,
                        parse_mode="HTML",
                        reply_markup=keyboard
                    )
            else:
                await context.bot.send_message(
                    chat.id,
                    formatted_text,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
        except Exception as e:
            logger.error(f"Welcome message error: {e}")
            # Fallback to simple welcome
            try:
                await context.bot.send_message(
                    chat.id,
                    f"✦ {ST.bold_fancy('Welcome')} {get_user_link(new_member)}! ✦",
                    parse_mode="HTML"
                )
            except Exception:
                pass


def format_welcome_text(text: str, user, chat) -> str:
    """Replace placeholders in welcome/goodbye text. HTML-safe output."""
    replacements = {
        "{first_name}": escape_html(user.first_name or ""),
        "{last_name}": escape_html(user.last_name or ""),
        "{full_name}": escape_html(f"{user.first_name or ''} {user.last_name or ''}".strip()),
        "{user_id}": str(user.id),
        "{username}": f"@{user.username}" if user.username else "No username",
        "{mention}": get_user_link(user),
        "{chat_title}": escape_html(chat.title or ""),
        "{chat_id}": str(chat.id),
        "{member_count}": "N/A",
        "{user}": get_user_link(user),
        "{chatname}": escape_html(chat.title or ""),
        "{id}": str(user.id),
        "{first}": escape_html(user.first_name or ""),
        "{rules}": "/rules",
    }

    for placeholder, value in replacements.items():
        text = text.replace(placeholder, value)

    # Strip any leftover {placeholder} — prevents HTML parse crashes
    import re as _re
    text = _re.sub(r'\{[a-zA-Z_][a-zA-Z0-9_]*\}', '', text)

    return text


async def captcha_timeout(context: ContextTypes.DEFAULT_TYPE):
    """Auto-kick user if they don't complete captcha in time."""
    job = context.job
    chat_id = job.data["chat_id"]
    user_id = job.data["user_id"]

    # Check if already verified
    captcha_key = f"{chat_id}_{user_id}"
    if captcha_key in captcha_verified:
        captcha_verified.discard(captcha_key)
        return

    try:
        await context.bot.ban_chat_member(chat_id, user_id)
        await asyncio.sleep(1)
        await context.bot.unban_chat_member(chat_id, user_id)

        await context.bot.send_message(
            chat_id,
            f"⏱ {ST.bold_fancy('Captcha Timeout!')}\n"
            f"✧ User <code>{user_id}</code> was kicked for not completing captcha.\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
    except Exception:
        pass

    captcha_answers.pop(captcha_key, None)


async def captcha_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle captcha verification buttons."""
    query = update.callback_query
    data = query.data
    user = query.from_user
    chat = query.message.chat

    if data.startswith("captcha_verify_"):
        target_user_id = int(data.split("_")[2])

        if user.id != target_user_id:
            await query.answer("❌ This captcha is not for you!", show_alert=True)
            return

        # Verify — unmute user
        try:
            await chat.restrict_member(
                user.id,
                ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                    can_send_polls=True,
                    can_invite_users=True,
                )
            )
        except Exception:
            pass

        captcha_key = f"{chat.id}_{user.id}"
        captcha_verified.add(captcha_key)

        # Cancel timeout job
        jobs = context.job_queue.get_jobs_by_name(f"captcha_timeout_{chat.id}_{user.id}")
        for job in jobs:
            job.schedule_removal()

        await query.message.edit_text(
            f"✅ {ST.bold_fancy('Captcha Verified!')}\n"
            f"✧ {get_user_link(user)} {ST.bold_fancy('is now verified!')}\n"
            f"✧ {ST.bold_fancy('Welcome to the group!')} 🎉\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
        await query.answer("✅ Verified! Welcome!")

    elif data.startswith("mathcaptcha_"):
        parts = data.split("_")
        target_user_id = int(parts[1])
        selected_answer = parts[2]

        if user.id != target_user_id:
            await query.answer("❌ This captcha is not for you!", show_alert=True)
            return

        captcha_key = f"{chat.id}_{user.id}"
        correct_answer = captcha_answers.get(captcha_key)

        if selected_answer == correct_answer:
            # Correct!
            try:
                await chat.restrict_member(
                    user.id,
                    ChatPermissions(
                        can_send_messages=True,
                        can_send_media_messages=True,
                        can_send_other_messages=True,
                        can_add_web_page_previews=True,
                        can_send_polls=True,
                        can_invite_users=True,
                    )
                )
            except Exception:
                pass

            captcha_verified.add(captcha_key)
            captcha_answers.pop(captcha_key, None)

            jobs = context.job_queue.get_jobs_by_name(f"captcha_timeout_{chat.id}_{user.id}")
            for job in jobs:
                job.schedule_removal()

            await query.message.edit_text(
                f"✅ {ST.bold_fancy('Captcha Verified!')}\n"
                f"✧ {get_user_link(user)} {ST.bold_fancy('answered correctly!')}\n"
                f"✧ {ST.bold_fancy('Welcome!')} 🎉\n"
                f"{TPL.mini_footer()}",
                parse_mode="HTML"
            )
            await query.answer("✅ Correct! Welcome!")
        else:
            # Wrong answer — kick
            try:
                await chat.ban_member(user.id)
                await asyncio.sleep(0.5)
                await chat.unban_member(user.id)
            except Exception:
                pass

            captcha_answers.pop(captcha_key, None)

            jobs = context.job_queue.get_jobs_by_name(f"captcha_timeout_{chat.id}_{user.id}")
            for job in jobs:
                job.schedule_removal()

            await query.message.edit_text(
                f"❌ {ST.bold_fancy('Wrong Answer!')}\n"
                f"✧ {get_user_link(user)} {ST.bold_fancy('has been kicked.')}\n"
                f"✧ {ST.bold_fancy('They can rejoin and try again.')}\n"
                f"{TPL.mini_footer()}",
                parse_mode="HTML"
            )
            await query.answer("❌ Wrong answer! You've been kicked.", show_alert=True)


# ─────────────────────────────────────────────
#  6.2  WELCOME CONFIGURATION COMMANDS
# ─────────────────────────────────────────────

@admin_required
@group_only
async def cmd_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Configure welcome message. Usage: /welcome [on/off/text/show/reset]"""
    args = update.message.text.split(None, 1)
    chat_id = update.effective_chat.id

    if len(args) < 2:
        session = get_db()
        try:
            db_chat = session.query(DBChat).filter(DBChat.chat_id == chat_id).first()
            enabled = db_chat.welcome_enabled if db_chat and db_chat.welcome_enabled is not None else True
            has_custom = bool(db_chat and db_chat.welcome_text)
            has_media = bool(db_chat and db_chat.welcome_media)
        finally:
            close_db(session)

        await update.message.reply_text(
            f"👋 {ST.bold_fancy('Welcome Settings')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"╔═══[ {ST.bold_fancy('Configuration')} ]═════╗\n"
            f"║ ✧ {ST.bold_fancy('Status')}: {'ON ✅' if enabled else 'OFF ❌'}\n"
            f"║ ✧ {ST.bold_fancy('Custom Text')}: {'Yes ✅' if has_custom else 'No (default)'}\n"
            f"║ ✧ {ST.bold_fancy('Media')}: {'Yes ✅' if has_media else 'No ❌'}\n"
            f"╚════════════════╝\n\n"
            f"⚙️ {ST.bold_fancy('Commands')}:\n"
            f"  • /welcome on/off — Toggle\n"
            f"  • /setwelcome &lt;text&gt; — Set custom text\n"
            f"  • /resetwelcome — Reset to default\n"
            f"  • /showwelcome — Preview current\n"
            f"  • /setwelcomemedia — Reply to photo/gif\n"
            f"  • /resetwelcomemedia — Remove media\n\n"
            f"📝 {ST.bold_fancy('Placeholders')}:\n"
            f"  {{first_name}} {{last_name}} {{full_name}}\n"
            f"  {{user_id}} {{username}} {{mention}}\n"
            f"  {{chat_title}} {{chat_id}}\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
        return

    action = args[1].lower().strip()

    if action in ("on", "yes", "1", "true"):
        db_update_chat_setting(chat_id, welcome_enabled=True)
        await update.message.reply_text(
            TPL.success(f"👋 {ST.bold_fancy('Welcome messages enabled!')}"),
            parse_mode="HTML"
        )
    elif action in ("off", "no", "0", "false"):
        db_update_chat_setting(chat_id, welcome_enabled=False)
        await update.message.reply_text(
            TPL.success(f"👋 {ST.bold_fancy('Welcome messages disabled!')}"),
            parse_mode="HTML"
        )
    else:
        await update.message.reply_text(
            f"✧ {ST.bold_fancy('Use')}: /welcome on/off\n"
            f"✧ {ST.bold_fancy('Or')}: /setwelcome &lt;text&gt;",
            parse_mode="HTML"
        )


@admin_required
@group_only
async def cmd_setwelcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set custom welcome message text."""
    args = update.message.text.split(None, 1)
    if len(args) < 2:
        await update.message.reply_text(
            f"👋 {ST.bold_fancy('Set Welcome Message')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Usage')}: /setwelcome &lt;your message&gt;\n\n"
            f"📝 {ST.bold_fancy('Available Placeholders')}:\n"
            f"  {{first_name}} — User's first name\n"
            f"  {{last_name}} — User's last name\n"
            f"  {{full_name}} — Full name\n"
            f"  {{user_id}} — User ID\n"
            f"  {{username}} — @username\n"
            f"  {{mention}} — Clickable mention\n"
            f"  {{chat_title}} — Group name\n"
            f"  {{chat_id}} — Group ID\n\n"
            f"✧ {ST.bold_fancy('HTML supported')}: <b>bold</b>, <i>italic</i>, <code>code</code>\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
        return

    welcome_text = args[1]

    # Validate length
    if len(welcome_text) > 4000:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy('Welcome message is too long! Max 4000 characters.')}"),
            parse_mode="HTML"
        )
        return

    db_update_chat_setting(update.effective_chat.id, welcome_text=welcome_text)
    await update.message.reply_text(
        TPL.success(f"👋 {ST.bold_fancy('Welcome message updated!')}\n"
                    f"✧ Use /showwelcome to preview"),
        parse_mode="HTML"
    )


@admin_required
@group_only
async def cmd_resetwelcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset welcome message to default."""
    db_update_chat_setting(update.effective_chat.id, welcome_text=None)
    await update.message.reply_text(
        TPL.success(f"👋 {ST.bold_fancy('Welcome message reset to default!')}"),
        parse_mode="HTML"
    )


@admin_required
@group_only
async def cmd_showwelcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Preview the current welcome message."""
    chat = update.effective_chat
    user = update.effective_user

    session = get_db()
    try:
        db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
        welcome_text = db_chat.welcome_text if db_chat else None
        welcome_media = db_chat.welcome_media if db_chat else None
    finally:
        close_db(session)

    if not welcome_text:
        welcome_text = "(Default welcome message will be used)"

    formatted = format_welcome_text(welcome_text, user, chat)

    await update.message.reply_text(
        f"👁 {ST.bold_fancy('Welcome Message Preview')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"{formatted}\n\n"
        f"{TPL.SEPARATOR}\n"
        f"✧ {ST.bold_fancy('Has media')}: {'Yes' if welcome_media else 'No'}",
        parse_mode="HTML"
    )


@admin_required
@group_only
async def cmd_setwelcomemedia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set welcome media (reply to photo/gif/video/sticker)."""
    message = update.message

    if not message.reply_to_message:
        await message.reply_text(
            f"🖼 {ST.bold_fancy('Set Welcome Media')}\n"
            f"✧ {ST.bold_fancy('Usage')}: Reply to a photo/gif/video/sticker with /setwelcomemedia",
            parse_mode="HTML"
        )
        return

    reply = message.reply_to_message
    media_id = None
    media_type = None

    if reply.photo:
        media_id = reply.photo[-1].file_id
        media_type = "photo"
    elif reply.animation:
        media_id = reply.animation.file_id
        media_type = "gif"
    elif reply.video:
        media_id = reply.video.file_id
        media_type = "video"
    elif reply.sticker:
        media_id = reply.sticker.file_id
        media_type = "sticker"
    else:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('Please reply to a photo, gif, video, or sticker!')}"),
            parse_mode="HTML"
        )
        return

    session = get_db()
    try:
        db_chat = session.query(DBChat).filter(DBChat.chat_id == update.effective_chat.id).first()
        if db_chat:
            db_chat.welcome_media = media_id
            db_chat.welcome_media_type = media_type
            session.commit()
    except Exception:
        session.rollback()
    finally:
        close_db(session)

    await message.reply_text(
        TPL.success(f"🖼 {ST.bold_fancy(f'Welcome media set! Type: {media_type}')}"),
        parse_mode="HTML"
    )


@admin_required
@group_only
async def cmd_resetwelcomemedia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove welcome media."""
    session = get_db()
    try:
        db_chat = session.query(DBChat).filter(DBChat.chat_id == update.effective_chat.id).first()
        if db_chat:
            db_chat.welcome_media = None
            db_chat.welcome_media_type = None
            session.commit()
    except Exception:
        session.rollback()
    finally:
        close_db(session)

    await update.message.reply_text(
        TPL.success(f"🖼 {ST.bold_fancy('Welcome media removed!')}"),
        parse_mode="HTML"
    )


# ─────────────────────────────────────────────
#  6.3  GOODBYE HANDLER
# ─────────────────────────────────────────────

async def handle_goodbye(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle member leave and send goodbye message."""
    message = update.message
    if not message or not message.left_chat_member:
        return

    chat = update.effective_chat
    left_member = message.left_chat_member

    if chat.type == ChatType.PRIVATE:
        return

    if left_member.is_bot:
        return

    session = get_db()
    try:
        db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
        if not db_chat:
            return

        goodbye_enabled = getattr(db_chat, 'goodbye_enabled', False)
        if not goodbye_enabled:
            return

        goodbye_text = getattr(db_chat, 'goodbye_text', None)
    finally:
        close_db(session)

    if not goodbye_text:
        goodbye_text = (
            f"👋 {ST.bold_fancy('Goodbye')} {{mention}}!\n"
            f"✧ {ST.bold_fancy('We will miss you in')} {{chat_title}} 😢"
        )

    formatted = format_welcome_text(goodbye_text, left_member, chat)

    try:
        await context.bot.send_message(
            chat.id,
            formatted,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Goodbye message error: {e}")


@admin_required
@group_only
async def cmd_goodbye(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Configure goodbye message."""
    args = update.message.text.split(None, 1)
    chat_id = update.effective_chat.id

    if len(args) < 2:
        session = get_db()
        try:
            db_chat = session.query(DBChat).filter(DBChat.chat_id == chat_id).first()
            enabled = getattr(db_chat, 'goodbye_enabled', False) if db_chat else False
        finally:
            close_db(session)

        await update.message.reply_text(
            f"👋 {ST.bold_fancy('Goodbye Settings')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Status')}: {'ON ✅' if enabled else 'OFF ❌'}\n"
            f"✧ /goodbye on/off\n"
            f"✧ /setgoodbye &lt;text&gt;\n"
            f"✧ /resetgoodbye\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
        return

    action = args[1].lower()
    if action in ("on", "yes", "1"):
        db_update_chat_setting(chat_id, goodbye_enabled=True)
        await update.message.reply_text(
            TPL.success(f"👋 {ST.bold_fancy('Goodbye messages enabled!')}"),
            parse_mode="HTML"
        )
    elif action in ("off", "no", "0"):
        db_update_chat_setting(chat_id, goodbye_enabled=False)
        await update.message.reply_text(
            TPL.success(f"👋 {ST.bold_fancy('Goodbye messages disabled!')}"),
            parse_mode="HTML"
        )


@admin_required
@group_only
async def cmd_setgoodbye(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set custom goodbye text."""
    args = update.message.text.split(None, 1)
    if len(args) < 2:
        await update.message.reply_text(
            f"✧ {ST.bold_fancy('Usage')}: /setgoodbye &lt;text&gt;\n"
            f"✧ Same placeholders as welcome: {{first_name}}, {{mention}}, etc.",
            parse_mode="HTML"
        )
        return

    db_update_chat_setting(update.effective_chat.id, goodbye_text=args[1])
    await update.message.reply_text(
        TPL.success(f"👋 {ST.bold_fancy('Goodbye message updated!')}"),
        parse_mode="HTML"
    )


@admin_required
@group_only
async def cmd_resetgoodbye(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset goodbye message to default."""
    db_update_chat_setting(update.effective_chat.id, goodbye_text=None)
    await update.message.reply_text(
        TPL.success(f"👋 {ST.bold_fancy('Goodbye message reset!')}"),
        parse_mode="HTML"
    )


# ─────────────────────────────────────────────
#  6.4  CAPTCHA CONFIGURATION
# ─────────────────────────────────────────────

@admin_required
@group_only
async def cmd_captcha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Configure CAPTCHA system."""
    args = update.message.text.split()
    chat_id = update.effective_chat.id

    if len(args) < 2:
        session = get_db()
        try:
            db_chat = session.query(DBChat).filter(DBChat.chat_id == chat_id).first()
            enabled = getattr(db_chat, 'captcha_enabled', False) if db_chat else False
            c_type = getattr(db_chat, 'captcha_type', 'button') if db_chat else 'button'
        finally:
            close_db(session)

        await update.message.reply_text(
            f"🔒 {ST.bold_fancy('CAPTCHA Settings')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"╔═══[ {ST.bold_fancy('Configuration')} ]═════╗\n"
            f"║ ✧ {ST.bold_fancy('Status')}: {'ON ✅' if enabled else 'OFF ❌'}\n"
            f"║ ✧ {ST.bold_fancy('Type')}: {c_type}\n"
            f"║ ✧ {ST.bold_fancy('Timeout')}: 5 minutes\n"
            f"╚════════════════╝\n\n"
            f"⚙️ {ST.bold_fancy('Commands')}:\n"
            f"  • /captcha on/off\n"
            f"  • /captchatype &lt;button/math&gt;\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
        return

    action = args[1].lower()
    if action in ("on", "yes", "1"):
        db_update_chat_setting(chat_id, captcha_enabled=True)
        await update.message.reply_text(
            TPL.success(f"🔒 {ST.bold_fancy('CAPTCHA enabled! New members must verify.')}"),
            parse_mode="HTML"
        )
    elif action in ("off", "no", "0"):
        db_update_chat_setting(chat_id, captcha_enabled=False)
        await update.message.reply_text(
            TPL.success(f"🔒 {ST.bold_fancy('CAPTCHA disabled!')}"),
            parse_mode="HTML"
        )


@admin_required
@group_only
async def cmd_captchatype(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set captcha type. Usage: /captchatype &lt;button/math&gt;"""
    args = update.message.text.split()
    if len(args) < 2 or args[1].lower() not in ("button", "math"):
        await update.message.reply_text(
            f"🔒 {ST.bold_fancy('Captcha Types')}:\n"
            f"  • button — Click 'I am Human' button\n"
            f"  • math — Solve a math problem\n"
            f"✧ {ST.bold_fancy('Usage')}: /captchatype &lt;button/math&gt;",
            parse_mode="HTML"
        )
        return

    c_type = args[1].lower()
    db_update_chat_setting(update.effective_chat.id, captcha_type=c_type)
    await update.message.reply_text(
        TPL.success(f"🔒 {ST.bold_fancy(f'Captcha type set to: {c_type}')}"),
        parse_mode="HTML"
    )


# ═══════════════════════════════════════════════════════════════
# ██╗  SECTION 7: NOTES / FILTERS / CUSTOM COMMANDS
# ═══════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────
#  7.1  NOTES SYSTEM
# ─────────────────────────────────────────────

@disabled_check
async def cmd_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save a note. Usage: /save &lt;name&gt; &lt;content&gt; or reply with /save &lt;name&gt;"""
    message = update.message
    chat = update.effective_chat
    user = update.effective_user
    args = message.text.split(None, 2)

    # Only admins can save notes
    if not await is_admin(update, user.id):
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('Only admins can save notes!')}"),
            parse_mode="HTML"
        )
        return

    if len(args) < 2:
        await message.reply_text(
            f"📝 {ST.bold_fancy('Save Note')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Usage')}: /save &lt;name&gt; &lt;text&gt;\n"
            f"✧ {ST.bold_fancy('Or')}: Reply to a message with /save &lt;name&gt;\n"
            f"✧ {ST.bold_fancy('Get')}: /get &lt;name&gt; or #name\n"
            f"✧ {ST.bold_fancy('List')}: /notes\n"
            f"✧ {ST.bold_fancy('Delete')}: /clear &lt;name&gt;\n\n"
            f"📌 {ST.bold_fancy('Formatting Variables')}:\n"
            f"  • {{first}} - User first name\n"
            f"  • {{last}} - User last name\n"
            f"  • {{fullname}} - Full name\n"
            f"  • {{username}} - Username\n"
            f"  • {{id}} - User ID\n"
            f"  • {{chatname}} - Chat name\n"
            f"  • {{mention}} - Mention user\n"
            f"  • {{count}} - Member count\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
        return

    note_name = args[1].lower().strip().replace("#", "")
    note_content = None
    note_media = None
    note_media_type = None
    note_buttons = None

    # ── Extract content from reply or args ──
    if message.reply_to_message:
        reply = message.reply_to_message
        note_content = reply.text_html or reply.caption_html or reply.text or reply.caption or ""

        # Detect media type
        if reply.photo:
            note_media = reply.photo[-1].file_id
            note_media_type = "photo"
        elif reply.animation:
            note_media = reply.animation.file_id
            note_media_type = "animation"
        elif reply.video:
            note_media = reply.video.file_id
            note_media_type = "video"
        elif reply.audio:
            note_media = reply.audio.file_id
            note_media_type = "audio"
        elif reply.voice:
            note_media = reply.voice.file_id
            note_media_type = "voice"
        elif reply.video_note:
            note_media = reply.video_note.file_id
            note_media_type = "video_note"
        elif reply.document:
            note_media = reply.document.file_id
            note_media_type = "document"
        elif reply.sticker:
            note_media = reply.sticker.file_id
            note_media_type = "sticker"

        # Additional text from command args
        if len(args) > 2:
            extra_text = args[2]
            if note_content:
                note_content = note_content + "\n" + extra_text
            else:
                note_content = extra_text

    elif len(args) > 2:
        note_content = args[2]
    else:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('Please provide content or reply to a message!')}"),
            parse_mode="HTML"
        )
        return

    # ── Parse inline buttons from content ──
    # Format: [button text](buttonurl://link)
    if note_content:
        note_content, note_buttons = parse_note_buttons(note_content)

    # ── Save to database ──
    session = get_db()
    try:
        existing = session.query(DBNote).filter(
            DBNote.chat_id == chat.id,
            DBNote.name == note_name
        ).first()

        if existing:
            existing.content = note_content
            existing.media_id = note_media
            existing.media_type = note_media_type
            existing.buttons = json.dumps(note_buttons) if note_buttons else None
            existing.updated_by = user.id
            existing.updated_at = datetime.datetime.utcnow()
        else:
            note = DBNote(
                chat_id=chat.id,
                name=note_name,
                content=note_content,
                media_id=note_media,
                media_type=note_media_type,
                buttons=json.dumps(note_buttons) if note_buttons else None,
                created_by=user.id,
                updated_by=user.id
            )
            session.add(note)

        session.commit()

        media_info = ""
        if note_media_type:
            media_info = f"\n✧ {ST.bold_fancy('Media')}: {note_media_type.upper()} attached"

        btn_info = ""
        if note_buttons:
            btn_info = f"\n✧ {ST.bold_fancy('Buttons')}: {len(note_buttons)} button(s)"

        await message.reply_text(
            f"📝 {ST.bold_fancy('Note Saved!')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"╔═══[ {ST.bold_fancy('Note Info')} ]═════╗\n"
            f"║ ✧ {ST.bold_fancy('Name')}: #{note_name}\n"
            f"║ ✧ {ST.bold_fancy('By')}: {get_user_link(user)}{media_info}{btn_info}\n"
            f"╚════════════════╝\n\n"
            f"✧ {ST.bold_fancy('Get it')}: <code>/get {note_name}</code> or <code>#{note_name}</code>\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )

    except Exception as e:
        session.rollback()
        logger.error(f"Error saving note: {e}")
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error saving note: {e}')}"),
            parse_mode="HTML"
        )
    finally:
        close_db(session)


def parse_note_buttons(text: str):
    """Parse inline buttons from note text.
    Format: [Button Text](buttonurl://https://example.com)
    Same row: [Button](buttonurl://link:same)
    """
    button_pattern = re.compile(
        r'\[(.+?)\]\(buttonurl://(.+?)\)',
        re.IGNORECASE
    )

    buttons = []
    matches = button_pattern.findall(text)

    for btn_text, btn_url in matches:
        same_row = False
        if btn_url.endswith(":same"):
            btn_url = btn_url[:-5]
            same_row = True

        buttons.append({
            "text": btn_text.strip(),
            "url": btn_url.strip(),
            "same_row": same_row
        })

    # Remove button markup from text
    cleaned_text = button_pattern.sub("", text).strip()

    return cleaned_text, buttons if buttons else None


def build_note_keyboard(buttons_json: str) -> InlineKeyboardMarkup:
    """Build InlineKeyboardMarkup from saved buttons JSON."""
    if not buttons_json:
        return None

    try:
        buttons = json.loads(buttons_json)
    except (json.JSONDecodeError, TypeError):
        return None

    if not buttons:
        return None

    keyboard_rows = []
    current_row = []

    for btn in buttons:
        button = InlineKeyboardButton(
            text=btn.get("text", "Button"),
            url=btn.get("url", "https://t.me")
        )

        if btn.get("same_row") and current_row:
            current_row.append(button)
        else:
            if current_row:
                keyboard_rows.append(current_row)
            current_row = [button]

    if current_row:
        keyboard_rows.append(current_row)

    return InlineKeyboardMarkup(keyboard_rows) if keyboard_rows else None


def format_note_text(text: str, user, chat) -> str:
    """Replace formatting variables in note text."""
    if not text:
        return ""

    first = user.first_name if user else "User"
    last = user.last_name or ""
    fullname = f"{first} {last}".strip()
    username = f"@{user.username}" if user and user.username else "NoUsername"
    user_id = str(user.id) if user else "0"
    chatname = chat.title if chat and chat.title else "Private"
    mention = f'<a href="tg://user?id={user.id}">{escape_html(first)}</a>' if user else "User"

    replacements = {
        "{first}": escape_html(first),
        "{last}": escape_html(last),
        "{fullname}": escape_html(fullname),
        "{username}": escape_html(username),
        "{id}": user_id,
        "{chatname}": escape_html(chatname),
        "{mention}": mention,
        "{count}": "N/A",  # Will be replaced if possible
        "{rules}": "/rules",  # HTML-safe - no angle brackets
    }

    result = text
    for key, value in replacements.items():
        result = result.replace(key, value)

    return result


async def send_note(chat_id: int, note, user, chat, context: ContextTypes.DEFAULT_TYPE,
                    reply_to_message_id: int = None):
    """Send a saved note with proper formatting, media, and buttons."""
    content = format_note_text(note.content or "", user, chat)
    keyboard = build_note_keyboard(note.buttons) if note.buttons else None

    try:
        if note.media_id and note.media_type:
            # ── Send with media ──
            if note.media_type == "photo":
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=note.media_id,
                    caption=content[:1024] if content else None,
                    parse_mode="HTML",
                    reply_markup=keyboard,
                    reply_to_message_id=reply_to_message_id
                )
            elif note.media_type == "animation":
                await context.bot.send_animation(
                    chat_id=chat_id,
                    animation=note.media_id,
                    caption=content[:1024] if content else None,
                    parse_mode="HTML",
                    reply_markup=keyboard,
                    reply_to_message_id=reply_to_message_id
                )
            elif note.media_type == "video":
                await context.bot.send_video(
                    chat_id=chat_id,
                    video=note.media_id,
                    caption=content[:1024] if content else None,
                    parse_mode="HTML",
                    reply_markup=keyboard,
                    reply_to_message_id=reply_to_message_id
                )
            elif note.media_type == "audio":
                await context.bot.send_audio(
                    chat_id=chat_id,
                    audio=note.media_id,
                    caption=content[:1024] if content else None,
                    parse_mode="HTML",
                    reply_markup=keyboard,
                    reply_to_message_id=reply_to_message_id
                )
            elif note.media_type == "voice":
                await context.bot.send_voice(
                    chat_id=chat_id,
                    voice=note.media_id,
                    caption=content[:1024] if content else None,
                    parse_mode="HTML",
                    reply_markup=keyboard,
                    reply_to_message_id=reply_to_message_id
                )
            elif note.media_type == "video_note":
                await context.bot.send_video_note(
                    chat_id=chat_id,
                    video_note=note.media_id,
                    reply_markup=keyboard,
                    reply_to_message_id=reply_to_message_id
                )
            elif note.media_type == "document":
                await context.bot.send_document(
                    chat_id=chat_id,
                    document=note.media_id,
                    caption=content[:1024] if content else None,
                    parse_mode="HTML",
                    reply_markup=keyboard,
                    reply_to_message_id=reply_to_message_id
                )
            elif note.media_type == "sticker":
                await context.bot.send_sticker(
                    chat_id=chat_id,
                    sticker=note.media_id,
                    reply_to_message_id=reply_to_message_id
                )
                # Send text separately if sticker + content
                if content:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=content,
                        parse_mode="HTML",
                        reply_markup=keyboard,
                        reply_to_message_id=reply_to_message_id
                    )
            else:
                # Fallback: send as document
                await context.bot.send_document(
                    chat_id=chat_id,
                    document=note.media_id,
                    caption=content[:1024] if content else None,
                    parse_mode="HTML",
                    reply_markup=keyboard,
                    reply_to_message_id=reply_to_message_id
                )
        else:
            # ── Text only ──
            if content:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=content,
                    parse_mode="HTML",
                    reply_markup=keyboard,
                    reply_to_message_id=reply_to_message_id,
                    disable_web_page_preview=True
                )
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"📝 {ST.bold_fancy('Note has no content!')}",
                    parse_mode="HTML",
                    reply_to_message_id=reply_to_message_id
                )

    except Exception as e:
        logger.error(f"Error sending note: {e}")
        # Fallback: try plain text
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=content or f"📝 {ST.bold_fancy('Error sending note media.')}",
                parse_mode="HTML",
                reply_to_message_id=reply_to_message_id
            )
        except Exception as e2:
            logger.error(f"Fallback note send also failed: {e2}")


@disabled_check
async def cmd_get(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get a saved note. Usage: /get &lt;name&gt; or #name"""
    message = update.message
    chat = update.effective_chat
    user = update.effective_user

    # Parse note name
    text = message.text or ""
    if text.startswith("#"):
        note_name = text[1:].split()[0].lower().strip()
    else:
        args = text.split(None, 1)
        if len(args) < 2:
            await message.reply_text(
                f"📝 {ST.bold_fancy('Get Note')}\n"
                f"{TPL.SEPARATOR}\n\n"
                f"✧ {ST.bold_fancy('Usage')}: /get &lt;note_name&gt;\n"
                f"✧ {ST.bold_fancy('Or')}: #note_name\n"
                f"✧ {ST.bold_fancy('List')}: /notes\n"
                f"{TPL.mini_footer()}",
                parse_mode="HTML"
            )
            return
        note_name = args[1].lower().strip().replace("#", "")

    # Fetch from DB
    session = get_db()
    try:
        note = session.query(DBNote).filter(
            DBNote.chat_id == chat.id,
            DBNote.name == note_name
        ).first()

        if not note:
            # Try fuzzy search
            all_notes = session.query(DBNote.name).filter(
                DBNote.chat_id == chat.id
            ).all()

            suggestions = []
            for (n,) in all_notes:
                if note_name in n or n in note_name:
                    suggestions.append(n)

            suggest_text = ""
            if suggestions:
                suggest_text = (
                    f"\n\n💡 {ST.bold_fancy('Did you mean')}:\n"
                    + "\n".join(f"  • #{s}" for s in suggestions[:5])
                )

            await message.reply_text(
                f"❌ {ST.bold_fancy(f'Note \"{note_name}\" not found!')}"
                f"{suggest_text}\n\n"
                f"✧ {ST.bold_fancy('Use')} /notes {ST.bold_fancy('to see all notes')}",
                parse_mode="HTML"
            )
            return

        # Send the note
        reply_to = message.reply_to_message.message_id if message.reply_to_message else message.message_id
        await send_note(chat.id, note, user, chat, context, reply_to_message_id=reply_to)

    except Exception as e:
        logger.error(f"Error getting note: {e}")
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )
    finally:
        close_db(session)


async def hashtag_note_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle #notename messages to fetch notes."""
    message = update.message
    if not message or not message.text:
        return

    text = message.text.strip()
    if not text.startswith("#"):
        return

    chat = update.effective_chat
    if chat.type == ChatType.PRIVATE:
        return

    # Extract note name after #
    note_name = text[1:].split()[0].lower().strip()
    if not note_name:
        return

    # Check if note exists
    session = get_db()
    try:
        note = session.query(DBNote).filter(
            DBNote.chat_id == chat.id,
            DBNote.name == note_name
        ).first()

        if note:
            user = update.effective_user
            reply_to = message.reply_to_message.message_id if message.reply_to_message else message.message_id
            await send_note(chat.id, note, user, chat, context, reply_to_message_id=reply_to)
    except Exception as e:
        logger.error(f"Hashtag note error: {e}")
    finally:
        close_db(session)


@disabled_check
async def cmd_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all saved notes in the chat."""
    chat = update.effective_chat

    session = get_db()
    try:
        notes = session.query(DBNote).filter(
            DBNote.chat_id == chat.id
        ).order_by(DBNote.name).all()

        if not notes:
            await update.message.reply_text(
                f"📝 {ST.bold_fancy('No notes saved in this chat!')}\n\n"
                f"✧ {ST.bold_fancy('Use')}: /save &lt;name&gt; &lt;text&gt; to save a note",
                parse_mode="HTML"
            )
            return

        text = (
            f"📝 {ST.bold_fancy('Notes List')}\n"
            f"{TPL.SEPARATOR}\n"
            f"✧ {ST.bold_fancy('Chat')}: {escape_html(chat.title or 'Unknown')}\n\n"
        )

        for i, note in enumerate(notes, 1):
            media_icon = ""
            if note.media_type:
                media_icons = {
                    "photo": "🖼",
                    "animation": "🎞",
                    "video": "🎬",
                    "audio": "🎵",
                    "voice": "🎤",
                    "video_note": "📹",
                    "document": "📎",
                    "sticker": "🎨"
                }
                media_icon = media_icons.get(note.media_type, "📁") + " "

            btn_icon = "🔘 " if note.buttons else ""

            text += f"  {i}. {media_icon}{btn_icon}<code>#{note.name}</code>\n"

        text += (
            f"\n{ST.bold_fancy('Total')}: {len(notes)} note(s)\n"
            f"✧ {ST.bold_fancy('Get')}: /get &lt;name&gt; or #name\n"
            f"{TPL.mini_footer()}"
        )

        # Add button to get notes in PM
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                text=f"📝 {ST.bold_fancy('Get Notes in PM')}",
                callback_data=f"notes_pm_{chat.id}"
            )]
        ])

        await update.message.reply_text(
            text, parse_mode="HTML", reply_markup=keyboard
        )

    finally:
        close_db(session)


async def notes_pm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send notes list to user's PM."""
    query = update.callback_query
    data = query.data

    if not data.startswith("notes_pm_"):
        return

    chat_id = int(data.split("_")[2])
    user = query.from_user

    session = get_db()
    try:
        notes = session.query(DBNote).filter(
            DBNote.chat_id == chat_id
        ).order_by(DBNote.name).all()

        if not notes:
            await query.answer("No notes found!", show_alert=True)
            return

        text = (
            f"📝 {ST.bold_fancy('Notes List')}\n"
            f"{TPL.SEPARATOR}\n\n"
        )

        for i, note in enumerate(notes, 1):
            preview = ""
            if note.content:
                preview = note.content[:50] + "..." if len(note.content) > 50 else note.content
                preview = escape_html(preview)
            text += f"  {i}. <code>#{note.name}</code>\n     └ {preview or 'Media note'}\n"

        text += f"\n{TPL.mini_footer()}"

        try:
            await context.bot.send_message(
                chat_id=user.id,
                text=text,
                parse_mode="HTML"
            )
            await query.answer("✅ Notes sent to your PM!")
        except Exception:
            await query.answer("❌ Please start the bot in PM first!", show_alert=True)

    finally:
        close_db(session)


@admin_required
@group_only
async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete a saved note. Usage: /clear &lt;name&gt;"""
    message = update.message
    chat = update.effective_chat
    args = message.text.split(None, 1)

    if len(args) < 2:
        await message.reply_text(
            f"🗑 {ST.bold_fancy('Usage')}: /clear &lt;note_name&gt;\n"
            f"✧ {ST.bold_fancy('Delete all')}: /clearall",
            parse_mode="HTML"
        )
        return

    note_name = args[1].lower().strip().replace("#", "")

    session = get_db()
    try:
        deleted = session.query(DBNote).filter(
            DBNote.chat_id == chat.id,
            DBNote.name == note_name
        ).delete()
        session.commit()

        if deleted:
            await message.reply_text(
                TPL.success(f"🗑 {ST.bold_fancy(f'Note \"{note_name}\" deleted!')}"),
                parse_mode="HTML"
            )
        else:
            await message.reply_text(
                TPL.error(f"{ST.bold_fancy(f'Note \"{note_name}\" not found!')}"),
                parse_mode="HTML"
            )
    except Exception:
        session.rollback()
    finally:
        close_db(session)


@admin_required
@group_only
async def cmd_clearall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete ALL notes in the chat. Usage: /clearall"""
    chat = update.effective_chat

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text="⚠️ Yes, delete ALL notes",
                callback_data=f"clearallnotes_yes_{chat.id}"
            ),
            InlineKeyboardButton(
                text="❌ Cancel",
                callback_data="clearallnotes_no"
            )
        ]
    ])

    await update.message.reply_text(
        f"⚠️ {ST.bold_fancy('Are you sure?')}\n\n"
        f"This will delete ALL saved notes in this chat.\n"
        f"This action cannot be undone!",
        parse_mode="HTML",
        reply_markup=keyboard
    )


async def clearall_notes_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle clearall notes confirmation."""
    query = update.callback_query
    data = query.data
    user = query.from_user

    if data.startswith("clearallnotes_yes_"):
        chat_id = int(data.split("_")[2])

        if not await is_admin(update, user.id):
            await query.answer("❌ Only admins!", show_alert=True)
            return

        session = get_db()
        try:
            count = session.query(DBNote).filter(
                DBNote.chat_id == chat_id
            ).delete()
            session.commit()

            await query.message.edit_text(
                TPL.success(f"🗑 {ST.bold_fancy(f'Deleted {count} note(s)!')}"),
                parse_mode="HTML"
            )
        except Exception:
            session.rollback()
            await query.answer("❌ Error!", show_alert=True)
        finally:
            close_db(session)

    elif data == "clearallnotes_no":
        await query.message.edit_text(
            f"✅ {ST.bold_fancy('Cancelled. Notes are safe!')}",
            parse_mode="HTML"
        )


@admin_required
@group_only
async def cmd_privatenotes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle sending notes in PM. Usage: /privatenotes on/off"""
    args = update.message.text.split()
    chat = update.effective_chat

    if len(args) < 2:
        session = get_db()
        try:
            db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
            status = "ON" if (db_chat and db_chat.private_notes) else "OFF"
        finally:
            close_db(session)

        await update.message.reply_text(
            f"📝 {ST.bold_fancy('Private Notes')}: {status}\n"
            f"✧ {ST.bold_fancy('Usage')}: /privatenotes on/off\n"
            f"✧ {ST.bold_fancy('When ON')}: Notes are sent in PM",
            parse_mode="HTML"
        )
        return

    action = args[1].lower()
    if action in ("on", "yes", "1"):
        db_update_chat_setting(chat.id, private_notes=True)
        await update.message.reply_text(
            TPL.success(f"📝 {ST.bold_fancy('Notes will be sent in PM!')}"),
            parse_mode="HTML"
        )
    elif action in ("off", "no", "0"):
        db_update_chat_setting(chat.id, private_notes=False)
        await update.message.reply_text(
            TPL.success(f"📝 {ST.bold_fancy('Notes will be sent in the group!')}"),
            parse_mode="HTML"
        )


# ─────────────────────────────────────────────
#  7.2  FILTERS SYSTEM (Auto-Reply / Triggers)
# ─────────────────────────────────────────────

@admin_required
@group_only
async def cmd_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a custom filter/trigger. 
    Usage: /filter &lt;keyword&gt; &lt;reply text&gt;
    Or reply to a message with /filter &lt;keyword&gt;
    """
    message = update.message
    chat = update.effective_chat
    user = update.effective_user
    args = message.text.split(None, 2)

    if len(args) < 2:
        await message.reply_text(
            f"🔍 {ST.bold_fancy('Add Filter')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Usage')}: /filter &lt;keyword&gt; &lt;reply&gt;\n"
            f"✧ {ST.bold_fancy('Or')}: Reply to a message with /filter &lt;keyword&gt;\n"
            f"✧ {ST.bold_fancy('List')}: /filters\n"
            f"✧ {ST.bold_fancy('Delete')}: /stop &lt;keyword&gt;\n\n"
            f"📌 {ST.bold_fancy('Advanced')}:\n"
            f"  • Multiple words: /filter \"hello world\" response\n"
            f"  • With buttons: Add [text](buttonurl://link)\n"
            f"  • Variables: {{first}}, {{username}}, etc.\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
        return

    # Parse keyword (support quoted keywords)
    remaining_text = message.text.split(None, 1)[1]
    keyword = None
    filter_content = None

    if remaining_text.startswith('"'):
        # Quoted keyword
        end_quote = remaining_text.find('"', 1)
        if end_quote > 0:
            keyword = remaining_text[1:end_quote].lower().strip()
            filter_content = remaining_text[end_quote + 1:].strip() or None
        else:
            keyword = args[1].lower().strip()
            filter_content = args[2] if len(args) > 2 else None
    else:
        keyword = args[1].lower().strip()
        filter_content = args[2] if len(args) > 2 else None

    if not keyword:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('Please provide a keyword!')}"),
            parse_mode="HTML"
        )
        return

    # Extract media from reply
    filter_media = None
    filter_media_type = None
    filter_buttons = None

    if message.reply_to_message:
        reply = message.reply_to_message
        if not filter_content:
            filter_content = reply.text_html or reply.caption_html or reply.text or reply.caption or ""

        if reply.photo:
            filter_media = reply.photo[-1].file_id
            filter_media_type = "photo"
        elif reply.animation:
            filter_media = reply.animation.file_id
            filter_media_type = "animation"
        elif reply.video:
            filter_media = reply.video.file_id
            filter_media_type = "video"
        elif reply.audio:
            filter_media = reply.audio.file_id
            filter_media_type = "audio"
        elif reply.voice:
            filter_media = reply.voice.file_id
            filter_media_type = "voice"
        elif reply.document:
            filter_media = reply.document.file_id
            filter_media_type = "document"
        elif reply.sticker:
            filter_media = reply.sticker.file_id
            filter_media_type = "sticker"

    if not filter_content and not filter_media:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('Please provide a reply text or media!')}"),
            parse_mode="HTML"
        )
        return

    # Parse buttons
    if filter_content:
        filter_content, filter_buttons = parse_note_buttons(filter_content)

    # Save to DB
    session = get_db()
    try:
        existing = session.query(DBFilter).filter(
            DBFilter.chat_id == chat.id,
            DBFilter.keyword == keyword
        ).first()

        if existing:
            existing.content = filter_content
            existing.media_id = filter_media
            existing.media_type = filter_media_type
            existing.buttons = json.dumps(filter_buttons) if filter_buttons else None
            existing.updated_by = user.id
        else:
            db_filter = DBFilter(
                chat_id=chat.id,
                keyword=keyword,
                content=filter_content,
                media_id=filter_media,
                media_type=filter_media_type,
                buttons=json.dumps(filter_buttons) if filter_buttons else None,
                created_by=user.id
            )
            session.add(db_filter)

        session.commit()

        await message.reply_text(
            f"🔍 {ST.bold_fancy('Filter Saved!')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"╔═══[ {ST.bold_fancy('Filter Info')} ]═════╗\n"
            f"║ ✧ {ST.bold_fancy('Keyword')}: <code>{escape_html(keyword)}</code>\n"
            f"║ ✧ {ST.bold_fancy('By')}: {get_user_link(user)}\n"
            f"║ ✧ {ST.bold_fancy('Media')}: {filter_media_type or 'None'}\n"
            f"╚════════════════╝\n\n"
            f"✧ {ST.bold_fancy('I will now reply when someone says')}: \"{escape_html(keyword)}\"\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )

    except Exception as e:
        session.rollback()
        logger.error(f"Error saving filter: {e}")
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )
    finally:
        close_db(session)


@disabled_check
async def cmd_filters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all filters in the chat."""
    chat = update.effective_chat

    session = get_db()
    try:
        filters = session.query(DBFilter).filter(
            DBFilter.chat_id == chat.id
        ).order_by(DBFilter.keyword).all()

        if not filters:
            await update.message.reply_text(
                f"🔍 {ST.bold_fancy('No filters in this chat!')}\n\n"
                f"✧ {ST.bold_fancy('Use')}: /filter &lt;keyword&gt; &lt;reply&gt;",
                parse_mode="HTML"
            )
            return

        text = (
            f"🔍 {ST.bold_fancy('Filters List')}\n"
            f"{TPL.SEPARATOR}\n"
            f"✧ {ST.bold_fancy('Chat')}: {escape_html(chat.title or 'Unknown')}\n\n"
        )

        for i, f in enumerate(filters, 1):
            media_icon = ""
            if f.media_type:
                media_icons = {
                    "photo": "🖼", "animation": "🎞", "video": "🎬",
                    "audio": "🎵", "voice": "🎤", "document": "📎",
                    "sticker": "🎨"
                }
                media_icon = " " + media_icons.get(f.media_type, "📁")

            text += f"  {i}. <code>{escape_html(f.keyword)}</code>{media_icon}\n"

        text += (
            f"\n{ST.bold_fancy('Total')}: {len(filters)} filter(s)\n"
            f"✧ {ST.bold_fancy('Delete')}: /stop &lt;keyword&gt;\n"
            f"{TPL.mini_footer()}"
        )

        await update.message.reply_text(text, parse_mode="HTML")
    finally:
        close_db(session)


@admin_required
@group_only
async def cmd_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove a filter. Usage: /stop &lt;keyword&gt;"""
    message = update.message
    chat = update.effective_chat
    args = message.text.split(None, 1)

    if len(args) < 2:
        await message.reply_text(
            f"🗑 {ST.bold_fancy('Usage')}: /stop &lt;keyword&gt;\n"
            f"✧ {ST.bold_fancy('Remove all')}: /stopall",
            parse_mode="HTML"
        )
        return

    keyword = args[1].lower().strip().replace('"', '')

    session = get_db()
    try:
        deleted = session.query(DBFilter).filter(
            DBFilter.chat_id == chat.id,
            DBFilter.keyword == keyword
        ).delete()
        session.commit()

        if deleted:
            await message.reply_text(
                TPL.success(f"🗑 {ST.bold_fancy(f'Filter \"{keyword}\" removed!')}"),
                parse_mode="HTML"
            )
        else:
            await message.reply_text(
                TPL.error(f"{ST.bold_fancy(f'Filter \"{keyword}\" not found!')}"),
                parse_mode="HTML"
            )
    except Exception:
        session.rollback()
    finally:
        close_db(session)


@admin_required
@group_only
async def cmd_stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove ALL filters. Usage: /stopall"""
    chat = update.effective_chat

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text="⚠️ Yes, delete ALL filters",
                callback_data=f"stopall_yes_{chat.id}"
            ),
            InlineKeyboardButton(
                text="❌ Cancel",
                callback_data="stopall_no"
            )
        ]
    ])

    await update.message.reply_text(
        f"⚠️ {ST.bold_fancy('Are you sure?')}\n\n"
        f"This will delete ALL filters in this chat.\n"
        f"This action cannot be undone!",
        parse_mode="HTML",
        reply_markup=keyboard
    )


async def stopall_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle stopall confirmation."""
    query = update.callback_query
    data = query.data
    user = query.from_user

    if data.startswith("stopall_yes_"):
        chat_id = int(data.split("_")[2])

        if not await is_admin(update, user.id):
            await query.answer("❌ Only admins!", show_alert=True)
            return

        session = get_db()
        try:
            count = session.query(DBFilter).filter(
                DBFilter.chat_id == chat_id
            ).delete()
            session.commit()

            await query.message.edit_text(
                TPL.success(f"🗑 {ST.bold_fancy(f'Deleted {count} filter(s)!')}"),
                parse_mode="HTML"
            )
        except Exception:
            session.rollback()
        finally:
            close_db(session)

    elif data == "stopall_no":
        await query.message.edit_text(
            f"✅ {ST.bold_fancy('Cancelled. Filters are safe!')}",
            parse_mode="HTML"
        )


async def filter_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check incoming messages against saved filters and respond."""
    message = update.message
    if not message:
        return

    text = message.text or message.caption or ""
    if not text:
        return

    chat = update.effective_chat
    if chat.type == ChatType.PRIVATE:
        return

    text_lower = text.lower()

    # Get all filters for this chat
    session = get_db()
    try:
        filters = session.query(DBFilter).filter(
            DBFilter.chat_id == chat.id
        ).all()

        if not filters:
            return

        for filt in filters:
            keyword = filt.keyword.lower()

            # ── Match types ──
            matched = False

            # Exact word match (with word boundaries)
            if len(keyword.split()) == 1:
                # Single word - check word boundary
                pattern = r'(?:^|\s|[^\w])' + re.escape(keyword) + r'(?:$|\s|[^\w])'
                if re.search(pattern, text_lower):
                    matched = True
            else:
                # Multi-word phrase - simple contains
                if keyword in text_lower:
                    matched = True

            if matched:
                # Send filter response
                user = update.effective_user
                content = format_note_text(filt.content or "", user, chat)
                keyboard = build_note_keyboard(filt.buttons) if filt.buttons else None

                try:
                    if filt.media_id and filt.media_type:
                        if filt.media_type == "photo":
                            await message.reply_photo(
                                photo=filt.media_id,
                                caption=content[:1024] if content else None,
                                parse_mode="HTML",
                                reply_markup=keyboard
                            )
                        elif filt.media_type == "animation":
                            await message.reply_animation(
                                animation=filt.media_id,
                                caption=content[:1024] if content else None,
                                parse_mode="HTML",
                                reply_markup=keyboard
                            )
                        elif filt.media_type == "video":
                            await message.reply_video(
                                video=filt.media_id,
                                caption=content[:1024] if content else None,
                                parse_mode="HTML",
                                reply_markup=keyboard
                            )
                        elif filt.media_type == "audio":
                            await message.reply_audio(
                                audio=filt.media_id,
                                caption=content[:1024] if content else None,
                                parse_mode="HTML",
                                reply_markup=keyboard
                            )
                        elif filt.media_type == "voice":
                            await message.reply_voice(
                                voice=filt.media_id,
                                caption=content[:1024] if content else None,
                                parse_mode="HTML",
                                reply_markup=keyboard
                            )
                        elif filt.media_type == "document":
                            await message.reply_document(
                                document=filt.media_id,
                                caption=content[:1024] if content else None,
                                parse_mode="HTML",
                                reply_markup=keyboard
                            )
                        elif filt.media_type == "sticker":
                            await message.reply_sticker(sticker=filt.media_id)
                        else:
                            if content:
                                await message.reply_text(
                                    content,
                                    parse_mode="HTML",
                                    reply_markup=keyboard,
                                    disable_web_page_preview=True
                                )
                    else:
                        if content:
                            await message.reply_text(
                                content,
                                parse_mode="HTML",
                                reply_markup=keyboard,
                                disable_web_page_preview=True
                            )
                except Exception as e:
                    logger.error(f"Filter response error: {e}")

                # Only respond to first matching filter
                return

    except Exception as e:
        logger.error(f"Filter handler error: {e}")
    finally:
        close_db(session)


# ─────────────────────────────────────────────
#  7.3  CUSTOM COMMANDS (/addcmd, /delcmd)
# ─────────────────────────────────────────────

@admin_required
@group_only
async def cmd_addcmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a custom command. Usage: /addcmd &lt;command&gt; &lt;response&gt;
    The command will work as /commandname
    """
    message = update.message
    chat = update.effective_chat
    user = update.effective_user
    args = message.text.split(None, 2)

    if len(args) < 3 and not message.reply_to_message:
        await message.reply_text(
            f"⚙️ {ST.bold_fancy('Add Custom Command')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Usage')}: /addcmd &lt;command&gt; &lt;response&gt;\n"
            f"✧ {ST.bold_fancy('Or')}: Reply with /addcmd &lt;command&gt;\n"
            f"✧ {ST.bold_fancy('Example')}: /addcmd hello Hello World!\n"
            f"✧ {ST.bold_fancy('List')}: /customcmds\n"
            f"✧ {ST.bold_fancy('Delete')}: /delcmd &lt;command&gt;\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
        return

    if len(args) < 2:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('Please provide a command name!')}"),
            parse_mode="HTML"
        )
        return

    cmd_name = args[1].lower().strip().lstrip("/")
    cmd_content = None
    cmd_media = None
    cmd_media_type = None

    # Reserved commands that can't be overridden
    reserved_cmds = [
        "start", "help", "settings", "ban", "unban", "mute", "unmute",
        "kick", "warn", "warns", "notes", "filters", "rules", "save",
        "get", "clear", "filter", "stop", "promote", "demote", "id",
        "info", "addcmd", "delcmd", "customcmds", "ping", "stats"
    ]

    if cmd_name in reserved_cmds:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'/{cmd_name} is a reserved command and cannot be overridden!')}"),
            parse_mode="HTML"
        )
        return

    if message.reply_to_message:
        reply = message.reply_to_message
        cmd_content = reply.text_html or reply.caption_html or reply.text or reply.caption or ""

        if reply.photo:
            cmd_media = reply.photo[-1].file_id
            cmd_media_type = "photo"
        elif reply.animation:
            cmd_media = reply.animation.file_id
            cmd_media_type = "animation"
        elif reply.video:
            cmd_media = reply.video.file_id
            cmd_media_type = "video"
        elif reply.document:
            cmd_media = reply.document.file_id
            cmd_media_type = "document"
        elif reply.sticker:
            cmd_media = reply.sticker.file_id
            cmd_media_type = "sticker"
    elif len(args) > 2:
        cmd_content = args[2]
    else:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('Please provide a response or reply to a message!')}"),
            parse_mode="HTML"
        )
        return

    # Save to DB
    session = get_db()
    try:
        existing = session.query(DBCustomCmd).filter(
            DBCustomCmd.chat_id == chat.id,
            DBCustomCmd.command == cmd_name
        ).first()

        if existing:
            existing.content = cmd_content
            existing.media_id = cmd_media
            existing.media_type = cmd_media_type
            existing.updated_by = user.id
        else:
            custom_cmd = DBCustomCmd(
                chat_id=chat.id,
                command=cmd_name,
                content=cmd_content,
                media_id=cmd_media,
                media_type=cmd_media_type,
                created_by=user.id
            )
            session.add(custom_cmd)

        session.commit()

        await message.reply_text(
            f"⚙️ {ST.bold_fancy('Custom Command Saved!')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Command')}: /{cmd_name}\n"
            f"✧ {ST.bold_fancy('By')}: {get_user_link(user)}\n"
            f"✧ {ST.bold_fancy('Use')}: /{cmd_name}\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )

    except Exception as e:
        session.rollback()
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )
    finally:
        close_db(session)


@admin_required
@group_only
async def cmd_delcmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete a custom command. Usage: /delcmd &lt;command&gt;"""
    args = update.message.text.split(None, 1)
    chat = update.effective_chat

    if len(args) < 2:
        await update.message.reply_text(
            f"🗑 {ST.bold_fancy('Usage')}: /delcmd &lt;command_name&gt;",
            parse_mode="HTML"
        )
        return

    cmd_name = args[1].lower().strip().lstrip("/")

    session = get_db()
    try:
        deleted = session.query(DBCustomCmd).filter(
            DBCustomCmd.chat_id == chat.id,
            DBCustomCmd.command == cmd_name
        ).delete()
        session.commit()

        if deleted:
            await update.message.reply_text(
                TPL.success(f"🗑 {ST.bold_fancy(f'Command /{cmd_name} deleted!')}"),
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text(
                TPL.error(f"{ST.bold_fancy(f'Command /{cmd_name} not found!')}"),
                parse_mode="HTML"
            )
    except Exception:
        session.rollback()
    finally:
        close_db(session)


@group_only
async def cmd_customcmds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all custom commands."""
    chat = update.effective_chat

    session = get_db()
    try:
        cmds = session.query(DBCustomCmd).filter(
            DBCustomCmd.chat_id == chat.id
        ).order_by(DBCustomCmd.command).all()

        if not cmds:
            await update.message.reply_text(
                f"⚙️ {ST.bold_fancy('No custom commands!')}\n\n"
                f"✧ {ST.bold_fancy('Add')}: /addcmd &lt;command&gt; &lt;response&gt;",
                parse_mode="HTML"
            )
            return

        text = (
            f"⚙️ {ST.bold_fancy('Custom Commands')}\n"
            f"{TPL.SEPARATOR}\n"
            f"✧ {ST.bold_fancy('Chat')}: {escape_html(chat.title or 'Unknown')}\n\n"
        )

        for i, cmd in enumerate(cmds, 1):
            media_icon = ""
            if cmd.media_type:
                media_icon = " 📎"
            text += f"  {i}. /{cmd.command}{media_icon}\n"

        text += (
            f"\n{ST.bold_fancy('Total')}: {len(cmds)} command(s)\n"
            f"{TPL.mini_footer()}"
        )

        await update.message.reply_text(text, parse_mode="HTML")
    finally:
        close_db(session)


async def custom_cmd_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle custom commands from messages starting with /."""
    message = update.message
    if not message or not message.text:
        return

    text = message.text.strip()
    if not text.startswith("/"):
        return

    chat = update.effective_chat
    if chat.type == ChatType.PRIVATE:
        return

    # Extract command name
    cmd_text = text.split()[0].lstrip("/").split("@")[0].lower()

    if not cmd_text:
        return

    session = get_db()
    try:
        custom = session.query(DBCustomCmd).filter(
            DBCustomCmd.chat_id == chat.id,
            DBCustomCmd.command == cmd_text
        ).first()

        if not custom:
            return

        user = update.effective_user
        content = format_note_text(custom.content or "", user, chat)

        if custom.media_id and custom.media_type:
            try:
                if custom.media_type == "photo":
                    await message.reply_photo(
                        photo=custom.media_id,
                        caption=content[:1024] if content else None,
                        parse_mode="HTML"
                    )
                elif custom.media_type == "animation":
                    await message.reply_animation(
                        animation=custom.media_id,
                        caption=content[:1024] if content else None,
                        parse_mode="HTML"
                    )
                elif custom.media_type == "video":
                    await message.reply_video(
                        video=custom.media_id,
                        caption=content[:1024] if content else None,
                        parse_mode="HTML"
                    )
                elif custom.media_type == "document":
                    await message.reply_document(
                        document=custom.media_id,
                        caption=content[:1024] if content else None,
                        parse_mode="HTML"
                    )
                elif custom.media_type == "sticker":
                    await message.reply_sticker(sticker=custom.media_id)
                else:
                    if content:
                        await message.reply_text(content, parse_mode="HTML")
            except Exception as e:
                logger.error(f"Custom cmd media error: {e}")
                if content:
                    await message.reply_text(content, parse_mode="HTML")
        else:
            if content:
                await message.reply_text(
                    content,
                    parse_mode="HTML",
                    disable_web_page_preview=True
                )

    except Exception as e:
        logger.error(f"Custom cmd handler error: {e}")
    finally:
        close_db(session)


# ─────────────────────────────────────────────
#  7.4  DISABLE / ENABLE COMMANDS
# ─────────────────────────────────────────────

# List of commands that can be disabled
DISABLEABLE_COMMANDS = [
    "notes", "filters", "get", "info", "id", "adminlist", "rules",
    "start", "help", "ping", "gbanlist", "report", "afk",
    "weather", "translate", "tts", "ud", "wiki", "quote",
    "math", "base64encode", "base64decode", "bin", "hex",
    "reverse", "tiny", "flip", "mock", "vapor", "clap",
    "emoji", "shrug", "tableflip", "unflip", "runs",
    "insult", "truth", "dare", "roll", "flip_coin",
    "slap", "hug", "pat", "wink", "poke",
    "anime", "manga", "waifu", "neko",
    "github", "pypi", "stackoverflow",
    "dog", "cat", "fox", "panda",
    "lyrics", "movie", "imdb",
    "qr", "shorturl", "paste",
    "carbon", "ss", "telegraph",
    "sticker", "getsticker", "kang",
    "tagall", "staff", "zombies",
    "welcome", "goodbye",
]


@admin_required
@group_only
async def cmd_disable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Disable a command in this chat. Usage: /disable &lt;command&gt;"""
    args = update.message.text.split()
    chat = update.effective_chat

    if len(args) < 2:
        await update.message.reply_text(
            f"🚫 {ST.bold_fancy('Disable Command')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Usage')}: /disable &lt;command&gt;\n"
            f"✧ {ST.bold_fancy('Enable')}: /enable &lt;command&gt;\n"
            f"✧ {ST.bold_fancy('List disabled')}: /disabled\n"
            f"✧ {ST.bold_fancy('Disableable cmds')}: /disableable\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
        return

    cmd_name = args[1].lower().strip().lstrip("/")

    if cmd_name not in DISABLEABLE_COMMANDS:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'/{cmd_name} cannot be disabled!')}\n"
                      f"✧ {ST.bold_fancy('See')}: /disableable"),
            parse_mode="HTML"
        )
        return

    session = get_db()
    try:
        existing = session.query(DBDisabled).filter(
            DBDisabled.chat_id == chat.id,
            DBDisabled.command == cmd_name
        ).first()

        if existing:
            await update.message.reply_text(
                TPL.info(f"{ST.bold_fancy(f'/{cmd_name} is already disabled!')}"),
                parse_mode="HTML"
            )
            return

        disabled = DBDisabled(
            chat_id=chat.id,
            command=cmd_name,
            disabled_by=update.effective_user.id
        )
        session.add(disabled)
        session.commit()

        await update.message.reply_text(
            TPL.success(f"🚫 {ST.bold_fancy(f'/{cmd_name} has been disabled!')}"),
            parse_mode="HTML"
        )

    except Exception:
        session.rollback()
    finally:
        close_db(session)


@admin_required
@group_only
async def cmd_enable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enable a disabled command. Usage: /enable &lt;command&gt;"""
    args = update.message.text.split()
    chat = update.effective_chat

    if len(args) < 2:
        await update.message.reply_text(
            f"✅ {ST.bold_fancy('Usage')}: /enable &lt;command&gt;",
            parse_mode="HTML"
        )
        return

    cmd_name = args[1].lower().strip().lstrip("/")

    session = get_db()
    try:
        deleted = session.query(DBDisabled).filter(
            DBDisabled.chat_id == chat.id,
            DBDisabled.command == cmd_name
        ).delete()
        session.commit()

        if deleted:
            await update.message.reply_text(
                TPL.success(f"✅ {ST.bold_fancy(f'/{cmd_name} has been enabled!')}"),
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text(
                TPL.info(f"{ST.bold_fancy(f'/{cmd_name} was not disabled!')}"),
                parse_mode="HTML"
            )
    except Exception:
        session.rollback()
    finally:
        close_db(session)


@admin_required
@group_only
async def cmd_disabled(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all disabled commands in this chat."""
    chat = update.effective_chat

    session = get_db()
    try:
        disabled_cmds = session.query(DBDisabled).filter(
            DBDisabled.chat_id == chat.id
        ).all()

        if not disabled_cmds:
            await update.message.reply_text(
                f"✅ {ST.bold_fancy('No commands are disabled!')}",
                parse_mode="HTML"
            )
            return

        text = (
            f"🚫 {ST.bold_fancy('Disabled Commands')}\n"
            f"{TPL.SEPARATOR}\n\n"
        )

        for i, d in enumerate(disabled_cmds, 1):
            text += f"  {i}. /{d.command}\n"

        text += (
            f"\n{ST.bold_fancy('Total')}: {len(disabled_cmds)}\n"
            f"✧ {ST.bold_fancy('Enable')}: /enable &lt;command&gt;\n"
            f"{TPL.mini_footer()}"
        )

        await update.message.reply_text(text, parse_mode="HTML")
    finally:
        close_db(session)


async def cmd_disableable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all commands that can be disabled."""
    # Split into columns
    cmds = sorted(DISABLEABLE_COMMANDS)

    text = (
        f"🚫 {ST.bold_fancy('Disableable Commands')}\n"
        f"{TPL.SEPARATOR}\n\n"
    )

    for i, cmd in enumerate(cmds, 1):
        text += f"  {i}. /{cmd}\n"

    text += (
        f"\n{ST.bold_fancy('Total')}: {len(cmds)} commands\n"
        f"✧ {ST.bold_fancy('Disable')}: /disable &lt;command&gt;\n"
        f"{TPL.mini_footer()}"
    )

    await update.message.reply_text(text, parse_mode="HTML")


# ─────────────────────────────────────────────
#  7.5  BLACKLIST WORDS
# ─────────────────────────────────────────────

@admin_required
@group_only
async def cmd_blacklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manage blacklisted words.
    Usage: /blacklist - show list
           /blacklist &lt;word&gt; - add word
    """
    message = update.message
    chat = update.effective_chat
    args = message.text.split(None, 1)

    session = get_db()
    try:
        if len(args) < 2:
            # Show blacklist
            blacklisted = session.query(DBBlacklist).filter(
                DBBlacklist.chat_id == chat.id
            ).order_by(DBBlacklist.word).all()

            if not blacklisted:
                await message.reply_text(
                    f"📋 {ST.bold_fancy('No blacklisted words!')}\n\n"
                    f"✧ {ST.bold_fancy('Add')}: /blacklist &lt;word&gt;\n"
                    f"✧ {ST.bold_fancy('Remove')}: /unblacklist &lt;word&gt;\n"
                    f"✧ {ST.bold_fancy('Action')}: /blacklistmode &lt;action&gt;",
                    parse_mode="HTML"
                )
                return

            text = (
                f"📋 {ST.bold_fancy('Blacklisted Words')}\n"
                f"{TPL.SEPARATOR}\n\n"
            )

            for i, bl in enumerate(blacklisted, 1):
                text += f"  {i}. <code>{escape_html(bl.word)}</code>\n"

            db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
            action = db_chat.blacklist_action if db_chat else "delete"

            text += (
                f"\n{ST.bold_fancy('Total')}: {len(blacklisted)} word(s)\n"
                f"✧ {ST.bold_fancy('Action')}: {action}\n"
                f"{TPL.mini_footer()}"
            )

            await message.reply_text(text, parse_mode="HTML")
            return

        # Add word(s)
        words_text = args[1].strip()
        words = [w.strip().lower() for w in words_text.split("\n") if w.strip()]

        if not words:
            words = [words_text.lower().strip()]

        added_count = 0
        for word in words:
            if not word:
                continue

            existing = session.query(DBBlacklist).filter(
                DBBlacklist.chat_id == chat.id,
                DBBlacklist.word == word
            ).first()

            if not existing:
                bl = DBBlacklist(
                    chat_id=chat.id,
                    word=word,
                    added_by=update.effective_user.id
                )
                session.add(bl)
                added_count += 1

        session.commit()

        if added_count > 0:
            await message.reply_text(
                TPL.success(
                    f"📋 {ST.bold_fancy(f'Added {added_count} word(s) to blacklist!')}\n"
                    f"✧ {ST.bold_fancy('Messages containing these words will be actioned')}"
                ),
                parse_mode="HTML"
            )
        else:
            await message.reply_text(
                TPL.info(f"{ST.bold_fancy('All words already blacklisted!')}"),
                parse_mode="HTML"
            )

    except Exception as e:
        session.rollback()
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )
    finally:
        close_db(session)


@admin_required
@group_only
async def cmd_unblacklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove a word from blacklist. Usage: /unblacklist &lt;word&gt;"""
    args = update.message.text.split(None, 1)
    chat = update.effective_chat

    if len(args) < 2:
        await update.message.reply_text(
            f"✧ {ST.bold_fancy('Usage')}: /unblacklist &lt;word&gt;",
            parse_mode="HTML"
        )
        return

    word = args[1].lower().strip()

    session = get_db()
    try:
        deleted = session.query(DBBlacklist).filter(
            DBBlacklist.chat_id == chat.id,
            DBBlacklist.word == word
        ).delete()
        session.commit()

        if deleted:
            await update.message.reply_text(
                TPL.success(f"📋 {ST.bold_fancy(f'Removed \"{word}\" from blacklist!')}"),
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text(
                TPL.error(f"{ST.bold_fancy(f'\"{word}\" not in blacklist!')}"),
                parse_mode="HTML"
            )
    except Exception:
        session.rollback()
    finally:
        close_db(session)


@admin_required
@group_only
async def cmd_blacklistmode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set blacklist action. Usage: /blacklistmode &lt;delete/warn/mute/kick/ban&gt;"""
    args = update.message.text.split()
    chat = update.effective_chat

    valid_actions = ["delete", "warn", "mute", "kick", "ban"]

    if len(args) < 2:
        session = get_db()
        try:
            db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
            action = db_chat.blacklist_action if db_chat else "delete"
        finally:
            close_db(session)

        await update.message.reply_text(
            f"📋 {ST.bold_fancy('Blacklist Mode')}: {action}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Options')}: {', '.join(valid_actions)}\n"
            f"✧ {ST.bold_fancy('Usage')}: /blacklistmode &lt;action&gt;",
            parse_mode="HTML"
        )
        return

    action = args[1].lower()
    if action not in valid_actions:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Invalid action! Use: {', '.join(valid_actions)}')}"),
            parse_mode="HTML"
        )
        return

    db_update_chat_setting(chat.id, blacklist_action=action)
    await update.message.reply_text(
        TPL.success(f"📋 {ST.bold_fancy(f'Blacklist action set to: {action}')}"),
        parse_mode="HTML"
    )


@admin_required
@group_only
async def cmd_rmblacklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove ALL blacklisted words."""
    chat = update.effective_chat

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text="⚠️ Yes, clear blacklist",
                callback_data=f"rmblacklist_yes_{chat.id}"
            ),
            InlineKeyboardButton(
                text="❌ Cancel",
                callback_data="rmblacklist_no"
            )
        ]
    ])

    await update.message.reply_text(
        f"⚠️ {ST.bold_fancy('Remove ALL blacklisted words?')}\n"
        f"This cannot be undone!",
        parse_mode="HTML",
        reply_markup=keyboard
    )


async def rmblacklist_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle remove all blacklist callback."""
    query = update.callback_query
    data = query.data
    user = query.from_user

    if data.startswith("rmblacklist_yes_"):
        chat_id = int(data.split("_")[2])

        if not await is_admin(update, user.id):
            await query.answer("❌ Only admins!", show_alert=True)
            return

        session = get_db()
        try:
            count = session.query(DBBlacklist).filter(
                DBBlacklist.chat_id == chat_id
            ).delete()
            session.commit()

            await query.message.edit_text(
                TPL.success(f"📋 {ST.bold_fancy(f'Removed {count} blacklisted word(s)!')}"),
                parse_mode="HTML"
            )
        except Exception:
            session.rollback()
        finally:
            close_db(session)

    elif data == "rmblacklist_no":
        await query.message.edit_text(
            f"✅ {ST.bold_fancy('Cancelled.')}",
            parse_mode="HTML"
        )


async def blacklist_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check messages against blacklisted words."""
    message = update.message
    if not message:
        return

    text = (message.text or message.caption or "").lower()
    if not text:
        return

    chat = update.effective_chat
    user = update.effective_user

    if not chat or not user or chat.type == ChatType.PRIVATE:
        return

    # Skip admins and approved
    if await is_admin(update, user.id) or is_approved(chat.id, user.id):
        return

    session = get_db()
    try:
        blacklisted = session.query(DBBlacklist).filter(
            DBBlacklist.chat_id == chat.id
        ).all()

        if not blacklisted:
            return

        db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
        action = db_chat.blacklist_action if db_chat else "delete"

        for bl in blacklisted:
            if bl.word.lower() in text:
                # Blacklisted word found!
                try:
                    # Always try to delete the message
                    await message.delete()
                except Exception:
                    pass

                if action == "warn":
                    # Add a warn
                    warn = DBWarn(
                        user_id=user.id,
                        chat_id=chat.id,
                        warned_by=context.bot.id,
                        reason=f"Blacklisted word: {bl.word}"
                    )
                    session.add(warn)
                    session.commit()

                    warn_count = session.query(func.count(DBWarn.id)).filter(
                        DBWarn.user_id == user.id,
                        DBWarn.chat_id == chat.id
                    ).scalar() or 0

                    warn_limit = db_chat.warn_limit if db_chat else Config.WARN_LIMIT

                    await send_and_delete(
                        chat.id,
                        f"⚠️ {get_user_link(user)} {ST.bold_fancy('warned for using blacklisted word!')}\n"
                        f"✧ {ST.bold_fancy('Warns')}: {warn_count}/{warn_limit}",
                        context, seconds=15, parse_mode="HTML"
                    )

                elif action == "mute":
                    try:
                        await chat.restrict_member(
                            user.id,
                            ChatPermissions(can_send_messages=False),
                            until_date=datetime.datetime.utcnow() + datetime.timedelta(hours=1)
                        )
                    except Exception:
                        pass
                    await send_and_delete(
                        chat.id,
                        f"🔇 {get_user_link(user)} {ST.bold_fancy('muted for blacklisted word!')}",
                        context, seconds=15, parse_mode="HTML"
                    )

                elif action == "kick":
                    try:
                        await chat.ban_member(user.id)
                        await asyncio.sleep(0.5)
                        await chat.unban_member(user.id)
                    except Exception:
                        pass
                    await send_and_delete(
                        chat.id,
                        f"👢 {get_user_link(user)} {ST.bold_fancy('kicked for blacklisted word!')}",
                        context, seconds=15, parse_mode="HTML"
                    )

                elif action == "ban":
                    try:
                        await chat.ban_member(user.id)
                    except Exception:
                        pass
                    await send_and_delete(
                        chat.id,
                        f"🔨 {get_user_link(user)} {ST.bold_fancy('banned for blacklisted word!')}",
                        context, seconds=15, parse_mode="HTML"
                    )

                # Log
                try:
                    log = DBAntiSpamLog(
                        chat_id=chat.id,
                        user_id=user.id,
                        action=f"blacklist_{action}",
                        reason=f"Used word: {bl.word}"
                    )
                    session.add(log)
                    session.commit()
                except Exception:
                    session.rollback()

                return  # Stop after first match

    except Exception as e:
        logger.error(f"Blacklist handler error: {e}")
    finally:
        close_db(session)


# ─────────────────────────────────────────────
#  7.6  BLACKLIST STICKERS
# ─────────────────────────────────────────────

@admin_required
@group_only
async def cmd_blsticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Blacklist a sticker or sticker pack.
    Usage: /blsticker &lt;pack_name&gt; or reply to sticker with /blsticker
    """
    message = update.message
    chat = update.effective_chat
    args = message.text.split(None, 1)

    sticker_id = None
    pack_name = None

    if message.reply_to_message and message.reply_to_message.sticker:
        sticker = message.reply_to_message.sticker
        sticker_id = sticker.file_unique_id
        pack_name = sticker.set_name
    elif len(args) > 1:
        pack_name = args[1].strip()
    else:
        await message.reply_text(
            f"🎨 {ST.bold_fancy('Blacklist Sticker')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Usage')}: Reply to a sticker with /blsticker\n"
            f"✧ {ST.bold_fancy('Or')}: /blsticker &lt;pack_name&gt;\n"
            f"✧ {ST.bold_fancy('List')}: /blstickers\n"
            f"✧ {ST.bold_fancy('Remove')}: /unblsticker &lt;pack&gt;\n",
            parse_mode="HTML"
        )
        return

    session = get_db()
    try:
        identifier = pack_name or sticker_id
        existing = session.query(DBBlacklistSticker).filter(
            DBBlacklistSticker.chat_id == chat.id,
            DBBlacklistSticker.identifier == identifier
        ).first()

        if existing:
            await message.reply_text(
                TPL.info(f"{ST.bold_fancy('Already blacklisted!')}"),
                parse_mode="HTML"
            )
            return

        bls = DBBlacklistSticker(
            chat_id=chat.id,
            identifier=identifier,
            is_pack=bool(pack_name),
            added_by=update.effective_user.id
        )
        session.add(bls)
        session.commit()

        await message.reply_text(
            TPL.success(f"🎨 {ST.bold_fancy(f'Sticker{' pack' if pack_name else ''} blacklisted!')}\n"
                        f"✧ {ST.bold_fancy('ID')}: <code>{escape_html(identifier)}</code>"),
            parse_mode="HTML"
        )

    except Exception as e:
        session.rollback()
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )
    finally:
        close_db(session)


@admin_required
@group_only
async def cmd_unblsticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove sticker from blacklist."""
    message = update.message
    args = message.text.split(None, 1)
    chat = update.effective_chat

    identifier = None
    if message.reply_to_message and message.reply_to_message.sticker:
        sticker = message.reply_to_message.sticker
        identifier = sticker.set_name or sticker.file_unique_id
    elif len(args) > 1:
        identifier = args[1].strip()
    else:
        await message.reply_text(
            f"✧ {ST.bold_fancy('Usage')}: /unblsticker &lt;pack_name&gt; or reply to sticker",
            parse_mode="HTML"
        )
        return

    session = get_db()
    try:
        deleted = session.query(DBBlacklistSticker).filter(
            DBBlacklistSticker.chat_id == chat.id,
            DBBlacklistSticker.identifier == identifier
        ).delete()
        session.commit()

        if deleted:
            await message.reply_text(
                TPL.success(f"🎨 {ST.bold_fancy('Sticker un-blacklisted!')}"),
                parse_mode="HTML"
            )
        else:
            await message.reply_text(
                TPL.error(f"{ST.bold_fancy('Not found in blacklist!')}"),
                parse_mode="HTML"
            )
    except Exception:
        session.rollback()
    finally:
        close_db(session)


@admin_required
@group_only
async def cmd_blstickers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List blacklisted stickers."""
    chat = update.effective_chat

    session = get_db()
    try:
        stickers = session.query(DBBlacklistSticker).filter(
            DBBlacklistSticker.chat_id == chat.id
        ).all()

        if not stickers:
            await update.message.reply_text(
                f"🎨 {ST.bold_fancy('No blacklisted stickers!')}",
                parse_mode="HTML"
            )
            return

        text = (
            f"🎨 {ST.bold_fancy('Blacklisted Stickers')}\n"
            f"{TPL.SEPARATOR}\n\n"
        )

        for i, s in enumerate(stickers, 1):
            stype = "📦 Pack" if s.is_pack else "🎨 Sticker"
            text += f"  {i}. {stype}: <code>{escape_html(s.identifier)}</code>\n"

        text += f"\n{ST.bold_fancy('Total')}: {len(stickers)}"
        text += TPL.mini_footer()

        await update.message.reply_text(text, parse_mode="HTML")
    finally:
        close_db(session)


async def blacklist_sticker_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check stickers against blacklist."""
    message = update.message
    if not message or not message.sticker:
        return

    chat = update.effective_chat
    user = update.effective_user

    if not chat or not user or chat.type == ChatType.PRIVATE:
        return

    if await is_admin(update, user.id) or is_approved(chat.id, user.id):
        return

    sticker = message.sticker

    session = get_db()
    try:
        blacklisted = session.query(DBBlacklistSticker).filter(
            DBBlacklistSticker.chat_id == chat.id
        ).all()

        for bl in blacklisted:
            if bl.is_pack and sticker.set_name == bl.identifier:
                try:
                    await message.delete()
                except Exception:
                    pass
                await send_and_delete(
                    chat.id,
                    f"🎨 {get_user_link(user)} {ST.bold_fancy('that sticker pack is blacklisted!')}",
                    context, seconds=10, parse_mode="HTML"
                )
                return
            elif not bl.is_pack and sticker.file_unique_id == bl.identifier:
                try:
                    await message.delete()
                except Exception:
                    pass
                await send_and_delete(
                    chat.id,
                    f"🎨 {get_user_link(user)} {ST.bold_fancy('that sticker is blacklisted!')}",
                    context, seconds=10, parse_mode="HTML"
                )
                return

    except Exception as e:
        logger.error(f"Sticker blacklist error: {e}")
    finally:
        close_db(session)


# ─────────────────────────────────────────────
#  7.7  SLOW MODE CONTROL
# ─────────────────────────────────────────────

@admin_required
@group_only
@bot_admin_required
async def cmd_slowmode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set slow mode. Usage: /slowmode &lt;seconds&gt;
    0 = off, max 86400 (24h)
    """
    args = update.message.text.split()
    chat = update.effective_chat

    if len(args) < 2:
        await update.message.reply_text(
            f"⏳ {ST.bold_fancy('Slow Mode')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Usage')}: /slowmode &lt;seconds&gt;\n"
            f"✧ {ST.bold_fancy('Off')}: /slowmode 0\n"
            f"✧ {ST.bold_fancy('Quick')}: /slowmode 10 / 30 / 60\n"
            f"✧ {ST.bold_fancy('Max')}: 86400 seconds (24h)",
            parse_mode="HTML"
        )
        return

    try:
        seconds = int(args[1])
    except ValueError:
        # Try parsing time string
        duration = parse_time_string(args[1])
        if duration:
            seconds = int(duration.total_seconds())
        else:
            await update.message.reply_text(
                TPL.error(f"{ST.bold_fancy('Invalid number!')}"),
                parse_mode="HTML"
            )
            return

    if seconds < 0:
        seconds = 0
    elif seconds > 86400:
        seconds = 86400

    try:
        await context.bot.set_chat_slow_mode_delay(chat.id, seconds)

        if seconds == 0:
            await update.message.reply_text(
                TPL.success(f"⏳ {ST.bold_fancy('Slow mode disabled!')}"),
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text(
                TPL.success(f"⏳ {ST.bold_fancy(f'Slow mode set to {seconds} seconds!')}"),
                parse_mode="HTML"
            )
    except BadRequest as e:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Failed: {e}')}"),
            parse_mode="HTML"
        )


# ─────────────────────────────────────────────
#  7.8  LOCKS SYSTEM
# ─────────────────────────────────────────────

LOCK_TYPES = {
    "all": "All messages",
    "text": "Text messages",
    "media": "All media",
    "photo": "Photos",
    "video": "Videos",
    "audio": "Audio files",
    "voice": "Voice messages",
    "document": "Documents",
    "sticker": "Stickers",
    "gif": "GIFs/Animations",
    "url": "URLs/Links",
    "forward": "Forwarded messages",
    "game": "Games",
    "poll": "Polls",
    "contact": "Contacts",
    "location": "Locations",
    "inline": "Inline bot results",
    "button": "Buttons",
    "command": "Bot commands",
    "email": "Email addresses",
    "phone": "Phone numbers",
    "invite": "Invite links",
    "pin": "Pin messages",
    "info": "Change info",
    "rtl": "RTL text",
    "arabic": "Arabic text",
    "chinese": "Chinese text",
    "anonchannel": "Anonymous channel messages",
}


@admin_required
@group_only
async def cmd_lock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lock a message type. Usage: /lock &lt;type&gt;"""
    message = update.message
    chat = update.effective_chat
    args = message.text.split()

    if len(args) < 2:
        text = (
            f"🔒 {ST.bold_fancy('Lock Types')}\n"
            f"{TPL.SEPARATOR}\n\n"
        )

        for lock_type, description in LOCK_TYPES.items():
            text += f"  • <code>{lock_type}</code> - {description}\n"

        text += (
            f"\n✧ {ST.bold_fancy('Usage')}: /lock &lt;type&gt;\n"
            f"✧ {ST.bold_fancy('Unlock')}: /unlock &lt;type&gt;\n"
            f"✧ {ST.bold_fancy('List')}: /locks\n"
            f"{TPL.mini_footer()}"
        )

        await message.reply_text(text, parse_mode="HTML")
        return

    lock_type = args[1].lower()

    if lock_type not in LOCK_TYPES:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Unknown lock type: {lock_type}')}\n"
                      f"✧ {ST.bold_fancy('Use')}: /lock to see all types"),
            parse_mode="HTML"
        )
        return

    # Handle permission-based locks
    if lock_type in ("all", "text", "media", "sticker", "gif", "poll", "contact",
                      "location", "pin", "info", "invite"):
        try:
            perms = await get_chat_permissions(chat, context)
            new_perms = apply_lock_permission(perms, lock_type, locked=True)
            await context.bot.set_chat_permissions(chat.id, new_perms)
        except BadRequest as e:
            await message.reply_text(
                TPL.error(f"{ST.bold_fancy(f'Failed: {e}')}"),
                parse_mode="HTML"
            )
            return

    # Save lock to DB
    session = get_db()
    try:
        existing = session.query(DBLock).filter(
            DBLock.chat_id == chat.id,
            DBLock.lock_type == lock_type
        ).first()

        if existing:
            existing.is_locked = True
        else:
            lock = DBLock(
                chat_id=chat.id,
                lock_type=lock_type,
                locked_by=update.effective_user.id
            )
            session.add(lock)

        session.commit()

        await message.reply_text(
            f"🔒 {ST.bold_fancy(f'Locked: {LOCK_TYPES[lock_type]}!')}\n"
            f"✧ {ST.bold_fancy('Type')}: <code>{lock_type}</code>\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )

    except Exception as e:
        session.rollback()
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )
    finally:
        close_db(session)


@admin_required
@group_only
async def cmd_unlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unlock a message type. Usage: /unlock &lt;type&gt;"""
    message = update.message
    chat = update.effective_chat
    args = message.text.split()

    if len(args) < 2:
        await message.reply_text(
            f"🔓 {ST.bold_fancy('Usage')}: /unlock &lt;type&gt;\n"
            f"✧ {ST.bold_fancy('See types')}: /lock",
            parse_mode="HTML"
        )
        return

    lock_type = args[1].lower()

    if lock_type == "all":
        # Unlock everything
        try:
            await context.bot.set_chat_permissions(
                chat.id,
                ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                    can_send_polls=True,
                    can_invite_users=True,
                    can_pin_messages=False,
                    can_change_info=False,
                )
            )
        except Exception:
            pass

        session = get_db()
        try:
            session.query(DBLock).filter(
                DBLock.chat_id == chat.id
            ).update({DBLock.is_locked: False})
            session.commit()
        except Exception:
            session.rollback()
        finally:
            close_db(session)

        await message.reply_text(
            TPL.success(f"🔓 {ST.bold_fancy('All locks removed!')}"),
            parse_mode="HTML"
        )
        return

    if lock_type not in LOCK_TYPES:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Unknown lock type: {lock_type}')}"),
            parse_mode="HTML"
        )
        return

    # Handle permission-based unlocks
    if lock_type in ("text", "media", "sticker", "gif", "poll", "contact",
                      "location", "pin", "info", "invite"):
        try:
            perms = await get_chat_permissions(chat, context)
            new_perms = apply_lock_permission(perms, lock_type, locked=False)
            await context.bot.set_chat_permissions(chat.id, new_perms)
        except BadRequest as e:
            await message.reply_text(
                TPL.error(f"{ST.bold_fancy(f'Failed: {e}')}"),
                parse_mode="HTML"
            )
            return

    # Update DB
    session = get_db()
    try:
        lock = session.query(DBLock).filter(
            DBLock.chat_id == chat.id,
            DBLock.lock_type == lock_type
        ).first()

        if lock:
            lock.is_locked = False
            session.commit()

        await message.reply_text(
            f"🔓 {ST.bold_fancy(f'Unlocked: {LOCK_TYPES[lock_type]}!')}\n"
            f"✧ {ST.bold_fancy('Type')}: <code>{lock_type}</code>\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )

    except Exception:
        session.rollback()
    finally:
        close_db(session)


@admin_required
@group_only
async def cmd_locks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current locks."""
    chat = update.effective_chat

    session = get_db()
    try:
        locks = session.query(DBLock).filter(
            DBLock.chat_id == chat.id,
            DBLock.is_locked == True
        ).all()

        text = (
            f"🔒 {ST.bold_fancy('Current Locks')}\n"
            f"{TPL.SEPARATOR}\n"
            f"✧ {ST.bold_fancy('Chat')}: {escape_html(chat.title or 'Unknown')}\n\n"
        )

        if not locks:
            text += f"  ✅ {ST.bold_fancy('Nothing is locked!')}\n"
        else:
            for lock in locks:
                desc = LOCK_TYPES.get(lock.lock_type, lock.lock_type)
                text += f"  🔒 <code>{lock.lock_type}</code> - {desc}\n"

        text += f"\n{TPL.mini_footer()}"

        await update.message.reply_text(text, parse_mode="HTML")
    finally:
        close_db(session)


async def get_chat_permissions(chat, context):
    """Get current chat permissions."""
    try:
        full_chat = await context.bot.get_chat(chat.id)
        return full_chat.permissions
    except Exception:
        return ChatPermissions()


def apply_lock_permission(perms: ChatPermissions, lock_type: str, locked: bool) -> ChatPermissions:
    """Apply a lock/unlock to chat permissions."""
    # Get current values
    current = {
        "can_send_messages": perms.can_send_messages if perms else True,
        "can_send_media_messages": perms.can_send_media_messages if perms else True,
        "can_send_other_messages": perms.can_send_other_messages if perms else True,
        "can_add_web_page_previews": perms.can_add_web_page_previews if perms else True,
        "can_send_polls": perms.can_send_polls if perms else True,
        "can_invite_users": perms.can_invite_users if perms else True,
        "can_pin_messages": perms.can_pin_messages if perms else False,
        "can_change_info": perms.can_change_info if perms else False,
    }

    value = not locked

    lock_map = {
        "all": ["can_send_messages"],
        "text": ["can_send_messages"],
        "media": ["can_send_media_messages"],
        "sticker": ["can_send_other_messages"],
        "gif": ["can_send_other_messages"],
        "poll": ["can_send_polls"],
        "invite": ["can_invite_users"],
        "pin": ["can_pin_messages"],
        "info": ["can_change_info"],
        "contact": ["can_send_other_messages"],
        "location": ["can_send_other_messages"],
    }

    if lock_type in lock_map:
        for perm_key in lock_map[lock_type]:
            current[perm_key] = value

    return ChatPermissions(**current)


async def lock_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle locked message types that can't be handled by chat permissions."""
    message = update.message
    if not message:
        return

    chat = update.effective_chat
    user = update.effective_user

    if not chat or not user or chat.type == ChatType.PRIVATE:
        return

    if await is_admin(update, user.id) or is_approved(chat.id, user.id):
        return

    session = get_db()
    try:
        locks = session.query(DBLock).filter(
            DBLock.chat_id == chat.id,
            DBLock.is_locked == True
        ).all()

        if not locks:
            return

        locked_types = {l.lock_type for l in locks}

        should_delete = False
        reason = ""

        # Check various lock types
        if "photo" in locked_types and message.photo:
            should_delete = True
            reason = "Photos are locked"
        elif "video" in locked_types and message.video:
            should_delete = True
            reason = "Videos are locked"
        elif "audio" in locked_types and (message.audio or message.voice):
            should_delete = True
            reason = "Audio is locked"
        elif "voice" in locked_types and message.voice:
            should_delete = True
            reason = "Voice messages are locked"
        elif "document" in locked_types and message.document:
            should_delete = True
            reason = "Documents are locked"
        elif "sticker" in locked_types and message.sticker:
            should_delete = True
            reason = "Stickers are locked"
        elif "gif" in locked_types and message.animation:
            should_delete = True
            reason = "GIFs are locked"
        elif "forward" in locked_types and message.forward_date:
            should_delete = True
            reason = "Forwarded messages are locked"
        elif "game" in locked_types and message.game:
            should_delete = True
            reason = "Games are locked"
        elif "url" in locked_types:
            text = message.text or message.caption or ""
            if re.search(r'https?://\S+|www\.\S+', text, re.IGNORECASE):
                should_delete = True
                reason = "URLs are locked"
            elif message.entities:
                for entity in message.entities:
                    if entity.type in ("url", "text_link"):
                        should_delete = True
                        reason = "URLs are locked"
                        break
        elif "email" in locked_types:
            if message.entities:
                for entity in message.entities:
                    if entity.type == "email":
                        should_delete = True
                        reason = "Emails are locked"
                        break
        elif "phone" in locked_types:
            if message.entities:
                for entity in message.entities:
                    if entity.type == "phone_number":
                        should_delete = True
                        reason = "Phone numbers are locked"
                        break
            elif message.contact:
                should_delete = True
                reason = "Contacts are locked"
        elif "inline" in locked_types and message.via_bot:
            should_delete = True
            reason = "Inline bot results are locked"
        elif "button" in locked_types and message.reply_markup:
            should_delete = True
            reason = "Button messages are locked"
        elif "command" in locked_types and message.text and message.text.startswith("/"):
            should_delete = True
            reason = "Bot commands are locked"
        elif "rtl" in locked_types:
            text = message.text or ""
            if re.search(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF\u0590-\u05FF]', text):
                should_delete = True
                reason = "RTL text is locked"
        elif "arabic" in locked_types:
            text = message.text or ""
            if re.search(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]', text):
                should_delete = True
                reason = "Arabic text is locked"
        elif "chinese" in locked_types:
            text = message.text or ""
            if re.search(r'[\u4E00-\u9FFF\u3400-\u4DBF]', text):
                should_delete = True
                reason = "Chinese text is locked"
        elif "anonchannel" in locked_types and message.sender_chat:
            if message.sender_chat.type == "channel":
                should_delete = True
                reason = "Anonymous channel messages are locked"

        if should_delete:
            try:
                await message.delete()
            except Exception:
                pass
            await send_and_delete(
                chat.id,
                f"🔒 {get_user_link(user)} {ST.bold_fancy(reason)}",
                context, seconds=8, parse_mode="HTML"
            )

    except Exception as e:
        logger.error(f"Lock handler error: {e}")
    finally:
        close_db(session)


# ─────────────────────────────────────────────
#  7.9  PIN / UNPIN COMMANDS
# ─────────────────────────────────────────────

@admin_required
@group_only
@bot_admin_required
async def cmd_pin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pin a message. Usage: reply to a message with /pin [loud/notify/silent]"""
    message = update.message

    if not message.reply_to_message:
        await message.reply_text(
            f"📌 {ST.bold_fancy('Usage')}: Reply to a message with /pin\n"
            f"✧ {ST.bold_fancy('Options')}: /pin loud (with notification)\n"
            f"✧ {ST.bold_fancy('Default')}: Silent pin",
            parse_mode="HTML"
        )
        return

    args = message.text.split()
    silent = True
    if len(args) > 1 and args[1].lower() in ("loud", "notify", "noisy"):
        silent = False

    try:
        await message.reply_to_message.pin(disable_notification=silent)

        pin_type = "silently" if silent else "with notification"
        await message.reply_text(
            f"📌 {ST.bold_fancy(f'Message pinned {pin_type}!')}",
            parse_mode="HTML"
        )
    except BadRequest as e:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Failed to pin: {e}')}"),
            parse_mode="HTML"
        )


@admin_required
@group_only
@bot_admin_required
async def cmd_unpin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unpin a message or all messages. Usage: /unpin or /unpin all"""
    message = update.message
    chat = update.effective_chat
    args = message.text.split()

    try:
        if len(args) > 1 and args[1].lower() == "all":
            await context.bot.unpin_all_chat_messages(chat.id)
            await message.reply_text(
                TPL.success(f"📌 {ST.bold_fancy('All messages unpinned!')}"),
                parse_mode="HTML"
            )
        elif message.reply_to_message:
            await message.reply_to_message.unpin()
            await message.reply_text(
                TPL.success(f"📌 {ST.bold_fancy('Message unpinned!')}"),
                parse_mode="HTML"
            )
        else:
            await context.bot.unpin_all_chat_messages(chat.id)
            await message.reply_text(
                TPL.success(f"📌 {ST.bold_fancy('Latest pinned message unpinned!')}"),
                parse_mode="HTML"
            )
    except BadRequest as e:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Failed: {e}')}"),
            parse_mode="HTML"
        )


@admin_required
@group_only
async def cmd_permapin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pin a message permanently (resend as bot and pin).
    Usage: reply to a message with /permapin
    """
    message = update.message
    chat = update.effective_chat

    if not message.reply_to_message:
        await message.reply_text(
            f"📌 {ST.bold_fancy('Usage')}: Reply to a message with /permapin\n"
            f"✧ The bot will copy and pin the message",
            parse_mode="HTML"
        )
        return

    reply = message.reply_to_message

    try:
        # Copy and send as bot
        sent = await reply.copy(chat.id)

        # Pin the new message
        await context.bot.pin_chat_message(
            chat.id,
            sent.message_id,
            disable_notification=True
        )

        await message.reply_text(
            TPL.success(f"📌 {ST.bold_fancy('Message permanently pinned!')}"),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Failed: {e}')}"),
            parse_mode="HTML"
        )


@admin_required
@group_only
async def cmd_pinned(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get the current pinned message."""
    chat = update.effective_chat

    try:
        full_chat = await context.bot.get_chat(chat.id)
        pinned = full_chat.pinned_message

        if not pinned:
            await update.message.reply_text(
                f"📌 {ST.bold_fancy('No pinned message in this chat!')}",
                parse_mode="HTML"
            )
            return

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                text=f"📌 {ST.bold_fancy('Go to Pinned Message')}",
                url=f"https://t.me/c/{str(chat.id)[4:]}/{pinned.message_id}"
            )]
        ])

        preview = ""
        if pinned.text:
            preview = pinned.text[:200] + ("..." if len(pinned.text) > 200 else "")
        elif pinned.caption:
            preview = pinned.caption[:200]
        else:
            preview = "[Media message]"

        await update.message.reply_text(
            f"📌 {ST.bold_fancy('Pinned Message')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Preview')}:\n{escape_html(preview)}\n\n"
            f"✧ {ST.bold_fancy('By')}: {get_user_link(pinned.from_user) if pinned.from_user else 'Unknown'}\n"
            f"✧ {ST.bold_fancy('Date')}: {pinned.date.strftime('%Y-%m-%d %H:%M') if pinned.date else 'Unknown'}\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML",
            reply_markup=keyboard
        )
    except Exception as e:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )


# ─────────────────────────────────────────────
#  7.10  PURGE / DELETE MESSAGES
# ─────────────────────────────────────────────

@admin_required
@group_only
@bot_admin_required
async def cmd_purge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete messages from the replied message to current.
    Usage: Reply to a message with /purge
    """
    message = update.message
    chat = update.effective_chat

    if not message.reply_to_message:
        await message.reply_text(
            f"🗑 {ST.bold_fancy('Usage')}: Reply to a message with /purge\n"
            f"✧ All messages from that point will be deleted\n"
            f"✧ {ST.bold_fancy('Also')}: /purge &lt;number&gt; to delete last N messages",
            parse_mode="HTML"
        )
        return

    start_id = message.reply_to_message.message_id
    end_id = message.message_id

    deleted = 0
    failed = 0

    msg_ids = list(range(start_id, end_id + 1))

    # Delete in batches of 100 (Telegram limit)
    for i in range(0, len(msg_ids), 100):
        batch = msg_ids[i:i + 100]
        try:
            result = await context.bot.delete_messages(chat.id, batch)
            if result:
                deleted += len(batch)
        except Exception:
            # Try one by one
            for mid in batch:
                try:
                    await context.bot.delete_message(chat.id, mid)
                    deleted += 1
                except Exception:
                    failed += 1

    # Send summary and delete after delay
    await send_and_delete(
        chat.id,
        f"🗑 {ST.bold_fancy(f'Purged {deleted} messages!')}\n"
        f"{'⚠️ Failed: ' + str(failed) if failed else ''}",
        context,
        seconds=5,
        parse_mode="HTML"
    )


@admin_required
@group_only
@bot_admin_required
async def cmd_spurge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Silent purge - purge without confirmation message."""
    message = update.message
    chat = update.effective_chat

    if not message.reply_to_message:
        return

    start_id = message.reply_to_message.message_id
    end_id = message.message_id

    msg_ids = list(range(start_id, end_id + 1))

    for i in range(0, len(msg_ids), 100):
        batch = msg_ids[i:i + 100]
        try:
            await context.bot.delete_messages(chat.id, batch)
        except Exception:
            for mid in batch:
                try:
                    await context.bot.delete_message(chat.id, mid)
                except Exception:
                    pass


@admin_required
@group_only
@bot_admin_required
async def cmd_purgefrom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete N messages. Usage: /purgefrom &lt;number&gt;"""
    args = update.message.text.split()
    chat = update.effective_chat

    if len(args) < 2 or not args[1].isdigit():
        await update.message.reply_text(
            f"🗑 {ST.bold_fancy('Usage')}: /purgefrom &lt;number&gt;\n"
            f"✧ Deletes last N messages",
            parse_mode="HTML"
        )
        return

    count = int(args[1])
    if count > 500:
        count = 500

    end_id = update.message.message_id
    start_id = end_id - count

    msg_ids = list(range(start_id, end_id + 1))
    deleted = 0

    for i in range(0, len(msg_ids), 100):
        batch = msg_ids[i:i + 100]
        try:
            await context.bot.delete_messages(chat.id, batch)
            deleted += len(batch)
        except Exception:
            for mid in batch:
                try:
                    await context.bot.delete_message(chat.id, mid)
                    deleted += 1
                except Exception:
                    pass

    await send_and_delete(
        chat.id,
        f"🗑 {ST.bold_fancy(f'Purged {deleted} messages!')}",
        context, seconds=5, parse_mode="HTML"
    )


@admin_required
@group_only
@bot_admin_required
async def cmd_del(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete the replied message. Usage: reply with /del"""
    message = update.message

    if not message.reply_to_message:
        await message.reply_text(
            f"🗑 {ST.bold_fancy('Reply to a message with /del to delete it!')}",
            parse_mode="HTML"
        )
        return

    try:
        await message.reply_to_message.delete()
        await message.delete()
    except Exception as e:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Failed: {e}')}"),
            parse_mode="HTML"
        )


@admin_required
@group_only
@bot_admin_required
async def cmd_purgeuser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete all messages from a specific user (last 100).
    Usage: reply with /purgeuser or /purgeuser &lt;user_id&gt;
    """
    message = update.message
    chat = update.effective_chat

    user_id = None
    if message.reply_to_message and message.reply_to_message.from_user:
        user_id = message.reply_to_message.from_user.id
    else:
        args = message.text.split()
        if len(args) > 1:
            try:
                user_id = int(args[1])
            except ValueError:
                pass

    if not user_id:
        await message.reply_text(
            f"🗑 {ST.bold_fancy('Usage')}: Reply to a user message with /purgeuser\n"
            f"✧ {ST.bold_fancy('Or')}: /purgeuser &lt;user_id&gt;",
            parse_mode="HTML"
        )
        return

    # This is limited - Telegram doesn't let bots search messages by user
    # We'll delete the replied message and try recent messages
    deleted = 0

    if message.reply_to_message:
        try:
            await message.reply_to_message.delete()
            deleted += 1
        except Exception:
            pass

    try:
        await message.delete()
    except Exception:
        pass

    await send_and_delete(
        chat.id,
        f"🗑 {ST.bold_fancy(f'Deleted {deleted} message(s) from user {user_id}')}",
        context, seconds=5, parse_mode="HTML"
    )


# ─────────────────────────────────────────────
#  7.11  CLEAN COMMANDS (delete bot commands)
# ─────────────────────────────────────────────

@admin_required
@group_only
async def cmd_cleancmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle deleting command messages. /cleancmd on/off"""
    args = update.message.text.split()
    chat = update.effective_chat

    if len(args) < 2:
        session = get_db()
        try:
            db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
            status = "ON" if (db_chat and db_chat.clean_commands) else "OFF"
        finally:
            close_db(session)

        await update.message.reply_text(
            f"🧹 {ST.bold_fancy('Clean Commands')}: {status}\n"
            f"✧ {ST.bold_fancy('Usage')}: /cleancmd on/off\n"
            f"✧ {ST.bold_fancy('When ON')}: Bot command messages (like /ban) will be auto-deleted",
            parse_mode="HTML"
        )
        return

    action = args[1].lower()
    if action in ("on", "yes", "1"):
        db_update_chat_setting(chat.id, clean_commands=True)
        await update.message.reply_text(
            TPL.success(f"🧹 {ST.bold_fancy('Command messages will be auto-deleted!')}"),
            parse_mode="HTML"
        )
    elif action in ("off", "no", "0"):
        db_update_chat_setting(chat.id, clean_commands=False)
        await update.message.reply_text(
            TPL.success(f"🧹 {ST.bold_fancy('Command cleanup disabled!')}"),
            parse_mode="HTML"
        )


# ─────────────────────────────────────────────
#  7.12  NIGHT MODE (Auto-lock/unlock by time)
# ─────────────────────────────────────────────

@admin_required
@group_only
async def cmd_nightmode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle night mode. Usage: /nightmode on/off
    /setnighttime &lt;start_hour&gt; &lt;end_hour&gt;
    During night mode, group is automatically locked.
    """
    args = update.message.text.split()
    chat = update.effective_chat

    if len(args) < 2:
        session = get_db()
        try:
            db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
            enabled = db_chat.night_mode if db_chat else False
            start_hour = db_chat.night_start_hour if db_chat else 22
            end_hour = db_chat.night_end_hour if db_chat else 6
        finally:
            close_db(session)

        await update.message.reply_text(
            f"🌙 {ST.bold_fancy('Night Mode')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Status')}: {'ON ✅' if enabled else 'OFF ❌'}\n"
            f"✧ {ST.bold_fancy('Lock at')}: {start_hour}:00\n"
            f"✧ {ST.bold_fancy('Unlock at')}: {end_hour}:00\n\n"
            f"⚙️ {ST.bold_fancy('Commands')}:\n"
            f"  • /nightmode on/off\n"
            f"  • /setnighttime &lt;start&gt; &lt;end&gt;\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
        return

    action = args[1].lower()
    if action in ("on", "yes"):
        db_update_chat_setting(chat.id, night_mode=True)
        await update.message.reply_text(
            TPL.success(f"🌙 {ST.bold_fancy('Night mode enabled!')}"),
            parse_mode="HTML"
        )
    elif action in ("off", "no"):
        db_update_chat_setting(chat.id, night_mode=False)
        await update.message.reply_text(
            TPL.success(f"🌙 {ST.bold_fancy('Night mode disabled!')}"),
            parse_mode="HTML"
        )


@admin_required
@group_only
async def cmd_setnighttime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set night mode hours. Usage: /setnighttime &lt;start_hour&gt; &lt;end_hour&gt;"""
    args = update.message.text.split()

    if len(args) < 3:
        await update.message.reply_text(
            f"🌙 {ST.bold_fancy('Usage')}: /setnighttime &lt;start_hour&gt; &lt;end_hour&gt;\n"
            f"✧ {ST.bold_fancy('Example')}: /setnighttime 22 6\n"
            f"✧ Hours in 24h format (0-23)",
            parse_mode="HTML"
        )
        return

    try:
        start_hour = int(args[1])
        end_hour = int(args[2])
    except ValueError:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy('Invalid hours!')}"),
            parse_mode="HTML"
        )
        return

    if not (0 <= start_hour <= 23) or not (0 <= end_hour <= 23):
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy('Hours must be between 0-23!')}"),
            parse_mode="HTML"
        )
        return

    db_update_chat_setting(
        update.effective_chat.id,
        night_start_hour=start_hour,
        night_end_hour=end_hour
    )

    await update.message.reply_text(
        TPL.success(
            f"🌙 {ST.bold_fancy('Night mode times set!')}\n"
            f"✧ {ST.bold_fancy('Lock')}: {start_hour}:00\n"
            f"✧ {ST.bold_fancy('Unlock')}: {end_hour}:00"
        ),
        parse_mode="HTML"
    )


async def night_mode_job(context: ContextTypes.DEFAULT_TYPE):
    """Periodic job to check and apply night mode."""
    now = datetime.datetime.utcnow()
    current_hour = now.hour

    session = get_db()
    try:
        night_chats = session.query(DBChat).filter(
            DBChat.night_mode == True
        ).all()

        for db_chat in night_chats:
            start = db_chat.night_start_hour or 22
            end = db_chat.night_end_hour or 6

            is_night = False
            if start > end:
                # Night spans midnight (e.g., 22 -> 6)
                is_night = current_hour >= start or current_hour < end
            else:
                # Same day (e.g., 1 -> 5)
                is_night = start <= current_hour < end

            try:
                if is_night:
                    # Lock the group
                    await context.bot.set_chat_permissions(
                        db_chat.chat_id,
                        ChatPermissions(can_send_messages=False)
                    )
                else:
                    # Unlock the group
                    await context.bot.set_chat_permissions(
                        db_chat.chat_id,
                        ChatPermissions(
                            can_send_messages=True,
                            can_send_media_messages=True,
                            can_send_other_messages=True,
                            can_add_web_page_previews=True,
                            can_send_polls=True,
                            can_invite_users=True,
                        )
                    )
            except Exception as e:
                logger.error(f"Night mode error for {db_chat.chat_id}: {e}")

    except Exception as e:
        logger.error(f"Night mode job error: {e}")
    finally:
        close_db(session)


# ─────────────────────────────────────────────
#  7.13  FEDERATION SYSTEM (Basic)
# ─────────────────────────────────────────────

@disabled_check
async def cmd_newfed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Create a new federation. Usage: /newfed &lt;name&gt;"""
    user = update.effective_user
    args = update.message.text.split(None, 1)

    if len(args) < 2:
        await update.message.reply_text(
            f"🏛 {ST.bold_fancy('Create Federation')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Usage')}: /newfed &lt;federation_name&gt;\n"
            f"✧ {ST.bold_fancy('Info')}: Federations let you ban users across multiple groups\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
        return

    fed_name = args[1].strip()
    if len(fed_name) > 64:
        fed_name = fed_name[:64]

    fed_id = str(uuid.uuid4())[:8]

    session = get_db()
    try:
        # Check if user already owns a fed
        existing = session.query(DBFederation).filter(
            DBFederation.owner_id == user.id
        ).first()

        if existing and not is_sudo(user.id):
            await update.message.reply_text(
                TPL.error(f"{ST.bold_fancy('You already own a federation!')}\n"
                          f"✧ {ST.bold_fancy('Name')}: {escape_html(existing.name)}\n"
                          f"✧ {ST.bold_fancy('Delete with')}: /delfed"),
                parse_mode="HTML"
            )
            return

        fed = DBFederation(
            fed_id=fed_id,
            name=fed_name,
            owner_id=user.id
        )
        session.add(fed)
        session.commit()

        await update.message.reply_text(
            f"🏛 {ST.bold_fancy('Federation Created!')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"╔═══[ {ST.bold_fancy('Fed Info')} ]═════╗\n"
            f"║ ✧ {ST.bold_fancy('Name')}: {escape_html(fed_name)}\n"
            f"║ ✧ {ST.bold_fancy('ID')}: <code>{fed_id}</code>\n"
            f"║ ✧ {ST.bold_fancy('Owner')}: {get_user_link(user)}\n"
            f"╚════════════════╝\n\n"
            f"✧ {ST.bold_fancy('Join')}: /joinfed {fed_id}\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )

    except Exception as e:
        session.rollback()
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )
    finally:
        close_db(session)


@admin_required
@group_only
async def cmd_joinfed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Join a federation. Usage: /joinfed &lt;fed_id&gt;"""
    args = update.message.text.split()
    chat = update.effective_chat
    user = update.effective_user

    if len(args) < 2:
        await update.message.reply_text(
            f"🏛 {ST.bold_fancy('Usage')}: /joinfed &lt;federation_id&gt;",
            parse_mode="HTML"
        )
        return

    fed_id = args[1].strip()

    session = get_db()
    try:
        fed = session.query(DBFederation).filter(
            DBFederation.fed_id == fed_id
        ).first()

        if not fed:
            await update.message.reply_text(
                TPL.error(f"{ST.bold_fancy('Federation not found!')}"),
                parse_mode="HTML"
            )
            return

        # Check if chat already in a fed
        existing = session.query(DBFedChat).filter(
            DBFedChat.chat_id == chat.id
        ).first()

        if existing:
            await update.message.reply_text(
                TPL.error(f"{ST.bold_fancy('This chat is already in a federation!')}\n"
                          f"✧ {ST.bold_fancy('Leave first')}: /leavefed"),
                parse_mode="HTML"
            )
            return

        fed_chat = DBFedChat(
            fed_id=fed_id,
            chat_id=chat.id,
            joined_by=user.id
        )
        session.add(fed_chat)
        session.commit()

        await update.message.reply_text(
            TPL.success(
                f"🏛 {ST.bold_fancy(f'Joined federation: {escape_html(fed.name)}')}\n"
                f"✧ {ST.bold_fancy('Fed bans will now apply here')}"
            ),
            parse_mode="HTML"
        )

    except Exception:
        session.rollback()
    finally:
        close_db(session)


@admin_required
@group_only
async def cmd_leavefed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Leave the current federation."""
    chat = update.effective_chat

    session = get_db()
    try:
        deleted = session.query(DBFedChat).filter(
            DBFedChat.chat_id == chat.id
        ).delete()
        session.commit()

        if deleted:
            await update.message.reply_text(
                TPL.success(f"🏛 {ST.bold_fancy('Left the federation!')}"),
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text(
                TPL.info(f"{ST.bold_fancy('This chat is not in any federation!')}"),
                parse_mode="HTML"
            )
    except Exception:
        session.rollback()
    finally:
        close_db(session)


async def cmd_fban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Federation ban. Usage: /fban &lt;user&gt; [reason]"""
    message = update.message
    user = update.effective_user
    chat = update.effective_chat

    user_id, reason, user_obj = await extract_user_and_reason(message, context)

    if not user_id:
        await message.reply_text(
            f"🏛🔨 {ST.bold_fancy('Usage')}: /fban &lt;user&gt; [reason]",
            parse_mode="HTML"
        )
        return

    session = get_db()
    try:
        # Find the fed this chat belongs to
        fed_chat = session.query(DBFedChat).filter(
            DBFedChat.chat_id == chat.id
        ).first()

        if not fed_chat:
            await message.reply_text(
                TPL.error(f"{ST.bold_fancy('This chat is not in any federation!')}"),
                parse_mode="HTML"
            )
            return

        fed = session.query(DBFederation).filter(
            DBFederation.fed_id == fed_chat.fed_id
        ).first()

        if not fed:
            return

        # Only fed owner or sudo can fban
        if fed.owner_id != user.id and not is_sudo(user.id):
            fed_admins = json.loads(fed.admins) if fed.admins else []
            if user.id not in fed_admins:
                await message.reply_text(
                    TPL.error(f"{ST.bold_fancy('Only fed admins can fban!')}"),
                    parse_mode="HTML"
                )
                return

        if is_owner(user_id) or is_sudo(user_id):
            await message.reply_text(
                TPL.error(f"{ST.bold_fancy('Cannot fban this user!')}"),
                parse_mode="HTML"
            )
            return

        # Add fban
        existing = session.query(DBFedBan).filter(
            DBFedBan.fed_id == fed_chat.fed_id,
            DBFedBan.user_id == user_id
        ).first()

        if existing:
            existing.reason = reason or existing.reason
            existing.is_active = True
        else:
            fban = DBFedBan(
                fed_id=fed_chat.fed_id,
                user_id=user_id,
                reason=reason,
                banned_by=user.id
            )
            session.add(fban)

        session.commit()

        # Ban from all fed chats
        fed_chats = session.query(DBFedChat).filter(
            DBFedChat.fed_id == fed_chat.fed_id
        ).all()

        banned_count = 0
        for fc in fed_chats:
            try:
                await context.bot.ban_chat_member(fc.chat_id, user_id)
                banned_count += 1
            except Exception:
                pass

        user_name = get_user_link(user_obj) if user_obj else f"<code>{user_id}</code>"

        await message.reply_text(
            f"🏛🔨 {ST.bold_fancy('Federation Ban!')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"╔═══[ {ST.bold_fancy('FBan Info')} ]═════╗\n"
            f"║ ✧ {ST.bold_fancy('Fed')}: {escape_html(fed.name)}\n"
            f"║ ✧ {ST.bold_fancy('User')}: {user_name}\n"
            f"║ ✧ {ST.bold_fancy('Reason')}: {escape_html(reason or 'No reason')}\n"
            f"║ ✧ {ST.bold_fancy('Banned in')}: {banned_count} chat(s)\n"
            f"╚════════════════╝\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )

    except Exception as e:
        session.rollback()
        logger.error(f"FBan error: {e}")
    finally:
        close_db(session)


async def cmd_unfban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove federation ban."""
    message = update.message
    user = update.effective_user
    chat = update.effective_chat

    user_id, user_obj = await extract_user(message, context)
    if not user_id:
        await message.reply_text(
            f"✧ {ST.bold_fancy('Usage')}: /unfban &lt;user&gt;",
            parse_mode="HTML"
        )
        return

    session = get_db()
    try:
        fed_chat = session.query(DBFedChat).filter(
            DBFedChat.chat_id == chat.id
        ).first()

        if not fed_chat:
            await message.reply_text(
                TPL.error(f"{ST.bold_fancy('Not in a federation!')}"),
                parse_mode="HTML"
            )
            return

        fed = session.query(DBFederation).filter(
            DBFederation.fed_id == fed_chat.fed_id
        ).first()

        if fed.owner_id != user.id and not is_sudo(user.id):
            await message.reply_text(
                TPL.error(f"{ST.bold_fancy('Only fed owner can unfban!')}"),
                parse_mode="HTML"
            )
            return

        fban = session.query(DBFedBan).filter(
            DBFedBan.fed_id == fed_chat.fed_id,
            DBFedBan.user_id == user_id
        ).first()

        if fban:
            fban.is_active = False
            session.commit()

            # Unban from all fed chats
            fed_chats = session.query(DBFedChat).filter(
                DBFedChat.fed_id == fed_chat.fed_id
            ).all()

            for fc in fed_chats:
                try:
                    await context.bot.unban_chat_member(fc.chat_id, user_id)
                except Exception:
                    pass

            user_name = get_user_link(user_obj) if user_obj else f"<code>{user_id}</code>"
            await message.reply_text(
                TPL.success(f"🏛🔓 {ST.bold_fancy('User un-fbanned!')}\n"
                            f"✧ {ST.bold_fancy('User')}: {user_name}"),
                parse_mode="HTML"
            )
        else:
            await message.reply_text(
                TPL.info(f"{ST.bold_fancy('User is not fbanned!')}"),
                parse_mode="HTML"
            )

    except Exception:
        session.rollback()
    finally:
        close_db(session)


async def cmd_fedinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show federation info."""
    chat = update.effective_chat
    args = update.message.text.split()

    session = get_db()
    try:
        fed = None

        if len(args) > 1:
            fed = session.query(DBFederation).filter(
                DBFederation.fed_id == args[1]
            ).first()
        else:
            fed_chat = session.query(DBFedChat).filter(
                DBFedChat.chat_id == chat.id
            ).first()
            if fed_chat:
                fed = session.query(DBFederation).filter(
                    DBFederation.fed_id == fed_chat.fed_id
                ).first()

        if not fed:
            await update.message.reply_text(
                TPL.error(f"{ST.bold_fancy('Federation not found!')}"),
                parse_mode="HTML"
            )
            return

        chat_count = session.query(func.count(DBFedChat.id)).filter(
            DBFedChat.fed_id == fed.fed_id
        ).scalar() or 0

        ban_count = session.query(func.count(DBFedBan.id)).filter(
            DBFedBan.fed_id == fed.fed_id,
            DBFedBan.is_active == True
        ).scalar() or 0

        fed_admins = json.loads(fed.admins) if fed.admins else []

        await update.message.reply_text(
            f"🏛 {ST.bold_fancy('Federation Info')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"╔═══[ {ST.bold_fancy(escape_html(fed.name))} ]═════╗\n"
            f"║ ✧ {ST.bold_fancy('ID')}: <code>{fed.fed_id}</code>\n"
            f"║ ✧ {ST.bold_fancy('Owner')}: <code>{fed.owner_id}</code>\n"
            f"║ ✧ {ST.bold_fancy('Chats')}: {chat_count}\n"
            f"║ ✧ {ST.bold_fancy('Bans')}: {ban_count}\n"
            f"║ ✧ {ST.bold_fancy('Admins')}: {len(fed_admins)}\n"
            f"╚════════════════╝\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )

    finally:
        close_db(session)


async def cmd_delfed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete your federation."""
    user = update.effective_user

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text="⚠️ Yes, DELETE federation",
                callback_data=f"delfed_yes_{user.id}"
            ),
            InlineKeyboardButton(
                text="❌ Cancel",
                callback_data="delfed_no"
            )
        ]
    ])

    await update.message.reply_text(
        f"⚠️ {ST.bold_fancy('Are you sure?')}\n\n"
        f"This will delete your federation, all bans, and disconnect all chats.\n"
        f"This action CANNOT be undone!",
        parse_mode="HTML",
        reply_markup=keyboard
    )


async def delfed_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle delfed confirmation."""
    query = update.callback_query
    data = query.data
    user = query.from_user

    if data.startswith("delfed_yes_"):
        owner_id = int(data.split("_")[2])

        if user.id != owner_id:
            await query.answer("❌ Only the owner can delete!", show_alert=True)
            return

        session = get_db()
        try:
            fed = session.query(DBFederation).filter(
                DBFederation.owner_id == user.id
            ).first()

            if fed:
                fed_id = fed.fed_id
                session.query(DBFedBan).filter(DBFedBan.fed_id == fed_id).delete()
                session.query(DBFedChat).filter(DBFedChat.fed_id == fed_id).delete()
                session.delete(fed)
                session.commit()

                await query.message.edit_text(
                    TPL.success(f"🏛 {ST.bold_fancy('Federation deleted!')}"),
                    parse_mode="HTML"
                )
            else:
                await query.answer("❌ No federation found!", show_alert=True)

        except Exception:
            session.rollback()
        finally:
            close_db(session)

    elif data == "delfed_no":
        await query.message.edit_text(
            f"✅ {ST.bold_fancy('Cancelled.')}",
            parse_mode="HTML"
        )


async def cmd_fedadmins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List federation admins."""
    chat = update.effective_chat

    session = get_db()
    try:
        fed_chat = session.query(DBFedChat).filter(
            DBFedChat.chat_id == chat.id
        ).first()

        if not fed_chat:
            await update.message.reply_text(
                TPL.error(f"{ST.bold_fancy('Not in a federation!')}"),
                parse_mode="HTML"
            )
            return

        fed = session.query(DBFederation).filter(
            DBFederation.fed_id == fed_chat.fed_id
        ).first()

        admins = json.loads(fed.admins) if fed.admins else []

        text = (
            f"🏛 {ST.bold_fancy('Federation Admins')}\n"
            f"{TPL.SEPARATOR}\n"
            f"✧ {ST.bold_fancy('Fed')}: {escape_html(fed.name)}\n\n"
            f"👑 {ST.bold_fancy('Owner')}: <code>{fed.owner_id}</code>\n\n"
        )

        if admins:
            text += f"⚔️ {ST.bold_fancy('Admins')}:\n"
            for i, aid in enumerate(admins, 1):
                text += f"  {i}. <code>{aid}</code>\n"
        else:
            text += f"  {ST.bold_fancy('No additional admins')}\n"

        text += TPL.mini_footer()
        await update.message.reply_text(text, parse_mode="HTML")

    finally:
        close_db(session)


async def cmd_fpromote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a federation admin. Usage: /fpromote &lt;user&gt;"""
    user = update.effective_user
    chat = update.effective_chat

    target_id, target_obj = await extract_user(update.message, context)
    if not target_id:
        await update.message.reply_text(
            f"✧ {ST.bold_fancy('Usage')}: /fpromote &lt;user&gt;",
            parse_mode="HTML"
        )
        return

    session = get_db()
    try:
        fed_chat = session.query(DBFedChat).filter(
            DBFedChat.chat_id == chat.id
        ).first()

        if not fed_chat:
            await update.message.reply_text(
                TPL.error(f"{ST.bold_fancy('Not in a federation!')}"),
                parse_mode="HTML"
            )
            return

        fed = session.query(DBFederation).filter(
            DBFederation.fed_id == fed_chat.fed_id
        ).first()

        if fed.owner_id != user.id and not is_sudo(user.id):
            await update.message.reply_text(
                TPL.error(f"{ST.bold_fancy('Only the fed owner can promote!')}"),
                parse_mode="HTML"
            )
            return

        admins = json.loads(fed.admins) if fed.admins else []

        if target_id in admins:
            await update.message.reply_text(
                TPL.info(f"{ST.bold_fancy('User is already a fed admin!')}"),
                parse_mode="HTML"
            )
            return

        admins.append(target_id)
        fed.admins = json.dumps(admins)
        session.commit()

        target_name = get_user_link(target_obj) if target_obj else f"<code>{target_id}</code>"
        await update.message.reply_text(
            TPL.success(f"🏛 {ST.bold_fancy(f'{target_name} is now a fed admin!')}"),
            parse_mode="HTML"
        )

    except Exception:
        session.rollback()
    finally:
        close_db(session)


async def cmd_fdemote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove a federation admin."""
    user = update.effective_user
    chat = update.effective_chat

    target_id, target_obj = await extract_user(update.message, context)
    if not target_id:
        await update.message.reply_text(
            f"✧ {ST.bold_fancy('Usage')}: /fdemote &lt;user&gt;",
            parse_mode="HTML"
        )
        return

    session = get_db()
    try:
        fed_chat = session.query(DBFedChat).filter(
            DBFedChat.chat_id == chat.id
        ).first()

        if not fed_chat:
            return

        fed = session.query(DBFederation).filter(
            DBFederation.fed_id == fed_chat.fed_id
        ).first()

        if fed.owner_id != user.id and not is_sudo(user.id):
            await update.message.reply_text(
                TPL.error(f"{ST.bold_fancy('Only the fed owner can demote!')}"),
                parse_mode="HTML"
            )
            return

        admins = json.loads(fed.admins) if fed.admins else []

        if target_id not in admins:
            await update.message.reply_text(
                TPL.info(f"{ST.bold_fancy('User is not a fed admin!')}"),
                parse_mode="HTML"
            )
            return

        admins.remove(target_id)
        fed.admins = json.dumps(admins)
        session.commit()

        target_name = get_user_link(target_obj) if target_obj else f"<code>{target_id}</code>"
        await update.message.reply_text(
            TPL.success(f"🏛 {ST.bold_fancy(f'{target_name} removed from fed admins!')}"),
            parse_mode="HTML"
        )

    except Exception:
        session.rollback()
    finally:
        close_db(session)


async def cmd_fbanlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List federation bans."""
    chat = update.effective_chat

    session = get_db()
    try:
        fed_chat = session.query(DBFedChat).filter(
            DBFedChat.chat_id == chat.id
        ).first()

        if not fed_chat:
            await update.message.reply_text(
                TPL.error(f"{ST.bold_fancy('Not in a federation!')}"),
                parse_mode="HTML"
            )
            return

        bans = session.query(DBFedBan).filter(
            DBFedBan.fed_id == fed_chat.fed_id,
            DBFedBan.is_active == True
        ).order_by(DBFedBan.created_at.desc()).limit(50).all()

        if not bans:
            await update.message.reply_text(
                f"🏛 {ST.bold_fancy('No federation bans!')}",
                parse_mode="HTML"
            )
            return

        text = (
            f"🏛🔨 {ST.bold_fancy('Federation Ban List')}\n"
            f"{TPL.SEPARATOR}\n\n"
        )

        for i, ban in enumerate(bans, 1):
            text += (
                f"  {i}. <code>{ban.user_id}</code>\n"
                f"     📝 {escape_html(ban.reason or 'No reason')}\n"
            )

        text += f"\n{ST.bold_fancy('Total')}: {len(bans)}"
        text += TPL.mini_footer()

        await update.message.reply_text(text, parse_mode="HTML")

    finally:
        close_db(session)


async def cmd_chatfed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show which federation this chat belongs to."""
    chat = update.effective_chat

    session = get_db()
    try:
        fed_chat = session.query(DBFedChat).filter(
            DBFedChat.chat_id == chat.id
        ).first()

        if not fed_chat:
            await update.message.reply_text(
                f"🏛 {ST.bold_fancy('This chat is not in any federation!')}",
                parse_mode="HTML"
            )
            return

        fed = session.query(DBFederation).filter(
            DBFederation.fed_id == fed_chat.fed_id
        ).first()

        await update.message.reply_text(
            f"🏛 {ST.bold_fancy('Chat Federation')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Fed')}: {escape_html(fed.name)}\n"
            f"✧ {ST.bold_fancy('ID')}: <code>{fed.fed_id}</code>\n"
            f"✧ {ST.bold_fancy('Owner')}: <code>{fed.owner_id}</code>\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )

    finally:
        close_db(session)


# ─────────────────────────────────────────────
#  7.15  DATABASE MODELS FOR SECTION 7
# ─────────────────────────────────────────────

# NOTE: These DB model classes should be added to the database models section
# (Section 2 or wherever your SQLAlchemy models are defined)

"""
Required DB Models for Section 7:

class DBNote(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    content = Column(Text)
    media_id = Column(String(255))
    media_type = Column(String(50))
    buttons = Column(Text)  # JSON
    created_by = Column(BigInteger)
    updated_by = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)
    __table_args__ = (UniqueConstraint('chat_id', 'name'),)


class DBFilter(Base):
    __tablename__ = "filters"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    keyword = Column(String(255), nullable=False)
    content = Column(Text)
    media_id = Column(String(255))
    media_type = Column(String(50))
    buttons = Column(Text)  # JSON
    created_by = Column(BigInteger)
    updated_by = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    __table_args__ = (UniqueConstraint('chat_id', 'keyword'),)


class DBCustomCmd(Base):
    __tablename__ = "custom_cmds"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    command = Column(String(255), nullable=False)
    content = Column(Text)
    media_id = Column(String(255))
    media_type = Column(String(50))
    created_by = Column(BigInteger)
    updated_by = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    __table_args__ = (UniqueConstraint('chat_id', 'command'),)


class DBDisabled(Base):
    __tablename__ = "disabled_commands"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    command = Column(String(100), nullable=False)
    disabled_by = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    __table_args__ = (UniqueConstraint('chat_id', 'command'),)


class DBBlacklist(Base):
    __tablename__ = "blacklist"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    word = Column(String(255), nullable=False)
    added_by = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    __table_args__ = (UniqueConstraint('chat_id', 'word'),)


class DBBlacklistSticker(Base):
    __tablename__ = "blacklist_stickers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    identifier = Column(String(255), nullable=False)  # pack name or file_unique_id
    is_pack = Column(Boolean, default=False)
    added_by = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    __table_args__ = (UniqueConstraint('chat_id', 'identifier'),)


class DBLock(Base):
    __tablename__ = "locks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    lock_type = Column(String(50), nullable=False)
    is_locked = Column(Boolean, default=True)
    locked_by = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    __table_args__ = (UniqueConstraint('chat_id', 'lock_type'),)


class DBFederation(Base):
    __tablename__ = "federations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    fed_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    owner_id = Column(BigInteger, nullable=False)
    admins = Column(Text)  # JSON list of admin IDs
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class DBFedChat(Base):
    __tablename__ = "fed_chats"
    id = Column(Integer, primary_key=True, autoincrement=True)
    fed_id = Column(String(50), nullable=False, index=True)
    chat_id = Column(BigInteger, unique=True, nullable=False)
    joined_by = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class DBFedBan(Base):
    __tablename__ = "fed_bans"
    id = Column(Integer, primary_key=True, autoincrement=True)
    fed_id = Column(String(50), nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False)
    reason = Column(Text)
    banned_by = Column(BigInteger)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    __table_args__ = (UniqueConstraint('fed_id', 'user_id'),)
"""


# ─────────────────────────────────────────────
#  7.16  REGISTER SECTION 7 HANDLERS
# ─────────────────────────────────────────────

def register_section7_handlers(app):
    """Register all Section 7 command handlers."""

    # ── Notes ──
    app.add_handler(CommandHandler("save", cmd_save))
    app.add_handler(CommandHandler("get", cmd_get))
    app.add_handler(CommandHandler("notes", cmd_notes))
    app.add_handler(CommandHandler("saved", cmd_notes))  # alias
    app.add_handler(CommandHandler("clear", cmd_clear))
    app.add_handler(CommandHandler("clearall", cmd_clearall))
    app.add_handler(CommandHandler("privatenotes", cmd_privatenotes))

    # ── Filters ──
    app.add_handler(CommandHandler("filter", cmd_filter))
    app.add_handler(CommandHandler("filters", cmd_filters))
    app.add_handler(CommandHandler("stop", cmd_stop))
    app.add_handler(CommandHandler("stopall", cmd_stopall))

    # ── Custom Commands ──
    app.add_handler(CommandHandler("addcmd", cmd_addcmd))
    app.add_handler(CommandHandler("delcmd", cmd_delcmd))
    app.add_handler(CommandHandler("customcmds", cmd_customcmds))

    # ── Disable/Enable ──
    app.add_handler(CommandHandler("disable", cmd_disable))
    app.add_handler(CommandHandler("enable", cmd_enable))
    app.add_handler(CommandHandler("disabled", cmd_disabled))
    app.add_handler(CommandHandler("disableable", cmd_disableable))
    app.add_handler(CommandHandler("listcmds", cmd_disableable))  # alias

    # ── Blacklist ──
    app.add_handler(CommandHandler("blacklist", cmd_blacklist))
    app.add_handler(CommandHandler("addblacklist", cmd_blacklist))  # alias
    app.add_handler(CommandHandler("unblacklist", cmd_unblacklist))
    app.add_handler(CommandHandler("rmblacklist", cmd_rmblacklist))
    app.add_handler(CommandHandler("blacklistmode", cmd_blacklistmode))

    # ── Blacklist Stickers ──
    app.add_handler(CommandHandler("blsticker", cmd_blsticker))
    app.add_handler(CommandHandler("unblsticker", cmd_unblsticker))
    app.add_handler(CommandHandler("blstickers", cmd_blstickers))

    # ── Slow Mode ──
    app.add_handler(CommandHandler("slowmode", cmd_slowmode))

    # ── Locks ──
    app.add_handler(CommandHandler("lock", cmd_lock))
    app.add_handler(CommandHandler("unlock", cmd_unlock))
    app.add_handler(CommandHandler("locks", cmd_locks))
    app.add_handler(CommandHandler("locklist", cmd_locks))  # alias

    # ── Pin/Unpin ──
    app.add_handler(CommandHandler("pin", cmd_pin))
    app.add_handler(CommandHandler("unpin", cmd_unpin))
    app.add_handler(CommandHandler("permapin", cmd_permapin))
    app.add_handler(CommandHandler("pinned", cmd_pinned))

    # ── Purge/Delete ──
    app.add_handler(CommandHandler("purge", cmd_purge))
    app.add_handler(CommandHandler("spurge", cmd_spurge))
    app.add_handler(CommandHandler("purgefrom", cmd_purgefrom))
    app.add_handler(CommandHandler("del", cmd_del))
    app.add_handler(CommandHandler("delete", cmd_del))  # alias
    app.add_handler(CommandHandler("purgeuser", cmd_purgeuser))

    # ── Clean Commands ──
    app.add_handler(CommandHandler("cleancmd", cmd_cleancmd))
    app.add_handler(CommandHandler("cleancommand", cmd_cleancmd))  # alias

    # ── Night Mode ──
    app.add_handler(CommandHandler("nightmode", cmd_nightmode))
    app.add_handler(CommandHandler("setnighttime", cmd_setnighttime))

    # ── Federation ──
    app.add_handler(CommandHandler("newfed", cmd_newfed))
    app.add_handler(CommandHandler("joinfed", cmd_joinfed))
    app.add_handler(CommandHandler("leavefed", cmd_leavefed))
    app.add_handler(CommandHandler("fban", cmd_fban))
    app.add_handler(CommandHandler("unfban", cmd_unfban))
    app.add_handler(CommandHandler("fedinfo", cmd_fedinfo))
    app.add_handler(CommandHandler("delfed", cmd_delfed))
    app.add_handler(CommandHandler("fedadmins", cmd_fedadmins))
    app.add_handler(CommandHandler("fpromote", cmd_fpromote))
    app.add_handler(CommandHandler("fdemote", cmd_fdemote))
    app.add_handler(CommandHandler("fbanlist", cmd_fbanlist))
    app.add_handler(CommandHandler("chatfed", cmd_chatfed))
    app.add_handler(CommandHandler("myfed", cmd_chatfed))  # alias

    # ── Callback Handlers ──
    app.add_handler(CallbackQueryHandler(notes_pm_callback, pattern=r"^notes_pm_"))
    app.add_handler(CallbackQueryHandler(clearall_notes_callback, pattern=r"^clearallnotes_"))
    app.add_handler(CallbackQueryHandler(stopall_callback, pattern=r"^stopall_"))
    app.add_handler(CallbackQueryHandler(rmblacklist_callback, pattern=r"^rmblacklist_"))
    app.add_handler(CallbackQueryHandler(delfed_callback, pattern=r"^delfed_"))

    # ── Message Handlers (filters, notes hashtag, blacklist, locks, custom cmds, stickers) ──
    # These should be added with lower group priority so commands are processed first

    # Hashtag notes (#notename)
    app.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(r'^#\w+') & ~filters.COMMAND,
        hashtag_note_handler
    ), group=10)

    # Filter trigger handler
    app.add_handler(MessageHandler(
        (filters.TEXT | filters.CAPTION) & ~filters.COMMAND & filters.ChatType.GROUPS,
        filter_message_handler
    ), group=11)

    # Blacklist word handler
    app.add_handler(MessageHandler(
        (filters.TEXT | filters.CAPTION) & ~filters.COMMAND & filters.ChatType.GROUPS,
        blacklist_message_handler
    ), group=12)

    # Lock message handler
    app.add_handler(MessageHandler(
        filters.ALL & ~filters.COMMAND & filters.ChatType.GROUPS,
        lock_message_handler
    ), group=13)

    # Blacklist sticker handler
    app.add_handler(MessageHandler(
        filters.Sticker.ALL & filters.ChatType.GROUPS,
        blacklist_sticker_handler
    ), group=14)

    # Custom command handler (lowest priority)
    app.add_handler(MessageHandler(
        filters.COMMAND & filters.ChatType.GROUPS,
        custom_cmd_handler
    ), group=15)

    logger.info("✅ Section 7 handlers registered: Notes, Filters, Custom Cmds, "
                "Blacklist, Locks, Pin, Purge, Night Mode, Federation")


# ═══════════════════════════════════════════════════════════════
# END OF SECTION 7
# ═══════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════
# ██╗  SECTION 8: FUN / GAMES / ENTERTAINMENT / REACTIONS
# ═══════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────
#  8.1  TEXT FUN COMMANDS
# ─────────────────────────────────────────────

@disabled_check
async def cmd_runs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a random fun 'runs' text."""
    runs_list = [
        "Runs away from the explosion 💥",
        "Runs to the fridge 🏃‍♂️🍕",
        "Runs like Naruto 🏃‍♂️💨",
        "Tries to run but trips 😂",
        "Runs faster than light ⚡",
        "Runs and hides behind a pillow 🛋️",
        "Runs screaming into the void 🌌",
        "Runs while eating pizza 🍕",
        "Runs but forgot why 🤔",
        "Runs in circles 🔄",
        "Runs to grab coffee ☕",
        "Runs like a ninja 🥷",
        "Rolls away like a ball 🏃‍♂️",
        "Runs while vibing to music 🎵",
        "Runs and bumps into a wall 🧱",
        "Runs but in slow motion 🐢",
        "Runs with toast in mouth like anime 🍞",
        "Teleports away ✨",
        "Runs and does a backflip 🤸",
        "Runs like the wind 🌬️",
        "Runs away from responsibilities 📝",
        "Runs to pet a cat 🐱",
        "Runs upside down on the ceiling 🦎",
        "Runs and falls into a portal 🌀",
        "Runs off the screen ➡️",
    ]

    chosen = random.choice(runs_list)
    await update.message.reply_text(
        f"🏃 {get_user_link(update.effective_user)} {ST.bold_fancy(chosen)}",
        parse_mode="HTML"
    )


@disabled_check
async def cmd_insult(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a light-hearted insult (family-friendly)."""
    insults = [
        "You're like a cloud. When you disappear, it's a beautiful day ☁️",
        "You bring everyone so much joy... when you leave 😂",
        "If you were any slower, you'd be going backwards 🐌",
        "You're proof that even Google can't answer everything 🤷",
        "You're like a software update. Nobody wants you, but we deal with it 💻",
        "You have something on your chin... no, the 3rd one 😏",
        "I'd explain it to you, but I left my crayons at home 🖍️",
        "You're not stupid; you just have bad luck thinking 🧠",
        "If you were a vegetable, you'd be a cucumber... cool but pointless 🥒",
        "I'd roast you but my mom said I can't burn trash 🔥",
        "You're like a screen door on a submarine 🚢",
        "You have the energy of a sloth on vacation 🦥",
        "If brains were dynamite, you wouldn't have enough to blow your nose 💣",
        "You're the reason shampoo has instructions 🧴",
        "Your secrets are safe with me... I never listen anyway 🙉",
        "You're not useless. You can always serve as a bad example 📝",
        "You're as bright as a black hole ⚫",
        "I bet your keyboard is jealous of the amount of action your spacebar gets 🤣",
        "You're like Monday. Nobody likes you 📅",
        "If you were a spice, you'd be flour 🌾",
    ]

    target = update.effective_user
    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user

    chosen = random.choice(insults)
    await update.message.reply_text(
        f"😈 {get_user_link(target)},\n{ST.bold_fancy(chosen)}",
        parse_mode="HTML"
    )


@disabled_check
async def cmd_truth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a random truth question."""
    truths = [
        "What is the most embarrassing thing you've ever done? 😳",
        "What is your biggest fear? 😱",
        "Who was your first crush? 💕",
        "What is the biggest lie you've ever told? 🤥",
        "What's the most childish thing you still do? 👶",
        "What is your guilty pleasure? 🍫",
        "What's the worst grade you got in school? 📝",
        "Have you ever cheated in a game? 🎮",
        "What's the longest you've gone without showering? 🚿",
        "What's your most unpopular opinion? 🤔",
        "What's the dumbest thing you've ever said? 💬",
        "What's your screen time average? 📱",
        "Who do you secretly admire in this group? 👀",
        "What's the last thing you Googled? 🔍",
        "Have you ever pretended to be sick? 🤧",
        "What's your most embarrassing nickname? 😅",
        "What's something you're bad at but love doing? ❤️",
        "What's the weirdest food you've ever eaten? 🍽️",
        "Have you ever talked to yourself? 🗣️",
        "What's the silliest thing you've cried about? 😢",
        "What's the last lie you told? 🤫",
        "What's your hidden talent? 🌟",
        "Who do you text the most? 📲",
        "What's the most useless talent you have? 😂",
        "What song do you secretly love? 🎵",
    ]

    chosen = random.choice(truths)
    await update.message.reply_text(
        f"🎯 {ST.bold_fancy('Truth!')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"❓ {ST.bold_fancy(chosen)}\n\n"
        f"✧ {ST.bold_fancy('Asked to')}: {get_user_link(update.effective_user)}\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


@disabled_check
async def cmd_dare(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a random dare challenge."""
    dares = [
        "Send a voice message singing your favorite song 🎤",
        "Change your profile picture to a potato for 1 hour 🥔",
        "Type the next 5 messages with your eyes closed 👀",
        "Send the last photo in your gallery 📸",
        "Use only emojis for the next 10 minutes 😀",
        "Compliment everyone in the group 💝",
        "Send a message in ALL CAPS for next 5 minutes 📢",
        "Share the last YouTube video you watched 📺",
        "Tell a joke that makes everyone laugh 😂",
        "Speak only in questions for 5 minutes ❓",
        "Send a selfie right now 🤳",
        "Write a short poem about the group 📝",
        "Share your most played song 🎵",
        "Do 10 pushups and send proof 💪",
        "Text your best friend 'I love you' and screenshot 💬",
        "Change your username to something funny for 1 hour 🏷️",
        "Send a message to the group in a different language 🌍",
        "Share your battery percentage 🔋",
        "Tell your most embarrassing story 😅",
        "Send the oldest photo on your phone 📱",
        "Rate yourself out of 10 honestly ⭐",
        "Share your current wallpaper 🖼️",
        "Send a voice message saying 'I am a chicken' 🐔",
        "Describe yourself in 3 emojis 🤔",
        "Tag someone and say something nice 💕",
    ]

    chosen = random.choice(dares)
    await update.message.reply_text(
        f"🎲 {ST.bold_fancy('Dare!')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"💪 {ST.bold_fancy(chosen)}\n\n"
        f"✧ {ST.bold_fancy('Dared')}: {get_user_link(update.effective_user)}\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


@disabled_check
async def cmd_roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Roll a dice. Usage: /roll [sides] [count]"""
    args = update.message.text.split()
    sides = 6
    count = 1

    if len(args) > 1:
        try:
            sides = int(args[1])
            if sides < 2:
                sides = 2
            elif sides > 1000:
                sides = 1000
        except ValueError:
            pass

    if len(args) > 2:
        try:
            count = int(args[2])
            if count < 1:
                count = 1
            elif count > 20:
                count = 20
        except ValueError:
            pass

    results = [random.randint(1, sides) for _ in range(count)]
    total = sum(results)

    if count == 1:
        dice_emoji = "🎲"
        result_text = f"{dice_emoji} {ST.bold_fancy(f'Rolled: {results[0]}')}"
    else:
        rolls_str = ", ".join(str(r) for r in results)
        result_text = (
            f"🎲 {ST.bold_fancy('Dice Roll!')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Rolls')}: {rolls_str}\n"
            f"✧ {ST.bold_fancy('Total')}: {total}\n"
            f"✧ {ST.bold_fancy('Dice')}: {count}d{sides}"
        )

    await update.message.reply_text(
        result_text + f"\n{TPL.mini_footer()}",
        parse_mode="HTML"
    )


@disabled_check
async def cmd_flip_coin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Flip a coin."""
    result = random.choice(["Heads", "Tails"])
    emoji = "🪙" if result == "Heads" else "🪙"
    side_emoji = "👑" if result == "Heads" else "🔢"

    await update.message.reply_text(
        f"{emoji} {ST.bold_fancy('Coin Flip!')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"{side_emoji} {ST.bold_fancy(f'Result: {result}!')}\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


@disabled_check
async def cmd_rps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Rock Paper Scissors. Usage: /rps &lt;rock/paper/scissors&gt;"""
    args = update.message.text.split()
    choices = {"rock": "🪨", "paper": "📄", "scissors": "✂️",
               "r": "🪨", "p": "📄", "s": "✂️"}

    if len(args) < 2 or args[1].lower() not in choices:
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🪨 Rock", callback_data="rps_rock"),
                InlineKeyboardButton("📄 Paper", callback_data="rps_paper"),
                InlineKeyboardButton("✂️ Scissors", callback_data="rps_scissors"),
            ]
        ])
        await update.message.reply_text(
            f"✊ {ST.bold_fancy('Rock Paper Scissors!')}\n"
            f"✧ Choose your weapon!",
            parse_mode="HTML",
            reply_markup=keyboard
        )
        return

    user_choice = args[1].lower()
    if user_choice in ("r", "rock"):
        user_choice = "rock"
    elif user_choice in ("p", "paper"):
        user_choice = "paper"
    elif user_choice in ("s", "scissors"):
        user_choice = "scissors"

    bot_choice = random.choice(["rock", "paper", "scissors"])

    user_emoji = choices.get(user_choice[0], "❓")
    bot_emoji = choices.get(bot_choice[0], "❓")

    # Determine winner
    if user_choice == bot_choice:
        result = "🤝 It's a TIE!"
        result_color = "🟡"
    elif (user_choice == "rock" and bot_choice == "scissors") or \
         (user_choice == "paper" and bot_choice == "rock") or \
         (user_choice == "scissors" and bot_choice == "paper"):
        result = "🎉 You WIN!"
        result_color = "🟢"
    else:
        result = "😈 I WIN!"
        result_color = "🔴"

    await update.message.reply_text(
        f"✊ {ST.bold_fancy('Rock Paper Scissors!')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"✧ {ST.bold_fancy('You')}: {user_emoji} {user_choice.title()}\n"
        f"✧ {ST.bold_fancy('Bot')}: {bot_emoji} {bot_choice.title()}\n\n"
        f"{result_color} {ST.bold_fancy(result)}\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


async def rps_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle RPS button clicks."""
    query = update.callback_query
    data = query.data
    user = query.from_user

    if not data.startswith("rps_"):
        return

    user_choice = data.split("_")[1]
    bot_choice = random.choice(["rock", "paper", "scissors"])

    choices_emoji = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}
    user_emoji = choices_emoji[user_choice]
    bot_emoji = choices_emoji[bot_choice]

    if user_choice == bot_choice:
        result = "🤝 It's a TIE!"
    elif (user_choice == "rock" and bot_choice == "scissors") or \
         (user_choice == "paper" and bot_choice == "rock") or \
         (user_choice == "scissors" and bot_choice == "paper"):
        result = "🎉 You WIN!"
    else:
        result = "😈 I WIN!"

    await query.message.edit_text(
        f"✊ {ST.bold_fancy('Rock Paper Scissors!')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"✧ {ST.bold_fancy('Player')}: {get_user_link(user)}\n"
        f"✧ {ST.bold_fancy('You')}: {user_emoji} {user_choice.title()}\n"
        f"✧ {ST.bold_fancy('Bot')}: {bot_emoji} {bot_choice.title()}\n\n"
        f"{ST.bold_fancy(result)}\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )
    await query.answer()


@disabled_check
async def cmd_8ball(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Magic 8-ball. Usage: /8ball &lt;question&gt;"""
    args = update.message.text.split(None, 1)

    if len(args) < 2:
        await update.message.reply_text(
            f"🎱 {ST.bold_fancy('Ask the Magic 8-Ball!')}\n"
            f"✧ {ST.bold_fancy('Usage')}: /8ball &lt;your question&gt;",
            parse_mode="HTML"
        )
        return

    question = args[1]

    answers = [
        # Positive
        "🟢 It is certain!", "🟢 Without a doubt!", "🟢 Yes, definitely!",
        "🟢 You may rely on it!", "🟢 As I see it, yes!", "🟢 Most likely!",
        "🟢 Outlook good!", "🟢 Yes!", "🟢 Signs point to yes!",
        "🟢 Absolutely!", "🟢 100% yes!",
        # Neutral
        "🟡 Reply hazy, try again...", "🟡 Ask again later...",
        "🟡 Better not tell you now...", "🟡 Cannot predict now...",
        "🟡 Concentrate and ask again...", "🟡 Maybe...",
        "🟡 The stars are unclear...",
        # Negative
        "🔴 Don't count on it!", "🔴 My reply is no!",
        "🔴 My sources say no!", "🔴 Outlook not so good!",
        "🔴 Very doubtful!", "🔴 Nope!", "🔴 Absolutely not!",
        "🔴 The universe says no!",
    ]

    answer = random.choice(answers)

    await update.message.reply_text(
        f"🎱 {ST.bold_fancy('Magic 8-Ball')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"❓ {ST.bold_fancy('Question')}: {escape_html(question)}\n\n"
        f"🎱 {ST.bold_fancy('Answer')}: {answer}\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


@disabled_check
async def cmd_decide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help decide between choices. Usage: /decide option1 | option2 | option3"""
    args = update.message.text.split(None, 1)

    if len(args) < 2:
        await update.message.reply_text(
            f"🤔 {ST.bold_fancy('Decision Maker')}\n"
            f"✧ {ST.bold_fancy('Usage')}: /decide option1 | option2 | option3\n"
            f"✧ {ST.bold_fancy('Example')}: /decide pizza | burger | sushi",
            parse_mode="HTML"
        )
        return

    options_text = args[1]
    # Support multiple separators
    for sep in ["|", ",", " or "]:
        if sep in options_text:
            options = [o.strip() for o in options_text.split(sep) if o.strip()]
            break
    else:
        options = [o.strip() for o in options_text.split() if o.strip()]

    if len(options) < 2:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy('Please provide at least 2 options separated by | or ,')}"),
            parse_mode="HTML"
        )
        return

    chosen = random.choice(options)
    index = options.index(chosen) + 1

    options_text = "\n".join(f"  {i+1}. {escape_html(o)}" for i, o in enumerate(options))

    await update.message.reply_text(
        f"🤔 {ST.bold_fancy('Decision Made!')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"📋 {ST.bold_fancy('Options')}:\n{options_text}\n\n"
        f"✅ {ST.bold_fancy(f'I choose #{index}')}: {escape_html(chosen)}!\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


@disabled_check
async def cmd_quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get a random inspirational quote."""
    quotes = [
        ("The only way to do great work is to love what you do.", "Steve Jobs"),
        ("Innovation distinguishes between a leader and a follower.", "Steve Jobs"),
        ("Stay hungry, stay foolish.", "Steve Jobs"),
        ("Life is what happens when you're busy making other plans.", "John Lennon"),
        ("The future belongs to those who believe in the beauty of their dreams.", "Eleanor Roosevelt"),
        ("It is during our darkest moments that we must focus to see the light.", "Aristotle"),
        ("The only impossible journey is the one you never begin.", "Tony Robbins"),
        ("Success is not final, failure is not fatal: it is the courage to continue that counts.", "Winston Churchill"),
        ("In the middle of every difficulty lies opportunity.", "Albert Einstein"),
        ("Believe you can and you're halfway there.", "Theodore Roosevelt"),
        ("Be the change that you wish to see in the world.", "Mahatma Gandhi"),
        ("The best time to plant a tree was 20 years ago. The second best time is now.", "Chinese Proverb"),
        ("Your time is limited, don't waste it living someone else's life.", "Steve Jobs"),
        ("If you want to lift yourself up, lift up someone else.", "Booker T. Washington"),
        ("The mind is everything. What you think you become.", "Buddha"),
        ("An unexamined life is not worth living.", "Socrates"),
        ("Happiness is not something ready made. It comes from your own actions.", "Dalai Lama"),
        ("Turn your wounds into wisdom.", "Oprah Winfrey"),
        ("The only person you are destined to become is the person you decide to be.", "Ralph Waldo Emerson"),
        ("Everything you've ever wanted is on the other side of fear.", "George Addair"),
        ("We may encounter many defeats but we must not be defeated.", "Maya Angelou"),
        ("What you get by achieving your goals is not as important as what you become.", "Zig Ziglar"),
        ("You miss 100% of the shots you don't take.", "Wayne Gretzky"),
        ("I have not failed. I've just found 10,000 ways that won't work.", "Thomas Edison"),
        ("A person who never made a mistake never tried anything new.", "Albert Einstein"),
        ("The secret of getting ahead is getting started.", "Mark Twain"),
        ("Quality is not an act, it is a habit.", "Aristotle"),
        ("The best revenge is massive success.", "Frank Sinatra"),
        ("Do what you can, with what you have, where you are.", "Theodore Roosevelt"),
        ("Don't watch the clock; do what it does. Keep going.", "Sam Levenson"),
    ]

    text, author = random.choice(quotes)

    await update.message.reply_text(
        f"💬 {ST.bold_fancy('Quote of the Moment')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"  ❝ {ST.bold_fancy(text)} ❞\n\n"
        f"  — {ST.bold_fancy(author)}\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


@disabled_check
async def cmd_fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get a random fun fact."""
    facts = [
        "Honey never spoils. Archaeologists have found 3000-year-old honey that's still edible! 🍯",
        "Octopuses have three hearts and blue blood! 🐙",
        "A group of flamingos is called a 'flamboyance'! 🦩",
        "Bananas are berries, but strawberries aren't! 🍌",
        "The shortest war in history lasted 38-45 minutes (Anglo-Zanzibar War)! ⚔️",
        "A day on Venus is longer than a year on Venus! 🪐",
        "Humans share 60% of their DNA with bananas! 🧬",
        "The Eiffel Tower can grow up to 6 inches taller during summer! 🗼",
        "A jiffy is an actual unit of time: 1/100th of a second! ⏱",
        "There are more possible iterations of a chess game than atoms in the observable universe! ♟",
        "Cows have best friends and get stressed when separated! 🐄",
        "The inventor of the Pringles can is buried in one! 📦",
        "Wombat poop is cube-shaped! 🟫",
        "A cloud can weigh more than a million pounds! ☁️",
        "The total weight of all ants on Earth is close to the weight of all humans! 🐜",
        "Scotland's national animal is the unicorn! 🦄",
        "The tongue is the strongest muscle in the human body! 👅",
        "A bolt of lightning is 5x hotter than the surface of the sun! ⚡",
        "There are more stars in the universe than grains of sand on Earth! ⭐",
        "Dolphins sleep with one eye open! 🐬",
        "The average person walks about 100,000 miles in their lifetime! 🚶",
        "Your nose can remember 50,000 different scents! 👃",
        "The first computer virus was created in 1983! 💻",
        "A snail can sleep for three years! 🐌",
        "Cleopatra lived closer in time to the Moon landing than to the building of the Great Pyramid! 🏛",
    ]

    fact = random.choice(facts)

    await update.message.reply_text(
        f"🧠 {ST.bold_fancy('Fun Fact!')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"📖 {ST.bold_fancy(fact)}\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


@disabled_check
async def cmd_joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tell a random joke."""
    jokes = [
        ("Why don't scientists trust atoms?", "Because they make up everything! 😂"),
        ("Why did the scarecrow win an award?", "Because he was outstanding in his field! 🌾"),
        ("What do you call a fake noodle?", "An impasta! 🍝"),
        ("Why don't eggs tell jokes?", "They'd crack each other up! 🥚"),
        ("What do you call a bear with no teeth?", "A gummy bear! 🐻"),
        ("Why did the math book look sad?", "Because it had too many problems! 📚"),
        ("What do you call a sleeping dinosaur?", "A dino-snore! 🦕"),
        ("Why can't you give Elsa a balloon?", "Because she will let it go! 🎈"),
        ("What do you call a dog that does magic?", "A Labracadabrador! 🐕"),
        ("Why did the bicycle fall over?", "It was two-tired! 🚲"),
        ("What do you call a fish without eyes?", "A fsh! 🐟"),
        ("Why did the golfer bring two pants?", "In case he got a hole in one! ⛳"),
        ("What did the ocean say to the beach?", "Nothing, it just waved! 🌊"),
        ("Why don't skeletons fight each other?", "They don't have the guts! 💀"),
        ("What do you call cheese that isn't yours?", "Nacho cheese! 🧀"),
        ("Why did the cookie go to the hospital?", "Because it felt crummy! 🍪"),
        ("What do you call a lazy kangaroo?", "A pouch potato! 🦘"),
        ("Why can't you hear a pterodactyl in the bathroom?", "Because the p is silent! 🦖"),
        ("What did one wall say to the other?", "I'll meet you at the corner! 🏗"),
        ("Why don't programmers like nature?", "It has too many bugs! 🐛"),
    ]

    setup, punchline = random.choice(jokes)

    await update.message.reply_text(
        f"😂 {ST.bold_fancy('Joke Time!')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"❓ {ST.bold_fancy(setup)}\n\n"
        f"💡 {ST.bold_fancy(punchline)}\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


# ─────────────────────────────────────────────
#  8.2  TEXT FORMATTING / STYLE COMMANDS
# ─────────────────────────────────────────────

@disabled_check
async def cmd_reverse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reverse text. Usage: /reverse &lt;text&gt; or reply"""
    text = await get_text_from_args_or_reply(update)
    if not text:
        await update.message.reply_text(
            f"🔄 {ST.bold_fancy('Usage')}: /reverse &lt;text&gt;",
            parse_mode="HTML"
        )
        return

    reversed_text = text[::-1]
    await update.message.reply_text(
        f"🔄 {ST.bold_fancy('Reversed Text')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"✧ {ST.bold_fancy('Original')}: {escape_html(text)}\n"
        f"✧ {ST.bold_fancy('Reversed')}: {escape_html(reversed_text)}\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


@disabled_check
async def cmd_mock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """mOcKiNg SpOnGeBoB text. Usage: /mock &lt;text&gt; or reply"""
    text = await get_text_from_args_or_reply(update)
    if not text:
        await update.message.reply_text(
            f"🧽 {ST.bold_fancy('Usage')}: /mock &lt;text&gt;",
            parse_mode="HTML"
        )
        return

    mocked = ""
    for i, char in enumerate(text):
        if i % 2 == 0:
            mocked += char.lower()
        else:
            mocked += char.upper()

    await update.message.reply_text(
        f"🧽 {escape_html(mocked)}",
        parse_mode="HTML"
    )


@disabled_check
async def cmd_vapor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """V A P O R W A V E text. Usage: /vapor &lt;text&gt; or reply"""
    text = await get_text_from_args_or_reply(update)
    if not text:
        await update.message.reply_text(
            f"🌊 {ST.bold_fancy('Usage')}: /vapor &lt;text&gt;",
            parse_mode="HTML"
        )
        return

    vapored = " ".join(text.upper())
    await update.message.reply_text(
        f"🌊 {escape_html(vapored)}",
        parse_mode="HTML"
    )


@disabled_check
async def cmd_clap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add 👏 claps 👏 between 👏 words. Usage: /clap &lt;text&gt;"""
    text = await get_text_from_args_or_reply(update)
    if not text:
        await update.message.reply_text(
            f"👏 {ST.bold_fancy('Usage')}: /clap &lt;text&gt;",
            parse_mode="HTML"
        )
        return

    clapped = " 👏 ".join(text.split())
    await update.message.reply_text(f"👏 {clapped} 👏")


@disabled_check
async def cmd_tiny(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Convert text to tiny/superscript. Usage: /tiny &lt;text&gt;"""
    text = await get_text_from_args_or_reply(update)
    if not text:
        await update.message.reply_text(
            f"🔤 {ST.bold_fancy('Usage')}: /tiny &lt;text&gt;",
            parse_mode="HTML"
        )
        return

    tiny_map = {
        'a': 'ᵃ', 'b': 'ᵇ', 'c': 'ᶜ', 'd': 'ᵈ', 'e': 'ᵉ', 'f': 'ᶠ',
        'g': 'ᵍ', 'h': 'ʰ', 'i': 'ⁱ', 'j': 'ʲ', 'k': 'ᵏ', 'l': 'ˡ',
        'm': 'ᵐ', 'n': 'ⁿ', 'o': 'ᵒ', 'p': 'ᵖ', 'q': 'q', 'r': 'ʳ',
        's': 'ˢ', 't': 'ᵗ', 'u': 'ᵘ', 'v': 'ᵛ', 'w': 'ʷ', 'x': 'ˣ',
        'y': 'ʸ', 'z': 'ᶻ',
        'A': 'ᴬ', 'B': 'ᴮ', 'C': 'ᶜ', 'D': 'ᴰ', 'E': 'ᴱ', 'F': 'ᶠ',
        'G': 'ᴳ', 'H': 'ᴴ', 'I': 'ᴵ', 'J': 'ᴶ', 'K': 'ᴷ', 'L': 'ᴸ',
        'M': 'ᴹ', 'N': 'ᴺ', 'O': 'ᴼ', 'P': 'ᴾ', 'Q': 'Q', 'R': 'ᴿ',
        'S': 'ˢ', 'T': 'ᵀ', 'U': 'ᵁ', 'V': 'ⱽ', 'W': 'ᵂ', 'X': 'ˣ',
        'Y': 'ʸ', 'Z': 'ᶻ',
        '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
        '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
    }

    result = "".join(tiny_map.get(c, c) for c in text)
    await update.message.reply_text(f"🔤 {result}")


@disabled_check
async def cmd_flip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Flip text upside down. Usage: /flip &lt;text&gt;"""
    text = await get_text_from_args_or_reply(update)
    if not text:
        await update.message.reply_text(
            f"🙃 {ST.bold_fancy('Usage')}: /flip &lt;text&gt;",
            parse_mode="HTML"
        )
        return

    flip_map = {
        'a': 'ɐ', 'b': 'q', 'c': 'ɔ', 'd': 'p', 'e': 'ǝ', 'f': 'ɟ',
        'g': 'ƃ', 'h': 'ɥ', 'i': 'ᴉ', 'j': 'ɾ', 'k': 'ʞ', 'l': 'l',
        'm': 'ɯ', 'n': 'u', 'o': 'o', 'p': 'd', 'q': 'b', 'r': 'ɹ',
        's': 's', 't': 'ʇ', 'u': 'n', 'v': 'ʌ', 'w': 'ʍ', 'x': 'x',
        'y': 'ʎ', 'z': 'z',
        'A': '∀', 'B': 'q', 'C': 'Ɔ', 'D': 'p', 'E': 'Ǝ', 'F': 'Ⅎ',
        'G': 'פ', 'H': 'H', 'I': 'I', 'J': 'ɾ', 'K': 'ʞ', 'L': '˥',
        'M': 'W', 'N': 'N', 'O': 'O', 'P': 'Ԁ', 'Q': 'Q', 'R': 'ɹ',
        'S': 'S', 'T': '┴', 'U': '∩', 'V': 'Λ', 'W': 'M', 'X': 'X',
        'Y': '⅄', 'Z': 'Z',
        '1': 'Ɩ', '2': 'ᄅ', '3': 'Ɛ', '4': 'ㄣ', '5': 'ϛ',
        '6': '9', '7': 'Ɫ', '8': '8', '9': '6', '0': '0',
        '.': '˙', ',': "'", "'": ',', '"': ',,', '!': '¡',
        '?': '¿', '(': ')', ')': '(', '[': ']', ']': '[',
        '{': '}', '}': '{', '<': '>', '>': '<', '_': '‾',
        '&': '⅋', '/': '\\', '\\': '/',
    }

    flipped = "".join(flip_map.get(c, c) for c in reversed(text))
    await update.message.reply_text(f"🙃 {flipped}")


@disabled_check
async def cmd_shrug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """¯\\_(ツ)_/¯"""
    await update.message.reply_text("¯\\_(ツ)_/¯")


@disabled_check
async def cmd_tableflip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """(╯°□°)╯︵ ┻━┻"""
    await update.message.reply_text("(╯°□°)╯︵ ┻━┻")


@disabled_check
async def cmd_unflip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """┬─┬ ノ( ゜-゜ノ)"""
    await update.message.reply_text("┬─┬ ノ( ゜-゜ノ)")


@disabled_check
async def cmd_lenny(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """( ͡° ͜ʖ ͡°)"""
    lennys = [
        "( ͡° ͜ʖ ͡°)", "( ͡~ ͜ʖ ͡°)", "( ͡° ͜ʖ ͡ °)", "ᕦ( ͡° ͜ʖ ͡°)ᕤ",
        "( ͡ᵔ ͜ʖ ͡ᵔ )", "( ͡°( ͡° ͜ʖ( ͡° ͜ʖ ͡°)ʖ ͡°) ͡°)", "¯\\_( ͡° ͜ʖ ͡°)_/¯",
        "( ͡° ͜ʖ ͡°)╭∩╮", "( ͠° ͟ʖ ͡°)", "(☞ ͡° ͜ʖ ͡°)☞",
    ]
    await update.message.reply_text(random.choice(lennys))


@disabled_check
async def cmd_emoji(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send random emojis. Usage: /emoji [count]"""
    args = update.message.text.split()
    count = 5

    if len(args) > 1:
        try:
            count = int(args[1])
            if count > 50:
                count = 50
            if count < 1:
                count = 1
        except ValueError:
            pass

    emoji_list = [
        "😀", "😂", "🤣", "😊", "😎", "🥳", "😍", "🤩", "😇", "🥰",
        "😋", "🤪", "😜", "🤓", "😏", "😴", "🥺", "😭", "😤", "🤯",
        "🥶", "🥵", "😱", "👻", "💀", "👽", "🤖", "💩", "🎃", "🦄",
        "🐶", "🐱", "🐼", "🐨", "🦊", "🐯", "🦁", "🐮", "🐷", "🐸",
        "🌈", "⭐", "🌙", "☀️", "🔥", "💧", "❄️", "🌊", "🌸", "🌺",
        "🎵", "🎶", "💎", "💰", "🎯", "🏆", "🎪", "🎨", "🎭", "🎬",
        "🍕", "🍔", "🌮", "🍣", "🍦", "🧁", "🍩", "🍪", "🎂", "☕",
        "❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "💕", "💖",
    ]

    result = " ".join(random.choices(emoji_list, k=count))
    await update.message.reply_text(result)


@disabled_check
async def cmd_kaomoji(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a random kaomoji."""
    kaomojis = [
        "(｡◕‿◕｡)", "(╥_╥)", "(≧◡≦)", "ʕ•ᴥ•ʔ", "(ᵔᴥᵔ)", "₍ᐢ..ᐢ₎",
        "(✿◠‿◠)", "( ˘▽˘)っ♨", "(⁀ᗢ⁀)", "(*≧▽≦)", "(☆▽☆)", "(◕ᴗ◕✿)",
        "( ´ ▽ ` )ﾉ", "┗(^0^)┓", "╰(*°▽°*)╯", "(ﾉ◕ヮ◕)ﾉ*:・ﾟ✧",
        "ヾ(⌐■_■)ノ♪", "(ง'̀-'́)ง", "ᕙ(⇀‸↼‶)ᕗ", "(づ｡◕‿‿◕｡)づ",
        "(⊃｡•́‿•̀｡)⊃", "( T_T)＼(^-^ )", "(ﾉ´ з `)ノ", "♪♪♪ ヽ(ˇ∀ˇ )ゞ",
        "(╬ Ò﹏Ó)", "( ˃̣̣̥᷄⌓˂̣̣̥᷅ )", "(｡♥‿♥｡)", "٩(◕‿◕)۶",
    ]

    await update.message.reply_text(random.choice(kaomojis))


@disabled_check
async def cmd_aesthetic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Convert text to aesthetic/fullwidth. Usage: /aesthetic &lt;text&gt;"""
    text = await get_text_from_args_or_reply(update)
    if not text:
        await update.message.reply_text(
            f"✨ {ST.bold_fancy('Usage')}: /aesthetic &lt;text&gt;",
            parse_mode="HTML"
        )
        return

    result = ""
    for char in text:
        code = ord(char)
        if 33 <= code <= 126:
            result += chr(code + 65248)
        elif char == " ":
            result += "　"
        else:
            result += char

    await update.message.reply_text(f"✨ {result}")


@disabled_check
async def cmd_fancy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Convert text to fancy font. Usage: /fancy &lt;text&gt;"""
    text = await get_text_from_args_or_reply(update)
    if not text:
        await update.message.reply_text(
            f"✦ {ST.bold_fancy('Usage')}: /fancy &lt;text&gt;",
            parse_mode="HTML"
        )
        return

    result = ST.bold_fancy(text)
    await update.message.reply_text(f"✦ {result}", parse_mode="HTML")


@disabled_check
async def cmd_smallcaps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Convert text to small caps. Usage: /smallcaps &lt;text&gt;"""
    text = await get_text_from_args_or_reply(update)
    if not text:
        await update.message.reply_text(
            f"🔤 {ST.bold_fancy('Usage')}: /smallcaps &lt;text&gt;",
            parse_mode="HTML"
        )
        return

    result = ST.small_caps(text)
    await update.message.reply_text(f"🔤 {result}")


async def get_text_from_args_or_reply(update: Update) -> str:
    """Extract text from command args or replied message."""
    message = update.message
    args = message.text.split(None, 1)

    if len(args) > 1:
        return args[1]

    if message.reply_to_message:
        return message.reply_to_message.text or message.reply_to_message.caption or ""

    return ""


# ─────────────────────────────────────────────
#  8.3  SOCIAL / REACTION COMMANDS
# ─────────────────────────────────────────────

@disabled_check
async def cmd_slap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Slap a user! Usage: /slap or reply to someone"""
    user = update.effective_user
    target = None

    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user
    else:
        args = update.message.text.split(None, 1)
        if len(args) > 1:
            # Try to find user
            target_id, target = await extract_user(update.message, context)

    if not target or target.id == user.id:
        target = update.effective_user
        user_link = get_user_link(user)
        await update.message.reply_text(
            f"🤦 {user_link} {ST.bold_fancy('slapped themselves!')}",
            parse_mode="HTML"
        )
        return

    slap_templates = [
        "{user} slapped {target} with a large trout 🐟",
        "{user} slapped {target} across the face 👋",
        "{user} threw a mass of steel at {target} 🔩",
        "{user} hit {target} with a shoe 👟",
        "{user} slapped {target} with a keyboard ⌨️",
        "{user} smacked {target} with a rubber chicken 🐔",
        "{user} threw a mass of bricks at {target} 🧱",
        "{user} slapped {target} around with a wet noodle 🍜",
        "{user} gave {target} a nice friendly slap 😏",
        "{user} karate chopped {target} 🥋",
        "{user} bonked {target} on the head 🔨",
        "{user} threw a massive pie at {target}'s face 🥧",
        "{user} launched {target} into the sun ☀️",
        "{user} yeeted {target} into orbit 🚀",
        "{user} threw {target} into a pool of jello 🟢",
    ]

    template = random.choice(slap_templates)
    text = template.replace("{user}", get_user_link(user)).replace("{target}", get_user_link(target))

    await update.message.reply_text(
        f"👋 {text}",
        parse_mode="HTML"
    )


@disabled_check
async def cmd_hug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hug someone! Usage: /hug or reply"""
    user = update.effective_user
    target = None

    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user

    if not target:
        await update.message.reply_text(
            f"🤗 {get_user_link(user)} {ST.bold_fancy('is giving virtual hugs to everyone!')} 💕",
            parse_mode="HTML"
        )
        return

    hug_texts = [
        "{user} gives {target} a warm, cozy hug! 🤗",
        "{user} squeezes {target} tight! 💝",
        "{user} wraps {target} in a blanket of love! 🧸",
        "{user} sends {target} a virtual bear hug! 🐻",
        "{user} hugs {target} like there's no tomorrow! 💕",
        "{user} gives {target} the biggest hug ever! 🫂",
        "{user} cuddles {target} gently! 🥰",
        "{user} group hugs {target}! Everyone join in! 👥💕",
    ]

    template = random.choice(hug_texts)
    text = template.replace("{user}", get_user_link(user)).replace("{target}", get_user_link(target))

    await update.message.reply_text(text, parse_mode="HTML")


@disabled_check
async def cmd_pat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pat someone! Usage: /pat or reply"""
    user = update.effective_user
    target = None

    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user

    if not target:
        await update.message.reply_text(
            f"✋ {get_user_link(user)} {ST.bold_fancy('pats the air...')} 🌬️",
            parse_mode="HTML"
        )
        return

    pat_texts = [
        "{user} gently pats {target} on the head! 🤚",
        "{user} gives {target} comforting head pats! ✋",
        "*pat pat* {target} receives pats from {user}! 💆",
        "{user} pats {target} softly! Good human! 🐾",
        "{user} gives {target} the softest pat! 😊",
    ]

    template = random.choice(pat_texts)
    text = template.replace("{user}", get_user_link(user)).replace("{target}", get_user_link(target))

    await update.message.reply_text(text, parse_mode="HTML")


@disabled_check
async def cmd_poke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Poke someone! Usage: /poke or reply"""
    user = update.effective_user
    target = None

    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user

    if not target:
        await update.message.reply_text(
            f"👆 {get_user_link(user)} {ST.bold_fancy('pokes the void!')}",
            parse_mode="HTML"
        )
        return

    poke_texts = [
        "{user} pokes {target}! 👆",
        "*poke poke* {user} won't stop poking {target}! 😤",
        "{user} gives {target} a gentle poke! 👉",
        "{user} pokes {target} with a stick 🪵",
        "Hey {target}! {user} is poking you! 👈",
    ]

    template = random.choice(poke_texts)
    text = template.replace("{user}", get_user_link(user)).replace("{target}", get_user_link(target))

    await update.message.reply_text(text, parse_mode="HTML")


@disabled_check
async def cmd_wink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wink at someone! Usage: /wink or reply"""
    user = update.effective_user
    target = None

    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user

    if not target:
        await update.message.reply_text(
            f"😉 {get_user_link(user)} {ST.bold_fancy('winks at everyone!')}",
            parse_mode="HTML"
        )
        return

    await update.message.reply_text(
        f"😉 {get_user_link(user)} {ST.bold_fancy('winks at')} {get_user_link(target)}! 💫",
        parse_mode="HTML"
    )


@disabled_check
async def cmd_kiss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a kiss! Usage: /kiss or reply"""
    user = update.effective_user
    target = None

    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user

    if not target:
        await update.message.reply_text(
            f"💋 {get_user_link(user)} {ST.bold_fancy('blows a kiss to everyone!')} 😘",
            parse_mode="HTML"
        )
        return

    await update.message.reply_text(
        f"💋 {get_user_link(user)} {ST.bold_fancy('sends a kiss to')} {get_user_link(target)}! 😘",
        parse_mode="HTML"
    )


@disabled_check
async def cmd_highfive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """High-five someone!"""
    user = update.effective_user
    target = None

    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user

    if not target:
        await update.message.reply_text(
            f"🙌 {get_user_link(user)} {ST.bold_fancy('high-fives the air!')}",
            parse_mode="HTML"
        )
        return

    await update.message.reply_text(
        f"🙌 {get_user_link(user)} {ST.bold_fancy('high-fives')} {get_user_link(target)}! ✋",
        parse_mode="HTML"
    )


@disabled_check
async def cmd_punch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Punch someone! (fun)"""
    user = update.effective_user
    target = None

    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user

    if not target:
        await update.message.reply_text(
            f"👊 {get_user_link(user)} {ST.bold_fancy('punches the air!')} 💨",
            parse_mode="HTML"
        )
        return

    punch_texts = [
        "{user} throws a falcon punch at {target}! 👊💥",
        "{user} gives {target} a friendly punch! 🤜🤛",
        "ONE PUNCH! {user} knocks out {target}! 💥",
        "{user} punches {target} with the power of friendship! ✊💕",
        "K.O.! {user} defeats {target}! 🥊",
    ]

    template = random.choice(punch_texts)
    text = template.replace("{user}", get_user_link(user)).replace("{target}", get_user_link(target))

    await update.message.reply_text(text, parse_mode="HTML")


@disabled_check
async def cmd_wave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wave at someone!"""
    user = update.effective_user
    target = None

    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user

    if not target:
        await update.message.reply_text(
            f"👋 {get_user_link(user)} {ST.bold_fancy('waves hello to everyone!')}",
            parse_mode="HTML"
        )
        return

    await update.message.reply_text(
        f"👋 {get_user_link(user)} {ST.bold_fancy('waves at')} {get_user_link(target)}!",
        parse_mode="HTML"
    )


@disabled_check
async def cmd_dance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Dance!"""
    dances = [
        "💃🕺 {user} is dancing like nobody's watching!",
        "🕺 {user} breaks out the moonwalk!",
        "💃 {user} does the macarena!",
        "🎵 {user} is vibing and dancing! 🎶",
        "🕺💃 {user} starts a dance party! Everyone join!",
        "🎶 {user} does the robot! 🤖",
        "💃 {user} does a perfect pirouette! ✨",
        "🕺 {user} is breakdancing on the floor!",
    ]

    template = random.choice(dances)
    text = template.replace("{user}", get_user_link(update.effective_user))

    await update.message.reply_text(text, parse_mode="HTML")


# ─────────────────────────────────────────────
#  8.4  GAMES
# ─────────────────────────────────────────────

@disabled_check
async def cmd_tictactoe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Play Tic-Tac-Toe! Usage: /ttt or /tictactoe"""
    user = update.effective_user
    chat = update.effective_chat

    # Create empty board
    board = ["⬜"] * 9
    game_data = {
        "board": board,
        "player": user.id,
        "player_symbol": "❌",
        "bot_symbol": "⭕",
        "turn": "player",
        "finished": False
    }

    # Store game data
    game_key = f"ttt_{chat.id}_{user.id}"
    context.bot_data[game_key] = game_data

    keyboard = build_ttt_keyboard(board, game_key)

    await update.message.reply_text(
        f"🎮 {ST.bold_fancy('Tic-Tac-Toe!')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"✧ {ST.bold_fancy('Player')}: {get_user_link(user)} (❌)\n"
        f"✧ {ST.bold_fancy('Bot')}: 🤖 (⭕)\n\n"
        f"✧ {ST.bold_fancy('Your turn!')} Tap a square!",
        parse_mode="HTML",
        reply_markup=keyboard
    )


def build_ttt_keyboard(board: list, game_key: str) -> InlineKeyboardMarkup:
    """Build Tic-Tac-Toe keyboard."""
    rows = []
    for i in range(0, 9, 3):
        row = []
        for j in range(3):
            idx = i + j
            cell = board[idx]
            callback = f"{game_key}_{idx}" if cell == "⬜" else f"ttt_noop"
            row.append(InlineKeyboardButton(text=cell, callback_data=callback))
        rows.append(row)
    return InlineKeyboardMarkup(rows)


def check_ttt_winner(board: list) -> str:
    """Check for winner. Returns symbol or None."""
    win_combos = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # cols
        [0, 4, 8], [2, 4, 6],              # diagonals
    ]

    for combo in win_combos:
        a, b, c = combo
        if board[a] == board[b] == board[c] and board[a] != "⬜":
            return board[a]

    return None


def ttt_bot_move(board: list, bot_symbol: str, player_symbol: str) -> int:
    """Simple AI for Tic-Tac-Toe."""
    # Try to win
    for i in range(9):
        if board[i] == "⬜":
            board[i] = bot_symbol
            if check_ttt_winner(board) == bot_symbol:
                board[i] = "⬜"
                return i
            board[i] = "⬜"

    # Try to block
    for i in range(9):
        if board[i] == "⬜":
            board[i] = player_symbol
            if check_ttt_winner(board) == player_symbol:
                board[i] = "⬜"
                return i
            board[i] = "⬜"

    # Take center
    if board[4] == "⬜":
        return 4

    # Take corner
    corners = [0, 2, 6, 8]
    random.shuffle(corners)
    for c in corners:
        if board[c] == "⬜":
            return c

    # Take any
    available = [i for i in range(9) if board[i] == "⬜"]
    return random.choice(available) if available else -1


async def ttt_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Tic-Tac-Toe button clicks."""
    query = update.callback_query
    data = query.data

    if data == "ttt_noop":
        await query.answer("That cell is taken!")
        return

    if not data.startswith("ttt_"):
        return

    # Parse game key and position
    parts = data.rsplit("_", 1)
    if len(parts) < 2:
        return

    game_key = parts[0]
    try:
        position = int(parts[1])
    except ValueError:
        return

    game_data = context.bot_data.get(game_key)
    if not game_data:
        await query.answer("Game expired! Start a new one with /ttt")
        return

    # Verify it's the right player
    if query.from_user.id != game_data["player"]:
        await query.answer("This is not your game!", show_alert=True)
        return

    if game_data["finished"]:
        await query.answer("Game is already over!")
        return

    board = game_data["board"]

    # Player move
    if board[position] != "⬜":
        await query.answer("Cell already taken!")
        return

    board[position] = game_data["player_symbol"]

    # Check player win
    winner = check_ttt_winner(board)
    if winner:
        game_data["finished"] = True
        keyboard = build_ttt_keyboard(board, game_key)
        await query.message.edit_text(
            f"🎮 {ST.bold_fancy('Tic-Tac-Toe')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"🎉 {ST.bold_fancy('You WIN!')} ❌\n"
            f"✧ {ST.bold_fancy('Congratulations!')} 🏆",
            parse_mode="HTML",
            reply_markup=keyboard
        )
        await query.answer("🎉 You win!")
        return

    # Check draw
    if "⬜" not in board:
        game_data["finished"] = True
        keyboard = build_ttt_keyboard(board, game_key)
        await query.message.edit_text(
            f"🎮 {ST.bold_fancy('Tic-Tac-Toe')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"🤝 {ST.bold_fancy("It's a DRAW!")}",
            parse_mode="HTML",
            reply_markup=keyboard
        )
        await query.answer("🤝 Draw!")
        return

    # Bot move
    bot_pos = ttt_bot_move(board, game_data["bot_symbol"], game_data["player_symbol"])
    if bot_pos >= 0:
        board[bot_pos] = game_data["bot_symbol"]

    # Check bot win
    winner = check_ttt_winner(board)
    if winner:
        game_data["finished"] = True
        keyboard = build_ttt_keyboard(board, game_key)
        await query.message.edit_text(
            f"🎮 {ST.bold_fancy('Tic-Tac-Toe')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"😈 {ST.bold_fancy('Bot WINS!')} ⭕\n"
            f"✧ {ST.bold_fancy('Better luck next time!')}",
            parse_mode="HTML",
            reply_markup=keyboard
        )
        await query.answer("😈 Bot wins!")
        return

    # Check draw
    if "⬜" not in board:
        game_data["finished"] = True
        keyboard = build_ttt_keyboard(board, game_key)
        await query.message.edit_text(
            f"🎮 {ST.bold_fancy('Tic-Tac-Toe')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"🤝 {ST.bold_fancy("It's a DRAW!")}",
            parse_mode="HTML",
            reply_markup=keyboard
        )
        await query.answer("🤝 Draw!")
        return

    # Continue game
    keyboard = build_ttt_keyboard(board, game_key)
    await query.message.edit_reply_markup(reply_markup=keyboard)
    await query.answer("Your turn!")


@disabled_check
async def cmd_guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Number guessing game. The bot picks 1-100, you guess!"""
    user = update.effective_user
    chat = update.effective_chat

    game_key = f"guess_{chat.id}_{user.id}"

    # Check if game already exists
    if game_key in context.bot_data:
        game = context.bot_data[game_key]
        await update.message.reply_text(
            f"🔢 {ST.bold_fancy('You already have a game running!')}\n"
            f"✧ {ST.bold_fancy('Attempts')}: {game['attempts']}\n"
            f"✧ {ST.bold_fancy('Range')}: {game['low']}-{game['high']}\n"
            f"✧ {ST.bold_fancy('Guess')}: Send a number!\n"
            f"✧ {ST.bold_fancy('Give up')}: /giveup",
            parse_mode="HTML"
        )
        return

    number = random.randint(1, 100)
    context.bot_data[game_key] = {
        "number": number,
        "attempts": 0,
        "low": 1,
        "high": 100,
        "max_attempts": 7
    }

    await update.message.reply_text(
        f"🔢 {ST.bold_fancy('Number Guessing Game!')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"✧ I've picked a number between {ST.bold_fancy('1')} and {ST.bold_fancy('100')}\n"
        f"✧ You have {ST.bold_fancy('7')} attempts to guess it!\n"
        f"✧ Just type a number to guess\n"
        f"✧ /giveup to surrender\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


async def guess_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle number guesses."""
    message = update.message
    if not message or not message.text:
        return

    text = message.text.strip()
    if not text.isdigit():
        return

    user = update.effective_user
    chat = update.effective_chat
    game_key = f"guess_{chat.id}_{user.id}"

    if game_key not in context.bot_data:
        return

    game = context.bot_data[game_key]
    guess = int(text)
    game["attempts"] += 1

    if guess == game["number"]:
        del context.bot_data[game_key]
        await message.reply_text(
            f"🎉 {ST.bold_fancy('CORRECT!')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Number')}: {game['number']}\n"
            f"✧ {ST.bold_fancy('Attempts')}: {game['attempts']}/{game['max_attempts']}\n"
            f"✧ {ST.bold_fancy('Great job!')} 🏆\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
        return

    if game["attempts"] >= game["max_attempts"]:
        del context.bot_data[game_key]
        await message.reply_text(
            f"😢 {ST.bold_fancy('Game Over!')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('The number was')}: {game['number']}\n"
            f"✧ {ST.bold_fancy('Your attempts')}: {game['attempts']}\n"
            f"✧ {ST.bold_fancy('Better luck next time!')}\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
        return

    remaining = game["max_attempts"] - game["attempts"]

    if guess < game["number"]:
        game["low"] = max(game["low"], guess + 1)
        hint = f"📈 {ST.bold_fancy('Too LOW!')} Go higher!"
    else:
        game["high"] = min(game["high"], guess - 1)
        hint = f"📉 {ST.bold_fancy('Too HIGH!')} Go lower!"

    # Temperature hint
    diff = abs(guess - game["number"])
    if diff <= 3:
        temp = "🔥 VERY HOT!"
    elif diff <= 10:
        temp = "🌡️ Warm!"
    elif diff <= 25:
        temp = "😐 Cold"
    else:
        temp = "🥶 ICE COLD!"

    await message.reply_text(
        f"{hint}\n"
        f"✧ {ST.bold_fancy('Temperature')}: {temp}\n"
        f"✧ {ST.bold_fancy('Range')}: {game['low']}-{game['high']}\n"
        f"✧ {ST.bold_fancy('Remaining')}: {remaining} attempts",
        parse_mode="HTML"
    )


@disabled_check
async def cmd_giveup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Give up the guessing game."""
    user = update.effective_user
    chat = update.effective_chat
    game_key = f"guess_{chat.id}_{user.id}"

    if game_key not in context.bot_data:
        await update.message.reply_text(
            f"❓ {ST.bold_fancy('No active game! Start with /guess')}",
            parse_mode="HTML"
        )
        return

    game = context.bot_data.pop(game_key)
    await update.message.reply_text(
        f"🏳️ {ST.bold_fancy('You gave up!')}\n"
        f"✧ {ST.bold_fancy('The number was')}: {game['number']}\n"
        f"✧ {ST.bold_fancy('Attempts used')}: {game['attempts']}",
        parse_mode="HTML"
    )


@disabled_check
async def cmd_trivia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Play trivia! Answer within 30 seconds."""
    trivia_questions = [
        {
            "q": "What is the capital of Japan?",
            "options": ["Beijing", "Tokyo", "Seoul", "Bangkok"],
            "answer": 1
        },
        {
            "q": "Which planet is known as the Red Planet?",
            "options": ["Venus", "Jupiter", "Mars", "Saturn"],
            "answer": 2
        },
        {
            "q": "What is the largest ocean on Earth?",
            "options": ["Atlantic", "Indian", "Arctic", "Pacific"],
            "answer": 3
        },
        {
            "q": "Who painted the Mona Lisa?",
            "options": ["Van Gogh", "Picasso", "Da Vinci", "Michelangelo"],
            "answer": 2
        },
        {
            "q": "What is the chemical symbol for Gold?",
            "options": ["Go", "Gd", "Au", "Ag"],
            "answer": 2
        },
        {
            "q": "How many continents are there?",
            "options": ["5", "6", "7", "8"],
            "answer": 2
        },
        {
            "q": "What is the fastest land animal?",
            "options": ["Lion", "Cheetah", "Horse", "Gazelle"],
            "answer": 1
        },
        {
            "q": "What year did World War II end?",
            "options": ["1943", "1944", "1945", "1946"],
            "answer": 2
        },
        {
            "q": "Which element has the symbol 'O'?",
            "options": ["Osmium", "Oxygen", "Oganesson", "Olivine"],
            "answer": 1
        },
        {
            "q": "What is the largest mammal?",
            "options": ["Elephant", "Blue Whale", "Giraffe", "Hippo"],
            "answer": 1
        },
        {
            "q": "Who wrote 'Romeo and Juliet'?",
            "options": ["Dickens", "Shakespeare", "Austen", "Hemingway"],
            "answer": 1
        },
        {
            "q": "What is the smallest country in the world?",
            "options": ["Monaco", "Vatican City", "San Marino", "Liechtenstein"],
            "answer": 1
        },
        {
            "q": "How many bones are in the human body?",
            "options": ["186", "206", "226", "246"],
            "answer": 1
        },
        {
            "q": "What is the hardest natural substance?",
            "options": ["Gold", "Iron", "Diamond", "Platinum"],
            "answer": 2
        },
        {
            "q": "Which gas do plants absorb?",
            "options": ["Oxygen", "Nitrogen", "Carbon Dioxide", "Hydrogen"],
            "answer": 2
        },
        {
            "q": "What is the main language spoken in Brazil?",
            "options": ["Spanish", "Portuguese", "French", "English"],
            "answer": 1
        },
        {
            "q": "How many hearts does an octopus have?",
            "options": ["1", "2", "3", "4"],
            "answer": 2
        },
        {
            "q": "What is the boiling point of water in Celsius?",
            "options": ["90°C", "100°C", "110°C", "120°C"],
            "answer": 1
        },
        {
            "q": "Which country has the most population?",
            "options": ["India", "USA", "China", "Indonesia"],
            "answer": 0  # India recently overtook
        },
        {
            "q": "What does 'HTTP' stand for?",
            "options": ["HyperText Transfer Protocol", "High Tech Transfer Protocol",
                        "HyperText Transmission Process", "High Transfer Text Protocol"],
            "answer": 0
        },
    ]

    q = random.choice(trivia_questions)
    chat = update.effective_chat

    game_key = f"trivia_{chat.id}_{update.message.message_id}"

    context.bot_data[game_key] = {
        "answer": q["answer"],
        "answered": False,
        "question": q["q"]
    }

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=f"{'🅰' if i == 0 else '🅱' if i == 1 else '🅲' if i == 2 else '🅳'} {opt}",
            callback_data=f"trivia_{game_key}_{i}"
        )] for i, opt in enumerate(q["options"])
    ])

    await update.message.reply_text(
        f"❓ {ST.bold_fancy('Trivia Time!')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"📝 {ST.bold_fancy(q['q'])}\n\n"
        f"⏱ {ST.bold_fancy('30 seconds to answer!')}\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML",
        reply_markup=keyboard
    )

    # Auto-expire after 30 seconds
    async def expire_trivia():
        await asyncio.sleep(30)
        game = context.bot_data.get(game_key)
        if game and not game["answered"]:
            game["answered"] = True
            correct = q["options"][q["answer"]]
            try:
                await update.message.reply_text(
                    f"⏰ {ST.bold_fancy("Time's up!")}\n"
                    f"✧ {ST.bold_fancy('Answer was')}: {correct}",
                    parse_mode="HTML"
                )
            except Exception:
                pass

    asyncio.create_task(expire_trivia())


async def trivia_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle trivia answer buttons."""
    query = update.callback_query
    data = query.data

    if not data.startswith("trivia_"):
        return

    parts = data.rsplit("_", 1)
    game_key = parts[0].replace("trivia_", "", 1)
    chosen = int(parts[1])

    full_game_key = f"trivia_{game_key}"

    game = context.bot_data.get(full_game_key)
    if not game:
        await query.answer("Game expired!", show_alert=True)
        return

    if game["answered"]:
        await query.answer("Already answered!", show_alert=True)
        return

    game["answered"] = True
    user = query.from_user

    if chosen == game["answer"]:
        await query.message.edit_text(
            f"✅ {ST.bold_fancy('Correct!')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"❓ {ST.bold_fancy(game['question'])}\n\n"
            f"🎉 {get_user_link(user)} {ST.bold_fancy('got it right!')} 🏆\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
        await query.answer("🎉 Correct!")
    else:
        await query.message.edit_text(
            f"❌ {ST.bold_fancy('Wrong!')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"❓ {ST.bold_fancy(game['question'])}\n\n"
            f"😢 {get_user_link(user)} {ST.bold_fancy('answered incorrectly!')}\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
        await query.answer("❌ Wrong answer!")


@disabled_check
async def cmd_wordchain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start a word chain game. Next word must start with last letter!"""
    chat = update.effective_chat
    user = update.effective_user

    game_key = f"wordchain_{chat.id}"

    starter_words = ["elephant", "guitar", "rainbow", "mountain", "dolphin",
                     "universe", "chocolate", "adventure", "butterfly", "crystal"]
    word = random.choice(starter_words)

    context.bot_data[game_key] = {
        "last_word": word,
        "used_words": {word},
        "last_player": context.bot.id,
        "score": {},
        "active": True
    }

    await update.message.reply_text(
        f"🔗 {ST.bold_fancy('Word Chain Game!')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"✧ {ST.bold_fancy('Rules')}: Say a word that starts with the\n"
        f"  last letter of the previous word!\n"
        f"✧ {ST.bold_fancy('No repeating words!')}\n"
        f"✧ {ST.bold_fancy('English words only!')}\n\n"
        f"🟢 {ST.bold_fancy('Starting word')}: {ST.bold_fancy(word.upper())}\n"
        f"  └ Next word must start with: {ST.bold_fancy(word[-1].upper())}\n\n"
        f"✧ {ST.bold_fancy('End game')}: /endchain\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


@disabled_check
async def cmd_endchain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """End the word chain game."""
    chat = update.effective_chat
    game_key = f"wordchain_{chat.id}"

    game = context.bot_data.get(game_key)
    if not game:
        await update.message.reply_text(
            f"❌ {ST.bold_fancy('No active word chain game!')}",
            parse_mode="HTML"
        )
        return

    # Build scoreboard
    scores = game.get("score", {})
    del context.bot_data[game_key]

    if scores:
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        score_text = "\n".join(
            f"  {'🥇' if i == 0 else '🥈' if i == 1 else '🥉' if i == 2 else f'{i+1}.'} "
            f"<code>{uid}</code>: {score} words"
            for i, (uid, score) in enumerate(sorted_scores)
        )
    else:
        score_text = "  No scores recorded"

    await update.message.reply_text(
        f"🔗 {ST.bold_fancy('Word Chain Ended!')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"📊 {ST.bold_fancy('Scoreboard')}:\n{score_text}\n\n"
        f"✧ {ST.bold_fancy('Words used')}: {len(game.get('used_words', set()))}\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


async def wordchain_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle word chain game messages."""
    message = update.message
    if not message or not message.text:
        return

    chat = update.effective_chat
    if chat.type == ChatType.PRIVATE:
        return

    game_key = f"wordchain_{chat.id}"
    game = context.bot_data.get(game_key)

    if not game or not game.get("active"):
        return

    text = message.text.strip().lower()

    # Only single words, no commands
    if " " in text or text.startswith("/"):
        return

    # Only alphabetic
    if not text.isalpha():
        return

    if len(text) < 2:
        return

    last_word = game["last_word"]
    required_letter = last_word[-1].lower()

    # Check if starts with correct letter
    if text[0] != required_letter:
        return  # Silently ignore wrong starts

    # Check if already used
    if text in game["used_words"]:
        await message.reply_text(
            f"❌ {ST.bold_fancy(f'\"{text}\" already used!')}",
            parse_mode="HTML"
        )
        return

    # Accept the word
    game["last_word"] = text
    game["used_words"].add(text)
    game["last_player"] = message.from_user.id

    # Update score
    uid = str(message.from_user.id)
    game["score"][uid] = game["score"].get(uid, 0) + 1

    next_letter = text[-1].upper()

    await message.reply_text(
        f"✅ {ST.bold_fancy(text.upper())} 👍\n"
        f"🔤 Next: starts with {ST.bold_fancy(next_letter)}",
        parse_mode="HTML"
    )


# ─────────────────────────────────────────────
#  8.4B  SHIP COMMAND
# ─────────────────────────────────────────────

@disabled_check
async def cmd_ship(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ship two users! Usage: /ship or /ship @user1 @user2"""
    user = update.effective_user
    msg = update.message

    if msg.reply_to_message:
        user1 = user
        user2 = msg.reply_to_message.from_user
    else:
        args = msg.text.split()[1:]
        if len(args) >= 1:
            user1 = user
            user2 = None
            # Try to find second user from mention entities
            if msg.entities:
                for entity in msg.entities:
                    if entity.type == "mention":
                        uname = msg.text[entity.offset+1:entity.offset+entity.length]
                        session = get_db()
                        try:
                            db_u = session.query(DBUser).filter(
                                func.lower(DBUser.username) == uname.lower()
                            ).first()
                            if db_u:
                                from telegram import User as TGUser
                                class FakeUser:
                                    id = db_u.user_id
                                    first_name = db_u.first_name or uname
                                    last_name = db_u.last_name
                                    username = db_u.username
                                    full_name = f"{db_u.first_name or ''} {db_u.last_name or ''}".strip() or uname
                                user2 = FakeUser()
                        finally:
                            close_db(session)
        else:
            user1 = user
            user2 = None

    if not user2:
        # Ship with random group member concept
        await msg.reply_text(
            f"💞 {ST.bold_fancy('Ship')}\n"
            f"{TPL.SEPARATOR}\n"
            f"✧ Reply to a message or mention someone to ship!\n"
            f"✧ Usage: /ship @username\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
        return

    # Generate ship score
    seed_str = f"{min(user1.id, user2.id)}{max(user1.id, user2.id)}"
    import hashlib as _hashlib
    score = int(_hashlib.md5(seed_str.encode()).hexdigest(), 16) % 101

    # Ship name
    name1 = (user1.first_name or "")[:len(user1.first_name or "")//2]
    name2 = (user2.first_name or "")[len(user2.first_name or "")//2:]
    ship_name = name1 + name2

    # Bar
    filled = int(score / 10)
    bar = "❤️" * filled + "🖤" * (10 - filled)

    if score >= 80:
        emoji = "💕💞💕"
        verdict = "Perfect match! Made for each other!"
    elif score >= 60:
        emoji = "💖"
        verdict = "Great compatibility!"
    elif score >= 40:
        emoji = "💝"
        verdict = "There's something there..."
    elif score >= 20:
        emoji = "💔"
        verdict = "Hmm, maybe just friends?"
    else:
        emoji = "😬"
        verdict = "Not really compatible..."

    name1_safe = html.escape(user1.first_name or str(user1.id))
    name2_safe = html.escape(user2.first_name or "User")

    text = (
        f"💞 {ST.bold_fancy('Ship Meter')} {emoji}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"✧ {ST.bold_fancy('User 1')}: {name1_safe}\n"
        f"✧ {ST.bold_fancy('User 2')}: {name2_safe}\n"
        f"✧ {ST.bold_fancy('Ship Name')}: {html.escape(ship_name)}\n\n"
        f"  {bar}\n"
        f"  {ST.bold_fancy('Score')}: {score}%\n\n"
        f"💬 {ST.bold_fancy(verdict)}\n"
        f"{TPL.mini_footer()}"
    )

    await msg.reply_text(text, parse_mode="HTML")


# ─────────────────────────────────────────────
#  8.5  LOVE / COMPATIBILITY METER
# ─────────────────────────────────────────────

@disabled_check
async def cmd_love(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check love compatibility! Usage: /love or reply"""
    user = update.effective_user
    target = None

    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user

    if not target:
        args = update.message.text.split(None, 1)
        if len(args) > 1:
            target_id, target = await extract_user(update.message, context)

    if not target:
        await update.message.reply_text(
            f"💕 {ST.bold_fancy('Usage')}: /love &lt;@user&gt; or reply to someone",
            parse_mode="HTML"
        )
        return

    # Generate consistent score based on both user IDs
    seed = min(user.id, target.id) * 100 + max(user.id, target.id)
    random.seed(seed)
    percentage = random.randint(0, 100)
    random.seed()  # Reset seed

    # Build heart meter
    filled = percentage // 10
    empty = 10 - filled
    meter = "❤️" * filled + "🖤" * empty

    # Status text
    if percentage >= 90:
        status = "💖 SOULMATES! Perfect Match!"
        emoji = "🥰"
    elif percentage >= 70:
        status = "💕 Great Compatibility!"
        emoji = "😍"
    elif percentage >= 50:
        status = "💛 Good Friends!"
        emoji = "😊"
    elif percentage >= 30:
        status = "🤔 It's Complicated..."
        emoji = "😐"
    elif percentage >= 10:
        status = "😅 Just Acquaintances..."
        emoji = "😬"
    else:
        status = "💔 Enemies?! 😂"
        emoji = "😂"

    await update.message.reply_text(
        f"💕 {ST.bold_fancy('Love Calculator')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"╔═══[ {ST.bold_fancy('Results')} ]═════╗\n"
        f"║ {get_user_link(user)}\n"
        f"║       ❤️\n"
        f"║ {get_user_link(target)}\n"
        f"╚════════════════╝\n\n"
        f"  {meter}\n"
        f"  {emoji} {ST.bold_fancy(f'{percentage}%')}\n\n"
        f"  {ST.bold_fancy(status)}\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


@disabled_check
async def cmd_rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Rate something! Usage: /rate &lt;thing&gt; or reply"""
    text = await get_text_from_args_or_reply(update)

    if not text:
        # Rate the user
        text = update.effective_user.first_name

    seed = hash(text.lower()) % 2**32
    random.seed(seed)
    rating = random.randint(1, 10)
    random.seed()

    stars = "⭐" * rating + "☆" * (10 - rating)

    await update.message.reply_text(
        f"⭐ {ST.bold_fancy('Rating')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"✧ {ST.bold_fancy('Subject')}: {escape_html(text[:50])}\n"
        f"✧ {ST.bold_fancy('Rating')}: {rating}/10\n"
        f"  {stars}\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


@disabled_check
async def cmd_howgay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """How gay are you? Fun meter!"""
    user = update.effective_user
    target = user

    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user

    seed = target.id * 69
    random.seed(seed)
    percentage = random.randint(0, 100)
    random.seed()

    meter = "🏳️‍🌈" * (percentage // 10) + "⬜" * (10 - percentage // 10)

    await update.message.reply_text(
        f"🏳️‍🌈 {ST.bold_fancy('Gay Meter')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"✧ {ST.bold_fancy('User')}: {get_user_link(target)}\n"
        f"✧ {ST.bold_fancy('Result')}: {percentage}%\n"
        f"  {meter}\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


@disabled_check
async def cmd_howdumb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """How dumb are you? Fun meter!"""
    user = update.effective_user
    target = user

    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user

    seed = target.id * 42
    random.seed(seed)
    percentage = random.randint(0, 100)
    random.seed()

    meter = "🧠" * (10 - percentage // 10) + "💨" * (percentage // 10)

    await update.message.reply_text(
        f"🤪 {ST.bold_fancy('Dumb Meter')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"✧ {ST.bold_fancy('User')}: {get_user_link(target)}\n"
        f"✧ {ST.bold_fancy('Result')}: {percentage}%\n"
        f"  {meter}\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


@disabled_check
async def cmd_howcute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """How cute are you?"""
    user = update.effective_user
    target = user

    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user

    seed = target.id * 777
    random.seed(seed)
    percentage = random.randint(0, 100)
    random.seed()

    meter = "🥰" * (percentage // 10) + "😐" * (10 - percentage // 10)

    await update.message.reply_text(
        f"🥰 {ST.bold_fancy('Cute Meter')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"✧ {ST.bold_fancy('User')}: {get_user_link(target)}\n"
        f"✧ {ST.bold_fancy('Cuteness')}: {percentage}%\n"
        f"  {meter}\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


# ─────────────────────────────────────────────
#  8.6  TELEGRAM DICE/EMOJI GAMES
# ─────────────────────────────────────────────

@disabled_check
async def cmd_dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Roll a Telegram dice animation."""
    await update.message.reply_dice(emoji="🎲")


@disabled_check
async def cmd_dart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Throw a dart."""
    await update.message.reply_dice(emoji="🎯")


@disabled_check
async def cmd_basketball(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shoot a basketball."""
    await update.message.reply_dice(emoji="🏀")


@disabled_check
async def cmd_football(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kick a football."""
    await update.message.reply_dice(emoji="⚽")


@disabled_check
async def cmd_bowling(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Go bowling."""
    await update.message.reply_dice(emoji="🎳")


@disabled_check
async def cmd_slot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Play slot machine."""
    await update.message.reply_dice(emoji="🎰")


# ─────────────────────────────────────────────
#  8.7  AFK SYSTEM
# ─────────────────────────────────────────────

@disabled_check
async def cmd_afk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set AFK status. Usage: /afk [reason]"""
    user = update.effective_user
    args = update.message.text.split(None, 1)
    reason = args[1] if len(args) > 1 else "No reason given"

    session = get_db()
    try:
        existing = session.query(DBAFK).filter(DBAFK.user_id == user.id).first()

        if existing:
            existing.reason = reason
            existing.since = datetime.datetime.utcnow()
            existing.is_afk = True
        else:
            afk = DBAFK(
                user_id=user.id,
                reason=reason,
                since=datetime.datetime.utcnow(),
                is_afk=True
            )
            session.add(afk)

        session.commit()

        await update.message.reply_text(
            f"😴 {get_user_link(user)} {ST.bold_fancy('is now AFK!')}\n"
            f"✧ {ST.bold_fancy('Reason')}: {escape_html(reason)}\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )

    except Exception:
        session.rollback()
    finally:
        close_db(session)


async def afk_check_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check if user is back from AFK, and notify if mentioning AFK user."""
    message = update.message
    if not message or not message.from_user:
        return

    user = message.from_user
    chat = update.effective_chat

    if chat.type == ChatType.PRIVATE:
        return

    session = get_db()
    try:
        # Check if the sender was AFK (they're back now)
        user_afk = session.query(DBAFK).filter(
            DBAFK.user_id == user.id,
            DBAFK.is_afk == True
        ).first()

        if user_afk:
            user_afk.is_afk = False
            session.commit()

            duration = datetime.datetime.utcnow() - user_afk.since if user_afk.since else None
            duration_str = format_timedelta(duration) if duration else "a while"

            await message.reply_text(
                f"👋 {get_user_link(user)} {ST.bold_fancy('is back!')}\n"
                f"✧ {ST.bold_fancy('Was AFK for')}: {duration_str}",
                parse_mode="HTML"
            )

        # Check if message mentions/replies to AFK user
        mentioned_ids = set()

        # Check reply
        if message.reply_to_message and message.reply_to_message.from_user:
            mentioned_ids.add(message.reply_to_message.from_user.id)

        # Check mentions
        if message.entities:
            for entity in message.entities:
                if entity.type == "text_mention" and entity.user:
                    mentioned_ids.add(entity.user.id)
                elif entity.type == "mention":
                    mention_text = message.text[entity.offset:entity.offset + entity.length]
                    # We'd need to look up username, skip for now
                    pass

        for mid in mentioned_ids:
            if mid == user.id:
                continue

            afk_user = session.query(DBAFK).filter(
                DBAFK.user_id == mid,
                DBAFK.is_afk == True
            ).first()

            if afk_user:
                duration = datetime.datetime.utcnow() - afk_user.since if afk_user.since else None
                duration_str = format_timedelta(duration) if duration else "a while"

                await message.reply_text(
                    f"😴 {ST.bold_fancy('This user is AFK!')}\n"
                    f"✧ {ST.bold_fancy('Reason')}: {escape_html(afk_user.reason or 'No reason')}\n"
                    f"✧ {ST.bold_fancy('Since')}: {duration_str} ago",
                    parse_mode="HTML"
                )

    except Exception as e:
        logger.error(f"AFK check error: {e}")
    finally:
        close_db(session)


# ─────────────────────────────────────────────
#  8.8  STICKER COMMANDS
# ─────────────────────────────────────────────

@disabled_check
async def cmd_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get sticker pack info. Reply to a sticker with /sticker"""
    message = update.message

    if not message.reply_to_message or not message.reply_to_message.sticker:
        await message.reply_text(
            f"🎨 {ST.bold_fancy('Reply to a sticker to get info!')}",
            parse_mode="HTML"
        )
        return

    sticker = message.reply_to_message.sticker

    text = (
        f"🎨 {ST.bold_fancy('Sticker Info')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"✧ {ST.bold_fancy('Emoji')}: {sticker.emoji or 'None'}\n"
        f"✧ {ST.bold_fancy('Pack')}: {sticker.set_name or 'No pack'}\n"
        f"✧ {ST.bold_fancy('File ID')}: <code>{sticker.file_id[:30]}...</code>\n"
        f"✧ {ST.bold_fancy('Unique ID')}: <code>{sticker.file_unique_id}</code>\n"
        f"✧ {ST.bold_fancy('Type')}: {'Animated' if sticker.is_animated else 'Video' if sticker.is_video else 'Static'}\n"
        f"✧ {ST.bold_fancy('Size')}: {sticker.width}x{sticker.height}\n"
    )

    if sticker.set_name:
        text += f"\n✧ {ST.bold_fancy('Pack link')}: https://t.me/addstickers/{sticker.set_name}"

    text += f"\n{TPL.mini_footer()}"

    await message.reply_text(text, parse_mode="HTML")


@disabled_check
async def cmd_getsticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get sticker as file. Reply to a sticker."""
    message = update.message

    if not message.reply_to_message or not message.reply_to_message.sticker:
        await message.reply_text(
            f"🎨 {ST.bold_fancy('Reply to a sticker!')}",
            parse_mode="HTML"
        )
        return

    sticker = message.reply_to_message.sticker

    if sticker.is_animated or sticker.is_video:
        await message.reply_document(
            document=sticker.file_id,
            caption=f"🎨 Sticker file\n✧ Pack: {sticker.set_name or 'None'}"
        )
    else:
        # Convert to PNG
        file = await sticker.get_file()
        file_bytes = await file.download_as_bytearray()

        await message.reply_document(
            document=bytes(file_bytes),
            filename=f"sticker_{sticker.file_unique_id}.webp",
            caption=f"🎨 Sticker file\n✧ Pack: {sticker.set_name or 'None'}"
        )


@disabled_check
async def cmd_kang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Steal/Kang a sticker to your pack. Reply to a sticker with /kang [emoji]"""
    message = update.message
    user = update.effective_user

    if not message.reply_to_message or not message.reply_to_message.sticker:
        await message.reply_text(
            f"🎨 {ST.bold_fancy('Reply to a sticker with /kang to steal it!')}",
            parse_mode="HTML"
        )
        return

    sticker = message.reply_to_message.sticker
    args = message.text.split()
    emoji = args[1] if len(args) > 1 else sticker.emoji or "🤖"

    pack_name = f"a{user.id}_by_{context.bot.username}"
    pack_title = f"{user.first_name}'s Sticker Pack"

    # Download sticker
    try:
        sticker_file = await sticker.get_file()
        sticker_data = await sticker_file.download_as_bytearray()
    except Exception as e:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Failed to download sticker: {e}')}"),
            parse_mode="HTML"
        )
        return

    # Try to add to existing pack first
    try:
        if sticker.is_animated:
            await context.bot.add_sticker_to_set(
                user_id=user.id,
                name=pack_name,
                tgs_sticker=bytes(sticker_data),
                emojis=emoji
            )
        elif sticker.is_video:
            await context.bot.add_sticker_to_set(
                user_id=user.id,
                name=pack_name,
                webm_sticker=bytes(sticker_data),
                emojis=emoji
            )
        else:
            # Resize for static stickers
            try:
                from PIL import Image
                import io

                img = Image.open(io.BytesIO(sticker_data))
                if img.width > 512 or img.height > 512:
                    img.thumbnail((512, 512))
                img_bytes = io.BytesIO()
                img.save(img_bytes, format="PNG")
                img_bytes.seek(0)
                sticker_data = img_bytes.read()
            except ImportError:
                pass

            await context.bot.add_sticker_to_set(
                user_id=user.id,
                name=pack_name,
                png_sticker=bytes(sticker_data),
                emojis=emoji
            )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                text=f"📦 {ST.bold_fancy('View Pack')}",
                url=f"https://t.me/addstickers/{pack_name}"
            )]
        ])

        await message.reply_text(
            TPL.success(f"🎨 {ST.bold_fancy('Sticker kanged!')}"),
            parse_mode="HTML",
            reply_markup=keyboard
        )

    except BadRequest as e:
        if "Stickerset_invalid" in str(e) or "STICKERSET_INVALID" in str(e):
            # Create new pack
            try:
                if sticker.is_animated:
                    await context.bot.create_new_sticker_set(
                        user_id=user.id,
                        name=pack_name,
                        title=pack_title,
                        tgs_sticker=bytes(sticker_data),
                        emojis=emoji
                    )
                elif sticker.is_video:
                    await context.bot.create_new_sticker_set(
                        user_id=user.id,
                        name=pack_name,
                        title=pack_title,
                        webm_sticker=bytes(sticker_data),
                        emojis=emoji
                    )
                else:
                    await context.bot.create_new_sticker_set(
                        user_id=user.id,
                        name=pack_name,
                        title=pack_title,
                        png_sticker=bytes(sticker_data),
                        emojis=emoji
                    )

                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                        text=f"📦 {ST.bold_fancy('View Pack')}",
                        url=f"https://t.me/addstickers/{pack_name}"
                    )]
                ])

                await message.reply_text(
                    TPL.success(f"🎨 {ST.bold_fancy('New pack created & sticker kanged!')}"),
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
            except Exception as e2:
                await message.reply_text(
                    TPL.error(f"{ST.bold_fancy(f'Failed to create pack: {e2}')}"),
                    parse_mode="HTML"
                )
        else:
            await message.reply_text(
                TPL.error(f"{ST.bold_fancy(f'Failed: {e}')}"),
                parse_mode="HTML"
            )
    except Exception as e:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )


# ─────────────────────────────────────────────
#  8.9  RANDOM ANIMAL PICTURES (API)
# ─────────────────────────────────────────────

async def fetch_animal_image(animal: str) -> str:
    """Fetch random animal image from API."""
    apis = {
        "dog": "https://dog.ceo/api/breeds/image/random",
        "cat": "https://api.thecatapi.com/v1/images/search",
        "fox": "https://randomfox.ca/floof/",
        "panda": "https://some-random-api.com/animal/panda",
        "bird": "https://some-random-api.com/animal/bird",
        "koala": "https://some-random-api.com/animal/koala",
        "raccoon": "https://some-random-api.com/animal/raccoon",
        "kangaroo": "https://some-random-api.com/animal/kangaroo",
        "whale": "https://some-random-api.com/animal/whale",
    }

    url = apis.get(animal)
    if not url:
        return None

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

                if animal == "dog":
                    return data.get("message")
                elif animal == "cat":
                    return data[0].get("url") if data else None
                elif animal == "fox":
                    return data.get("image")
                else:
                    return data.get("image")
    except Exception as e:
        logger.error(f"Animal API error ({animal}): {e}")
        return None


@disabled_check
async def cmd_dog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get a random dog picture."""
    await update.message.reply_text(
        f"🐶 {ST.bold_fancy('Fetching a good boy...')}",
        parse_mode="HTML"
    )
    image_url = await fetch_animal_image("dog")
    if image_url:
        try:
            await update.message.reply_photo(
                photo=image_url,
                caption=f"🐶 {ST.bold_fancy('Woof!')} 🐾\n{TPL.mini_footer()}",
                parse_mode="HTML"
            )
        except Exception:
            await update.message.reply_text(
                f"🐶 {ST.bold_fancy('Here!')}: {image_url}",
                parse_mode="HTML"
            )
    else:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy('Could not fetch dog image!')}"),
            parse_mode="HTML"
        )


@disabled_check
async def cmd_cat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get a random cat picture."""
    image_url = await fetch_animal_image("cat")
    if image_url:
        try:
            await update.message.reply_photo(
                photo=image_url,
                caption=f"🐱 {ST.bold_fancy('Meow!')} 🐾\n{TPL.mini_footer()}",
                parse_mode="HTML"
            )
        except Exception:
            await update.message.reply_text(f"🐱 {image_url}")
    else:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy('Could not fetch cat image!')}"),
            parse_mode="HTML"
        )


@disabled_check
async def cmd_fox(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get a random fox picture."""
    image_url = await fetch_animal_image("fox")
    if image_url:
        try:
            await update.message.reply_photo(
                photo=image_url,
                caption=f"🦊 {ST.bold_fancy('What does the fox say?')} 🐾\n{TPL.mini_footer()}",
                parse_mode="HTML"
            )
        except Exception:
            await update.message.reply_text(f"🦊 {image_url}")
    else:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy('Could not fetch fox image!')}"),
            parse_mode="HTML"
        )


@disabled_check
async def cmd_panda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get a random panda picture."""
    image_url = await fetch_animal_image("panda")
    if image_url:
        try:
            await update.message.reply_photo(
                photo=image_url,
                caption=f"🐼 {ST.bold_fancy('Panda time!')} 🎋\n{TPL.mini_footer()}",
                parse_mode="HTML"
            )
        except Exception:
            await update.message.reply_text(f"🐼 {image_url}")
    else:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy('Could not fetch panda image!')}"),
            parse_mode="HTML"
        )


@disabled_check
async def cmd_bird(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get a random bird picture."""
    image_url = await fetch_animal_image("bird")
    if image_url:
        try:
            await update.message.reply_photo(
                photo=image_url,
                caption=f"🐦 {ST.bold_fancy('Tweet tweet!')} 🕊\n{TPL.mini_footer()}",
                parse_mode="HTML"
            )
        except Exception:
            await update.message.reply_text(f"🐦 {image_url}")
    else:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy('Could not fetch bird image!')}"),
            parse_mode="HTML"
        )


# ─────────────────────────────────────────────
#  8.10  ANIME COMMANDS
# ─────────────────────────────────────────────

@disabled_check
async def cmd_waifu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get a random anime waifu image."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.waifu.pics/sfw/waifu",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    url = data.get("url")
                    if url:
                        await update.message.reply_photo(
                            photo=url,
                            caption=f"🌸 {ST.bold_fancy('Random Waifu!')} ✨\n{TPL.mini_footer()}",
                            parse_mode="HTML"
                        )
                        return
    except Exception as e:
        logger.error(f"Waifu API error: {e}")

    await update.message.reply_text(
        TPL.error(f"{ST.bold_fancy('Could not fetch waifu image!')}"),
        parse_mode="HTML"
    )


@disabled_check
async def cmd_neko(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get a random neko image."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.waifu.pics/sfw/neko",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    url = data.get("url")
                    if url:
                        await update.message.reply_photo(
                            photo=url,
                            caption=f"😺 {ST.bold_fancy('Random Neko!')} 🐾\n{TPL.mini_footer()}",
                            parse_mode="HTML"
                        )
                        return
    except Exception:
        pass

    await update.message.reply_text(
        TPL.error(f"{ST.bold_fancy('Could not fetch neko image!')}"),
        parse_mode="HTML"
    )


@disabled_check
async def cmd_anime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search anime info. Usage: /anime &lt;name&gt;"""
    args = update.message.text.split(None, 1)
    if len(args) < 2:
        await update.message.reply_text(
            f"🎌 {ST.bold_fancy('Usage')}: /anime &lt;anime_name&gt;\n"
            f"✧ {ST.bold_fancy('Example')}: /anime Naruto",
            parse_mode="HTML"
        )
        return

    query_text = args[1].strip()

    try:
        # Using Jikan API (MyAnimeList)
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.jikan.moe/v4/anime?q={query_text}&limit=1",
                timeout=aiohttp.ClientTimeout(total=15)
            ) as resp:
                if resp.status != 200:
                    await update.message.reply_text(
                        TPL.error(f"{ST.bold_fancy('API error!')}"),
                        parse_mode="HTML"
                    )
                    return

                data = await resp.json()
                results = data.get("data", [])

                if not results:
                    await update.message.reply_text(
                        TPL.error(f"{ST.bold_fancy('Anime not found!')}"),
                        parse_mode="HTML"
                    )
                    return

                anime = results[0]

                title = anime.get("title", "Unknown")
                title_jp = anime.get("title_japanese", "")
                synopsis = anime.get("synopsis", "No synopsis available")
                if len(synopsis) > 500:
                    synopsis = synopsis[:500] + "..."

                score = anime.get("score", "N/A")
                episodes = anime.get("episodes", "N/A")
                status = anime.get("status", "Unknown")
                anime_type = anime.get("type", "Unknown")
                source = anime.get("source", "Unknown")
                rating = anime.get("rating", "Unknown")
                url = anime.get("url", "")
                image_url = anime.get("images", {}).get("jpg", {}).get("large_image_url", "")

                genres = ", ".join(g.get("name", "") for g in anime.get("genres", []))
                studios = ", ".join(s.get("name", "") for s in anime.get("studios", []))

                text = (
                    f"🎌 {ST.bold_fancy('Anime Info')}\n"
                    f"{TPL.SEPARATOR}\n\n"
                    f"╔═══[ {ST.bold_fancy(escape_html(title))} ]═════╗\n"
                    f"║ ✧ {ST.bold_fancy('Japanese')}: {escape_html(title_jp)}\n"
                    f"║ ✧ {ST.bold_fancy('Type')}: {anime_type}\n"
                    f"║ ✧ {ST.bold_fancy('Episodes')}: {episodes}\n"
                    f"║ ✧ {ST.bold_fancy('Score')}: ⭐ {score}\n"
                    f"║ ✧ {ST.bold_fancy('Status')}: {status}\n"
                    f"║ ✧ {ST.bold_fancy('Source')}: {source}\n"
                    f"║ ✧ {ST.bold_fancy('Rating')}: {escape_html(rating)}\n"
                    f"║ ✧ {ST.bold_fancy('Genres')}: {escape_html(genres or 'N/A')}\n"
                    f"║ ✧ {ST.bold_fancy('Studios')}: {escape_html(studios or 'N/A')}\n"
                    f"╚════════════════╝\n\n"
                    f"📖 {ST.bold_fancy('Synopsis')}:\n{escape_html(synopsis)}\n"
                    f"{TPL.mini_footer()}"
                )

                keyboard = None
                if url:
                    keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton(
                            text=f"🔗 {ST.bold_fancy('MyAnimeList')}",
                            url=url
                        )]
                    ])

                if image_url:
                    try:
                        await update.message.reply_photo(
                            photo=image_url,
                            caption=text[:1024],
                            parse_mode="HTML",
                            reply_markup=keyboard
                        )
                        return
                    except Exception:
                        pass

                await update.message.reply_text(
                    text,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )

    except Exception as e:
        logger.error(f"Anime search error: {e}")
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )


@disabled_check
async def cmd_manga(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search manga info. Usage: /manga &lt;name&gt;"""
    args = update.message.text.split(None, 1)
    if len(args) < 2:
        await update.message.reply_text(
            f"📚 {ST.bold_fancy('Usage')}: /manga &lt;manga_name&gt;",
            parse_mode="HTML"
        )
        return

    query_text = args[1].strip()

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.jikan.moe/v4/manga?q={query_text}&limit=1",
                timeout=aiohttp.ClientTimeout(total=15)
            ) as resp:
                if resp.status != 200:
                    await update.message.reply_text(
                        TPL.error(f"{ST.bold_fancy('API error!')}"),
                        parse_mode="HTML"
                    )
                    return

                data = await resp.json()
                results = data.get("data", [])

                if not results:
                    await update.message.reply_text(
                        TPL.error(f"{ST.bold_fancy('Manga not found!')}"),
                        parse_mode="HTML"
                    )
                    return

                manga = results[0]

                title = manga.get("title", "Unknown")
                synopsis = manga.get("synopsis", "No synopsis")
                if len(synopsis) > 500:
                    synopsis = synopsis[:500] + "..."

                score = manga.get("score", "N/A")
                chapters = manga.get("chapters", "N/A")
                volumes = manga.get("volumes", "N/A")
                status = manga.get("status", "Unknown")
                url = manga.get("url", "")
                image_url = manga.get("images", {}).get("jpg", {}).get("large_image_url", "")

                genres = ", ".join(g.get("name", "") for g in manga.get("genres", []))

                text = (
                    f"📚 {ST.bold_fancy('Manga Info')}\n"
                    f"{TPL.SEPARATOR}\n\n"
                    f"╔═══[ {ST.bold_fancy(escape_html(title))} ]═════╗\n"
                    f"║ ✧ {ST.bold_fancy('Score')}: ⭐ {score}\n"
                    f"║ ✧ {ST.bold_fancy('Chapters')}: {chapters}\n"
                    f"║ ✧ {ST.bold_fancy('Volumes')}: {volumes}\n"
                    f"║ ✧ {ST.bold_fancy('Status')}: {status}\n"
                    f"║ ✧ {ST.bold_fancy('Genres')}: {escape_html(genres or 'N/A')}\n"
                    f"╚════════════════╝\n\n"
                    f"📖 {escape_html(synopsis)}\n"
                    f"{TPL.mini_footer()}"
                )

                keyboard = None
                if url:
                    keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton(
                            text=f"🔗 {ST.bold_fancy('MyAnimeList')}",
                            url=url
                        )]
                    ])

                if image_url:
                    try:
                        await update.message.reply_photo(
                            photo=image_url,
                            caption=text[:1024],
                            parse_mode="HTML",
                            reply_markup=keyboard
                        )
                        return
                    except Exception:
                        pass

                await update.message.reply_text(
                    text, parse_mode="HTML", reply_markup=keyboard
                )

    except Exception as e:
        logger.error(f"Manga search error: {e}")
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )


# ─────────────────────────────────────────────
#  8.11  WOULD YOU RATHER
# ─────────────────────────────────────────────

@disabled_check
async def cmd_wyr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Would you rather game!"""
    wyr_list = [
        ("Have the ability to fly", "Have the ability to read minds"),
        ("Be invisible", "Be able to teleport"),
        ("Live without music", "Live without movies"),
        ("Always be cold", "Always be hot"),
        ("Be the funniest person", "Be the smartest person"),
        ("Have unlimited money", "Have unlimited time"),
        ("Never use social media again", "Never watch movies/TV again"),
        ("Be able to speak all languages", "Be able to play all instruments"),
        ("Have a rewind button for life", "Have a pause button for life"),
        ("Live in the past", "Live in the future"),
        ("Always know when someone is lying", "Always get away with lying"),
        ("Have x-ray vision", "Have super hearing"),
        ("Be famous", "Be rich"),
        ("Live on the moon", "Live under the sea"),
        ("Have a personal chef", "Have a personal driver"),
        ("Never sleep again", "Never eat again"),
        ("Be a superhero", "Be a supervillain"),
        ("Have 100 close friends", "Have 1 best friend"),
        ("Always be 10 minutes late", "Always be 20 minutes early"),
        ("Know how you will die", "Know when you will die"),
    ]

    option_a, option_b = random.choice(wyr_list)

    game_key = f"wyr_{update.effective_chat.id}_{update.message.message_id}"
    context.bot_data[game_key] = {"a": 0, "b": 0, "voters": set()}

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=f"🅰 {option_a} (0)",
            callback_data=f"wyr_a_{game_key}"
        )],
        [InlineKeyboardButton(
            text=f"🅱 {option_b} (0)",
            callback_data=f"wyr_b_{game_key}"
        )]
    ])

    await update.message.reply_text(
        f"🤔 {ST.bold_fancy('Would You Rather...')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"🅰 {ST.bold_fancy(option_a)}\n\n"
        f"           {ST.bold_fancy('OR')}\n\n"
        f"🅱 {ST.bold_fancy(option_b)}\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML",
        reply_markup=keyboard
    )


async def wyr_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Would You Rather votes."""
    query = update.callback_query
    data = query.data

    if not data.startswith("wyr_"):
        return

    parts = data.split("_", 2)
    if len(parts) < 3:
        return

    choice = parts[1]  # "a" or "b"
    game_key = parts[2]

    game = context.bot_data.get(game_key)
    if not game:
        await query.answer("Game expired!")
        return

    user_id = query.from_user.id

    if user_id in game.get("voters", set()):
        await query.answer("You already voted!", show_alert=True)
        return

    game["voters"].add(user_id)
    game[choice] += 1

    # Update button counts
    current_markup = query.message.reply_markup
    if current_markup:
        new_buttons = []
        for row in current_markup.inline_keyboard:
            new_row = []
            for btn in row:
                btn_data = btn.callback_data
                if btn_data.startswith(f"wyr_a_"):
                    text = btn.text.rsplit("(", 1)[0] + f"({game['a']})"
                    new_row.append(InlineKeyboardButton(text=text, callback_data=btn_data))
                elif btn_data.startswith(f"wyr_b_"):
                    text = btn.text.rsplit("(", 1)[0] + f"({game['b']})"
                    new_row.append(InlineKeyboardButton(text=text, callback_data=btn_data))
                else:
                    new_row.append(btn)
            new_buttons.append(new_row)

        try:
            await query.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup(new_buttons)
            )
        except Exception:
            pass

    await query.answer(f"You chose {'A' if choice == 'a' else 'B'}! ✅")


# ─────────────────────────────────────────────
#  8.12  POLL CREATION SHORTCUT
# ─────────────────────────────────────────────

@disabled_check
async def cmd_poll_create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quick poll creation. Usage: /poll &lt;question&gt; | &lt;option1&gt; | &lt;option2&gt; | ..."""
    args = update.message.text.split(None, 1)

    if len(args) < 2:
        await update.message.reply_text(
            f"📊 {ST.bold_fancy('Create Poll')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Usage')}: /poll &lt;question&gt; | &lt;opt1&gt; | &lt;opt2&gt; | ...\n"
            f"✧ {ST.bold_fancy('Example')}: /poll Best fruit? | Apple | Banana | Mango\n"
            f"✧ {ST.bold_fancy('Min')}: 2 options, {ST.bold_fancy('Max')}: 10 options",
            parse_mode="HTML"
        )
        return

    parts = [p.strip() for p in args[1].split("|") if p.strip()]

    if len(parts) < 3:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy('Need at least a question and 2 options!')}\n"
                      f"✧ Separate with | symbol"),
            parse_mode="HTML"
        )
        return

    question = parts[0]
    options = parts[1:10]  # Max 10 options

    try:
        await context.bot.send_poll(
            chat_id=update.effective_chat.id,
            question=question,
            options=options,
            is_anonymous=True
        )
    except Exception as e:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Failed: {e}')}"),
            parse_mode="HTML"
        )


# ─────────────────────────────────────────────
#  8.13  DB MODEL FOR AFK
# ─────────────────────────────────────────────

"""
Required DB Model:

class DBAFK(Base):
    __tablename__ = "afk"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, unique=True, nullable=False)
    reason = Column(Text, default="AFK")
    since = Column(DateTime, default=datetime.datetime.utcnow)
    is_afk = Column(Boolean, default=True)
"""


# ─────────────────────────────────────────────
#  8.14  REGISTER SECTION 8 HANDLERS
# ─────────────────────────────────────────────

def register_section8_handlers(app):
    """Register all Section 8 (Fun/Games) handlers."""

    # ── Text Fun ──
    app.add_handler(CommandHandler("runs", cmd_runs))
    app.add_handler(CommandHandler("insult", cmd_insult))
    app.add_handler(CommandHandler("truth", cmd_truth))
    app.add_handler(CommandHandler("dare", cmd_dare))
    app.add_handler(CommandHandler("roll", cmd_roll))
    app.add_handler(CommandHandler("flip", cmd_flip_coin))
    app.add_handler(CommandHandler("flipcoin", cmd_flip_coin))
    app.add_handler(CommandHandler("coin", cmd_flip_coin))
    app.add_handler(CommandHandler("rps", cmd_rps))
    app.add_handler(CommandHandler("8ball", cmd_8ball))
    app.add_handler(CommandHandler("decide", cmd_decide))
    app.add_handler(CommandHandler("choose", cmd_decide))
    app.add_handler(CommandHandler("quote", cmd_quote))
    app.add_handler(CommandHandler("fact", cmd_fact))
    app.add_handler(CommandHandler("joke", cmd_joke))

    # ── Text Formatting ──
    app.add_handler(CommandHandler("reverse", cmd_reverse))
    app.add_handler(CommandHandler("mock", cmd_mock))
    app.add_handler(CommandHandler("vapor", cmd_vapor))
    app.add_handler(CommandHandler("vaporwave", cmd_vapor))
    app.add_handler(CommandHandler("clap", cmd_clap))
    app.add_handler(CommandHandler("tiny", cmd_tiny))
    app.add_handler(CommandHandler("fliptext", cmd_flip))
    app.add_handler(CommandHandler("shrug", cmd_shrug))
    app.add_handler(CommandHandler("tableflip", cmd_tableflip))
    app.add_handler(CommandHandler("unflip", cmd_unflip))
    app.add_handler(CommandHandler("lenny", cmd_lenny))
    app.add_handler(CommandHandler("emoji", cmd_emoji))
    app.add_handler(CommandHandler("kaomoji", cmd_kaomoji))
    app.add_handler(CommandHandler("aesthetic", cmd_aesthetic))
    app.add_handler(CommandHandler("fancy", cmd_fancy))
    app.add_handler(CommandHandler("smallcaps", cmd_smallcaps))

    # ── Social / Reactions ──
    app.add_handler(CommandHandler("slap", cmd_slap))
    app.add_handler(CommandHandler("hug", cmd_hug))
    app.add_handler(CommandHandler("pat", cmd_pat))
    app.add_handler(CommandHandler("poke", cmd_poke))
    app.add_handler(CommandHandler("wink", cmd_wink))
    app.add_handler(CommandHandler("kiss", cmd_kiss))
    app.add_handler(CommandHandler("highfive", cmd_highfive))
    app.add_handler(CommandHandler("punch", cmd_punch))
    app.add_handler(CommandHandler("wave", cmd_wave))
    app.add_handler(CommandHandler("dance", cmd_dance))

    # ── Games ──
    app.add_handler(CommandHandler(["ttt", "tictactoe"], cmd_tictactoe))
    app.add_handler(CommandHandler("guess", cmd_guess))
    app.add_handler(CommandHandler("giveup", cmd_giveup))
    app.add_handler(CommandHandler("trivia", cmd_trivia))
    app.add_handler(CommandHandler("wyr", cmd_wyr))
    app.add_handler(CommandHandler("wordchain", cmd_wordchain))
    app.add_handler(CommandHandler("endchain", cmd_endchain))
    app.add_handler(CommandHandler("poll", cmd_poll_create))

    # ── Love / Meters ──
    app.add_handler(CommandHandler("ship", cmd_ship))
    app.add_handler(CommandHandler("love", cmd_love))
    app.add_handler(CommandHandler("rate", cmd_rate))
    app.add_handler(CommandHandler("howgay", cmd_howgay))
    app.add_handler(CommandHandler("howdumb", cmd_howdumb))
    app.add_handler(CommandHandler("howcute", cmd_howcute))

    # ── Telegram Dice ──
    app.add_handler(CommandHandler("dice", cmd_dice))
    app.add_handler(CommandHandler("dart", cmd_dart))
    app.add_handler(CommandHandler("basketball", cmd_basketball))
    app.add_handler(CommandHandler("football", cmd_football))
    app.add_handler(CommandHandler("bowling", cmd_bowling))
    app.add_handler(CommandHandler("slot", cmd_slot))

    # ── AFK ──
    app.add_handler(CommandHandler("afk", cmd_afk))
    app.add_handler(CommandHandler("brb", cmd_afk))

    # ── Stickers ──
    app.add_handler(CommandHandler("sticker", cmd_sticker))
    app.add_handler(CommandHandler("stickerinfo", cmd_sticker))
    app.add_handler(CommandHandler("getsticker", cmd_getsticker))
    app.add_handler(CommandHandler("kang", cmd_kang))
    app.add_handler(CommandHandler("steal", cmd_kang))

    # ── Animal Images ──
    app.add_handler(CommandHandler("dog", cmd_dog))
    app.add_handler(CommandHandler("cat", cmd_cat))
    app.add_handler(CommandHandler("fox", cmd_fox))
    app.add_handler(CommandHandler("panda", cmd_panda))
    app.add_handler(CommandHandler("bird", cmd_bird))

    # ── Anime ──
    app.add_handler(CommandHandler("waifu", cmd_waifu))
    app.add_handler(CommandHandler("neko", cmd_neko))
    app.add_handler(CommandHandler("anime", cmd_anime))
    app.add_handler(CommandHandler("manga", cmd_manga))

    # ── Callback Handlers ──
    app.add_handler(CallbackQueryHandler(rps_callback, pattern=r"^rps_"))
    app.add_handler(CallbackQueryHandler(ttt_callback, pattern=r"^ttt_"))
    app.add_handler(CallbackQueryHandler(trivia_callback, pattern=r"^trivia_"))
    app.add_handler(CallbackQueryHandler(wyr_callback, pattern=r"^wyr_"))

    # ── Message Handlers (AFK check, guess game, word chain) ──
    app.add_handler(MessageHandler(
        filters.ALL & ~filters.COMMAND & filters.ChatType.GROUPS,
        afk_check_handler
    ), group=20)

    # Number guess handler (only digits in groups where game is active)
    app.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(r'^\d+$') & filters.ChatType.GROUPS,
        guess_handler
    ), group=21)

    # Word chain handler
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.GROUPS,
        wordchain_handler
    ), group=22)

    logger.info("✅ Section 8 handlers registered: Fun, Games, Reactions, "
                "Stickers, Animals, Anime, AFK, Meters")


# ═══════════════════════════════════════════════════════════════
# END OF SECTION 8
# ═══════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════
# ██╗  SECTION 9: UTILITIES / TOOLS / API INTEGRATIONS
# ═══════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────
#  9.1  TRANSLATION
# ─────────────────────────────────────────────

LANGUAGE_CODES = {
    "en": "English", "hi": "Hindi", "es": "Spanish", "fr": "French",
    "de": "German", "it": "Italian", "pt": "Portuguese", "ru": "Russian",
    "ja": "Japanese", "ko": "Korean", "zh": "Chinese", "ar": "Arabic",
    "tr": "Turkish", "nl": "Dutch", "sv": "Swedish", "pl": "Polish",
    "th": "Thai", "vi": "Vietnamese", "id": "Indonesian", "ms": "Malay",
    "bn": "Bengali", "ta": "Tamil", "te": "Telugu", "mr": "Marathi",
    "ur": "Urdu", "pa": "Punjabi", "gu": "Gujarati", "kn": "Kannada",
    "ml": "Malayalam", "ne": "Nepali", "si": "Sinhala", "my": "Burmese",
    "uk": "Ukrainian", "cs": "Czech", "ro": "Romanian", "hu": "Hungarian",
    "el": "Greek", "he": "Hebrew", "fa": "Persian", "sw": "Swahili",
    "fil": "Filipino", "af": "Afrikaans", "am": "Amharic", "az": "Azerbaijani",
    "be": "Belarusian", "bg": "Bulgarian", "ca": "Catalan", "hr": "Croatian",
    "da": "Danish", "et": "Estonian", "fi": "Finnish", "ka": "Georgian",
    "is": "Icelandic", "lv": "Latvian", "lt": "Lithuanian", "mk": "Macedonian",
    "no": "Norwegian", "sk": "Slovak", "sl": "Slovenian", "sq": "Albanian",
    "sr": "Serbian", "uz": "Uzbek", "zu": "Zulu",
}


@disabled_check
async def cmd_translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Translate text. Usage: /tr &lt;lang&gt; &lt;text&gt; or reply with /tr &lt;lang&gt;
    Example: /tr hi Hello World
    """
    message = update.message
    args = message.text.split(None, 2)

    if len(args) < 2:
        # Show supported languages
        lang_list = "\n".join(
            f"  <code>{code}</code> → {name}"
            for code, name in sorted(LANGUAGE_CODES.items())[:30]
        )

        await message.reply_text(
            f"🌐 {ST.bold_fancy('Translate')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Usage')}: /tr &lt;lang_code&gt; &lt;text&gt;\n"
            f"✧ {ST.bold_fancy('Reply')}: Reply to msg with /tr &lt;lang&gt;\n"
            f"✧ {ST.bold_fancy('Example')}: /tr hi Hello World\n"
            f"✧ {ST.bold_fancy('Auto detect')}: /tr en &lt;any text&gt;\n\n"
            f"📋 {ST.bold_fancy('Popular Languages')}:\n{lang_list}\n"
            f"  ... and {len(LANGUAGE_CODES) - 30} more\n"
            f"✧ {ST.bold_fancy('Full list')}: /langs\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
        return

    target_lang = args[1].lower().strip()

    # Get source text
    source_text = None
    if message.reply_to_message:
        source_text = message.reply_to_message.text or message.reply_to_message.caption
        if len(args) > 2:
            source_text = args[2]
    elif len(args) > 2:
        source_text = args[2]

    if not source_text:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('Please provide text to translate!')}"),
            parse_mode="HTML"
        )
        return

    if target_lang not in LANGUAGE_CODES and len(target_lang) > 3:
        # Maybe the user forgot to put lang code
        target_lang = "en"
        source_text = " ".join(args[1:])

    # Use free translation API
    translated_text = await translate_text(source_text, target_lang)

    if translated_text:
        lang_name = LANGUAGE_CODES.get(target_lang, target_lang.upper())

        await message.reply_text(
            f"🌐 {ST.bold_fancy('Translation')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"╔═══[ {ST.bold_fancy('Result')} ]═════╗\n"
            f"║ ✧ {ST.bold_fancy('To')}: {lang_name} ({target_lang})\n"
            f"╚════════════════╝\n\n"
            f"📝 {ST.bold_fancy('Original')}:\n{escape_html(source_text[:500])}\n\n"
            f"🌍 {ST.bold_fancy('Translated')}:\n{escape_html(translated_text[:2000])}\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
    else:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('Translation failed! Try again later.')}"),
            parse_mode="HTML"
        )


async def translate_text(text: str, target_lang: str, source_lang: str = "auto") -> str:
    """Translate text using free API."""
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": source_lang,
            "tl": target_lang,
            "dt": "t",
            "q": text
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params,
                                   timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data and data[0]:
                        translated = "".join(
                            part[0] for part in data[0] if part[0]
                        )
                        return translated
    except Exception as e:
        logger.error(f"Translation error: {e}")

    return None


@disabled_check
async def cmd_langs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all supported languages."""
    lang_list = "\n".join(
        f"  <code>{code}</code> → {name}"
        for code, name in sorted(LANGUAGE_CODES.items())
    )

    # Split into chunks if too long
    text = (
        f"🌐 {ST.bold_fancy('Supported Languages')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"{lang_list}\n\n"
        f"{ST.bold_fancy('Total')}: {len(LANGUAGE_CODES)} languages\n"
        f"{TPL.mini_footer()}"
    )

    if len(text) > 4096:
        # Split into parts
        parts = []
        current = f"🌐 {ST.bold_fancy('Languages (Part {{part}})')}\n{TPL.SEPARATOR}\n\n"
        items = sorted(LANGUAGE_CODES.items())

        for i, (code, name) in enumerate(items):
            line = f"  <code>{code}</code> → {name}\n"
            if len(current) + len(line) > 3800:
                parts.append(current)
                current = ""
            current += line

        if current:
            parts.append(current)

        for j, part in enumerate(parts, 1):
            header = f"🌐 {ST.bold_fancy(f'Languages (Part {j}/{len(parts)})')}\n{TPL.SEPARATOR}\n\n"
            await update.message.reply_text(
                header + part + TPL.mini_footer(),
                parse_mode="HTML"
            )
    else:
        await update.message.reply_text(text, parse_mode="HTML")


# ─────────────────────────────────────────────
#  9.2  TEXT TO SPEECH (TTS)
# ─────────────────────────────────────────────

@disabled_check
async def cmd_tts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Text to speech. Usage: /tts [lang] &lt;text&gt;
    Example: /tts Hello World
    Example: /tts hi नमस्ते
    """
    message = update.message
    args = message.text.split(None, 2)

    if len(args) < 2:
        text_to_speak = None
        if message.reply_to_message:
            text_to_speak = message.reply_to_message.text or message.reply_to_message.caption
        if not text_to_speak:
            await message.reply_text(
                f"🔊 {ST.bold_fancy('Text to Speech')}\n"
                f"✧ {ST.bold_fancy('Usage')}: /tts &lt;text&gt;\n"
                f"✧ {ST.bold_fancy('With lang')}: /tts hi &lt;text&gt;\n"
                f"✧ {ST.bold_fancy('Reply')}: Reply to msg with /tts",
                parse_mode="HTML"
            )
            return
    else:
        text_to_speak = None

    lang = "en"

    if not text_to_speak:
        if message.reply_to_message and len(args) < 3:
            text_to_speak = message.reply_to_message.text or message.reply_to_message.caption
            if len(args) > 1 and args[1].lower() in LANGUAGE_CODES:
                lang = args[1].lower()
            elif len(args) > 1:
                text_to_speak = args[1]
        elif len(args) >= 3 and args[1].lower() in LANGUAGE_CODES:
            lang = args[1].lower()
            text_to_speak = args[2]
        elif len(args) >= 2:
            text_to_speak = " ".join(args[1:])

    if not text_to_speak:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('No text to convert!')}"),
            parse_mode="HTML"
        )
        return

    if len(text_to_speak) > 500:
        text_to_speak = text_to_speak[:500]

    try:
        tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={text_to_speak}&tl={lang}&client=tw-ob"

        async with aiohttp.ClientSession() as session:
            async with session.get(tts_url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    audio_data = await resp.read()

                    await message.reply_voice(
                        voice=audio_data,
                        caption=f"🔊 {ST.bold_fancy('TTS')} ({LANGUAGE_CODES.get(lang, lang)})",
                        parse_mode="HTML"
                    )
                    return

        # Fallback: try gtts if available
        try:
            from gtts import gTTS
            import io

            tts = gTTS(text=text_to_speak, lang=lang)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)

            await message.reply_voice(
                voice=fp,
                caption=f"🔊 {ST.bold_fancy('TTS')} ({LANGUAGE_CODES.get(lang, lang)})",
                parse_mode="HTML"
            )
        except ImportError:
            await message.reply_text(
                TPL.error(f"{ST.bold_fancy('TTS service unavailable!')}"),
                parse_mode="HTML"
            )

    except Exception as e:
        logger.error(f"TTS error: {e}")
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'TTS failed: {e}')}"),
            parse_mode="HTML"
        )


# ─────────────────────────────────────────────
#  9.3  DICTIONARY / URBAN DICTIONARY
# ─────────────────────────────────────────────

@disabled_check
async def cmd_ud(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Urban Dictionary lookup. Usage: /ud &lt;word&gt;"""
    args = update.message.text.split(None, 1)

    if len(args) < 2:
        await update.message.reply_text(
            f"📖 {ST.bold_fancy('Urban Dictionary')}\n"
            f"✧ {ST.bold_fancy('Usage')}: /ud &lt;word or phrase&gt;",
            parse_mode="HTML"
        )
        return

    word = args[1].strip()

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.urbandictionary.com/v0/define?term={word}",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status != 200:
                    await update.message.reply_text(
                        TPL.error(f"{ST.bold_fancy('API error!')}"),
                        parse_mode="HTML"
                    )
                    return

                data = await resp.json()
                definitions = data.get("list", [])

                if not definitions:
                    await update.message.reply_text(
                        TPL.error(f"{ST.bold_fancy(f'No definition found for \"{word}\"!')}"),
                        parse_mode="HTML"
                    )
                    return

                defn = definitions[0]
                definition_text = defn.get("definition", "No definition")
                example = defn.get("example", "No example")
                thumbs_up = defn.get("thumbs_up", 0)
                thumbs_down = defn.get("thumbs_down", 0)
                author = defn.get("author", "Unknown")
                permalink = defn.get("permalink", "")

                # Clean brackets
                definition_text = definition_text.replace("[", "").replace("]", "")
                example = example.replace("[", "").replace("]", "")

                if len(definition_text) > 1000:
                    definition_text = definition_text[:1000] + "..."
                if len(example) > 500:
                    example = example[:500] + "..."

                text = (
                    f"📖 {ST.bold_fancy('Urban Dictionary')}\n"
                    f"{TPL.SEPARATOR}\n\n"
                    f"╔═══[ {ST.bold_fancy(escape_html(word))} ]═════╗\n"
                    f"║ ✧ {ST.bold_fancy('Author')}: {escape_html(author)}\n"
                    f"║ ✧ 👍 {thumbs_up} | 👎 {thumbs_down}\n"
                    f"╚════════════════╝\n\n"
                    f"📝 {ST.bold_fancy('Definition')}:\n{escape_html(definition_text)}\n\n"
                    f"💬 {ST.bold_fancy('Example')}:\n<i>{escape_html(example)}</i>\n"
                    f"{TPL.mini_footer()}"
                )

                keyboard = None
                if permalink:
                    keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton(
                            text=f"🔗 {ST.bold_fancy('View on UD')}",
                            url=permalink
                        )]
                    ])

                if len(definitions) > 1:
                    text += f"\n✧ {ST.bold_fancy(f'{len(definitions)} more definitions available')}"

                await update.message.reply_text(
                    text, parse_mode="HTML", reply_markup=keyboard
                )

    except Exception as e:
        logger.error(f"UD error: {e}")
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )


@disabled_check
async def cmd_define(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Dictionary definition. Usage: /define &lt;word&gt;"""
    args = update.message.text.split(None, 1)

    if len(args) < 2:
        await update.message.reply_text(
            f"📚 {ST.bold_fancy('Usage')}: /define &lt;word&gt;",
            parse_mode="HTML"
        )
        return

    word = args[1].strip()

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status != 200:
                    await update.message.reply_text(
                        TPL.error(f"{ST.bold_fancy(f'Word \"{word}\" not found!')}"),
                        parse_mode="HTML"
                    )
                    return

                data = await resp.json()
                entry = data[0] if data else None

                if not entry:
                    return

                word_text = entry.get("word", word)
                phonetic = entry.get("phonetic", "")
                meanings = entry.get("meanings", [])

                text = (
                    f"📚 {ST.bold_fancy('Dictionary')}\n"
                    f"{TPL.SEPARATOR}\n\n"
                    f"📖 {ST.bold_fancy(escape_html(word_text))}"
                )

                if phonetic:
                    text += f" [{escape_html(phonetic)}]"

                text += "\n\n"

                for meaning in meanings[:3]:
                    part_of_speech = meaning.get("partOfSpeech", "")
                    definitions = meaning.get("definitions", [])

                    text += f"🔹 {ST.bold_fancy(part_of_speech.title())}:\n"

                    for i, defn in enumerate(definitions[:3], 1):
                        definition = defn.get("definition", "")
                        example = defn.get("example", "")

                        text += f"  {i}. {escape_html(definition)}\n"
                        if example:
                            text += f"     💬 <i>{escape_html(example)}</i>\n"

                    synonyms = meaning.get("synonyms", [])
                    if synonyms:
                        text += f"  🔗 {ST.bold_fancy('Synonyms')}: {', '.join(synonyms[:5])}\n"

                    antonyms = meaning.get("antonyms", [])
                    if antonyms:
                        text += f"  🔗 {ST.bold_fancy('Antonyms')}: {', '.join(antonyms[:5])}\n"

                    text += "\n"

                text += TPL.mini_footer()

                await update.message.reply_text(text, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Define error: {e}")
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )


# ─────────────────────────────────────────────
#  9.4  WIKIPEDIA
# ─────────────────────────────────────────────

@disabled_check
async def cmd_wiki(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wikipedia search. Usage: /wiki &lt;query&gt;"""
    args = update.message.text.split(None, 1)

    if len(args) < 2:
        await update.message.reply_text(
            f"📖 {ST.bold_fancy('Wikipedia')}\n"
            f"✧ {ST.bold_fancy('Usage')}: /wiki &lt;search query&gt;",
            parse_mode="HTML"
        )
        return

    query = args[1].strip()

    try:
        async with aiohttp.ClientSession() as session:
            # Search
            search_url = (
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
            )

            async with session.get(
                search_url,
                timeout=aiohttp.ClientTimeout(total=10),
                headers={"User-Agent": "RuhiBot/1.0"}
            ) as resp:
                if resp.status != 200:
                    # Try search API
                    search_url2 = (
                        f"https://en.wikipedia.org/w/api.php?action=opensearch"
                        f"&search={query}&limit=5&format=json"
                    )

                    async with session.get(search_url2,
                                           timeout=aiohttp.ClientTimeout(total=10)) as resp2:
                        if resp2.status == 200:
                            data2 = await resp2.json()
                            titles = data2[1] if len(data2) > 1 else []
                            links = data2[3] if len(data2) > 3 else []

                            if titles:
                                suggestions = "\n".join(
                                    f"  {i+1}. {escape_html(t)}"
                                    for i, t in enumerate(titles[:5])
                                )
                                await update.message.reply_text(
                                    f"📖 {ST.bold_fancy('Wikipedia Suggestions')}\n"
                                    f"{TPL.SEPARATOR}\n\n"
                                    f"🔍 {ST.bold_fancy(f'No exact match for \"{escape_html(query)}\"')}\n\n"
                                    f"💡 {ST.bold_fancy('Did you mean')}:\n{suggestions}\n"
                                    f"{TPL.mini_footer()}",
                                    parse_mode="HTML"
                                )
                            else:
                                await update.message.reply_text(
                                    TPL.error(f"{ST.bold_fancy(f'No results for \"{escape_html(query)}\"')}"),
                                    parse_mode="HTML"
                                )
                        return

                data = await resp.json()

                title = data.get("title", query)
                extract = data.get("extract", "No summary available")
                page_url = data.get("content_urls", {}).get("desktop", {}).get("page", "")
                thumbnail = data.get("thumbnail", {}).get("source", "")
                description = data.get("description", "")

                if len(extract) > 1500:
                    extract = extract[:1500] + "..."

                text = (
                    f"📖 {ST.bold_fancy('Wikipedia')}\n"
                    f"{TPL.SEPARATOR}\n\n"
                    f"╔═══[ {ST.bold_fancy(escape_html(title))} ]═════╗\n"
                )

                if description:
                    text += f"║ ✧ {escape_html(description)}\n"

                text += (
                    f"╚════════════════╝\n\n"
                    f"📝 {escape_html(extract)}\n"
                    f"{TPL.mini_footer()}"
                )

                keyboard = None
                if page_url:
                    keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton(
                            text=f"📖 {ST.bold_fancy('Read on Wikipedia')}",
                            url=page_url
                        )]
                    ])

                if thumbnail:
                    try:
                        await update.message.reply_photo(
                            photo=thumbnail,
                            caption=text[:1024],
                            parse_mode="HTML",
                            reply_markup=keyboard
                        )
                        return
                    except Exception:
                        pass

                await update.message.reply_text(
                    text, parse_mode="HTML", reply_markup=keyboard
                )

    except Exception as e:
        logger.error(f"Wiki error: {e}")
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )


# ─────────────────────────────────────────────
#  9.5  WEATHER
# ─────────────────────────────────────────────

@disabled_check
async def cmd_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get weather info. Usage: /weather &lt;city&gt;"""
    args = update.message.text.split(None, 1)

    if len(args) < 2:
        await update.message.reply_text(
            f"🌤 {ST.bold_fancy('Weather')}\n"
            f"✧ {ST.bold_fancy('Usage')}: /weather &lt;city name&gt;\n"
            f"✧ {ST.bold_fancy('Example')}: /weather London",
            parse_mode="HTML"
        )
        return

    city = args[1].strip()

    # Using wttr.in (free, no API key)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://wttr.in/{city}?format=j1",
                timeout=aiohttp.ClientTimeout(total=10),
                headers={"User-Agent": "curl/7.0"}
            ) as resp:
                if resp.status != 200:
                    await update.message.reply_text(
                        TPL.error(f"{ST.bold_fancy(f'City \"{escape_html(city)}\" not found!')}"),
                        parse_mode="HTML"
                    )
                    return

                data = await resp.json()

                current = data.get("current_condition", [{}])[0]
                area = data.get("nearest_area", [{}])[0]

                location_name = area.get("areaName", [{}])[0].get("value", city)
                country = area.get("country", [{}])[0].get("value", "")
                region = area.get("region", [{}])[0].get("value", "")

                temp_c = current.get("temp_C", "N/A")
                temp_f = current.get("temp_F", "N/A")
                feels_like_c = current.get("FeelsLikeC", "N/A")
                humidity = current.get("humidity", "N/A")
                wind_speed = current.get("windspeedKmph", "N/A")
                wind_dir = current.get("winddir16Point", "N/A")
                pressure = current.get("pressure", "N/A")
                visibility = current.get("visibility", "N/A")
                uv_index = current.get("uvIndex", "N/A")
                cloud_cover = current.get("cloudcover", "N/A")
                weather_desc = current.get("weatherDesc", [{}])[0].get("value", "Unknown")
                precip = current.get("precipMM", "0")
                observation_time = current.get("observation_time", "")

                # Weather emoji
                weather_emojis = {
                    "sunny": "☀️", "clear": "🌙", "partly cloudy": "⛅",
                    "cloudy": "☁️", "overcast": "🌥", "mist": "🌫",
                    "fog": "🌫", "rain": "🌧", "light rain": "🌦",
                    "heavy rain": "🌧", "snow": "🌨", "thunder": "⛈",
                    "drizzle": "🌦", "haze": "🌫", "sleet": "🌨",
                }

                weather_emoji = "🌤"
                for key, emoji in weather_emojis.items():
                    if key in weather_desc.lower():
                        weather_emoji = emoji
                        break

                # Forecast
                forecast_data = data.get("weather", [])
                forecast_text = ""
                for day in forecast_data[:3]:
                    date = day.get("date", "")
                    max_temp = day.get("maxtempC", "N/A")
                    min_temp = day.get("mintempC", "N/A")
                    avg_temp = day.get("avgtempC", "N/A")
                    day_desc = day.get("hourly", [{}])[4].get("weatherDesc", [{}])[0].get("value", "") if day.get("hourly") else ""
                    forecast_text += f"  📅 {date}: {min_temp}°~{max_temp}°C ({escape_html(day_desc)})\n"

                await update.message.reply_text(
                    f"{weather_emoji} {ST.bold_fancy('Weather Report')}\n"
                    f"{TPL.SEPARATOR}\n\n"
                    f"╔═══[ {ST.bold_fancy(f'{escape_html(location_name)}, {escape_html(country)}')} ]═════╗\n"
                    f"║ ✧ {ST.bold_fancy('Condition')}: {escape_html(weather_desc)}\n"
                    f"║ ✧ {ST.bold_fancy('Temperature')}: {temp_c}°C / {temp_f}°F\n"
                    f"║ ✧ {ST.bold_fancy('Feels Like')}: {feels_like_c}°C\n"
                    f"║ ✧ {ST.bold_fancy('Humidity')}: {humidity}%\n"
                    f"║ ✧ {ST.bold_fancy('Wind')}: {wind_speed} km/h {wind_dir}\n"
                    f"║ ✧ {ST.bold_fancy('Pressure')}: {pressure} mb\n"
                    f"║ ✧ {ST.bold_fancy('Visibility')}: {visibility} km\n"
                    f"║ ✧ {ST.bold_fancy('UV Index')}: {uv_index}\n"
                    f"║ ✧ {ST.bold_fancy('Cloud Cover')}: {cloud_cover}%\n"
                    f"║ ✧ {ST.bold_fancy('Precipitation')}: {precip} mm\n"
                    f"╚════════════════╝\n\n"
                    f"📊 {ST.bold_fancy('3-Day Forecast')}:\n{forecast_text}\n"
                    f"🕐 {ST.bold_fancy('Observed at')}: {observation_time} UTC\n"
                    f"{TPL.mini_footer()}",
                    parse_mode="HTML"
                )

    except Exception as e:
        logger.error(f"Weather error: {e}")
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error fetching weather: {e}')}"),
            parse_mode="HTML"
        )


# ─────────────────────────────────────────────
#  9.6  MATH / CALCULATOR
# ─────────────────────────────────────────────

@disabled_check
async def cmd_math(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Calculate math expressions. Usage: /math &lt;expression&gt;
    Example: /math 2+2, /math sqrt(144), /math 5**3
    """
    args = update.message.text.split(None, 1)

    if len(args) < 2:
        await update.message.reply_text(
            f"🧮 {ST.bold_fancy('Math Calculator')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Usage')}: /math &lt;expression&gt;\n"
            f"✧ {ST.bold_fancy('Examples')}:\n"
            f"  • /math 2+2\n"
            f"  • /math 5**3\n"
            f"  • /math sqrt(144)\n"
            f"  • /math sin(3.14)\n"
            f"  • /math log(100)\n"
            f"  • /math 10!\n"
            f"  • /math pi * 5**2\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
        return

    expression = args[1].strip()

    # Safe math evaluation
    result = safe_math_eval(expression)

    if result is not None:
        await update.message.reply_text(
            f"🧮 {ST.bold_fancy('Calculator')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"📝 {ST.bold_fancy('Expression')}:\n  <code>{escape_html(expression)}</code>\n\n"
            f"✅ {ST.bold_fancy('Result')}:\n  <code>{result}</code>\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
    else:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy('Invalid expression or calculation error!')}"),
            parse_mode="HTML"
        )


def safe_math_eval(expression: str):
    """Safely evaluate math expressions."""
    import math as math_module

    # Allowed names
    allowed_names = {
        "abs": abs, "round": round, "min": min, "max": max,
        "sum": sum, "pow": pow, "int": int, "float": float,
        "sqrt": math_module.sqrt, "sin": math_module.sin,
        "cos": math_module.cos, "tan": math_module.tan,
        "log": math_module.log, "log2": math_module.log2,
        "log10": math_module.log10, "exp": math_module.exp,
        "pi": math_module.pi, "e": math_module.e,
        "ceil": math_module.ceil, "floor": math_module.floor,
        "factorial": math_module.factorial, "gcd": math_module.gcd,
        "radians": math_module.radians, "degrees": math_module.degrees,
        "asin": math_module.asin, "acos": math_module.acos,
        "atan": math_module.atan, "atan2": math_module.atan2,
        "hypot": math_module.hypot, "inf": math_module.inf,
        "tau": math_module.tau,
    }

    # Replace common symbols
    expression = expression.replace("×", "*").replace("÷", "/")
    expression = expression.replace("^", "**")

    # Handle factorial notation (5!)
    expression = re.sub(r'(\d+)!', r'factorial(\1)', expression)

    # Remove anything suspicious
    forbidden = [
        "__", "import", "exec", "eval", "open", "os.",
        "sys.", "subprocess", "compile", "globals", "locals",
        "getattr", "setattr", "delattr", "dir(", "vars(",
        "type(", "class", "lambda", "def ", "return",
    ]

    expr_lower = expression.lower()
    for f in forbidden:
        if f in expr_lower:
            return None

    try:
        # Use restricted eval
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        if isinstance(result, (int, float, complex)):
            if isinstance(result, float) and result == int(result) and abs(result) < 10**15:
                return str(int(result))
            return str(result)
        return str(result)
    except Exception:
        return None


# ─────────────────────────────────────────────
#  9.7  ENCODING / DECODING
# ─────────────────────────────────────────────

@disabled_check
async def cmd_base64encode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Base64 encode. Usage: /b64encode &lt;text&gt;"""
    text = await get_text_from_args_or_reply(update)
    if not text:
        await update.message.reply_text(
            f"🔐 {ST.bold_fancy('Usage')}: /b64encode &lt;text&gt;",
            parse_mode="HTML"
        )
        return

    encoded = base64.b64encode(text.encode()).decode()

    await update.message.reply_text(
        f"🔐 {ST.bold_fancy('Base64 Encode')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"📝 {ST.bold_fancy('Input')}: {escape_html(text[:200])}\n\n"
        f"🔒 {ST.bold_fancy('Encoded')}:\n<code>{escape_html(encoded)}</code>\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


@disabled_check
async def cmd_base64decode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Base64 decode. Usage: /b64decode &lt;encoded_text&gt;"""
    text = await get_text_from_args_or_reply(update)
    if not text:
        await update.message.reply_text(
            f"🔓 {ST.bold_fancy('Usage')}: /b64decode &lt;base64_text&gt;",
            parse_mode="HTML"
        )
        return

    try:
        decoded = base64.b64decode(text.encode()).decode()
        await update.message.reply_text(
            f"🔓 {ST.bold_fancy('Base64 Decode')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"🔒 {ST.bold_fancy('Input')}: <code>{escape_html(text[:200])}</code>\n\n"
            f"📝 {ST.bold_fancy('Decoded')}: {escape_html(decoded)}\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
    except Exception:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy('Invalid base64 string!')}"),
            parse_mode="HTML"
        )


@disabled_check
async def cmd_binary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Convert text to binary. Usage: /bin &lt;text&gt;"""
    text = await get_text_from_args_or_reply(update)
    if not text:
        await update.message.reply_text(
            f"💻 {ST.bold_fancy('Usage')}: /bin &lt;text&gt; (text to binary)\n"
            f"✧ {ST.bold_fancy('Reverse')}: /frombin &lt;binary&gt;",
            parse_mode="HTML"
        )
        return

    binary = " ".join(format(ord(c), '08b') for c in text[:100])

    await update.message.reply_text(
        f"💻 {ST.bold_fancy('Binary Conversion')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"📝 {ST.bold_fancy('Text')}: {escape_html(text[:100])}\n\n"
        f"🔢 {ST.bold_fancy('Binary')}:\n<code>{binary}</code>\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


@disabled_check
async def cmd_frombin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Convert binary to text. Usage: /frombin &lt;binary&gt;"""
    text = await get_text_from_args_or_reply(update)
    if not text:
        await update.message.reply_text(
            f"💻 {ST.bold_fancy('Usage')}: /frombin &lt;binary string&gt;",
            parse_mode="HTML"
        )
        return

    try:
        binary_values = text.strip().split()
        decoded = "".join(chr(int(b, 2)) for b in binary_values)

        await update.message.reply_text(
            f"💻 {ST.bold_fancy('Binary to Text')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"🔢 {ST.bold_fancy('Binary')}: <code>{escape_html(text[:200])}</code>\n\n"
            f"📝 {ST.bold_fancy('Text')}: {escape_html(decoded)}\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
    except Exception:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy('Invalid binary string!')}"),
            parse_mode="HTML"
        )


@disabled_check
async def cmd_hex(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Convert text to hex. Usage: /hex &lt;text&gt;"""
    text = await get_text_from_args_or_reply(update)
    if not text:
        await update.message.reply_text(
            f"🔢 {ST.bold_fancy('Usage')}: /hex &lt;text&gt;",
            parse_mode="HTML"
        )
        return

    hex_text = " ".join(format(ord(c), '02x') for c in text[:100])

    await update.message.reply_text(
        f"🔢 {ST.bold_fancy('Hex Conversion')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"📝 {ST.bold_fancy('Text')}: {escape_html(text[:100])}\n\n"
        f"🔡 {ST.bold_fancy('Hex')}: <code>{hex_text}</code>\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


@disabled_check
async def cmd_fromhex(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Convert hex to text. Usage: /fromhex &lt;hex_string&gt;"""
    text = await get_text_from_args_or_reply(update)
    if not text:
        await update.message.reply_text(
            f"🔢 {ST.bold_fancy('Usage')}: /fromhex &lt;hex_string&gt;",
            parse_mode="HTML"
        )
        return

    try:
        hex_values = text.strip().replace(" ", "")
        decoded = bytes.fromhex(hex_values).decode()

        await update.message.reply_text(
            f"🔢 {ST.bold_fancy('Hex to Text')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"🔡 {ST.bold_fancy('Hex')}: <code>{escape_html(text[:200])}</code>\n\n"
            f"📝 {ST.bold_fancy('Text')}: {escape_html(decoded)}\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
    except Exception:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy('Invalid hex string!')}"),
            parse_mode="HTML"
        )


@disabled_check
async def cmd_morse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Convert text to Morse code. Usage: /morse &lt;text&gt;"""
    text = await get_text_from_args_or_reply(update)
    if not text:
        await update.message.reply_text(
            f"📡 {ST.bold_fancy('Usage')}: /morse &lt;text&gt;\n"
            f"✧ {ST.bold_fancy('Decode')}: /frommorse &lt;morse_code&gt;",
            parse_mode="HTML"
        )
        return

    morse_dict = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
        'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
        'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
        'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
        'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
        'Z': '--..', '0': '-----', '1': '.----', '2': '..---',
        '3': '...--', '4': '....-', '5': '.....', '6': '-....',
        '7': '--...', '8': '---..', '9': '----.', ' ': '/',
        '.': '.-.-.-', ',': '--..--', '?': '..--..', '!': '-.-.--',
        "'": '.----.', '"': '.-..-.', '(': '-.--.', ')': '-.--.-',
        '&': '.-...', ':': '---...', ';': '-.-.-.', '=': '-...-',
        '+': '.-.-.', '-': '-....-', '_': '..--.-', '/': '-..-.',
        '@': '.--.-.', '$': '...-..-',
    }

    morse = " ".join(morse_dict.get(c.upper(), c) for c in text[:200])

    await update.message.reply_text(
        f"📡 {ST.bold_fancy('Morse Code')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"📝 {ST.bold_fancy('Text')}: {escape_html(text[:200])}\n\n"
        f"📡 {ST.bold_fancy('Morse')}:\n<code>{escape_html(morse)}</code>\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


@disabled_check
async def cmd_frommorse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Convert Morse code to text. Usage: /frommorse &lt;morse&gt;"""
    text = await get_text_from_args_or_reply(update)
    if not text:
        await update.message.reply_text(
            f"📡 {ST.bold_fancy('Usage')}: /frommorse &lt;morse_code&gt;",
            parse_mode="HTML"
        )
        return

    morse_to_text = {
        '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
        '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
        '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
        '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
        '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
        '--..': 'Z', '-----': '0', '.----': '1', '..---': '2',
        '...--': '3', '....-': '4', '.....': '5', '-....': '6',
        '--...': '7', '---..': '8', '----.': '9', '/': ' ',
    }

    words = text.strip().split(" / ") if " / " in text else text.strip().split("   ")
    decoded_words = []

    for word in words:
        letters = word.strip().split()
        decoded_word = "".join(morse_to_text.get(l, '?') for l in letters)
        decoded_words.append(decoded_word)

    decoded = " ".join(decoded_words)

    await update.message.reply_text(
        f"📡 {ST.bold_fancy('Morse to Text')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"📡 {ST.bold_fancy('Morse')}: <code>{escape_html(text[:200])}</code>\n\n"
        f"📝 {ST.bold_fancy('Text')}: {escape_html(decoded)}\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


@disabled_check
async def cmd_hash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate hash of text. Usage: /hash &lt;text&gt;"""
    text = await get_text_from_args_or_reply(update)
    if not text:
        await update.message.reply_text(
            f"🔐 {ST.bold_fancy('Usage')}: /hash &lt;text&gt;",
            parse_mode="HTML"
        )
        return

    import hashlib

    md5 = hashlib.md5(text.encode()).hexdigest()
    sha1 = hashlib.sha1(text.encode()).hexdigest()
    sha256 = hashlib.sha256(text.encode()).hexdigest()
    sha512 = hashlib.sha512(text.encode()).hexdigest()[:64] + "..."

    await update.message.reply_text(
        f"🔐 {ST.bold_fancy('Hash Generator')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"📝 {ST.bold_fancy('Input')}: {escape_html(text[:50])}\n\n"
        f"✧ {ST.bold_fancy('MD5')}:\n<code>{md5}</code>\n\n"
        f"✧ {ST.bold_fancy('SHA1')}:\n<code>{sha1}</code>\n\n"
        f"✧ {ST.bold_fancy('SHA256')}:\n<code>{sha256}</code>\n\n"
        f"✧ {ST.bold_fancy('SHA512')}:\n<code>{sha512}</code>\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


# ─────────────────────────────────────────────
#  9.8  URL TOOLS
# ─────────────────────────────────────────────

@disabled_check
async def cmd_shorturl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shorten a URL. Usage: /shorturl &lt;url&gt;"""
    args = update.message.text.split(None, 1)

    if len(args) < 2:
        await update.message.reply_text(
            f"🔗 {ST.bold_fancy('Usage')}: /shorturl &lt;url&gt;",
            parse_mode="HTML"
        )
        return

    url = args[1].strip()

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        # Using is.gd API
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://is.gd/create.php?format=json&url={url}",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    short_url = data.get("shorturl")

                    if short_url:
                        await update.message.reply_text(
                            f"🔗 {ST.bold_fancy('URL Shortened!')}\n"
                            f"{TPL.SEPARATOR}\n\n"
                            f"📎 {ST.bold_fancy('Original')}: {escape_html(url[:100])}\n"
                            f"✂️ {ST.bold_fancy('Short')}: {short_url}\n"
                            f"{TPL.mini_footer()}",
                            parse_mode="HTML"
                        )
                        return

        # Fallback: tinyurl
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://tinyurl.com/api-create.php?url={url}",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    short_url = await resp.text()

                    await update.message.reply_text(
                        f"🔗 {ST.bold_fancy('URL Shortened!')}\n"
                        f"{TPL.SEPARATOR}\n\n"
                        f"📎 {ST.bold_fancy('Original')}: {escape_html(url[:100])}\n"
                        f"✂️ {ST.bold_fancy('Short')}: {short_url}\n"
                        f"{TPL.mini_footer()}",
                        parse_mode="HTML"
                    )
                    return

        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy('Failed to shorten URL!')}"),
            parse_mode="HTML"
        )

    except Exception as e:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )


@disabled_check
async def cmd_qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate QR code. Usage: /qr &lt;text or url&gt;"""
    text = await get_text_from_args_or_reply(update)
    if not text:
        await update.message.reply_text(
            f"📱 {ST.bold_fancy('Usage')}: /qr &lt;text or url&gt;",
            parse_mode="HTML"
        )
        return

    if len(text) > 1000:
        text = text[:1000]

    encoded_text = text.replace(" ", "+")
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=400x400&data={encoded_text}"

    try:
        await update.message.reply_photo(
            photo=qr_url,
            caption=(
                f"📱 {ST.bold_fancy('QR Code')}\n"
                f"{TPL.SEPARATOR}\n\n"
                f"✧ {ST.bold_fancy('Content')}: {escape_html(text[:100])}\n"
                f"{TPL.mini_footer()}"
            ),
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Failed to generate QR: {e}')}"),
            parse_mode="HTML"
        )


@disabled_check
async def cmd_readqr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Read a QR code from image. Reply to a photo with /readqr"""
    message = update.message

    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.reply_text(
            f"📱 {ST.bold_fancy('Reply to a photo containing a QR code!')}",
            parse_mode="HTML"
        )
        return

    photo = message.reply_to_message.photo[-1]

    try:
        file = await photo.get_file()
        file_url = file.file_path

        # Use API to decode
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.qrserver.com/v1/read-qr-code/?fileurl={file_url}",
                timeout=aiohttp.ClientTimeout(total=15)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data and data[0]:
                        qr_data = data[0].get("symbol", [{}])[0].get("data")

                        if qr_data:
                            await message.reply_text(
                                f"📱 {ST.bold_fancy('QR Code Read!')}\n"
                                f"{TPL.SEPARATOR}\n\n"
                                f"✧ {ST.bold_fancy('Content')}:\n<code>{escape_html(qr_data)}</code>\n"
                                f"{TPL.mini_footer()}",
                                parse_mode="HTML"
                            )
                            return

        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('Could not read QR code!')}"),
            parse_mode="HTML"
        )

    except Exception as e:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )


@disabled_check
async def cmd_paste(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Paste text to a paste service. Usage: /paste &lt;text&gt; or reply"""
    text = await get_text_from_args_or_reply(update)
    if not text:
        await update.message.reply_text(
            f"📋 {ST.bold_fancy('Usage')}: /paste &lt;text&gt; or reply to message",
            parse_mode="HTML"
        )
        return

    try:
        # Using dpaste.org
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://dpaste.org/api/",
                data={"content": text, "format": "url", "expires": "2592000"},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    paste_url = (await resp.text()).strip()

                    if paste_url.startswith("http"):
                        await update.message.reply_text(
                            f"📋 {ST.bold_fancy('Pasted!')}\n"
                            f"{TPL.SEPARATOR}\n\n"
                            f"🔗 {ST.bold_fancy('URL')}: {paste_url}\n"
                            f"✧ {ST.bold_fancy('Expires')}: 30 days\n"
                            f"✧ {ST.bold_fancy('Length')}: {len(text)} chars\n"
                            f"{TPL.mini_footer()}",
                            parse_mode="HTML"
                        )
                        return

        # Fallback: nekobin
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://nekobin.com/api/documents",
                json={"content": text},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200 or resp.status == 201:
                    data = await resp.json()
                    key = data.get("result", {}).get("key")
                    if key:
                        await update.message.reply_text(
                            f"📋 {ST.bold_fancy('Pasted!')}\n"
                            f"{TPL.SEPARATOR}\n\n"
                            f"🔗 {ST.bold_fancy('URL')}: https://nekobin.com/{key}\n"
                            f"✧ {ST.bold_fancy('Raw')}: https://nekobin.com/raw/{key}\n"
                            f"✧ {ST.bold_fancy('Length')}: {len(text)} chars\n"
                            f"{TPL.mini_footer()}",
                            parse_mode="HTML"
                        )
                        return

        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy('Failed to paste!')}"),
            parse_mode="HTML"
        )

    except Exception as e:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )


# ─────────────────────────────────────────────
#  9.9  GITHUB / DEVELOPER TOOLS
# ─────────────────────────────────────────────

@disabled_check
async def cmd_github(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get GitHub user/repo info. Usage: /github &lt;username&gt; or /github &lt;user/repo&gt;"""
    args = update.message.text.split(None, 1)

    if len(args) < 2:
        await update.message.reply_text(
            f"🐙 {ST.bold_fancy('GitHub Lookup')}\n"
            f"✧ {ST.bold_fancy('User')}: /github &lt;username&gt;\n"
            f"✧ {ST.bold_fancy('Repo')}: /github &lt;user/repo&gt;",
            parse_mode="HTML"
        )
        return

    query = args[1].strip()

    if "/" in query:
        # Repo lookup
        await github_repo_lookup(update, query)
    else:
        # User lookup
        await github_user_lookup(update, query)


async def github_user_lookup(update: Update, username: str):
    """Lookup GitHub user."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.github.com/users/{username}",
                timeout=aiohttp.ClientTimeout(total=10),
                headers={"Accept": "application/vnd.github.v3+json"}
            ) as resp:
                if resp.status != 200:
                    await update.message.reply_text(
                        TPL.error(f"{ST.bold_fancy(f'User \"{username}\" not found!')}"),
                        parse_mode="HTML"
                    )
                    return

                data = await resp.json()

                name = data.get("name", username)
                bio = data.get("bio", "No bio")
                public_repos = data.get("public_repos", 0)
                followers = data.get("followers", 0)
                following = data.get("following", 0)
                location = data.get("location", "N/A")
                company = data.get("company", "N/A")
                blog = data.get("blog", "")
                created = data.get("created_at", "")[:10]
                avatar = data.get("avatar_url", "")
                html_url = data.get("html_url", "")
                public_gists = data.get("public_gists", 0)
                user_type = data.get("type", "User")

                text = (
                    f"🐙 {ST.bold_fancy('GitHub User')}\n"
                    f"{TPL.SEPARATOR}\n\n"
                    f"╔═══[ {ST.bold_fancy(escape_html(name or username))} ]═════╗\n"
                    f"║ ✧ {ST.bold_fancy('Username')}: {escape_html(username)}\n"
                    f"║ ✧ {ST.bold_fancy('Type')}: {user_type}\n"
                    f"║ ✧ {ST.bold_fancy('Bio')}: {escape_html(str(bio)[:100])}\n"
                    f"║ ✧ {ST.bold_fancy('Repos')}: {public_repos}\n"
                    f"║ ✧ {ST.bold_fancy('Gists')}: {public_gists}\n"
                    f"║ ✧ {ST.bold_fancy('Followers')}: {followers}\n"
                    f"║ ✧ {ST.bold_fancy('Following')}: {following}\n"
                    f"║ ✧ {ST.bold_fancy('Location')}: {escape_html(str(location))}\n"
                    f"║ ✧ {ST.bold_fancy('Company')}: {escape_html(str(company))}\n"
                    f"║ ✧ {ST.bold_fancy('Joined')}: {created}\n"
                    f"╚════════════════╝\n"
                    f"{TPL.mini_footer()}"
                )

                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                        text=f"🐙 {ST.bold_fancy('View Profile')}",
                        url=html_url
                    )]
                ])

                if avatar:
                    try:
                        await update.message.reply_photo(
                            photo=avatar,
                            caption=text[:1024],
                            parse_mode="HTML",
                            reply_markup=keyboard
                        )
                        return
                    except Exception:
                        pass

                await update.message.reply_text(
                    text, parse_mode="HTML", reply_markup=keyboard
                )

    except Exception as e:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )


async def github_repo_lookup(update: Update, repo_path: str):
    """Lookup GitHub repo."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.github.com/repos/{repo_path}",
                timeout=aiohttp.ClientTimeout(total=10),
                headers={"Accept": "application/vnd.github.v3+json"}
            ) as resp:
                if resp.status != 200:
                    await update.message.reply_text(
                        TPL.error(f"{ST.bold_fancy(f'Repo \"{repo_path}\" not found!')}"),
                        parse_mode="HTML"
                    )
                    return

                data = await resp.json()

                name = data.get("full_name", repo_path)
                description = data.get("description", "No description")
                stars = data.get("stargazers_count", 0)
                forks = data.get("forks_count", 0)
                watchers = data.get("watchers_count", 0)
                language = data.get("language", "N/A")
                license_info = data.get("license", {})
                license_name = license_info.get("name", "None") if license_info else "None"
                open_issues = data.get("open_issues_count", 0)
                size = data.get("size", 0)
                created = data.get("created_at", "")[:10]
                updated = data.get("updated_at", "")[:10]
                html_url = data.get("html_url", "")
                is_fork = data.get("fork", False)
                default_branch = data.get("default_branch", "main")
                topics = data.get("topics", [])

                # Format size
                if size > 1024:
                    size_str = f"{size / 1024:.1f} MB"
                else:
                    size_str = f"{size} KB"

                topics_str = ", ".join(topics[:5]) if topics else "None"

                text = (
                    f"📦 {ST.bold_fancy('GitHub Repository')}\n"
                    f"{TPL.SEPARATOR}\n\n"
                    f"╔═══[ {ST.bold_fancy(escape_html(name))} ]═════╗\n"
                    f"║ ✧ {ST.bold_fancy('Description')}: {escape_html(str(description)[:150])}\n"
                    f"║ ✧ {ST.bold_fancy('Language')}: {escape_html(str(language))}\n"
                    f"║ ✧ ⭐ {ST.bold_fancy('Stars')}: {stars:,}\n"
                    f"║ ✧ 🍴 {ST.bold_fancy('Forks')}: {forks:,}\n"
                    f"║ ✧ 👁 {ST.bold_fancy('Watchers')}: {watchers:,}\n"
                    f"║ ✧ 🐛 {ST.bold_fancy('Issues')}: {open_issues}\n"
                    f"║ ✧ 📏 {ST.bold_fancy('Size')}: {size_str}\n"
                    f"║ ✧ 📜 {ST.bold_fancy('License')}: {escape_html(license_name)}\n"
                    f"║ ✧ 🌿 {ST.bold_fancy('Branch')}: {default_branch}\n"
                    f"║ ✧ 🏷 {ST.bold_fancy('Topics')}: {escape_html(topics_str)}\n"
                    f"║ ✧ 📅 {ST.bold_fancy('Created')}: {created}\n"
                    f"║ ✧ 🔄 {ST.bold_fancy('Updated')}: {updated}\n"
                    f"║ ✧ {ST.bold_fancy('Fork')}: {'Yes' if is_fork else 'No'}\n"
                    f"╚════════════════╝\n"
                    f"{TPL.mini_footer()}"
                )

                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                        text=f"📦 {ST.bold_fancy('View Repo')}",
                        url=html_url
                    )]
                ])

                await update.message.reply_text(
                    text, parse_mode="HTML", reply_markup=keyboard
                )

    except Exception as e:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )


@disabled_check
async def cmd_pypi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search PyPI packages. Usage: /pypi &lt;package_name&gt;"""
    args = update.message.text.split(None, 1)

    if len(args) < 2:
        await update.message.reply_text(
            f"🐍 {ST.bold_fancy('Usage')}: /pypi &lt;package_name&gt;",
            parse_mode="HTML"
        )
        return

    package = args[1].strip()

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://pypi.org/pypi/{package}/json",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status != 200:
                    await update.message.reply_text(
                        TPL.error(f"{ST.bold_fancy(f'Package \"{package}\" not found!')}"),
                        parse_mode="HTML"
                    )
                    return

                data = await resp.json()
                info = data.get("info", {})

                name = info.get("name", package)
                version = info.get("version", "N/A")
                summary = info.get("summary", "No description")
                author = info.get("author", "Unknown")
                license_info = info.get("license", "N/A")
                home_page = info.get("home_page", "")
                package_url = info.get("package_url", "")
                requires_python = info.get("requires_python", "N/A")
                keywords = info.get("keywords", "")

                await update.message.reply_text(
                    f"🐍 {ST.bold_fancy('PyPI Package')}\n"
                    f"{TPL.SEPARATOR}\n\n"
                    f"╔═══[ {ST.bold_fancy(escape_html(name))} ]═════╗\n"
                    f"║ ✧ {ST.bold_fancy('Version')}: {escape_html(version)}\n"
                    f"║ ✧ {ST.bold_fancy('Author')}: {escape_html(str(author)[:50])}\n"
                    f"║ ✧ {ST.bold_fancy('License')}: {escape_html(str(license_info)[:50])}\n"
                    f"║ ✧ {ST.bold_fancy('Python')}: {escape_html(str(requires_python))}\n"
                    f"╚════════════════╝\n\n"
                    f"📝 {escape_html(str(summary)[:300])}\n\n"
                    f"📦 <code>pip install {escape_html(name)}</code>\n"
                    f"{TPL.mini_footer()}",
                    parse_mode="HTML"
                )

    except Exception as e:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )


# ─────────────────────────────────────────────
#  9.10  UNIT CONVERTER
# ─────────────────────────────────────────────

@disabled_check
async def cmd_convert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unit converter. Usage: /convert &lt;value&gt; &lt;from&gt; to &lt;to&gt;
    Example: /convert 100 km to miles
    """
    args = update.message.text.split(None, 1)

    if len(args) < 2:
        await update.message.reply_text(
            f"📐 {ST.bold_fancy('Unit Converter')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Usage')}: /convert &lt;value&gt; &lt;from&gt; to &lt;to&gt;\n\n"
            f"📋 {ST.bold_fancy('Examples')}:\n"
            f"  • /convert 100 km to miles\n"
            f"  • /convert 72 F to C\n"
            f"  • /convert 1 kg to lb\n"
            f"  • /convert 1 usd to inr\n"
            f"  • /convert 500 mb to gb\n"
            f"  • /convert 24 hours to minutes\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
        return

    text = args[1].strip().lower()

    # Parse: value unit to unit
    match = re.match(r'([\d.]+)\s*(\S+)\s+(?:to|in|=)\s+(\S+)', text)

    if not match:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy('Format: /convert &lt;value&gt; &lt;from&gt; to &lt;to&gt;')}"),
            parse_mode="HTML"
        )
        return

    value = float(match.group(1))
    from_unit = match.group(2).lower()
    to_unit = match.group(3).lower()

    result = unit_convert(value, from_unit, to_unit)

    if result is not None:
        await update.message.reply_text(
            f"📐 {ST.bold_fancy('Conversion Result')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy(f'{value} {from_unit}')}\n"
            f"  ═══ ➤\n"
            f"✅ {ST.bold_fancy(f'{result:.6g} {to_unit}')}\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
    else:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Cannot convert {from_unit} to {to_unit}!')}"),
            parse_mode="HTML"
        )


def unit_convert(value: float, from_unit: str, to_unit: str):
    """Convert between units."""

    # Aliases
    aliases = {
        "km": "kilometer", "mi": "mile", "miles": "mile",
        "m": "meter", "meters": "meter", "ft": "foot", "feet": "foot",
        "cm": "centimeter", "mm": "millimeter", "in": "inch", "inches": "inch",
        "yd": "yard", "yards": "yard", "nm": "nautical_mile",
        "kg": "kilogram", "g": "gram", "grams": "gram", "lb": "pound",
        "lbs": "pound", "oz": "ounce", "ounces": "ounce", "mg": "milligram",
        "t": "tonne", "ton": "tonne",
        "l": "liter", "ml": "milliliter", "gal": "gallon", "gallons": "gallon",
        "qt": "quart", "pt": "pint", "cup": "cup", "fl_oz": "fluid_ounce",
        "c": "celsius", "f": "fahrenheit", "k": "kelvin",
        "celsius": "celsius", "fahrenheit": "fahrenheit", "kelvin": "kelvin",
        "s": "second", "sec": "second", "seconds": "second",
        "min": "minute", "mins": "minute", "minutes": "minute",
        "h": "hour", "hr": "hour", "hrs": "hour", "hours": "hour",
        "d": "day", "days": "day", "w": "week", "weeks": "week",
        "months": "month", "y": "year", "years": "year",
        "b": "byte", "bytes": "byte", "kb": "kilobyte",
        "mb": "megabyte", "gb": "gigabyte", "tb": "terabyte",
        "pb": "petabyte", "kib": "kibibyte", "mib": "mebibyte",
        "gib": "gibibyte",
        "mph": "miles_per_hour", "kph": "km_per_hour", "kmh": "km_per_hour",
        "ms": "meters_per_second", "knots": "knot", "knot": "knot",
    }

    from_u = aliases.get(from_unit, from_unit)
    to_u = aliases.get(to_unit, to_unit)

    # Length conversions (to meters)
    length = {
        "meter": 1, "kilometer": 1000, "centimeter": 0.01,
        "millimeter": 0.001, "mile": 1609.344, "yard": 0.9144,
        "foot": 0.3048, "inch": 0.0254, "nautical_mile": 1852,
    }

    # Weight conversions (to grams)
    weight = {
        "gram": 1, "kilogram": 1000, "milligram": 0.001,
        "pound": 453.592, "ounce": 28.3495, "tonne": 1000000,
    }

    # Volume conversions (to milliliters)
    volume = {
        "liter": 1000, "milliliter": 1, "gallon": 3785.41,
        "quart": 946.353, "pint": 473.176, "cup": 236.588,
        "fluid_ounce": 29.5735,
    }

    # Time conversions (to seconds)
    time_units = {
        "second": 1, "minute": 60, "hour": 3600,
        "day": 86400, "week": 604800, "month": 2592000,
        "year": 31536000,
    }

    # Data conversions (to bytes)
    data_units = {
        "byte": 1, "kilobyte": 1024, "megabyte": 1048576,
        "gigabyte": 1073741824, "terabyte": 1099511627776,
        "petabyte": 1125899906842624,
        "kibibyte": 1024, "mebibyte": 1048576, "gibibyte": 1073741824,
    }

    # Speed (to m/s)
    speed = {
        "meters_per_second": 1, "km_per_hour": 0.277778,
        "miles_per_hour": 0.44704, "knot": 0.514444,
    }

    # Temperature (special handling)
    if from_u in ("celsius", "fahrenheit", "kelvin") and to_u in ("celsius", "fahrenheit", "kelvin"):
        return temp_convert(value, from_u, to_u)

    # Try each category
    for category in [length, weight, volume, time_units, data_units, speed]:
        if from_u in category and to_u in category:
            base_value = value * category[from_u]
            result = base_value / category[to_u]
            return result

    return None


def temp_convert(value: float, from_u: str, to_u: str) -> float:
    """Convert temperature."""
    if from_u == to_u:
        return value

    # Convert to Celsius first
    if from_u == "fahrenheit":
        celsius = (value - 32) * 5 / 9
    elif from_u == "kelvin":
        celsius = value - 273.15
    else:
        celsius = value

    # Convert from Celsius to target
    if to_u == "fahrenheit":
        return celsius * 9 / 5 + 32
    elif to_u == "kelvin":
        return celsius + 273.15
    else:
        return celsius


# ─────────────────────────────────────────────
#  9.11  CURRENCY CONVERTER
# ─────────────────────────────────────────────

@disabled_check
async def cmd_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Convert currency. Usage: /currency &lt;amount&gt; &lt;from&gt; &lt;to&gt;
    Example: /currency 100 USD INR
    """
    args = update.message.text.split()

    if len(args) < 4:
        await update.message.reply_text(
            f"💰 {ST.bold_fancy('Currency Converter')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Usage')}: /currency &lt;amount&gt; &lt;from&gt; &lt;to&gt;\n"
            f"✧ {ST.bold_fancy('Example')}: /currency 100 USD INR\n"
            f"✧ {ST.bold_fancy('Example')}: /currency 50 EUR GBP\n\n"
            f"📋 {ST.bold_fancy('Popular Codes')}: USD, EUR, GBP, INR,\n"
            f"  JPY, CNY, AUD, CAD, CHF, KRW, RUB, BRL\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
        return

    try:
        amount = float(args[1])
    except ValueError:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy('Invalid amount!')}"),
            parse_mode="HTML"
        )
        return

    from_curr = args[2].upper()
    to_curr = args[3].upper()

    try:
        async with aiohttp.ClientSession() as session:
            # Using exchangerate-api
            async with session.get(
                f"https://api.exchangerate-api.com/v4/latest/{from_curr}",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status != 200:
                    await update.message.reply_text(
                        TPL.error(f"{ST.bold_fancy(f'Invalid currency code: {from_curr}')}"),
                        parse_mode="HTML"
                    )
                    return

                data = await resp.json()
                rates = data.get("rates", {})

                if to_curr not in rates:
                    await update.message.reply_text(
                        TPL.error(f"{ST.bold_fancy(f'Invalid currency code: {to_curr}')}"),
                        parse_mode="HTML"
                    )
                    return

                rate = rates[to_curr]
                result = amount * rate

                await update.message.reply_text(
                    f"💰 {ST.bold_fancy('Currency Conversion')}\n"
                    f"{TPL.SEPARATOR}\n\n"
                    f"╔═══[ {ST.bold_fancy('Result')} ]═════╗\n"
                    f"║ ✧ {ST.bold_fancy(f'{amount:,.2f} {from_curr}')}\n"
                    f"║   ═══ ➤\n"
                    f"║ ✅ {ST.bold_fancy(f'{result:,.2f} {to_curr}')}\n"
                    f"╚════════════════╝\n\n"
                    f"✧ {ST.bold_fancy('Rate')}: 1 {from_curr} = {rate:.4f} {to_curr}\n"
                    f"✧ {ST.bold_fancy('Source')}: exchangerate-api.com\n"
                    f"{TPL.mini_footer()}",
                    parse_mode="HTML"
                )

    except Exception as e:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )


# ─────────────────────────────────────────────
#  9.12  IP / DOMAIN LOOKUP
# ─────────────────────────────────────────────

@disabled_check
async def cmd_ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """IP address lookup. Usage: /ip &lt;ip_address or domain&gt;"""
    args = update.message.text.split(None, 1)

    if len(args) < 2:
        await update.message.reply_text(
            f"🌐 {ST.bold_fancy('Usage')}: /ip &lt;ip_address or domain&gt;",
            parse_mode="HTML"
        )
        return

    target = args[1].strip()

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://ip-api.com/json/{target}?fields=status,message,country,countryCode,"
                f"region,regionName,city,zip,lat,lon,timezone,isp,org,as,query",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                data = await resp.json()

                if data.get("status") != "success":
                    await update.message.reply_text(
                        TPL.error(f"{ST.bold_fancy(f'Could not lookup: {target}')}"),
                        parse_mode="HTML"
                    )
                    return

                await update.message.reply_text(
                    f"🌐 {ST.bold_fancy('IP Lookup')}\n"
                    f"{TPL.SEPARATOR}\n\n"
                    f"╔═══[ {ST.bold_fancy(escape_html(target))} ]═════╗\n"
                    f"║ ✧ {ST.bold_fancy('IP')}: {data.get('query', 'N/A')}\n"
                    f"║ ✧ {ST.bold_fancy('Country')}: {data.get('country', 'N/A')} ({data.get('countryCode', '')})\n"
                    f"║ ✧ {ST.bold_fancy('Region')}: {data.get('regionName', 'N/A')}\n"
                    f"║ ✧ {ST.bold_fancy('City')}: {data.get('city', 'N/A')}\n"
                    f"║ ✧ {ST.bold_fancy('ZIP')}: {data.get('zip', 'N/A')}\n"
                    f"║ ✧ {ST.bold_fancy('Timezone')}: {data.get('timezone', 'N/A')}\n"
                    f"║ ✧ {ST.bold_fancy('ISP')}: {escape_html(data.get('isp', 'N/A'))}\n"
                    f"║ ✧ {ST.bold_fancy('Org')}: {escape_html(data.get('org', 'N/A'))}\n"
                    f"║ ✧ {ST.bold_fancy('AS')}: {escape_html(data.get('as', 'N/A'))}\n"
                    f"║ ✧ {ST.bold_fancy('Coords')}: {data.get('lat', '')}, {data.get('lon', '')}\n"
                    f"╚════════════════╝\n"
                    f"{TPL.mini_footer()}",
                    parse_mode="HTML"
                )

    except Exception as e:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )


# ─────────────────────────────────────────────
#  9.13  SCREENSHOTS / TELEGRAPH
# ─────────────────────────────────────────────

@disabled_check
async def cmd_ss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Take a screenshot of a website. Usage: /ss &lt;url&gt;"""
    args = update.message.text.split(None, 1)

    if len(args) < 2:
        await update.message.reply_text(
            f"📸 {ST.bold_fancy('Usage')}: /ss &lt;url&gt;\n"
            f"✧ {ST.bold_fancy('Example')}: /ss google.com",
            parse_mode="HTML"
        )
        return

    url = args[1].strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    loading_msg = await update.message.reply_text(
        f"📸 {ST.bold_fancy('Taking screenshot...')} ⏳",
        parse_mode="HTML"
    )

    try:
        # Using screenshotmachine or similar free API
        ss_url = f"https://image.thum.io/get/width/1280/crop/800/noanimate/{url}"

        await update.message.reply_photo(
            photo=ss_url,
            caption=(
                f"📸 {ST.bold_fancy('Screenshot')}\n"
                f"{TPL.SEPARATOR}\n"
                f"✧ {ST.bold_fancy('URL')}: {escape_html(url[:100])}\n"
                f"{TPL.mini_footer()}"
            ),
            parse_mode="HTML"
        )

        try:
            await loading_msg.delete()
        except Exception:
            pass

    except Exception as e:
        try:
            await loading_msg.edit_text(
                TPL.error(f"{ST.bold_fancy(f'Screenshot failed: {e}')}"),
                parse_mode="HTML"
            )
        except Exception:
            pass


@disabled_check
async def cmd_telegraph(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Upload image to Telegraph. Reply to an image with /telegraph"""
    message = update.message

    file_id = None
    if message.reply_to_message:
        reply = message.reply_to_message
        if reply.photo:
            file_id = reply.photo[-1].file_id
        elif reply.document and reply.document.mime_type and reply.document.mime_type.startswith("image/"):
            file_id = reply.document.file_id
    elif message.photo:
        file_id = message.photo[-1].file_id

    if not file_id:
        await message.reply_text(
            f"📤 {ST.bold_fancy('Reply to an image with /telegraph to upload!')}",
            parse_mode="HTML"
        )
        return

    try:
        file = await context.bot.get_file(file_id)
        file_data = await file.download_as_bytearray()

        # Upload to Telegraph
        async with aiohttp.ClientSession() as session:
            form_data = aiohttp.FormData()
            form_data.add_field(
                'file',
                bytes(file_data),
                filename='image.jpg',
                content_type='image/jpeg'
            )

            async with session.post(
                "https://telegra.ph/upload",
                data=form_data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data and isinstance(data, list) and data[0].get("src"):
                        telegraph_url = f"https://telegra.ph{data[0]['src']}"

                        await message.reply_text(
                            f"📤 {ST.bold_fancy('Uploaded to Telegraph!')}\n"
                            f"{TPL.SEPARATOR}\n\n"
                            f"🔗 {ST.bold_fancy('URL')}: {telegraph_url}\n"
                            f"✧ {ST.bold_fancy('Direct link, no expiry!')}\n"
                            f"{TPL.mini_footer()}",
                            parse_mode="HTML"
                        )
                        return

        await message.reply_text(
            TPL.error(f"{ST.bold_fancy('Upload failed!')}"),
            parse_mode="HTML"
        )

    except Exception as e:
        await message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )


# ─────────────────────────────────────────────
#  9.14  TEXT COUNTER / ANALYZER
# ─────────────────────────────────────────────

@disabled_check
async def cmd_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Count characters, words, lines. Usage: /count &lt;text&gt; or reply"""
    text = await get_text_from_args_or_reply(update)
    if not text:
        await update.message.reply_text(
            f"📊 {ST.bold_fancy('Usage')}: /count &lt;text&gt; or reply to a message",
            parse_mode="HTML"
        )
        return

    chars = len(text)
    chars_no_space = len(text.replace(" ", ""))
    words = len(text.split())
    lines = text.count("\n") + 1
    sentences = len(re.split(r'[.!?]+', text)) - 1
    paragraphs = len([p for p in text.split("\n\n") if p.strip()])

    # Character frequency (top 5)
    from collections import Counter
    char_freq = Counter(text.lower().replace(" ", ""))
    top_chars = char_freq.most_common(5)
    freq_text = ", ".join(f"'{c}': {n}" for c, n in top_chars)

    # Average word length
    word_list = text.split()
    avg_word_len = sum(len(w) for w in word_list) / len(word_list) if word_list else 0

    # Reading time (200 words per minute)
    reading_time = max(1, words // 200)

    await update.message.reply_text(
        f"📊 {ST.bold_fancy('Text Analysis')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"╔═══[ {ST.bold_fancy('Statistics')} ]═════╗\n"
        f"║ ✧ {ST.bold_fancy('Characters')}: {chars:,}\n"
        f"║ ✧ {ST.bold_fancy('No spaces')}: {chars_no_space:,}\n"
        f"║ ✧ {ST.bold_fancy('Words')}: {words:,}\n"
        f"║ ✧ {ST.bold_fancy('Lines')}: {lines:,}\n"
        f"║ ✧ {ST.bold_fancy('Sentences')}: {max(sentences, 1)}\n"
        f"║ ✧ {ST.bold_fancy('Paragraphs')}: {paragraphs}\n"
        f"║ ✧ {ST.bold_fancy('Avg word len')}: {avg_word_len:.1f}\n"
        f"║ ✧ {ST.bold_fancy('Reading time')}: ~{reading_time} min\n"
        f"╚════════════════╝\n\n"
        f"🔤 {ST.bold_fancy('Top chars')}: {freq_text}\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


# ─────────────────────────────────────────────
#  9.15  JSON FORMATTER
# ─────────────────────────────────────────────

@disabled_check
async def cmd_json(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Format/prettify JSON. Usage: /json &lt;json_string&gt; or reply"""
    text = await get_text_from_args_or_reply(update)
    if not text:
        await update.message.reply_text(
            f"📋 {ST.bold_fancy('Usage')}: /json &lt;json_string&gt; or reply",
            parse_mode="HTML"
        )
        return

    try:
        parsed = json.loads(text)
        pretty = json.dumps(parsed, indent=2, ensure_ascii=False)

        if len(pretty) > 3500:
            pretty = pretty[:3500] + "\n..."

        await update.message.reply_text(
            f"📋 {ST.bold_fancy('Formatted JSON')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"<pre>{escape_html(pretty)}</pre>\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
    except json.JSONDecodeError as e:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Invalid JSON: {e}')}"),
            parse_mode="HTML"
        )


# ─────────────────────────────────────────────
#  9.16  TIMESTAMP / TIME TOOLS
# ─────────────────────────────────────────────

@disabled_check
async def cmd_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current time in various timezones. Usage: /time [timezone]"""
    args = update.message.text.split(None, 1)

    now_utc = datetime.datetime.utcnow()

    if len(args) < 2:
        # Show multiple timezones
        timezones = {
            "🇮🇳 IST": 5.5, "🇺🇸 EST": -5, "🇺🇸 PST": -8,
            "🇬🇧 GMT": 0, "🇪🇺 CET": 1, "🇯🇵 JST": 9,
            "🇦🇺 AEST": 10, "🇷🇺 MSK": 3, "🇨🇳 CST": 8,
            "🇸🇬 SGT": 8, "🇦🇪 GST": 4, "🇧🇷 BRT": -3,
        }

        text = (
            f"🕐 {ST.bold_fancy('World Clock')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"📅 {ST.bold_fancy('UTC')}: {now_utc.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        )

        for tz_name, offset in timezones.items():
            local_time = now_utc + datetime.timedelta(hours=offset)
            text += f"  {tz_name}: {local_time.strftime('%H:%M:%S')}\n"

        text += (
            f"\n✧ {ST.bold_fancy('Timestamp')}: <code>{int(now_utc.timestamp())}</code>\n"
            f"✧ {ST.bold_fancy('Specific')}: /time &lt;offset&gt; (e.g., /time +5.5)\n"
            f"{TPL.mini_footer()}"
        )

        await update.message.reply_text(text, parse_mode="HTML")

    else:
        # Show specific timezone
        tz_input = args[1].strip()

        try:
            offset = float(tz_input.replace("+", ""))
            local_time = now_utc + datetime.timedelta(hours=offset)

            sign = "+" if offset >= 0 else ""

            await update.message.reply_text(
                f"🕐 {ST.bold_fancy(f'Time (UTC{sign}{offset})')}\n"
                f"{TPL.SEPARATOR}\n\n"
                f"📅 {ST.bold_fancy('Date')}: {local_time.strftime('%A, %B %d, %Y')}\n"
                f"🕐 {ST.bold_fancy('Time')}: {local_time.strftime('%H:%M:%S')}\n"
                f"✧ {ST.bold_fancy('Timestamp')}: <code>{int(now_utc.timestamp())}</code>\n"
                f"{TPL.mini_footer()}",
                parse_mode="HTML"
            )
        except ValueError:
            await update.message.reply_text(
                TPL.error(f"{ST.bold_fancy('Invalid timezone offset! Use: +5.5, -8, 0')}"),
                parse_mode="HTML"
            )


@disabled_check
async def cmd_timestamp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Convert timestamp. Usage: /timestamp [unix_timestamp]"""
    args = update.message.text.split()

    if len(args) < 2:
        now = datetime.datetime.utcnow()
        ts = int(now.timestamp())

        await update.message.reply_text(
            f"⏱ {ST.bold_fancy('Current Timestamp')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Unix')}: <code>{ts}</code>\n"
            f"✧ {ST.bold_fancy('ISO')}: <code>{now.isoformat()}Z</code>\n"
            f"✧ {ST.bold_fancy('Human')}: {now.strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
            f"✧ {ST.bold_fancy('Convert')}: /timestamp &lt;unix_ts&gt;\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
        return

    try:
        ts = int(args[1])
        dt = datetime.datetime.utcfromtimestamp(ts)

        await update.message.reply_text(
            f"⏱ {ST.bold_fancy('Timestamp Conversion')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Unix')}: <code>{ts}</code>\n"
            f"✧ {ST.bold_fancy('UTC')}: {dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"✧ {ST.bold_fancy('ISO')}: {dt.isoformat()}Z\n"
            f"✧ {ST.bold_fancy('Day')}: {dt.strftime('%A')}\n"
            f"✧ {ST.bold_fancy('Relative')}: {format_timedelta(datetime.datetime.utcnow() - dt)} ago\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
    except (ValueError, OSError):
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy('Invalid timestamp!')}"),
            parse_mode="HTML"
        )


# ─────────────────────────────────────────────
#  9.17  COLOR INFO
# ─────────────────────────────────────────────

@disabled_check
async def cmd_color(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get color info. Usage: /color &lt;hex&gt; or /color &lt;name&gt;
    Example: /color #FF5733 or /color red
    """
    args = update.message.text.split(None, 1)

    if len(args) < 2:
        await update.message.reply_text(
            f"🎨 {ST.bold_fancy('Color Info')}\n"
            f"✧ {ST.bold_fancy('Usage')}: /color &lt;hex_code&gt;\n"
            f"✧ {ST.bold_fancy('Example')}: /color #FF5733\n"
            f"✧ {ST.bold_fancy('Example')}: /color red",
            parse_mode="HTML"
        )
        return

    color_input = args[1].strip()

    # Named colors
    named_colors = {
        "red": "#FF0000", "green": "#00FF00", "blue": "#0000FF",
        "white": "#FFFFFF", "black": "#000000", "yellow": "#FFFF00",
        "cyan": "#00FFFF", "magenta": "#FF00FF", "orange": "#FFA500",
        "purple": "#800080", "pink": "#FFC0CB", "brown": "#A52A2A",
        "gray": "#808080", "grey": "#808080", "gold": "#FFD700",
        "silver": "#C0C0C0", "navy": "#000080", "teal": "#008080",
        "maroon": "#800000", "olive": "#808000", "lime": "#00FF00",
        "aqua": "#00FFFF", "coral": "#FF7F50", "salmon": "#FA8072",
        "indigo": "#4B0082", "violet": "#EE82EE", "crimson": "#DC143C",
        "turquoise": "#40E0D0", "beige": "#F5F5DC", "ivory": "#FFFFF0",
    }

    if color_input.lower() in named_colors:
        hex_color = named_colors[color_input.lower()]
    elif color_input.startswith("#"):
        hex_color = color_input
    elif re.match(r'^[0-9a-fA-F]{6}$', color_input):
        hex_color = f"#{color_input}"
    elif re.match(r'^[0-9a-fA-F]{3}$', color_input):
        hex_color = f"#{color_input[0]*2}{color_input[1]*2}{color_input[2]*2}"
    else:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy('Invalid color! Use hex (#FF0000) or name (red)')}"),
            parse_mode="HTML"
        )
        return

    hex_clean = hex_color.lstrip("#")
    if len(hex_clean) != 6:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy('Invalid hex color!')}"),
            parse_mode="HTML"
        )
        return

    # Convert to RGB
    r = int(hex_clean[0:2], 16)
    g = int(hex_clean[2:4], 16)
    b = int(hex_clean[4:6], 16)

    # Convert to HSL
    r_norm, g_norm, b_norm = r / 255, g / 255, b / 255
    max_c = max(r_norm, g_norm, b_norm)
    min_c = min(r_norm, g_norm, b_norm)
    l = (max_c + min_c) / 2

    if max_c == min_c:
        h = s = 0
    else:
        d = max_c - min_c
        s = d / (2 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)
        if max_c == r_norm:
            h = (g_norm - b_norm) / d + (6 if g_norm < b_norm else 0)
        elif max_c == g_norm:
            h = (b_norm - r_norm) / d + 2
        else:
            h = (r_norm - g_norm) / d + 4
        h /= 6

    h_deg = int(h * 360)
    s_pct = int(s * 100)
    l_pct = int(l * 100)

    # Generate color image
    color_image_url = f"https://via.placeholder.com/200/{hex_clean}/{hex_clean}.png"

    # Color blocks using emoji
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    is_light = brightness > 128

    try:
        await update.message.reply_photo(
            photo=color_image_url,
            caption=(
                f"🎨 {ST.bold_fancy('Color Info')}\n"
                f"{TPL.SEPARATOR}\n\n"
                f"✧ {ST.bold_fancy('Hex')}: {hex_color}\n"
                f"✧ {ST.bold_fancy('RGB')}: ({r}, {g}, {b})\n"
                f"✧ {ST.bold_fancy('HSL')}: ({h_deg}°, {s_pct}%, {l_pct}%)\n"
                f"✧ {ST.bold_fancy('Brightness')}: {'Light ☀️' if is_light else 'Dark 🌙'}\n"
                f"{TPL.mini_footer()}"
            ),
            parse_mode="HTML"
        )
    except Exception:
        await update.message.reply_text(
            f"🎨 {ST.bold_fancy('Color Info')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Hex')}: {hex_color}\n"
            f"✧ {ST.bold_fancy('RGB')}: ({r}, {g}, {b})\n"
            f"✧ {ST.bold_fancy('HSL')}: ({h_deg}°, {s_pct}%, {l_pct}%)\n"
            f"✧ {ST.bold_fancy('Brightness')}: {'Light ☀️' if is_light else 'Dark 🌙'}\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )


# ─────────────────────────────────────────────
#  9.18  PASSWORD GENERATOR
# ─────────────────────────────────────────────

@disabled_check
async def cmd_genpass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate a random password. Usage: /genpass [length]"""
    args = update.message.text.split()
    length = 16

    if len(args) > 1:
        try:
            length = int(args[1])
            if length < 4:
                length = 4
            elif length > 128:
                length = 128
        except ValueError:
            pass

    import string

    # Generate strong password
    chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-="
    password = "".join(random.SystemRandom().choice(chars) for _ in range(length))

    # Ensure at least one of each type
    if length >= 8:
        password = list(password)
        password[0] = random.choice(string.ascii_uppercase)
        password[1] = random.choice(string.ascii_lowercase)
        password[2] = random.choice(string.digits)
        password[3] = random.choice("!@#$%^&*()_+-=")
        random.shuffle(password)
        password = "".join(password)

    # Strength indicator
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=" for c in password)
    score = sum([has_upper, has_lower, has_digit, has_special])

    if score >= 4 and length >= 12:
        strength = "🟢 Strong"
    elif score >= 3 and length >= 8:
        strength = "🟡 Medium"
    else:
        strength = "🔴 Weak"

    # Send in PM for security
    try:
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=(
                f"🔑 {ST.bold_fancy('Generated Password')}\n"
                f"{TPL.SEPARATOR}\n\n"
                f"🔐 <code>{escape_html(password)}</code>\n\n"
                f"✧ {ST.bold_fancy('Length')}: {length}\n"
                f"✧ {ST.bold_fancy('Strength')}: {strength}\n"
                f"✧ ✅ Uppercase: {'Yes' if has_upper else 'No'}\n"
                f"✧ ✅ Lowercase: {'Yes' if has_lower else 'No'}\n"
                f"✧ ✅ Numbers: {'Yes' if has_digit else 'No'}\n"
                f"✧ ✅ Special: {'Yes' if has_special else 'No'}\n"
                f"{TPL.mini_footer()}"
            ),
            parse_mode="HTML"
        )

        if update.effective_chat.type != ChatType.PRIVATE:
            await update.message.reply_text(
                f"🔑 {ST.bold_fancy('Password sent to your PM!')} 📩",
                parse_mode="HTML"
            )

    except Exception:
        # If can't DM, send spoiler
        await update.message.reply_text(
            f"🔑 {ST.bold_fancy('Generated Password')}\n"
            f"✧ {ST.bold_fancy('Click to reveal')}: <tg-spoiler>{escape_html(password)}</tg-spoiler>\n"
            f"✧ {ST.bold_fancy('Length')}: {length} | {strength}",
            parse_mode="HTML"
        )


# ─────────────────────────────────────────────
#  9.19  RANDOM NUMBER / UUID GENERATOR
# ─────────────────────────────────────────────

@disabled_check
async def cmd_random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate random number. Usage: /random [min] [max]"""
    args = update.message.text.split()

    min_val = 1
    max_val = 100

    if len(args) > 1:
        try:
            max_val = int(args[1])
        except ValueError:
            pass

    if len(args) > 2:
        try:
            min_val = int(args[1])
            max_val = int(args[2])
        except ValueError:
            pass

    if min_val > max_val:
        min_val, max_val = max_val, min_val

    result = random.randint(min_val, max_val)

    await update.message.reply_text(
        f"🎲 {ST.bold_fancy('Random Number')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"✧ {ST.bold_fancy('Range')}: {min_val:,} - {max_val:,}\n"
        f"✧ {ST.bold_fancy('Result')}: {ST.bold_fancy(str(result))}\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


@disabled_check
async def cmd_uuid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate UUID."""
    new_uuid = str(uuid.uuid4())

    await update.message.reply_text(
        f"🔑 {ST.bold_fancy('UUID Generated')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"✧ {ST.bold_fancy('UUID v4')}:\n<code>{new_uuid}</code>\n\n"
        f"✧ {ST.bold_fancy('No dashes')}:\n<code>{new_uuid.replace('-', '')}</code>\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


# ─────────────────────────────────────────────
#  9.20  MOVIE / IMDB SEARCH
# ─────────────────────────────────────────────

@disabled_check
async def cmd_imdb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search movie/show info. Usage: /imdb &lt;movie name&gt;"""
    args = update.message.text.split(None, 1)

    if len(args) < 2:
        await update.message.reply_text(
            f"🎬 {ST.bold_fancy('Usage')}: /imdb &lt;movie or show name&gt;",
            parse_mode="HTML"
        )
        return

    query = args[1].strip()

    try:
        # Using OMDb API (free tier)
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://www.omdbapi.com/?t={query}&apikey=b9a3b45f",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status != 200:
                    await update.message.reply_text(
                        TPL.error(f"{ST.bold_fancy('API error!')}"),
                        parse_mode="HTML"
                    )
                    return

                data = await resp.json()

                if data.get("Response") == "False":
                    await update.message.reply_text(
                        TPL.error(f"{ST.bold_fancy(f'Movie not found: {escape_html(query)}')}"),
                        parse_mode="HTML"
                    )
                    return

                title = data.get("Title", "N/A")
                year = data.get("Year", "N/A")
                rated = data.get("Rated", "N/A")
                released = data.get("Released", "N/A")
                runtime = data.get("Runtime", "N/A")
                genre = data.get("Genre", "N/A")
                director = data.get("Director", "N/A")
                writer = data.get("Writer", "N/A")
                actors = data.get("Actors", "N/A")
                plot = data.get("Plot", "N/A")
                language = data.get("Language", "N/A")
                country = data.get("Country", "N/A")
                awards = data.get("Awards", "N/A")
                poster = data.get("Poster", "")
                imdb_rating = data.get("imdbRating", "N/A")
                imdb_votes = data.get("imdbVotes", "N/A")
                imdb_id = data.get("imdbID", "")
                media_type = data.get("Type", "movie")
                box_office = data.get("BoxOffice", "N/A")

                # Other ratings
                ratings = data.get("Ratings", [])
                rating_text = ""
                for r in ratings:
                    rating_text += f"  • {r.get('Source', '')}: {r.get('Value', '')}\n"

                text = (
                    f"🎬 {ST.bold_fancy('Movie/Show Info')}\n"
                    f"{TPL.SEPARATOR}\n\n"
                    f"╔═══[ {ST.bold_fancy(escape_html(title))} ({year}) ]═════╗\n"
                    f"║ ✧ {ST.bold_fancy('Type')}: {media_type.title()}\n"
                    f"║ ✧ {ST.bold_fancy('Rated')}: {rated}\n"
                    f"║ ✧ {ST.bold_fancy('Released')}: {released}\n"
                    f"║ ✧ {ST.bold_fancy('Runtime')}: {runtime}\n"
                    f"║ ✧ {ST.bold_fancy('Genre')}: {escape_html(genre)}\n"
                    f"║ ✧ {ST.bold_fancy('Director')}: {escape_html(director)}\n"
                    f"║ ✧ {ST.bold_fancy('Actors')}: {escape_html(actors)}\n"
                    f"║ ✧ {ST.bold_fancy('Language')}: {escape_html(language)}\n"
                    f"║ ✧ {ST.bold_fancy('Country')}: {escape_html(country)}\n"
                    f"║ ✧ ⭐ {ST.bold_fancy('IMDB')}: {imdb_rating}/10 ({imdb_votes} votes)\n"
                )

                if box_office and box_office != "N/A":
                    text += f"║ ✧ 💰 {ST.bold_fancy('Box Office')}: {box_office}\n"

                if awards and awards != "N/A":
                    text += f"║ ✧ 🏆 {ST.bold_fancy('Awards')}: {escape_html(awards)}\n"

                text += f"╚════════════════╝\n\n"

                if rating_text:
                    text += f"📊 {ST.bold_fancy('Ratings')}:\n{rating_text}\n"

                text += f"📖 {ST.bold_fancy('Plot')}: {escape_html(plot)}\n"
                text += TPL.mini_footer()

                keyboard = None
                if imdb_id:
                    keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton(
                            text=f"🎬 {ST.bold_fancy('View on IMDB')}",
                            url=f"https://www.imdb.com/title/{imdb_id}"
                        )]
                    ])

                if poster and poster != "N/A":
                    try:
                        await update.message.reply_photo(
                            photo=poster,
                            caption=text[:1024],
                            parse_mode="HTML",
                            reply_markup=keyboard
                        )
                        return
                    except Exception:
                        pass

                await update.message.reply_text(
                    text, parse_mode="HTML", reply_markup=keyboard
                )

    except Exception as e:
        logger.error(f"IMDB error: {e}")
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )


# ─────────────────────────────────────────────
#  9.21  LYRICS SEARCH
# ─────────────────────────────────────────────

@disabled_check
async def cmd_lyrics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search song lyrics. Usage: /lyrics &lt;song name&gt;"""
    args = update.message.text.split(None, 1)

    if len(args) < 2:
        await update.message.reply_text(
            f"🎵 {ST.bold_fancy('Usage')}: /lyrics &lt;song name&gt;\n"
            f"✧ {ST.bold_fancy('Example')}: /lyrics Shape of You",
            parse_mode="HTML"
        )
        return

    query = args[1].strip()

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://some-random-api.com/lyrics?title={query}",
                timeout=aiohttp.ClientTimeout(total=15)
            ) as resp:
                if resp.status != 200:
                    await update.message.reply_text(
                        TPL.error(f"{ST.bold_fancy('Lyrics not found!')}"),
                        parse_mode="HTML"
                    )
                    return

                data = await resp.json()

                if "error" in data:
                    await update.message.reply_text(
                        TPL.error(f"{ST.bold_fancy(f'Lyrics not found for: {escape_html(query)}')}"),
                        parse_mode="HTML"
                    )
                    return

                title = data.get("title", query)
                author = data.get("author", "Unknown")
                lyrics_text = data.get("lyrics", "No lyrics found")
                thumbnail = data.get("thumbnail", {}).get("genius", "")

                # Split lyrics if too long
                if len(lyrics_text) > 3500:
                    lyrics_text = lyrics_text[:3500] + "\n\n... (truncated)"

                text = (
                    f"🎵 {ST.bold_fancy('Lyrics')}\n"
                    f"{TPL.SEPARATOR}\n\n"
                    f"🎶 {ST.bold_fancy(escape_html(title))}\n"
                    f"🎤 {ST.bold_fancy(escape_html(author))}\n\n"
                    f"{escape_html(lyrics_text)}\n"
                    f"{TPL.mini_footer()}"
                )

                # Split into multiple messages if needed
                if len(text) > 4096:
                    parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
                    for part in parts:
                        await update.message.reply_text(part, parse_mode="HTML")
                else:
                    await update.message.reply_text(text, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Lyrics error: {e}")
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )


# ─────────────────────────────────────────────
#  9.22  CARBON CODE IMAGE
# ─────────────────────────────────────────────

@disabled_check
async def cmd_carbon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate carbon.now.sh code image. Reply to code with /carbon"""
    text = await get_text_from_args_or_reply(update)
    if not text:
        await update.message.reply_text(
            f"💻 {ST.bold_fancy('Carbon Code Image')}\n"
            f"✧ {ST.bold_fancy('Usage')}: /carbon <code> or reply to code",
            parse_mode="HTML"
        )
        return

    # Generate carbon URL
    import urllib.parse
    encoded = urllib.parse.quote(text[:2000])

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=f"💻 {ST.bold_fancy('Open in Carbon')}",
            url=f"https://carbon.now.sh/?code={encoded}&bg=rgba(0,0,0,1)"
        )]
    ])

    await update.message.reply_text(
        f"💻 {ST.bold_fancy('Carbon Code')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"✧ Click the button below to generate your code image!\n"
        f"✧ Code preview:\n<pre>{escape_html(text[:500])}</pre>\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML",
        reply_markup=keyboard
    )


# ─────────────────────────────────────────────
#  9.23  REMINDER SYSTEM
# ─────────────────────────────────────────────

@disabled_check
async def cmd_remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set a reminder. Usage: /remind &lt;time&gt; &lt;message&gt;
    Example: /remind 1h Check email
    Example: /remind 30m Take a break
    """
    args = update.message.text.split(None, 2)

    if len(args) < 3:
        await update.message.reply_text(
            f"⏰ {ST.bold_fancy('Set Reminder')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Usage')}: /remind &lt;time&gt; &lt;message&gt;\n"
            f"✧ {ST.bold_fancy('Examples')}:\n"
            f"  • /remind 1h Check email\n"
            f"  • /remind 30m Take a break\n"
            f"  • /remind 2d Pay bills\n"
            f"  • /remind 1w Weekly meeting\n\n"
            f"⏱ {ST.bold_fancy('Time formats')}: s, m/min, h/hr, d, w\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
        return

    time_str = args[1]
    reminder_text = args[2]

    duration = parse_time_string(time_str)
    if not duration:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy('Invalid time! Use: 1h, 30m, 2d, 1w')}"),
            parse_mode="HTML"
        )
        return

    if duration.total_seconds() > 31536000:  # 1 year
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy('Maximum reminder time is 1 year!')}"),
            parse_mode="HTML"
        )
        return

    if duration.total_seconds() < 30:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy('Minimum reminder time is 30 seconds!')}"),
            parse_mode="HTML"
        )
        return

    user = update.effective_user
    chat = update.effective_chat
    remind_time = datetime.datetime.utcnow() + duration

    # Save reminder to DB
    session = get_db()
    try:
        reminder = DBReminder(
            user_id=user.id,
            chat_id=chat.id,
            message=reminder_text,
            remind_at=remind_time,
            created_at=datetime.datetime.utcnow()
        )
        session.add(reminder)
        session.commit()
        reminder_id = reminder.id
    except Exception as e:
        session.rollback()
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )
        return
    finally:
        close_db(session)

    # Schedule the reminder
    async def send_reminder():
        await asyncio.sleep(duration.total_seconds())
        try:
            await context.bot.send_message(
                chat_id=chat.id,
                text=(
                    f"⏰ {ST.bold_fancy('Reminder!')}\n"
                    f"{TPL.SEPARATOR}\n\n"
                    f"✧ {ST.bold_fancy('For')}: {get_user_link(user)}\n"
                    f"✧ {ST.bold_fancy('Message')}: {escape_html(reminder_text)}\n"
                    f"✧ {ST.bold_fancy('Set')}: {format_timedelta(duration)} ago\n"
                    f"{TPL.mini_footer()}"
                ),
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Reminder send error: {e}")

        # Mark as sent
        sess = get_db()
        try:
            r = sess.query(DBReminder).filter(DBReminder.id == reminder_id).first()
            if r:
                r.sent = True
                sess.commit()
        except Exception:
            sess.rollback()
        finally:
            close_db(sess)

    asyncio.create_task(send_reminder())

    await update.message.reply_text(
        f"⏰ {ST.bold_fancy('Reminder Set!')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"✧ {ST.bold_fancy('Time')}: {format_timedelta(duration)}\n"
        f"✧ {ST.bold_fancy('At')}: {remind_time.strftime('%Y-%m-%d %H:%M UTC')}\n"
        f"✧ {ST.bold_fancy('Message')}: {escape_html(reminder_text)}\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


@disabled_check
async def cmd_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List your active reminders."""
    user = update.effective_user

    session = get_db()
    try:
        reminders = session.query(DBReminder).filter(
            DBReminder.user_id == user.id,
            DBReminder.sent == False,
            DBReminder.remind_at > datetime.datetime.utcnow()
        ).order_by(DBReminder.remind_at).all()

        if not reminders:
            await update.message.reply_text(
                f"⏰ {ST.bold_fancy('No active reminders!')}",
                parse_mode="HTML"
            )
            return

        text = (
            f"⏰ {ST.bold_fancy('Your Reminders')}\n"
            f"{TPL.SEPARATOR}\n\n"
        )

        for i, r in enumerate(reminders, 1):
            time_left = r.remind_at - datetime.datetime.utcnow()
            text += (
                f"  {i}. {escape_html(r.message[:50])}\n"
                f"     ⏱ In {format_timedelta(time_left)}\n"
            )

        text += f"\n{ST.bold_fancy('Total')}: {len(reminders)}"
        text += TPL.mini_footer()

        await update.message.reply_text(text, parse_mode="HTML")
    finally:
        close_db(session)


# ─────────────────────────────────────────────
#  9.24  DB MODELS FOR SECTION 9
# ─────────────────────────────────────────────

"""
Required DB Model:

class DBReminder(Base):
    __tablename__ = "reminders"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    chat_id = Column(BigInteger, nullable=False)
    message = Column(Text, nullable=False)
    remind_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    sent = Column(Boolean, default=False)
"""


# ─────────────────────────────────────────────
#  9.25  REGISTER SECTION 9 HANDLERS
# ─────────────────────────────────────────────

def register_section9_handlers(app):
    """Register all Section 9 (Utilities/Tools) handlers."""

    # ── Translation ──
    app.add_handler(CommandHandler(["tr", "translate"], cmd_translate))
    app.add_handler(CommandHandler("langs", cmd_langs))
    app.add_handler(CommandHandler("languages", cmd_langs))

    # ── TTS ──
    app.add_handler(CommandHandler("tts", cmd_tts))
    app.add_handler(CommandHandler("speak", cmd_tts))

    # ── Dictionary ──
    app.add_handler(CommandHandler("ud", cmd_ud))
    app.add_handler(CommandHandler("urban", cmd_ud))
    app.add_handler(CommandHandler("define", cmd_define))
    app.add_handler(CommandHandler("dict", cmd_define))

    # ── Wikipedia ──
    app.add_handler(CommandHandler("wiki", cmd_wiki))
    app.add_handler(CommandHandler("wikipedia", cmd_wiki))

    # ── Weather ──
    app.add_handler(CommandHandler("weather", cmd_weather))
    app.add_handler(CommandHandler("w", cmd_weather))

    # ── Math ──
    app.add_handler(CommandHandler("math", cmd_math))
    app.add_handler(CommandHandler("calc", cmd_math))
    app.add_handler(CommandHandler("calculate", cmd_math))

    # ── Encoding ──
    app.add_handler(CommandHandler("b64encode", cmd_base64encode))
    app.add_handler(CommandHandler("base64encode", cmd_base64encode))
    app.add_handler(CommandHandler("b64decode", cmd_base64decode))
    app.add_handler(CommandHandler("base64decode", cmd_base64decode))
    app.add_handler(CommandHandler("bin", cmd_binary))
    app.add_handler(CommandHandler("binary", cmd_binary))
    app.add_handler(CommandHandler("frombin", cmd_frombin))
    app.add_handler(CommandHandler("hex", cmd_hex))
    app.add_handler(CommandHandler("fromhex", cmd_fromhex))
    app.add_handler(CommandHandler("morse", cmd_morse))
    app.add_handler(CommandHandler("frommorse", cmd_frommorse))
    app.add_handler(CommandHandler("hash", cmd_hash))

    # ── URL Tools ──
    app.add_handler(CommandHandler("shorturl", cmd_shorturl))
    app.add_handler(CommandHandler("short", cmd_shorturl))
    app.add_handler(CommandHandler("qr", cmd_qr))
    app.add_handler(CommandHandler("readqr", cmd_readqr))
    app.add_handler(CommandHandler("paste", cmd_paste))

    # ── Developer ──
    app.add_handler(CommandHandler("github", cmd_github))
    app.add_handler(CommandHandler("gh", cmd_github))
    app.add_handler(CommandHandler("pypi", cmd_pypi))
    app.add_handler(CommandHandler("pip", cmd_pypi))

    # ── Converter ──
    app.add_handler(CommandHandler("convert", cmd_convert))
    app.add_handler(CommandHandler("currency", cmd_currency))
    app.add_handler(CommandHandler("cur", cmd_currency))

    # ── Network ──
    app.add_handler(CommandHandler("ip", cmd_ip))
    app.add_handler(CommandHandler("iplookup", cmd_ip))

    # ── Media Tools ──
    app.add_handler(CommandHandler("ss", cmd_ss))
    app.add_handler(CommandHandler("screenshot", cmd_ss))
    app.add_handler(CommandHandler("telegraph", cmd_telegraph))
    app.add_handler(CommandHandler("tg", cmd_telegraph))

    # ── Text Tools ──
    app.add_handler(CommandHandler("count", cmd_count))
    app.add_handler(CommandHandler("wordcount", cmd_count))
    app.add_handler(CommandHandler("json", cmd_json))
    app.add_handler(CommandHandler("formatjson", cmd_json))

    # ── Time ──
    app.add_handler(CommandHandler("time", cmd_time))
    app.add_handler(CommandHandler("clock", cmd_time))
    app.add_handler(CommandHandler("timestamp", cmd_timestamp))
    app.add_handler(CommandHandler("ts", cmd_timestamp))

    # ── Color ──
    app.add_handler(CommandHandler("color", cmd_color))
    app.add_handler(CommandHandler("colour", cmd_color))

    # ── Generators ──
    app.add_handler(CommandHandler("genpass", cmd_genpass))
    app.add_handler(CommandHandler("password", cmd_genpass))
    app.add_handler(CommandHandler("random", cmd_random))
    app.add_handler(CommandHandler("rand", cmd_random))
    app.add_handler(CommandHandler("uuid", cmd_uuid))

    # ── Entertainment ──
    app.add_handler(CommandHandler("imdb", cmd_imdb))
    app.add_handler(CommandHandler("movie", cmd_imdb))
    app.add_handler(CommandHandler("lyrics", cmd_lyrics))

    # ── Code ──
    app.add_handler(CommandHandler("carbon", cmd_carbon))

    # ── Reminders ──
    app.add_handler(CommandHandler("remind", cmd_remind))
    app.add_handler(CommandHandler("reminder", cmd_remind))
    app.add_handler(CommandHandler("reminders", cmd_reminders))
    app.add_handler(CommandHandler("myreminders", cmd_reminders))

    logger.info("✅ Section 9 handlers registered: Translation, TTS, Dictionary, "
                "Wikipedia, Weather, Math, Encoding, URL Tools, GitHub, PyPI, "
                "Converter, Currency, IP, Screenshot, Telegraph, Text Tools, "
                "Time, Color, Generators, IMDB, Lyrics, Carbon, Reminders")


# ═══════════════════════════════════════════════════════════════
# END OF SECTION 9
# ═══════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════
# ██╗  SECTION 10: OWNER PANEL / SUDO / BROADCAST / STATS /
# ██╗               MAINTENANCE / MAIN() / FULL REGISTRATION
# ═══════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────
#  10.1  OWNER COMMANDS
# ─────────────────────────────────────────────

@owner_required
async def cmd_sudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a sudo user. Usage: /sudo &lt;user_id&gt;"""
    args = update.message.text.split()
    if len(args) < 2:
        await update.message.reply_text(
            f"👑 {ST.bold_fancy('Sudo Management')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Add')}: /sudo &lt;user_id&gt;\n"
            f"✧ {ST.bold_fancy('Remove')}: /rmsudo &lt;user_id&gt;\n"
            f"✧ {ST.bold_fancy('List')}: /sudolist\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
        return

    try:
        user_id = int(args[1])
    except ValueError:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy('Invalid user ID!')}"),
            parse_mode="HTML"
        )
        return

    session = get_db()
    try:
        existing = session.query(DBSudo).filter(DBSudo.user_id == user_id).first()
        if existing:
            await update.message.reply_text(
                TPL.info(f"{ST.bold_fancy('User is already sudo!')}"),
                parse_mode="HTML"
            )
            return

        sudo = DBSudo(user_id=user_id, added_by=update.effective_user.id)
        session.add(sudo)
        session.commit()

        # Update cache
        sudo_users_cache.add(user_id)

        await update.message.reply_text(
            f"👑 {ST.bold_fancy('Sudo User Added!')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('User ID')}: <code>{user_id}</code>\n"
            f"✧ {ST.bold_fancy('By')}: {get_user_link(update.effective_user)}\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )

    except Exception as e:
        session.rollback()
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )
    finally:
        close_db(session)


@owner_required
async def cmd_rmsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove a sudo user. Usage: /rmsudo &lt;user_id&gt;"""
    args = update.message.text.split()
    if len(args) < 2:
        await update.message.reply_text(
            f"✧ {ST.bold_fancy('Usage')}: /rmsudo &lt;user_id&gt;",
            parse_mode="HTML"
        )
        return

    try:
        user_id = int(args[1])
    except ValueError:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy('Invalid user ID!')}"),
            parse_mode="HTML"
        )
        return

    session = get_db()
    try:
        deleted = session.query(DBSudo).filter(DBSudo.user_id == user_id).delete()
        session.commit()

        sudo_users_cache.discard(user_id)

        if deleted:
            await update.message.reply_text(
                TPL.success(f"👑 {ST.bold_fancy(f'Removed sudo: {user_id}')}"),
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text(
                TPL.error(f"{ST.bold_fancy('User was not sudo!')}"),
                parse_mode="HTML"
            )
    except Exception:
        session.rollback()
    finally:
        close_db(session)


@owner_required
async def cmd_sudolist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all sudo users."""
    session = get_db()
    try:
        sudos = session.query(DBSudo).all()

        if not sudos:
            await update.message.reply_text(
                f"👑 {ST.bold_fancy('No sudo users!')}",
                parse_mode="HTML"
            )
            return

        text = (
            f"👑 {ST.bold_fancy('Sudo Users')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"🔱 {ST.bold_fancy('Owner')}: <code>{Config.OWNER_ID}</code>\n\n"
            f"⚔️ {ST.bold_fancy('Sudo Users')}:\n"
        )

        for i, s in enumerate(sudos, 1):
            text += f"  {i}. <code>{s.user_id}</code>\n"

        text += f"\n{ST.bold_fancy('Total')}: {len(sudos)}"
        text += TPL.mini_footer()

        await update.message.reply_text(text, parse_mode="HTML")
    finally:
        close_db(session)


@owner_required
async def cmd_addsupport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add support user (limited sudo). Usage: /addsupport &lt;user_id&gt;"""
    args = update.message.text.split()
    if len(args) < 2:
        await update.message.reply_text(
            f"🛡 {ST.bold_fancy('Usage')}: /addsupport &lt;user_id&gt;",
            parse_mode="HTML"
        )
        return

    try:
        user_id = int(args[1])
    except ValueError:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy('Invalid user ID!')}"),
            parse_mode="HTML"
        )
        return

    session = get_db()
    try:
        existing = session.query(DBSupport).filter(DBSupport.user_id == user_id).first()
        if existing:
            await update.message.reply_text(
                TPL.info(f"{ST.bold_fancy('Already a support user!')}"),
                parse_mode="HTML"
            )
            return

        support = DBSupport(user_id=user_id, added_by=update.effective_user.id)
        session.add(support)
        session.commit()

        support_users_cache.add(user_id)

        await update.message.reply_text(
            TPL.success(f"🛡 {ST.bold_fancy(f'Support user added: {user_id}')}"),
            parse_mode="HTML"
        )
    except Exception:
        session.rollback()
    finally:
        close_db(session)


@owner_required
async def cmd_rmsupport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove support user."""
    args = update.message.text.split()
    if len(args) < 2:
        return

    try:
        user_id = int(args[1])
    except ValueError:
        return

    session = get_db()
    try:
        session.query(DBSupport).filter(DBSupport.user_id == user_id).delete()
        session.commit()
        support_users_cache.discard(user_id)
        await update.message.reply_text(
            TPL.success(f"🛡 {ST.bold_fancy(f'Removed support: {user_id}')}"),
            parse_mode="HTML"
        )
    except Exception:
        session.rollback()
    finally:
        close_db(session)


@owner_required
async def cmd_supportlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List support users."""
    session = get_db()
    try:
        supports = session.query(DBSupport).all()
        if not supports:
            await update.message.reply_text(
                f"🛡 {ST.bold_fancy('No support users!')}",
                parse_mode="HTML"
            )
            return

        text = f"🛡 {ST.bold_fancy('Support Users')}\n{TPL.SEPARATOR}\n\n"
        for i, s in enumerate(supports, 1):
            text += f"  {i}. <code>{s.user_id}</code>\n"

        text += f"\n{ST.bold_fancy('Total')}: {len(supports)}"
        text += TPL.mini_footer()
        await update.message.reply_text(text, parse_mode="HTML")
    finally:
        close_db(session)


# ─────────────────────────────────────────────
#  10.2  BROADCAST SYSTEM
# ─────────────────────────────────────────────

@sudo_required
async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast message to all chats. Usage: /broadcast &lt;message&gt; or reply"""
    message = update.message
    broadcast_text = None
    broadcast_media = None
    broadcast_media_type = None

    args = message.text.split(None, 1)

    if message.reply_to_message:
        reply = message.reply_to_message
        broadcast_text = reply.text_html or reply.caption_html or reply.text or reply.caption or ""

        if reply.photo:
            broadcast_media = reply.photo[-1].file_id
            broadcast_media_type = "photo"
        elif reply.video:
            broadcast_media = reply.video.file_id
            broadcast_media_type = "video"
        elif reply.animation:
            broadcast_media = reply.animation.file_id
            broadcast_media_type = "animation"
        elif reply.document:
            broadcast_media = reply.document.file_id
            broadcast_media_type = "document"
        elif reply.audio:
            broadcast_media = reply.audio.file_id
            broadcast_media_type = "audio"
    elif len(args) > 1:
        broadcast_text = args[1]

    if not broadcast_text and not broadcast_media:
        await message.reply_text(
            f"📢 {ST.bold_fancy('Broadcast')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {ST.bold_fancy('Usage')}: /broadcast &lt;message&gt;\n"
            f"✧ {ST.bold_fancy('Or')}: Reply to a message with /broadcast\n"
            f"✧ {ST.bold_fancy('Forward')}: /forward (forward the reply)\n"
            f"✧ {ST.bold_fancy('Users only')}: /broadcastusers &lt;msg&gt;\n"
            f"✧ {ST.bold_fancy('Groups only')}: /broadcastgroups &lt;msg&gt;\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
        return

    # Confirm broadcast
    session = get_db()
    try:
        total_chats = session.query(func.count(DBChat.id)).scalar() or 0
        total_users = session.query(func.count(DBUser.user_id)).scalar() or 0
    finally:
        close_db(session)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text=f"✅ Send to ALL ({total_chats + total_users})",
                callback_data=f"broadcast_all_{message.message_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"👥 Groups only ({total_chats})",
                callback_data=f"broadcast_groups_{message.message_id}"
            ),
            InlineKeyboardButton(
                text=f"👤 Users only ({total_users})",
                callback_data=f"broadcast_users_{message.message_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="❌ Cancel",
                callback_data="broadcast_cancel"
            )
        ]
    ])

    # Store broadcast data
    context.bot_data[f"broadcast_{message.message_id}"] = {
        "text": broadcast_text,
        "media": broadcast_media,
        "media_type": broadcast_media_type,
        "sender": update.effective_user.id
    }

    preview = (broadcast_text or "[Media]")[:200]

    await message.reply_text(
        f"📢 {ST.bold_fancy('Broadcast Preview')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"📝 {ST.bold_fancy('Message')}:\n{escape_html(preview)}\n\n"
        f"✧ {ST.bold_fancy('Groups')}: {total_chats}\n"
        f"✧ {ST.bold_fancy('Users')}: {total_users}\n\n"
        f"⚠️ {ST.bold_fancy('Confirm broadcast?')}",
        parse_mode="HTML",
        reply_markup=keyboard
    )


async def broadcast_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle broadcast confirmation callbacks."""
    query = update.callback_query
    data = query.data
    user = query.from_user

    if not is_sudo(user.id):
        await query.answer("❌ Only sudo users!", show_alert=True)
        return

    if data == "broadcast_cancel":
        await query.message.edit_text(
            f"❌ {ST.bold_fancy('Broadcast cancelled!')}",
            parse_mode="HTML"
        )
        return

    parts = data.split("_")
    if len(parts) < 3:
        return

    broadcast_type = parts[1]  # all, groups, users
    msg_id = parts[2]

    broadcast_data = context.bot_data.get(f"broadcast_{msg_id}")
    if not broadcast_data:
        await query.answer("Broadcast data expired!", show_alert=True)
        return

    await query.message.edit_text(
        f"📢 {ST.bold_fancy('Broadcasting...')} ⏳\n"
        f"✧ {ST.bold_fancy('Type')}: {broadcast_type}\n"
        f"✧ {ST.bold_fancy('Please wait...')}",
        parse_mode="HTML"
    )

    # Execute broadcast
    success = 0
    failed = 0
    blocked = 0

    session = get_db()
    try:
        targets = []

        if broadcast_type in ("all", "groups"):
            chats = session.query(DBChat.chat_id).all()
            targets.extend([(c.chat_id, "group") for c in chats])

        if broadcast_type in ("all", "users"):
            users = session.query(DBUser.user_id).all()
            targets.extend([(u.user_id, "user") for u in users])

    finally:
        close_db(session)

    text = broadcast_data.get("text", "")
    media = broadcast_data.get("media")
    media_type = broadcast_data.get("media_type")

    for target_id, target_type in targets:
        try:
            if media and media_type:
                if media_type == "photo":
                    await context.bot.send_photo(
                        chat_id=target_id, photo=media,
                        caption=text[:1024] if text else None,
                        parse_mode="HTML"
                    )
                elif media_type == "video":
                    await context.bot.send_video(
                        chat_id=target_id, video=media,
                        caption=text[:1024] if text else None,
                        parse_mode="HTML"
                    )
                elif media_type == "animation":
                    await context.bot.send_animation(
                        chat_id=target_id, animation=media,
                        caption=text[:1024] if text else None,
                        parse_mode="HTML"
                    )
                elif media_type == "document":
                    await context.bot.send_document(
                        chat_id=target_id, document=media,
                        caption=text[:1024] if text else None,
                        parse_mode="HTML"
                    )
                elif media_type == "audio":
                    await context.bot.send_audio(
                        chat_id=target_id, audio=media,
                        caption=text[:1024] if text else None,
                        parse_mode="HTML"
                    )
                else:
                    if text:
                        await context.bot.send_message(
                            chat_id=target_id, text=text, parse_mode="HTML"
                        )
            else:
                if text:
                    await context.bot.send_message(
                        chat_id=target_id, text=text, parse_mode="HTML"
                    )

            success += 1

        except Forbidden:
            blocked += 1
            # Remove blocked users/chats
            sess = get_db()
            try:
                if target_type == "user":
                    sess.query(DBUser).filter(DBUser.user_id == target_id).delete()
                else:
                    sess.query(DBChat).filter(DBChat.chat_id == target_id).delete()
                sess.commit()
            except Exception:
                sess.rollback()
            finally:
                close_db(sess)

        except Exception as e:
            failed += 1
            logger.error(f"Broadcast error to {target_id}: {e}")

        # Rate limiting
        await asyncio.sleep(0.05)

    # Clean up
    context.bot_data.pop(f"broadcast_{msg_id}", None)

    await query.message.edit_text(
        f"📢 {ST.bold_fancy('Broadcast Complete!')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"╔═══[ {ST.bold_fancy('Results')} ]═════╗\n"
        f"║ ✅ {ST.bold_fancy('Success')}: {success}\n"
        f"║ ❌ {ST.bold_fancy('Failed')}: {failed}\n"
        f"║ 🚫 {ST.bold_fancy('Blocked')}: {blocked}\n"
        f"║ 📊 {ST.bold_fancy('Total')}: {success + failed + blocked}\n"
        f"╚════════════════╝\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


@sudo_required
async def cmd_broadcastgroups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast to groups only."""
    args = update.message.text.split(None, 1)
    if len(args) < 2 and not update.message.reply_to_message:
        await update.message.reply_text(
            f"📢 {ST.bold_fancy('Usage')}: /broadcastgroups &lt;message&gt;",
            parse_mode="HTML"
        )
        return

    text = args[1] if len(args) > 1 else ""
    if update.message.reply_to_message:
        text = update.message.reply_to_message.text_html or update.message.reply_to_message.text or text

    if not text:
        return

    session = get_db()
    try:
        chats = session.query(DBChat.chat_id).all()
    finally:
        close_db(session)

    success = 0
    failed = 0

    status_msg = await update.message.reply_text(
        f"📢 {ST.bold_fancy(f'Broadcasting to {len(chats)} groups...')} ⏳",
        parse_mode="HTML"
    )

    for (chat_id,) in chats:
        try:
            await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
            success += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)

    await status_msg.edit_text(
        f"📢 {ST.bold_fancy('Group Broadcast Done!')}\n"
        f"✅ {success} | ❌ {failed}",
        parse_mode="HTML"
    )


@sudo_required
async def cmd_broadcastusers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast to users only."""
    args = update.message.text.split(None, 1)
    if len(args) < 2 and not update.message.reply_to_message:
        await update.message.reply_text(
            f"📢 {ST.bold_fancy('Usage')}: /broadcastusers &lt;message&gt;",
            parse_mode="HTML"
        )
        return

    text = args[1] if len(args) > 1 else ""
    if update.message.reply_to_message:
        text = update.message.reply_to_message.text_html or update.message.reply_to_message.text or text

    if not text:
        return

    session = get_db()
    try:
        users = session.query(DBUser.user_id).all()
    finally:
        close_db(session)

    success = 0
    failed = 0

    status_msg = await update.message.reply_text(
        f"📢 {ST.bold_fancy(f'Broadcasting to {len(users)} users...')} ⏳",
        parse_mode="HTML"
    )

    for (user_id,) in users:
        try:
            await context.bot.send_message(chat_id=user_id, text=text, parse_mode="HTML")
            success += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)

    await status_msg.edit_text(
        f"📢 {ST.bold_fancy('User Broadcast Done!')}\n"
        f"✅ {success} | ❌ {failed}",
        parse_mode="HTML"
    )


# ─────────────────────────────────────────────
#  10.3  BOT STATISTICS
# ─────────────────────────────────────────────

@disabled_check
async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot statistics."""
    session = get_db()
    try:
        total_users = session.query(func.count(DBUser.user_id)).scalar() or 0
        total_chats = session.query(func.count(DBChat.id)).scalar() or 0
        total_notes = session.query(func.count(DBNote.id)).scalar() or 0
        total_filters = session.query(func.count(DBFilter.id)).scalar() or 0
        total_warns = session.query(func.count(DBWarn.id)).scalar() or 0
        total_bans = session.query(func.count(DBBan.id)).scalar() or 0
        total_gbans = session.query(func.count(DBGban.id)).filter(DBGban.is_active == True).scalar() or 0
        total_feds = session.query(func.count(DBFederation.id)).scalar() or 0
        total_reminders = session.query(func.count(DBReminder.id)).filter(DBReminder.sent == False).scalar() or 0
        total_blacklist = session.query(func.count(DBBlacklist.id)).scalar() or 0
        total_custom_cmds = session.query(func.count(DBCustomCmd.id)).scalar() or 0
        total_disabled = session.query(func.count(DBDisabled.id)).scalar() or 0

    finally:
        close_db(session)

    # System stats
    import platform
    uptime = datetime.datetime.utcnow() - bot_start_time
    uptime_str = format_timedelta(uptime)

    # Memory usage
    try:
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        cpu_percent = process.cpu_percent(interval=0.1)
        memory_str = f"{memory_mb:.1f} MB"
        cpu_str = f"{cpu_percent:.1f}%"
    except ImportError:
        import resource
        memory_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        memory_str = f"{memory_kb / 1024:.1f} MB"
        cpu_str = "N/A"

    python_ver = platform.python_version()
    os_info = f"{platform.system()} {platform.release()}"

    await update.message.reply_text(
        f"📊 {ST.bold_fancy('Bot Statistics')}\n"
        f"{TPL.SEPARATOR}\n\n"
        f"╔═══[ {ST.bold_fancy('Usage Stats')} ]═════╗\n"
        f"║ 👤 {ST.bold_fancy('Users')}: {total_users:,}\n"
        f"║ 👥 {ST.bold_fancy('Groups')}: {total_chats:,}\n"
        f"║ 📝 {ST.bold_fancy('Notes')}: {total_notes:,}\n"
        f"║ 🔍 {ST.bold_fancy('Filters')}: {total_filters:,}\n"
        f"║ ⚙️ {ST.bold_fancy('Custom Cmds')}: {total_custom_cmds:,}\n"
        f"║ ⚠️ {ST.bold_fancy('Warns')}: {total_warns:,}\n"
        f"║ 🔨 {ST.bold_fancy('Bans')}: {total_bans:,}\n"
        f"║ 🌍 {ST.bold_fancy('GBans')}: {total_gbans:,}\n"
        f"║ 🏛 {ST.bold_fancy('Federations')}: {total_feds:,}\n"
        f"║ 📋 {ST.bold_fancy('Blacklisted')}: {total_blacklist:,}\n"
        f"║ 🚫 {ST.bold_fancy('Disabled Cmds')}: {total_disabled:,}\n"
        f"║ ⏰ {ST.bold_fancy('Reminders')}: {total_reminders:,}\n"
        f"╚════════════════╝\n\n"
        f"╔═══[ {ST.bold_fancy('System Info')} ]═════╗\n"
        f"║ ⏱ {ST.bold_fancy('Uptime')}: {uptime_str}\n"
        f"║ 💾 {ST.bold_fancy('Memory')}: {memory_str}\n"
        f"║ 🖥 {ST.bold_fancy('CPU')}: {cpu_str}\n"
        f"║ 🐍 {ST.bold_fancy('Python')}: {python_ver}\n"
        f"║ 💻 {ST.bold_fancy('OS')}: {os_info}\n"
        f"║ 🤖 {ST.bold_fancy('PTB')}: {telegram.__version__}\n"
        f"╚════════════════╝\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


@sudo_required
async def cmd_dbstats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Detailed database statistics."""
    session = get_db()
    try:
        # Get all table counts
        tables_info = {}
        for table_name in Base.metadata.tables.keys():
            try:
                count = session.execute(
                    text(f"SELECT COUNT(*) FROM {table_name}")
                ).scalar()
                tables_info[table_name] = count
            except Exception:
                tables_info[table_name] = "Error"

        text_msg = (
            f"🗄 {ST.bold_fancy('Database Statistics')}\n"
            f"{TPL.SEPARATOR}\n\n"
        )

        total_rows = 0
        for table, count in sorted(tables_info.items()):
            if isinstance(count, int):
                total_rows += count
            text_msg += f"  📋 {table}: {count:,}\n" if isinstance(count, int) else f"  📋 {table}: {count}\n"

        text_msg += (
            f"\n{ST.bold_fancy('Total rows')}: {total_rows:,}\n"
            f"✧ {ST.bold_fancy('DB Type')}: PostgreSQL (Render)\n"
            f"{TPL.mini_footer()}"
        )

        await update.message.reply_text(text_msg, parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )
    finally:
        close_db(session)


# ─────────────────────────────────────────────
#  10.4  MAINTENANCE COMMANDS
# ─────────────────────────────────────────────

@sudo_required
async def cmd_maintenance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle maintenance mode. /maintenance on/off"""
    args = update.message.text.split()
    if len(args) < 2:
        status = "ON 🔴" if Config.MAINTENANCE_MODE else "OFF 🟢"
        await update.message.reply_text(
            f"🔧 {ST.bold_fancy('Maintenance Mode')}: {status}\n"
            f"✧ /maintenance on/off",
            parse_mode="HTML"
        )
        return

    if args[1].lower() in ("on", "yes", "1"):
        Config.MAINTENANCE_MODE = True
        await update.message.reply_text(
            f"🔴 {ST.bold_fancy('Maintenance mode ENABLED!')}\n"
            f"✧ Only sudo users can use the bot",
            parse_mode="HTML"
        )
    else:
        Config.MAINTENANCE_MODE = False
        await update.message.reply_text(
            f"🟢 {ST.bold_fancy('Maintenance mode DISABLED!')}",
            parse_mode="HTML"
        )


@sudo_required
async def cmd_shell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Execute shell command (OWNER ONLY). Usage: /sh &lt;command&gt;"""
    if not is_owner(update.effective_user.id):
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy('Owner only command!')}"),
            parse_mode="HTML"
        )
        return

    args = update.message.text.split(None, 1)
    if len(args) < 2:
        await update.message.reply_text(
            f"💻 {ST.bold_fancy('Usage')}: /sh &lt;command&gt;",
            parse_mode="HTML"
        )
        return

    cmd = args[1]

    try:
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)

        output = stdout.decode() if stdout else ""
        error = stderr.decode() if stderr else ""

        result = output or error or "No output"

        if len(result) > 3500:
            result = result[:3500] + "\n... (truncated)"

        await update.message.reply_text(
            f"💻 {ST.bold_fancy('Shell Output')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"📝 {ST.bold_fancy('Command')}: <code>{escape_html(cmd)}</code>\n\n"
            f"📤 {ST.bold_fancy('Output')}:\n<pre>{escape_html(result)}</pre>\n"
            f"✧ {ST.bold_fancy('Exit code')}: {process.returncode}\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )

    except asyncio.TimeoutError:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy('Command timed out (30s)!')}"),
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )


@sudo_required
async def cmd_eval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Evaluate Python expression (OWNER ONLY). Usage: /eval &lt;expression&gt;"""
    if not is_owner(update.effective_user.id):
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy('Owner only!')}"),
            parse_mode="HTML"
        )
        return

    args = update.message.text.split(None, 1)
    if len(args) < 2:
        await update.message.reply_text(
            f"🐍 {ST.bold_fancy('Usage')}: /eval &lt;python_expression&gt;",
            parse_mode="HTML"
        )
        return

    code = args[1]

    # Environment for eval
    env = {
        "context": context, "update": update, "bot": context.bot,
        "message": update.message, "chat": update.effective_chat,
        "user": update.effective_user,
        "asyncio": asyncio, "json": json, "os": os,
        "datetime": datetime, "re": re,
    }

    try:
        result = eval(code, env)
        if asyncio.iscoroutine(result):
            result = await result

        result_str = str(result)
        if len(result_str) > 3500:
            result_str = result_str[:3500] + "..."

        await update.message.reply_text(
            f"🐍 {ST.bold_fancy('Eval Result')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"📝 <code>{escape_html(code)}</code>\n\n"
            f"📤 {ST.bold_fancy('Result')}:\n<pre>{escape_html(result_str)}</pre>\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(
            f"🐍 {ST.bold_fancy('Eval Error')}\n\n"
            f"❌ <pre>{escape_html(str(e))}</pre>",
            parse_mode="HTML"
        )


@sudo_required
async def cmd_exec(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Execute Python code (OWNER ONLY). Usage: /exec <code>"""
    if not is_owner(update.effective_user.id):
        return

    args = update.message.text.split(None, 1)
    if len(args) < 2:
        await update.message.reply_text(
            f"🐍 {ST.bold_fancy('Usage')}: /exec &lt;python_code&gt;",
            parse_mode="HTML"
        )
        return

    code = args[1]
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()

    try:
        exec_globals = {
            "context": context, "update": update, "bot": context.bot,
            "message": update.message, "asyncio": asyncio,
            "json": json, "os": os, "datetime": datetime,
        }

        exec(code, exec_globals)
        output = buffer.getvalue()

        if not output:
            output = "No output"

        if len(output) > 3500:
            output = output[:3500] + "..."

        await update.message.reply_text(
            f"🐍 {ST.bold_fancy('Exec Output')}\n{TPL.SEPARATOR}\n\n"
            f"<pre>{escape_html(output)}</pre>",
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ <pre>{escape_html(str(e))}</pre>",
            parse_mode="HTML"
        )
    finally:
        sys.stdout = old_stdout


@sudo_required
async def cmd_restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Restart the bot (re-executes the script)."""
    if not is_owner(update.effective_user.id):
        return

    await update.message.reply_text(
        f"🔄 {ST.bold_fancy('Restarting bot...')}",
        parse_mode="HTML"
    )

    # On Render, we can restart by exiting (Render auto-restarts)
    os.execl(sys.executable, sys.executable, *sys.argv)


@sudo_required
async def cmd_leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Make bot leave a chat. Usage: /leave &lt;chat_id&gt;"""
    args = update.message.text.split()
    if len(args) < 2:
        await update.message.reply_text(
            f"✧ {ST.bold_fancy('Usage')}: /leave &lt;chat_id&gt;",
            parse_mode="HTML"
        )
        return

    try:
        chat_id = int(args[1])
        await context.bot.leave_chat(chat_id)

        session = get_db()
        try:
            session.query(DBChat).filter(DBChat.chat_id == chat_id).delete()
            session.commit()
        except Exception:
            session.rollback()
        finally:
            close_db(session)

        await update.message.reply_text(
            TPL.success(f"✧ {ST.bold_fancy(f'Left chat: {chat_id}')}"),
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )


@sudo_required
async def cmd_chatlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all chats bot is in."""
    session = get_db()
    try:
        chats = session.query(DBChat).order_by(DBChat.id.desc()).limit(50).all()

        if not chats:
            await update.message.reply_text(
                f"📋 {ST.bold_fancy('No chats in database!')}",
                parse_mode="HTML"
            )
            return

        text = f"📋 {ST.bold_fancy('Chat List')}\n{TPL.SEPARATOR}\n\n"

        for i, c in enumerate(chats, 1):
            name = escape_html(c.title or "Unknown")[:30]
            text += f"  {i}. {name}\n     └ <code>{c.chat_id}</code>\n"

        total = session.query(func.count(DBChat.id)).scalar() or 0
        text += f"\n{ST.bold_fancy('Showing')}: {len(chats)}/{total}"
        text += TPL.mini_footer()

        await update.message.reply_text(text, parse_mode="HTML")
    finally:
        close_db(session)


@sudo_required
async def cmd_userlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user count and recent users."""
    session = get_db()
    try:
        total = session.query(func.count(DBUser.user_id)).scalar() or 0
        recent = session.query(DBUser).order_by(DBUser.user_id.desc()).limit(20).all()

        text = f"👥 {ST.bold_fancy('User List')}\n{TPL.SEPARATOR}\n\n"
        text += f"✧ {ST.bold_fancy('Total Users')}: {total:,}\n\n"

        if recent:
            text += f"📋 {ST.bold_fancy('Recent')} (last 20):\n"
            for i, u in enumerate(recent, 1):
                name = escape_html(u.first_name or "Unknown")[:25]
                text += f"  {i}. {name} (<code>{u.user_id}</code>)\n"

        text += TPL.mini_footer()
        await update.message.reply_text(text, parse_mode="HTML")
    finally:
        close_db(session)


@sudo_required
async def cmd_cleandb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clean database - remove inactive entries."""
    if not is_owner(update.effective_user.id):
        return

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⚠️ Yes, clean DB", callback_data="cleandb_yes"),
            InlineKeyboardButton("❌ Cancel", callback_data="cleandb_no")
        ]
    ])

    await update.message.reply_text(
        f"⚠️ {ST.bold_fancy('Clean Database?')}\n\n"
        f"This will remove:\n"
        f"• Expired bans\n"
        f"• Old warnings\n"
        f"• Sent reminders\n"
        f"• Inactive entries",
        parse_mode="HTML",
        reply_markup=keyboard
    )


async def cleandb_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle cleandb confirmation."""
    query = update.callback_query

    if query.data == "cleandb_no":
        await query.message.edit_text(
            f"✅ {ST.bold_fancy('Cancelled.')}",
            parse_mode="HTML"
        )
        return

    if query.data == "cleandb_yes":
        if not is_owner(query.from_user.id):
            await query.answer("❌ Owner only!", show_alert=True)
            return

        session = get_db()
        cleaned = 0
        try:
            # Remove sent reminders
            c1 = session.query(DBReminder).filter(DBReminder.sent == True).delete()
            cleaned += c1

            # Remove expired bans
            c2 = session.query(DBBan).filter(
                DBBan.is_active == False,
                DBBan.created_at < datetime.datetime.utcnow() - datetime.timedelta(days=30)
            ).delete()
            cleaned += c2

            # Remove old mutes
            c3 = session.query(DBMute).filter(
                DBMute.is_active == False
            ).delete()
            cleaned += c3

            # Remove old anti-spam logs
            c4 = session.query(DBAntiSpamLog).filter(
                DBAntiSpamLog.created_at < datetime.datetime.utcnow() - datetime.timedelta(days=7)
            ).delete()
            cleaned += c4

            session.commit()

            await query.message.edit_text(
                f"🧹 {ST.bold_fancy('Database Cleaned!')}\n"
                f"✧ Removed {cleaned:,} entries",
                parse_mode="HTML"
            )
        except Exception as e:
            session.rollback()
            await query.message.edit_text(
                TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
                parse_mode="HTML"
            )
        finally:
            close_db(session)


@sudo_required
async def cmd_ip_self(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show server IP (owner only)."""
    if not is_owner(update.effective_user.id):
        return

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.ipify.org?format=json",
                                   timeout=aiohttp.ClientTimeout(total=5)) as resp:
                data = await resp.json()
                ip = data.get("ip", "Unknown")

        await update.message.reply_text(
            f"🌐 {ST.bold_fancy('Server IP')}: <tg-spoiler>{ip}</tg-spoiler>",
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )


@sudo_required
async def cmd_setbotname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Change bot name. Usage: /setbotname &lt;name&gt;"""
    if not is_owner(update.effective_user.id):
        return

    args = update.message.text.split(None, 1)
    if len(args) < 2:
        await update.message.reply_text(
            f"✧ {ST.bold_fancy('Usage')}: /setbotname &lt;new_name&gt;",
            parse_mode="HTML"
        )
        return

    try:
        await context.bot.set_my_name(args[1].strip())
        await update.message.reply_text(
            TPL.success(f"✧ {ST.bold_fancy(f'Bot name set to: {args[1].strip()}')}"),
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )


@sudo_required
async def cmd_setbotdesc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set bot description. Usage: /setbotdesc &lt;description&gt;"""
    if not is_owner(update.effective_user.id):
        return

    args = update.message.text.split(None, 1)
    if len(args) < 2:
        return

    try:
        await context.bot.set_my_description(args[1].strip())
        await update.message.reply_text(
            TPL.success(f"✧ {ST.bold_fancy('Bot description updated!')}"),
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )


@sudo_required
async def cmd_setbotpic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set bot profile photo. Reply to a photo."""
    if not is_owner(update.effective_user.id):
        return

    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        await update.message.reply_text(
            f"✧ {ST.bold_fancy('Reply to a photo!')}",
            parse_mode="HTML"
        )
        return

    try:
        photo = update.message.reply_to_message.photo[-1]
        file = await photo.get_file()
        file_data = await file.download_as_bytearray()

        await context.bot.set_chat_photo(
            chat_id=context.bot.id,
            photo=bytes(file_data)
        )
        await update.message.reply_text(
            TPL.success(f"✧ {ST.bold_fancy('Bot photo updated!')}"),
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )


# ─────────────────────────────────────────────
#  10.5  CHAT MANAGEMENT (GROUP TITLE, PHOTO, etc.)
# ─────────────────────────────────────────────

@admin_required
@group_only
@bot_admin_required
async def cmd_setchattitle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set chat title. Usage: /setchattitle &lt;title&gt;"""
    args = update.message.text.split(None, 1)
    if len(args) < 2:
        await update.message.reply_text(
            f"✧ {ST.bold_fancy('Usage')}: /setchattitle &lt;new_title&gt;",
            parse_mode="HTML"
        )
        return

    try:
        await update.effective_chat.set_title(args[1].strip())
        await update.message.reply_text(
            TPL.success(f"✧ {ST.bold_fancy(f'Chat title set!')}"),
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )


@admin_required
@group_only
@bot_admin_required
async def cmd_setchatdesc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set chat description. Usage: /setchatdesc &lt;description&gt;"""
    args = update.message.text.split(None, 1)
    if len(args) < 2:
        await update.message.reply_text(
            f"✧ {ST.bold_fancy('Usage')}: /setchatdesc &lt;description&gt;",
            parse_mode="HTML"
        )
        return

    try:
        await update.effective_chat.set_description(args[1].strip())
        await update.message.reply_text(
            TPL.success(f"✧ {ST.bold_fancy('Chat description updated!')}"),
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )


@admin_required
@group_only
@bot_admin_required
async def cmd_setchatphoto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set chat photo. Reply to a photo."""
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        await update.message.reply_text(
            f"✧ {ST.bold_fancy('Reply to a photo!')}",
            parse_mode="HTML"
        )
        return

    try:
        photo = update.message.reply_to_message.photo[-1]
        file = await photo.get_file()
        file_data = await file.download_as_bytearray()

        await update.effective_chat.set_photo(photo=bytes(file_data))
        await update.message.reply_text(
            TPL.success(f"✧ {ST.bold_fancy('Chat photo updated!')}"),
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )


@admin_required
@group_only
@bot_admin_required
async def cmd_delchatphoto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete chat photo."""
    try:
        await update.effective_chat.delete_photo()
        await update.message.reply_text(
            TPL.success(f"✧ {ST.bold_fancy('Chat photo removed!')}"),
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )


@admin_required
@group_only
async def cmd_setinvite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get/create invite link."""
    try:
        link = await update.effective_chat.export_invite_link()
        await update.message.reply_text(
            f"🔗 {ST.bold_fancy('Invite Link')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"✧ {link}\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )


# ─────────────────────────────────────────────
#  10.6  TAG ALL / STAFF / ZOMBIES
# ─────────────────────────────────────────────

@admin_required
@group_only
async def cmd_tagall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tag all members. Usage: /tagall [message]"""
    args = update.message.text.split(None, 1)
    tag_msg = args[1] if len(args) > 1 else "📢 Attention everyone!"

    try:
        members = []
        async for member in update.effective_chat.get_members():
            if not member.user.is_bot:
                members.append(member.user)

        if not members:
            await update.message.reply_text(
                f"❌ {ST.bold_fancy('No members found!')}",
                parse_mode="HTML"
            )
            return

        # Send in batches (5 members per message)
        batch_size = 5
        first_msg = True

        for i in range(0, len(members), batch_size):
            batch = members[i:i + batch_size]
            mentions = " ".join(
                f'<a href="tg://user?id={m.id}">{escape_html(m.first_name[:10])}</a>'
                for m in batch
            )

            text = f"📢 {escape_html(tag_msg)}\n\n{mentions}" if first_msg else mentions
            first_msg = False

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text,
                parse_mode="HTML"
            )

            await asyncio.sleep(1)

    except Exception as e:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )


@admin_required
@group_only
async def cmd_staff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tag all admins."""
    try:
        admins = await update.effective_chat.get_administrators()
        mentions = " ".join(
            f'<a href="tg://user?id={a.user.id}">{escape_html(a.user.first_name[:10])}</a>'
            for a in admins if not a.user.is_bot
        )

        await update.message.reply_text(
            f"📢 {ST.bold_fancy('Calling all staff!')} 🚨\n\n{mentions}",
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )


@admin_required
@group_only
@bot_admin_required
async def cmd_zombies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Find and remove deleted accounts. Usage: /zombies [clean]"""
    args = update.message.text.split()
    clean = len(args) > 1 and args[1].lower() == "clean"

    chat = update.effective_chat
    zombie_count = 0
    removed = 0

    status_msg = await update.message.reply_text(
        f"🧟 {ST.bold_fancy('Scanning for zombies...')} ⏳",
        parse_mode="HTML"
    )

    try:
        async for member in chat.get_members():
            if member.user.first_name == "" or member.user.is_deleted if hasattr(member.user, 'is_deleted') else member.user.first_name is None:
                zombie_count += 1
                if clean:
                    try:
                        await chat.ban_member(member.user.id)
                        await asyncio.sleep(0.3)
                        await chat.unban_member(member.user.id)
                        removed += 1
                    except Exception:
                        pass

        if clean:
            await status_msg.edit_text(
                f"🧟 {ST.bold_fancy('Zombie Cleanup Done!')}\n"
                f"{TPL.SEPARATOR}\n\n"
                f"✧ {ST.bold_fancy('Found')}: {zombie_count}\n"
                f"✧ {ST.bold_fancy('Removed')}: {removed}\n"
                f"{TPL.mini_footer()}",
                parse_mode="HTML"
            )
        else:
            if zombie_count > 0:
                await status_msg.edit_text(
                    f"🧟 {ST.bold_fancy(f'Found {zombie_count} zombies!')}\n"
                    f"✧ Use /zombies clean to remove them",
                    parse_mode="HTML"
                )
            else:
                await status_msg.edit_text(
                    f"✅ {ST.bold_fancy('No zombies found!')}",
                    parse_mode="HTML"
                )

    except Exception as e:
        await status_msg.edit_text(
            TPL.error(f"{ST.bold_fancy(f'Error: {e}')}"),
            parse_mode="HTML"
        )


# ─────────────────────────────────────────────
#  10.7  ERROR HANDLER
# ─────────────────────────────────────────────

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Global error handler — shows friendly message to all, details to sudo only."""
    error_str = str(context.error)
    logger.error(f"Exception while handling update: {error_str}", exc_info=context.error)

    # Skip non-actionable errors silently
    SILENT_ERRORS = (
        "Query is too old",
        "Message is not modified",
        "Forbidden: bot was blocked",
        "Forbidden: user is deactivated",
        "Chat not found",
        "User not found",
        "Have no rights to send a message",
        "CHAT_WRITE_FORBIDDEN",
        "BOT_KICKED",
        "Connection reset",
        "timed out",
        "getaddrinfo failed",
    )
    for silent in SILENT_ERRORS:
        if silent.lower() in error_str.lower():
            return

    try:
        if not update:
            return
        if not hasattr(update, 'effective_message') or not update.effective_message:
            return
        if not update.effective_user:
            return

        msg = update.effective_message

        if is_sudo(update.effective_user.id):
            # Sudo users get full error details
            error_text = escape_html(error_str[:500])
            await msg.reply_text(
                f"⚠️ {ST.bold_fancy('Error occurred')}\n"
                f"<pre>{error_text}</pre>",
                parse_mode="HTML"
            )
        else:
            # Regular users get a friendly message
            await msg.reply_text(
                f"⚠️ {ST.bold_fancy('Error occurred')}\n"
                f"Something went wrong. Please try again.",
                parse_mode="HTML"
            )
    except Exception:
        pass


# ─────────────────────────────────────────────
#  10.8  MAINTENANCE CHECK MIDDLEWARE
# ─────────────────────────────────────────────

async def maintenance_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check if bot is in maintenance mode."""
    if not Config.MAINTENANCE_MODE:
        return

    if not update.effective_user:
        return

    if is_sudo(update.effective_user.id):
        return

    if update.message and update.message.text and update.message.text.startswith("/"):
        await update.message.reply_text(
            f"🔧 {ST.bold_fancy('Bot is under maintenance!')}\n"
            f"✧ {ST.bold_fancy('Please try again later.')}\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )


# ─────────────────────────────────────────────
#  10.9  SERVICE MESSAGE HANDLER
# ─────────────────────────────────────────────

async def service_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle service messages (clean if enabled)."""
    message = update.message
    if not message:
        return

    chat = update.effective_chat
    if not chat or chat.type == ChatType.PRIVATE:
        return

    # Check if clean service is enabled
    session = get_db()
    try:
        db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
        if db_chat and db_chat.clean_service:
            try:
                await message.delete()
            except Exception:
                pass
    except Exception:
        pass
    finally:
        close_db(session)


# ─────────────────────────────────────────────
#  10.10  DB MODELS FOR SECTION 10
# ─────────────────────────────────────────────

class DBSudo(Base):
    """Sudo users with elevated permissions."""
    __tablename__ = "sudo_users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, unique=True, nullable=False)
    added_by = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class DBSupport(Base):
    """Support users with limited elevated permissions."""
    __tablename__ = "support_users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, unique=True, nullable=False)
    added_by = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


def init_db():
    """Initialize database - create all tables."""
    try:
        Base.metadata.create_all(engine)
        logger.info("✅ Database tables initialized successfully!")
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        raise


# ─────────────────────────────────────────────
#  10.11  GLOBAL VARIABLES / STARTUP
# ─────────────────────────────────────────────

# Bot start time
bot_start_time = datetime.datetime.utcnow()

# Caches
sudo_users_cache = set()
support_users_cache = set()
# Note: admin_cache and flood_data are already defined in Section 2


def load_caches():
    """Load sudo/support users into memory cache."""
    global sudo_users_cache, support_users_cache

    session = get_db()
    try:
        sudos = session.query(DBSudo.user_id).all()
        sudo_users_cache = {s.user_id for s in sudos}

        supports = session.query(DBSupport.user_id).all()
        support_users_cache = {s.user_id for s in supports}

        logger.info(f"Loaded {len(sudo_users_cache)} sudo users, "
                    f"{len(support_users_cache)} support users")
    except Exception as e:
        logger.error(f"Failed to load caches: {e}")
    finally:
        close_db(session)


# ─────────────────────────────────────────────
#  10.12  REGISTER SECTION 10 HANDLERS
# ─────────────────────────────────────────────

def register_section10_handlers(app):
    """Register all Section 10 handlers."""

    # ── Sudo Management ──
    app.add_handler(CommandHandler("sudo", cmd_sudo))
    app.add_handler(CommandHandler("addsudo", cmd_sudo))
    app.add_handler(CommandHandler("rmsudo", cmd_rmsudo))
    app.add_handler(CommandHandler("sudolist", cmd_sudolist))
    app.add_handler(CommandHandler("addsupport", cmd_addsupport))
    app.add_handler(CommandHandler("rmsupport", cmd_rmsupport))
    app.add_handler(CommandHandler("supportlist", cmd_supportlist))

    # ── Broadcast ──
    app.add_handler(CommandHandler("broadcast", cmd_broadcast))
    app.add_handler(CommandHandler("broadcastgroups", cmd_broadcastgroups))
    app.add_handler(CommandHandler("broadcastusers", cmd_broadcastusers))

    # ── Stats ──
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("botstats", cmd_stats))
    app.add_handler(CommandHandler("dbstats", cmd_dbstats))

    # ── Maintenance ──
    app.add_handler(CommandHandler("maintenance", cmd_maintenance))
    app.add_handler(CommandHandler(["sh", "shell", "term"], cmd_shell))
    app.add_handler(CommandHandler("eval", cmd_eval))
    app.add_handler(CommandHandler("exec", cmd_exec))
    app.add_handler(CommandHandler("restart", cmd_restart))
    app.add_handler(CommandHandler("leave", cmd_leave))
    app.add_handler(CommandHandler("chatlist", cmd_chatlist))
    app.add_handler(CommandHandler("chats", cmd_chatlist))
    app.add_handler(CommandHandler("userlist", cmd_userlist))
    app.add_handler(CommandHandler("users", cmd_userlist))
    app.add_handler(CommandHandler("cleandb", cmd_cleandb))
    app.add_handler(CommandHandler("serverip", cmd_ip_self))
    app.add_handler(CommandHandler("setbotname", cmd_setbotname))
    app.add_handler(CommandHandler("setbotdesc", cmd_setbotdesc))
    app.add_handler(CommandHandler("setbotpic", cmd_setbotpic))

    # ── Chat Management ──
    app.add_handler(CommandHandler("setchattitle", cmd_setchattitle))
    app.add_handler(CommandHandler("setchatdesc", cmd_setchatdesc))
    app.add_handler(CommandHandler("setchatphoto", cmd_setchatphoto))
    app.add_handler(CommandHandler("delchatphoto", cmd_delchatphoto))
    app.add_handler(CommandHandler("setinvite", cmd_setinvite))
    app.add_handler(CommandHandler("invitelink", cmd_setinvite))

    # ── Tag All / Staff / Zombies ──
    app.add_handler(CommandHandler("tagall", cmd_tagall))
    app.add_handler(CommandHandler("all", cmd_tagall))
    app.add_handler(CommandHandler("staff", cmd_staff))
    app.add_handler(CommandHandler("admins", cmd_staff))
    app.add_handler(CommandHandler("zombies", cmd_zombies))

    # ── Callback Handlers ──
    app.add_handler(CallbackQueryHandler(broadcast_callback, pattern=r"^broadcast_"))
    app.add_handler(CallbackQueryHandler(cleandb_callback, pattern=r"^cleandb_"))

    # ── Service message handler ──
    app.add_handler(MessageHandler(
        (filters.StatusUpdate.NEW_CHAT_MEMBERS |
         filters.StatusUpdate.LEFT_CHAT_MEMBER |
         filters.StatusUpdate.NEW_CHAT_TITLE |
         filters.StatusUpdate.NEW_CHAT_PHOTO |
         filters.StatusUpdate.DELETE_CHAT_PHOTO |
         filters.StatusUpdate.PINNED_MESSAGE),
        service_message_handler
    ), group=30)

    # ── Error handler ──
    app.add_error_handler(error_handler)

    logger.info("✅ Section 10 handlers registered: Owner, Sudo, Broadcast, "
                "Stats, Maintenance, Chat Management, Error Handler")


# ═══════════════════════════════════════════════════════════════
#  10.13  FLASK WEB SERVER (for Render Web Service)
# ═══════════════════════════════════════════════════════════════

# Note: flask_app routes are defined earlier (Section 1).
# Additional routes added here for the enhanced home page.

@flask_app.route("/status")
def status():
    return {
        "status": "online",
        "uptime": str(datetime.datetime.utcnow() - bot_start_time),
        "version": "2.0.0"
    }


def run_flask():
    """Run Flask server in background thread."""
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port, debug=False)


# ═══════════════════════════════════════════════════════════════
#  10.14  MAIN APPLICATION - REGISTER ALL HANDLERS & RUN
# ═══════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════
#  MISSING CORE FUNCTIONS (Section 1-3: Start, Help, Settings)
# ═══════════════════════════════════════════════════════════════

# ─── Alias: captcha_callback → captcha_callback_handler ───
captcha_callback = captcha_callback_handler


# ─── Welcome / Goodbye message handlers (StatusUpdate) ───

async def welcome_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle new member joins via StatusUpdate filter."""
    if not update.message or not update.message.new_chat_members:
        return
    chat = update.effective_chat
    for new_member in update.message.new_chat_members:
        if new_member.is_bot:
            continue
        db_save_user(new_member)
        await handle_new_member(update, context, chat, new_member)


async def goodbye_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle member leaving via StatusUpdate filter."""
    if not update.message or not update.message.left_chat_member:
        return
    chat = update.effective_chat
    user = update.message.left_chat_member
    if user.is_bot:
        return
    await handle_member_left(update, context, chat, user)


async def welcome_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle welcome message inline buttons (pattern: wlcm_)."""
    query = update.callback_query
    await query.answer()


# ─── CMD: /start ───

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command - shows bot welcome message."""
    user = update.effective_user
    chat = update.effective_chat

    db_save_user(user)

    if chat.type == ChatType.PRIVATE:
        text = (
            f"✦ {ST.bold_fancy('Welcome')} ✦\n"
            f"{TPL.SEPARATOR}\n\n"
            f"👋 {ST.bold_fancy('Hello')} {html.escape(user.first_name)}!\n\n"
            f"ℹ️ I am {ST.bold_fancy(Config.BOT_NAME)}\n"
            f"A powerful group management bot.\n\n"
            f"📌 {ST.bold_fancy('Commands')}:\n"
            f"• /help – Show all commands\n"
            f"• /id – Get your user ID\n"
            f"• /info – Your profile info\n\n"
            f"{TPL.footer()}"
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{Config.BOT_USERNAME}?startgroup=true")],
            [InlineKeyboardButton("📋 Help", callback_data="start_help"),
             InlineKeyboardButton("ℹ️ About", callback_data="start_about")],
        ])
        if Config.START_IMG:
            try:
                await update.message.reply_photo(
                    Config.START_IMG, caption=text,
                    parse_mode="HTML", reply_markup=buttons
                )
                return
            except Exception:
                pass
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=buttons)
    else:
        await update.message.reply_text(
            f"✅ {ST.bold_fancy('Bot is active!')}\n"
            f"Use /help to see available commands.",
            parse_mode="HTML"
        )


# ─── CMD: /help ───

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command - shows available commands."""
    chat = update.effective_chat
    user = update.effective_user

    help_text = (
        f"✦ {ST.bold_fancy('Help Menu')} ✦\n"
        f"{TPL.SEPARATOR}\n\n"
        f"╔═══[ {ST.bold_fancy('Admin Commands')} ]═════╗\n"
        f"║ /ban • /unban • /tban\n"
        f"║ /mute • /unmute • /tmute\n"
        f"║ /kick • /warn • /warns\n"
        f"║ /promote • /demote • /adminlist\n"
        f"╚════════════════╝\n\n"
        f"╔═══[ {ST.bold_fancy('Welcome & Rules')} ]═════╗\n"
        f"║ /welcome • /setwelcome\n"
        f"║ /goodbye • /setgoodbye\n"
        f"║ /rules • /setrules\n"
        f"╚════════════════╝\n\n"
        f"╔═══[ {ST.bold_fancy('Notes & Filters')} ]═════╗\n"
        f"║ /save • /get • /notes • /clear\n"
        f"║ /filter • /filters • /stop\n"
        f"╚════════════════╝\n\n"
        f"╔═══[ {ST.bold_fancy('Protection')} ]═════╗\n"
        f"║ /antiflood • /antilink\n"
        f"║ /blacklist • /lock • /unlock\n"
        f"╚════════════════╝\n\n"
        f"╔═══[ {ST.bold_fancy('Info & Utility')} ]═════╗\n"
        f"║ /id • /info • /ping • /alive\n"
        f"║ /stats • /purge • /del\n"
        f"╚════════════════╝\n\n"
        f"{TPL.footer()}"
    )

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔒 Admin", callback_data="help_admin"),
         InlineKeyboardButton("👋 Welcome", callback_data="help_welcome")],
        [InlineKeyboardButton("🛡 Protection", callback_data="help_protection"),
         InlineKeyboardButton("📋 Notes", callback_data="help_notes")],
        [InlineKeyboardButton("🔧 Utility", callback_data="help_utility"),
         InlineKeyboardButton("🎮 Fun", callback_data="help_fun")],
        [InlineKeyboardButton("❌ Close", callback_data="help_close")],
    ])

    if chat.type != ChatType.PRIVATE:
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📩 Help in PM", url=f"t.me/{Config.BOT_USERNAME}?start=help")],
        ])

    await update.message.reply_text(help_text, parse_mode="HTML", reply_markup=buttons)


# ─── CMD: /settings ───

async def cmd_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Settings command - show group settings."""
    chat = update.effective_chat
    if chat.type == ChatType.PRIVATE:
        await update.message.reply_text(
            TPL.info(f"{ST.bold_fancy('Use /settings in a group!')}"),
            parse_mode="HTML"
        )
        return

    session = get_db()
    try:
        db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
        if not db_chat:
            db_chat = DBChat(chat_id=chat.id, chat_title=chat.title)
            session.add(db_chat)
            session.commit()

        text = (
            f"⚙️ {ST.bold_fancy('Settings')} — {html.escape(chat.title or 'Group')}\n"
            f"{TPL.SEPARATOR}\n\n"
            f"👋 {ST.bold_fancy('Welcome')}: {'✅' if db_chat.welcome_enabled else '❌'}\n"
            f"👋 {ST.bold_fancy('Goodbye')}: {'✅' if db_chat.goodbye_enabled else '❌'}\n"
            f"🔒 {ST.bold_fancy('Captcha')}: {'✅' if db_chat.captcha_enabled else '❌'}\n"
            f"🌊 {ST.bold_fancy('Antiflood')}: {'✅' if db_chat.antiflood_enabled else '❌'}\n"
            f"🔗 {ST.bold_fancy('Antilink')}: {'✅' if db_chat.antilink_enabled else '❌'}\n"
            f"🚫 {ST.bold_fancy('Warn Limit')}: {db_chat.warn_limit}\n"
            f"⚡ {ST.bold_fancy('Warn Action')}: {db_chat.warn_action}\n"
            f"\n{TPL.mini_footer()}"
        )

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                f"{'✅' if db_chat.welcome_enabled else '❌'} Welcome",
                callback_data=f"settings_toggle_welcome_{chat.id}"
            ), InlineKeyboardButton(
                f"{'✅' if db_chat.captcha_enabled else '❌'} Captcha",
                callback_data=f"settings_toggle_captcha_{chat.id}"
            )],
            [InlineKeyboardButton(
                f"{'✅' if db_chat.antiflood_enabled else '❌'} Antiflood",
                callback_data=f"settings_toggle_antiflood_{chat.id}"
            ), InlineKeyboardButton(
                f"{'✅' if db_chat.antilink_enabled else '❌'} Antilink",
                callback_data=f"settings_toggle_antilink_{chat.id}"
            )],
            [InlineKeyboardButton("❌ Close", callback_data="settings_close")],
        ])

    except Exception as e:
        logger.error(f"Settings error: {e}")
        text = TPL.error("Failed to load settings.")
        buttons = None
    finally:
        close_db(session)

    await update.message.reply_text(
        text, parse_mode="HTML",
        reply_markup=buttons
    )


# ─── CMD: /id ───

async def cmd_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user/chat ID."""
    user = update.effective_user
    chat = update.effective_chat
    msg = update.message

    if msg.reply_to_message:
        target = msg.reply_to_message.from_user
        text = (
            f"🆔 {ST.bold_fancy('User ID Info')}\n"
            f"{TPL.SEPARATOR}\n"
            f"✧ {ST.bold_fancy('User')}: {get_user_link(target)}\n"
            f"✧ {ST.bold_fancy('User ID')}: <code>{target.id}</code>\n"
            f"✧ {ST.bold_fancy('Chat ID')}: <code>{chat.id}</code>\n"
            f"{TPL.mini_footer()}"
        )
    else:
        text = (
            f"🆔 {ST.bold_fancy('ID Info')}\n"
            f"{TPL.SEPARATOR}\n"
            f"✧ {ST.bold_fancy('Your ID')}: <code>{user.id}</code>\n"
            f"✧ {ST.bold_fancy('Chat ID')}: <code>{chat.id}</code>\n"
            f"{TPL.mini_footer()}"
        )

    await msg.reply_text(text, parse_mode="HTML")


# ─── CMD: /info ───

async def cmd_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user profile info."""
    msg = update.message
    chat = update.effective_chat

    if msg.reply_to_message:
        user = msg.reply_to_message.from_user
    else:
        user = update.effective_user

    if not user:
        await msg.reply_text(TPL.error("User not found."), parse_mode="HTML")
        return

    # Try to get full info via DB
    session = get_db()
    try:
        db_user = session.query(DBUser).filter(DBUser.user_id == user.id).first()
    finally:
        close_db(session)

    status = "Unknown"
    try:
        member = await chat.get_member(user.id)
        status_map = {
            ChatMemberStatus.OWNER: "👑 Owner",
            ChatMemberStatus.ADMINISTRATOR: "🔰 Admin",
            ChatMemberStatus.MEMBER: "👤 Member",
            ChatMemberStatus.RESTRICTED: "🚫 Restricted",
            ChatMemberStatus.LEFT: "🚪 Left",
            ChatMemberStatus.BANNED: "⛔ Banned",
        }
        status = status_map.get(member.status, "Unknown")
    except Exception:
        pass

    bio = getattr(db_user, 'bio', None) or "No bio set"
    total_msgs = getattr(db_user, 'total_messages', 0) or 0

    text = (
        f"👤 {ST.bold_fancy('User Info')}\n"
        f"{TPL.SEPARATOR}\n"
        f"✧ {ST.bold_fancy('Name')}: {html.escape(user.full_name)}\n"
        f"✧ {ST.bold_fancy('ID')}: <code>{user.id}</code>\n"
        f"✧ {ST.bold_fancy('Username')}: @{user.username or 'N/A'}\n"
        f"✧ {ST.bold_fancy('Status')}: {status}\n"
        f"✧ {ST.bold_fancy('Premium')}: {'✅' if getattr(user, 'is_premium', False) else '❌'}\n"
        f"✧ {ST.bold_fancy('Bot')}: {'✅' if user.is_bot else '❌'}\n"
        f"✧ {ST.bold_fancy('Messages')}: {format_number(total_msgs)}\n"
        f"✧ {ST.bold_fancy('Bio')}: {html.escape(bio[:100])}\n"
        f"{TPL.mini_footer()}"
    )

    await msg.reply_text(text, parse_mode="HTML")


# ─── CMD: /ping ───

async def cmd_ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check bot response speed."""
    start = time.time()
    msg = await update.message.reply_text("🏓 Pinging...")
    elapsed = round((time.time() - start) * 1000, 2)
    await msg.edit_text(
        f"🏓 {ST.bold_fancy('Pong!')} — {elapsed}ms\n"
        f"✧ {ST.bold_fancy('Status')}: Online ✅\n"
        f"{TPL.mini_footer()}",
        parse_mode="HTML"
    )


# ─── CMD: /alive ───

async def cmd_alive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot is alive with uptime."""
    uptime = datetime.datetime.utcnow() - bot_start_time
    text = (
        f"✦ {ST.bold_fancy('Bot is Alive!')} ✦\n"
        f"{TPL.SEPARATOR}\n"
        f"✧ {ST.bold_fancy('Status')}: 🟢 Online\n"
        f"✧ {ST.bold_fancy('Uptime')}: {format_timedelta(uptime)}\n"
        f"✧ {ST.bold_fancy('Bot')}: {Config.BOT_NAME}\n"
        f"✧ {ST.bold_fancy('Owner')}: {Config.OWNER_NAME}\n"
        f"✧ {ST.bold_fancy('Python')}: {platform.python_version()}\n"
        f"{TPL.footer()}"
    )
    if Config.ALIVE_IMG:
        try:
            await update.message.reply_photo(Config.ALIVE_IMG, caption=text, parse_mode="HTML")
            return
        except Exception:
            pass
    await update.message.reply_text(text, parse_mode="HTML")


# ─── Callback: start_ ───

async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle start menu inline buttons."""
    query = update.callback_query
    data = query.data
    await query.answer()

    if data == "start_help":
        await query.message.edit_text(
            f"📋 {ST.bold_fancy('Help')} — use /help for full list.",
            parse_mode="HTML"
        )
    elif data == "start_about":
        await query.message.edit_text(
            f"ℹ️ {ST.bold_fancy('About')}\n"
            f"{TPL.SEPARATOR}\n"
            f"✧ Bot: {Config.BOT_NAME}\n"
            f"✧ Owner: {Config.OWNER_NAME}\n"
            f"✧ Platform: Render (PostgreSQL)\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )


# ─── Callback: help_ ───

async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle help menu inline buttons."""
    query = update.callback_query
    data = query.data
    await query.answer()

    HELP_SECTIONS = {
        "help_admin": (
            "🔒 Admin Commands",
            "/ban /unban /tban /sban\n/mute /unmute /tmute /smute\n"
            "/kick /skick /kickme\n/warn /warns /resetwarns\n"
            "/promote /demote /fullpromote\n/adminlist /settitle\n"
            "/gban /ungban /gbanlist\n/approve /disapprove"
        ),
        "help_welcome": (
            "👋 Welcome/Goodbye",
            "/welcome /setwelcome /resetwelcome\n"
            "/goodbye /setgoodbye\n/captcha\n"
            "/rules /setrules /clearrules\n/cleanwelcome"
        ),
        "help_protection": (
            "🛡 Protection",
            "/antiflood /setflood\n/antilink /allowlink\n"
            "/blacklist /unblacklist\n/lock /unlock /locks"
        ),
        "help_notes": (
            "📋 Notes & Filters",
            "/save /get /notes /clear /clearall\n"
            "/filter /filters /stop"
        ),
        "help_utility": (
            "🔧 Utility",
            "/id /info /ping /alive\n/purge /del /pin /unpin\n"
            "/stats /setlog /unsetlog"
        ),
        "help_fun": (
            "🎮 Fun & Games",
            "/truth /dare /ship /roll\n"
            "/slap /punch /hug /kiss\n"
            "/tictactoe /rps"
        ),
    }

    if data == "help_close":
        await query.message.delete()
        return

    section = HELP_SECTIONS.get(data)
    if section:
        title, content = section
        back_btn = InlineKeyboardMarkup([[
            InlineKeyboardButton("◀️ Back", callback_data="help_back")
        ]])
        await query.message.edit_text(
            f"✦ {ST.bold_fancy(title)} ✦\n{TPL.SEPARATOR}\n\n{content}\n\n{TPL.mini_footer()}",
            parse_mode="HTML", reply_markup=back_btn
        )
    elif data == "help_back":
        await cmd_help(update, context)


# ─── Callback: settings_ ───

async def settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle settings toggle inline buttons."""
    query = update.callback_query
    user = query.from_user
    data = query.data
    chat = query.message.chat

    await query.answer()

    if data == "settings_close":
        await query.message.delete()
        return

    # Must be admin to toggle settings
    if not await is_admin(update, user.id):
        await query.answer("❌ Only admins can change settings!", show_alert=True)
        return

    if data.startswith("settings_toggle_"):
        parts = data.split("_")
        # format: settings_toggle_{field}_{chat_id}
        field = parts[2]
        toggle_map = {
            "welcome": "welcome_enabled",
            "captcha": "captcha_enabled",
            "antiflood": "antiflood_enabled",
            "antilink": "antilink_enabled",
            "goodbye": "goodbye_enabled",
        }
        db_field = toggle_map.get(field)
        if db_field:
            session = get_db()
            try:
                db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
                if db_chat:
                    current = getattr(db_chat, db_field, False)
                    setattr(db_chat, db_field, not current)
                    session.commit()
                    await query.answer(f"{'✅ Enabled' if not current else '❌ Disabled'} {field}!")
            except Exception:
                session.rollback()
            finally:
                close_db(session)

    # Refresh settings message
    fake_update = update
    await cmd_settings(fake_update, context)


# ─── Alias for cmd_welcomemute (maps to cmd_welcomemutenew) ───
cmd_welcomemute = cmd_welcomemutenew

# ─── Alias for cmd_setantilink (maps to cmd_antilink as setter) ───
cmd_setantilink = cmd_antilink


# ═══════════════════════════════════════════════════════════════
#  SECTION 7: WHOIS / BIO / USER LOOKUP (Missing implementations)
# ═══════════════════════════════════════════════════════════════

async def cmd_whois(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Full user information lookup. Usage: /whois [reply|@user|id]"""
    msg = update.message
    chat = update.effective_chat

    if msg.reply_to_message:
        target = msg.reply_to_message.from_user
    else:
        user_id, target = await extract_user(msg, context)
        if not user_id and not target:
            target = update.effective_user
            user_id = target.id

    if not target:
        await msg.reply_text(
            TPL.error("❌ User not found. Reply to a message or provide @username / ID."),
            parse_mode="HTML"
        )
        return

    # Get DB info
    session = get_db()
    try:
        db_user = session.query(DBUser).filter(DBUser.user_id == target.id).first()
        db_warns_count = session.query(DBWarn).filter(
            DBWarn.user_id == target.id,
            DBWarn.chat_id == chat.id
        ).count()
        gban = session.query(DBGban).filter(
            DBGban.user_id == target.id,
            DBGban.is_active == True
        ).first()
    finally:
        close_db(session)

    # Get chat status
    member_status = "Unknown"
    try:
        member = await chat.get_member(target.id)
        status_map = {
            ChatMemberStatus.OWNER: "👑 Owner",
            ChatMemberStatus.ADMINISTRATOR: "🔰 Admin",
            ChatMemberStatus.MEMBER: "👤 Member",
            ChatMemberStatus.RESTRICTED: "🚫 Restricted",
            ChatMemberStatus.LEFT: "🚪 Left",
            ChatMemberStatus.BANNED: "⛔ Banned",
        }
        member_status = status_map.get(member.status, "Unknown")
    except Exception:
        pass

    # Build bio
    bio = ""
    if db_user and db_user.bio:
        bio = f"\n✧ {ST.bold_fancy('Bio')}: {escape_html(db_user.bio[:200])}"

    # Build text
    text = (
        f"🔍 {ST.bold_fancy('Whois')} — Full Profile\n"
        f"{TPL.SEPARATOR}\n"
        f"✧ {ST.bold_fancy('Name')}: {html.escape(target.full_name)}\n"
        f"✧ {ST.bold_fancy('ID')}: <code>{target.id}</code>\n"
        f"✧ {ST.bold_fancy('Username')}: {'@' + target.username if target.username else 'N/A'}\n"
        f"✧ {ST.bold_fancy('Status in Chat')}: {member_status}\n"
        f"✧ {ST.bold_fancy('Premium')}: {'✅' if getattr(target, 'is_premium', False) else '❌'}\n"
        f"✧ {ST.bold_fancy('Bot')}: {'✅' if target.is_bot else '❌'}\n"
        f"✧ {ST.bold_fancy('Warns Here')}: {db_warns_count}\n"
        f"✧ {ST.bold_fancy('GBanned')}: {'🔴 Yes' if gban else '🟢 No'}\n"
        f"✧ {ST.bold_fancy('Total Messages')}: {format_number(getattr(db_user, 'total_messages', 0) or 0)}\n"
        f"✧ {ST.bold_fancy('Seen')}: {time_since(getattr(db_user, 'last_seen', None)) if db_user else 'Never'}"
        f"{bio}\n"
        f"{TPL.mini_footer()}"
    )

    try:
        photos = await context.bot.get_user_profile_photos(target.id, limit=1)
        if photos.total_count > 0:
            await msg.reply_photo(
                photos.photos[0][-1].file_id,
                caption=text, parse_mode="HTML"
            )
            return
    except Exception:
        pass

    await msg.reply_text(text, parse_mode="HTML")


async def cmd_bio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View bio of yourself or another user. Usage: /bio [reply|@user|id]"""
    msg = update.message

    if msg.reply_to_message:
        target = msg.reply_to_message.from_user
        target_id = target.id if target else None
    else:
        target_id, target = await extract_user(msg, context)
        if not target_id:
            target = update.effective_user
            target_id = target.id

    if not target_id:
        await msg.reply_text(TPL.error("User not found."), parse_mode="HTML")
        return

    session = get_db()
    try:
        db_user = session.query(DBUser).filter(DBUser.user_id == target_id).first()
    finally:
        close_db(session)

    bio = getattr(db_user, 'bio', None) if db_user else None
    name = html.escape(target.first_name if target else str(target_id))

    if bio:
        text = (
            f"📝 {ST.bold_fancy('Bio')} of {name}\n"
            f"{TPL.SEPARATOR}\n"
            f"{escape_html(bio)}\n"
            f"{TPL.mini_footer()}"
        )
    else:
        text = (
            f"📝 {ST.bold_fancy('Bio')} of {name}\n"
            f"{TPL.SEPARATOR}\n"
            f"ℹ️ No bio set yet.\n"
            f"Use /setbio &lt;text&gt; to set yours!\n"
            f"{TPL.mini_footer()}"
        )

    await msg.reply_text(text, parse_mode="HTML")


async def cmd_setbio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set your bio. Usage: /setbio &lt;text&gt;"""
    msg = update.message
    user = update.effective_user

    args = msg.text.split(None, 1)
    if len(args) < 2:
        await msg.reply_text(
            f"ℹ️ {ST.bold_fancy('Usage')}: /setbio &lt;your bio text&gt;\n"
            f"✧ Max 200 characters.\n"
            f"✧ Use /bio to view your bio.",
            parse_mode="HTML"
        )
        return

    bio_text = args[1].strip()
    if len(bio_text) > 200:
        await msg.reply_text(
            TPL.error(f"Bio too long! Max 200 chars. You wrote {len(bio_text)}."),
            parse_mode="HTML"
        )
        return

    session = get_db()
    try:
        db_user = session.query(DBUser).filter(DBUser.user_id == user.id).first()
        if db_user:
            db_user.bio = bio_text
        else:
            db_user = DBUser(
                user_id=user.id,
                first_name=user.first_name,
                username=user.username,
                bio=bio_text
            )
            session.add(db_user)
        session.commit()
        await msg.reply_text(
            f"✅ {ST.bold_fancy('Bio updated!')}\n"
            f"✧ {escape_html(bio_text)}\n"
            f"{TPL.mini_footer()}",
            parse_mode="HTML"
        )
    except Exception as e:
        session.rollback()
        logger.error(f"setbio error: {e}")
        await msg.reply_text(TPL.error("Failed to set bio. Try again."), parse_mode="HTML")
    finally:
        close_db(session)


def main():
    """Main entry point - initialize bot and run."""
    logger.info("=" * 60)
    logger.info("  ✦ Ruhi x Assistant - Starting Up ✦")
    logger.info("=" * 60)

    # ── Validate config ──
    if not Config.BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not set!")
        sys.exit(1)

    if not Config.DATABASE_URL:
        logger.error("❌ DATABASE_URL not set!")
        sys.exit(1)

    # ── Initialize database ──
    logger.info("📦 Initializing database...")
    init_db()
    logger.info("✅ Database ready!")

    # ── Load caches ──
    logger.info("📋 Loading caches...")
    load_caches()

    # ── Build application ──
    logger.info("🤖 Building bot application...")

    app = (
        ApplicationBuilder()
        .token(Config.BOT_TOKEN)
        .read_timeout(30)
        .write_timeout(30)
        .connect_timeout(30)
        .pool_timeout(30)
        .build()
    )

    # ═══════════════════════════════════════════
    #  REGISTER ALL SECTION HANDLERS
    # ═══════════════════════════════════════════

    logger.info("📝 Registering handlers...")

    # Section 1-3: Core (start, help, settings, user tracking)
    # These are registered inline below

    # ── Section 1-3 Core Commands ──
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("settings", cmd_settings))
    app.add_handler(CommandHandler("id", cmd_id))
    app.add_handler(CommandHandler("info", cmd_info))
    app.add_handler(CommandHandler("ping", cmd_ping))
    app.add_handler(CommandHandler("alive", cmd_alive))
    app.add_handler(CommandHandler("rules", cmd_rules))
    app.add_handler(CommandHandler("setrules", cmd_setrules))
    app.add_handler(CommandHandler("clearrules", cmd_clearrules))

    # ── Section 3 Extra: Whois / Bio / User Info ──
    app.add_handler(CommandHandler("whois", cmd_whois))
    app.add_handler(CommandHandler("bio", cmd_bio))
    app.add_handler(CommandHandler("setbio", cmd_setbio))
    app.add_handler(CommandHandler("getbio", cmd_bio))

    # Section 3 callbacks
    app.add_handler(CallbackQueryHandler(help_callback, pattern=r"^help_"))
    app.add_handler(CallbackQueryHandler(settings_callback, pattern=r"^settings_"))
    app.add_handler(CallbackQueryHandler(start_callback, pattern=r"^start_"))

    # ── Section 4: Admin & Moderation ──
    app.add_handler(CommandHandler("ban", cmd_ban))
    app.add_handler(CommandHandler("unban", cmd_unban))
    app.add_handler(CommandHandler("tban", cmd_tban))
    app.add_handler(CommandHandler("sban", cmd_sban))
    app.add_handler(CommandHandler("mute", cmd_mute))
    app.add_handler(CommandHandler("unmute", cmd_unmute))
    app.add_handler(CommandHandler("tmute", cmd_tmute))
    app.add_handler(CommandHandler("smute", cmd_smute))
    app.add_handler(CommandHandler("kick", cmd_kick))
    app.add_handler(CommandHandler("skick", cmd_skick))
    app.add_handler(CommandHandler("kickme", cmd_kickme))
    app.add_handler(CommandHandler("warn", cmd_warn))
    app.add_handler(CommandHandler("warns", cmd_warns))
    app.add_handler(CommandHandler("resetwarns", cmd_resetwarns))
    app.add_handler(CommandHandler("warnlimit", cmd_warnlimit))
    app.add_handler(CommandHandler("warnaction", cmd_warnaction))
    app.add_handler(CommandHandler("promote", cmd_promote))
    app.add_handler(CommandHandler("demote", cmd_demote))
    app.add_handler(CommandHandler("fullpromote", cmd_fullpromote))
    app.add_handler(CommandHandler("settitle", cmd_settitle))
    app.add_handler(CommandHandler("adminlist", cmd_adminlist))
    app.add_handler(CommandHandler("baninfo", cmd_baninfo))
    app.add_handler(CommandHandler("gban", cmd_gban))
    app.add_handler(CommandHandler("ungban", cmd_ungban))
    app.add_handler(CommandHandler("gbanlist", cmd_gbanlist))
    app.add_handler(CommandHandler("report", cmd_report))
    app.add_handler(CommandHandler("reports", cmd_reports))
    app.add_handler(CommandHandler("approve", cmd_approve))
    app.add_handler(CommandHandler("disapprove", cmd_disapprove))
    app.add_handler(CommandHandler("approved", cmd_approved))
    app.add_handler(CommandHandler("cleanservice", cmd_cleanservice))
    app.add_handler(CommandHandler("setlog", cmd_setlog))
    app.add_handler(CommandHandler("unsetlog", cmd_unsetlog))

    # Section 4 callbacks
    app.add_handler(CallbackQueryHandler(warn_callback_handler, pattern=r"^rmwarn_"))
    app.add_handler(CallbackQueryHandler(resetwarns_callback, pattern=r"^resetwarns_"))

    # ── Section 5-6: Anti-spam, Anti-flood, Anti-link, Welcome ──
    app.add_handler(CommandHandler("antiflood", cmd_antiflood))
    app.add_handler(CommandHandler("setflood", cmd_setflood))
    app.add_handler(CommandHandler("setfloodtime", cmd_setfloodtime))
    app.add_handler(CommandHandler("setfloodaction", cmd_setfloodaction))
    app.add_handler(CommandHandler("welcome", cmd_welcome))
    app.add_handler(CommandHandler("setwelcome", cmd_setwelcome))
    app.add_handler(CommandHandler("resetwelcome", cmd_resetwelcome))
    app.add_handler(CommandHandler("goodbye", cmd_goodbye))
    app.add_handler(CommandHandler("setgoodbye", cmd_setgoodbye))
    app.add_handler(CommandHandler("cleanwelcome", cmd_cleanwelcome))
    app.add_handler(CommandHandler("welcomemute", cmd_welcomemute))
    app.add_handler(CommandHandler("captcha", cmd_captcha))
    app.add_handler(CommandHandler("antilink", cmd_antilink))
    app.add_handler(CommandHandler("setantilink", cmd_setantilink))
    app.add_handler(CommandHandler("allowlink", cmd_allowlink))

    # Section 5-6 callbacks
    app.add_handler(CallbackQueryHandler(captcha_callback, pattern=r"^captcha_"))
    app.add_handler(CallbackQueryHandler(welcome_button_callback, pattern=r"^wlcm_"))

    # ── Section 7: Notes, Filters, Locks, Pin, Purge, etc. ──
    register_section7_handlers(app)

    # ── Section 8: Fun, Games, Reactions ──
    register_section8_handlers(app)

    # ── Section 9: Utilities, Tools, APIs ──
    register_section9_handlers(app)

    # ── Section 10: Owner, Stats, Broadcast, Maintenance ──
    register_section10_handlers(app)

    # ═══════════════════════════════════════════
    #  MESSAGE HANDLERS (Global - lowest priority)
    # ═══════════════════════════════════════════

    # Maintenance check (highest priority)
    app.add_handler(MessageHandler(
        filters.ALL,
        maintenance_check
    ), group=0)

    # User/chat tracking
    app.add_handler(MessageHandler(
        filters.ALL,
        track_user_chat
    ), group=1)

    # Anti-flood check
    app.add_handler(MessageHandler(
        filters.ALL & ~filters.COMMAND & filters.ChatType.GROUPS,
        flood_check_handler
    ), group=5)

    # Anti-link check
    app.add_handler(MessageHandler(
        (filters.TEXT | filters.CAPTION) & filters.ChatType.GROUPS,
        antilink_check_handler
    ), group=6)

    # GBan enforcement on join
    app.add_handler(MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS,
        gban_join_check
    ), group=7)

    # Welcome handler
    app.add_handler(MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS,
        welcome_handler
    ), group=8)

    # Goodbye handler
    app.add_handler(MessageHandler(
        filters.StatusUpdate.LEFT_CHAT_MEMBER,
        goodbye_handler
    ), group=9)

    # ═══════════════════════════════════════════
    #  SCHEDULED JOBS
    # ═══════════════════════════════════════════

    job_queue = app.job_queue

    # Night mode check every 5 minutes
    if job_queue:
        job_queue.run_repeating(
            night_mode_job,
            interval=300,
            first=60,
            name="night_mode_check"
        )

    # ═══════════════════════════════════════════
    #  START FLASK WEB SERVER (for Render)
    # ═══════════════════════════════════════════

    logger.info("🌐 Starting web server...")
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"✅ Web server running on port {port}")

    # ═══════════════════════════════════════════
    #  START BOT
    # ═══════════════════════════════════════════

    logger.info("=" * 60)
    logger.info("  🚀 Bot is starting with polling...")
    logger.info(f"  👑 Owner ID: {Config.OWNER_ID}")
    logger.info(f"  📊 Sudo users: {len(sudo_users_cache)}")
    logger.info(f"  🤖 Bot Token: ...{Config.BOT_TOKEN[-8:]}")
    logger.info("=" * 60)

    # Run the bot
    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES,
        close_loop=False
    )


# ═══════════════════════════════════════════════════════════════
#  WRAPPER HANDLERS (referenced in main but defined elsewhere)
# ═══════════════════════════════════════════════════════════════

async def track_user_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Track users and chats in database."""
    if not update.effective_user:
        return

    user = update.effective_user
    chat = update.effective_chat

    session = get_db()
    try:
        # Track user
        db_user = session.query(DBUser).filter(DBUser.user_id == user.id).first()
        if db_user:
            db_user.first_name = user.first_name
            db_user.last_name = user.last_name
            db_user.username = user.username
            db_user.last_seen = datetime.datetime.utcnow()
        else:
            db_user = DBUser(
                user_id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username
            )
            session.add(db_user)

        # Track chat
        if chat and chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
            db_chat = session.query(DBChat).filter(DBChat.chat_id == chat.id).first()
            if db_chat:
                db_chat.title = chat.title
            else:
                db_chat = DBChat(
                    chat_id=chat.id,
                    title=chat.title,
                    chat_type=str(chat.type)
                )
                session.add(db_chat)

        session.commit()
    except Exception:
        session.rollback()
    finally:
        close_db(session)


async def flood_check_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper for flood check."""
    await check_flood(update, context)


async def antilink_check_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper for antilink check."""
    await check_antilink(update, context)


async def gban_join_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check if joining user is gbanned."""
    if not update.message or not update.message.new_chat_members:
        return

    chat = update.effective_chat

    session = get_db()
    try:
        for new_member in update.message.new_chat_members:
            gban = session.query(DBGban).filter(
                DBGban.user_id == new_member.id,
                DBGban.is_active == True
            ).first()

            if gban:
                try:
                    await chat.ban_member(new_member.id)
                    await send_and_delete(
                        chat.id,
                        f"🌍🔨 {ST.bold_fancy('GBanned user detected!')}\n"
                        f"✧ {get_user_link(new_member)} is globally banned.\n"
                        f"✧ {ST.bold_fancy('Reason')}: {escape_html(gban.reason or 'No reason')}",
                        context, seconds=15, parse_mode="HTML"
                    )
                except Exception:
                    pass

            # Also check federation bans
            fed_chat = session.query(DBFedChat).filter(
                DBFedChat.chat_id == chat.id
            ).first()

            if fed_chat:
                fban = session.query(DBFedBan).filter(
                    DBFedBan.fed_id == fed_chat.fed_id,
                    DBFedBan.user_id == new_member.id,
                    DBFedBan.is_active == True
                ).first()

                if fban:
                    try:
                        await chat.ban_member(new_member.id)
                        await send_and_delete(
                            chat.id,
                            f"🏛🔨 {ST.bold_fancy('FBanned user detected!')}",
                            context, seconds=10, parse_mode="HTML"
                        )
                    except Exception:
                        pass

    except Exception as e:
        logger.error(f"GBan join check error: {e}")
    finally:
        close_db(session)


# ═══════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Validate telegram installed
    try:
        import telegram  # noqa: F401
    except ImportError:
        print("❌ python-telegram-bot not installed!")
        print("Run: pip install python-telegram-bot[all]")
        sys.exit(1)

    main()


# ═══════════════════════════════════════════════════════════════
# END OF SECTION 10 — END OF PART 1 (Sections 1-10)
# ═══════════════════════════════════════════════════════════════
