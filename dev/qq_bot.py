from botpy.message     import Message, DirectMessage
from botpy.interaction import Interaction
from botpy.reaction    import Reaction
from rich              import print
import botpy


appid = '102790871'
token = 'pmkigecaZYXWVUUUUUUUVWXYZacegikm'


class MyClient(botpy.Client):
    async def on_ready(self):
        print(f"robot 「{self.robot.name}」 on_ready!")

    async def on_direct_message_create(self, message: DirectMessage):
        await self.api.post_dms(
            guild_id=message.guild_id,
            content=f"机器人{self.robot.name}收到你的私信了: {message.content}",
            msg_id=message.id,
        )

    async def on_at_message_create(self, message: Message):
        if "/私信" in message.content:
            dms_payload = await self.api.create_dms(message.guild_id, message.author.id)
            print("发送私信")
            await self.api.post_dms(dms_payload["guild_id"], content="hello", msg_id=message.id)

    async def on_at_message_create(self, message: Message):
        print(message.author.avatar)
        print(message.author.username)
        await message.reply(content=f"机器人{self.robot.name}收到你的@消息了: {message.content}")


intents = botpy.Intents(
    public_guild_messages=True,
    guild_message_reactions=True,
    interaction=True,
    direct_message=True,
)
client = MyClient(intents=intents)
client.run(appid=appid, secret=token)