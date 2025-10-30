from fastapi import HTTPException
from beanie import PydanticObjectId
import logging

from shared.models import Chat, User, Message
from shared.schemas import ChatSchemaOut, ChatSchemaIn, UserRead, MessageSchemaIn, MessageSchemaOut


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chat-service")


async def get_user_by_id(user_id: str) -> UserRead:
    user = await User.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"no user with id: {user_id}")
    
    return UserRead(
        id=str(user.id),
        username=user.username,
        email=user.email,
        created_at=user.created_at
    )


async def is_user_in_chat(user_id: str, chat_id: str) -> bool:
    user = await User.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"no user with id: {user_id}")
    
    chat = await Chat.get(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail=f"no chat with id: {chat_id}")
    
    return PydanticObjectId(user_id) in [p.ref.id for p in chat.participants]



# TO OPTIMIZE
async def get_chats_db(user_id: str) -> list[ChatSchemaOut]:
    try:
        user = await User.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"no user with id: {user_id}")
        
                
        db_chats = await Chat.find(
            Chat.participants.id == user.id,
            fetch_links=True
        ).to_list()
        logger.info(db_chats)

        chats = [
            ChatSchemaOut(
                    id = str(chat.id),
                    participants=[str(part.id) for part in chat.participants],
                    name=chat.name,
                    created_at=chat.created_at
                )
            for chat in db_chats
        ]

        return chats

    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    

async def create_chat_db(user_id: str, chat_schema: ChatSchemaIn) -> ChatSchemaOut:
    try:
        user = await User.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"no user with id: {user_id}")
        
        db_participants = [await User.get(part_id) for part_id in chat_schema.participants] 
        db_participants.append(user)
        
        chat = Chat(
            participants=db_participants,
            name=chat_schema.name,
            created_at=chat_schema.created_at
        )
        await chat.insert()

        return ChatSchemaOut(
            id=str(chat.id),
            participants=chat_schema.participants,
            name=chat.name,
            created_at = chat_schema.created_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    

async def create_message(message_scheme: MessageSchemaIn):
    user = await User.get(message_scheme.user)
    chat = await Chat.get(message_scheme.chat)
    message = Message(
        user=user,
        chat=chat,
        text=message_scheme.text
    )
    await message.insert()


async def get_message_from_chat(chat_id: str, limit: int = 50) -> list[MessageSchemaOut]:
    chat = await Chat.get(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail=f"no chat with id: {chat_id}")
    
    try:
        db_messages = await Message.find(
            Message.chat.id == PydanticObjectId(chat_id),
            fetch_links=True
        ).sort(-Message.created_at).limit(limit).to_list()

        messages = [
            MessageSchemaOut(
                id=str(message.id),
                chat=str(chat.id),
                text=message.text,
                user=str(message.user.id)
            )
            for message in db_messages
        ]
        
        return messages
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))