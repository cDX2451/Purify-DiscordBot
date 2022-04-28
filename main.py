# -*- coding: utf-8 -*-

import discord
import requests
from discord.ext import tasks, commands
import asyncio
import PIL
from PIL import Image

admin_tag = "Admin#0000"
token = "#############"
origin_channel_id = 0
destin_channel_id = 0
censor_emoji = 0

attachment_q = []

def censorImage():
        params = (
            ('type', 'black'),
            ('classes', 'ftite,ftitc,fgene,fgenc,feete,anusc,anuse'),
            )
        files = {'file': open('uncensored2.jpg','rb')}

        try:
            response = requests.post('http://pury.fi/censor', params=params, files=files, timeout=15)
        except:
            TIME_OUT = 1
        
        if response:
            if response.status_code == 200:
                with open('censored.jpg', 'wb') as f:
                    f.write(response.content)
                return True
            else:
                return False
        else:
            return False
        return False


class MyClient(discord.Client):
    async def on_ready(self):
        print(f"Running")
        self.process_Q.start()

    async def on_reaction_add(self, reaction, user):
        destin_channel = client.get_channel(destin_channel_id)
        origin_channel = client.get_channel(origin_channel_id)
        
        if reaction.message.channel.id == origin_channel_id:
            if reaction.custom_emoji:
                if reaction.emoji.id == censor_emoji:
                    if reaction.count == 1:
                        if reaction.message.attachments:
                            if reaction.message.attachments[0].height >= 1:
                                if reaction.message.attachments[0].url.endswith('.png') or reaction.message.attachments[0].url.endswith('.jpg') or reaction.message.attachments[0].url.endswith('.jpeg'):
                                    attachment_q.append(reaction.message.id)

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.channel.type == discord.ChannelType.private:
            if str(message.author) == admin_tag:
                if message.content.startswith(f"!reset censorbot"):
                    attachment_q.clear()

    @tasks.loop(seconds=4.0)
    async def process_Q(self):
        items = len(attachment_q)
        print(f"Qeued items: {items}")
        if items >= 1:
            cur_msg = await client.get_channel(origin_channel_id).fetch_message(attachment_q[0])
            if cur_msg.attachments:
                await cur_msg.attachments[0].save("uncensored.jpg")
                mywidth = 500
                img = Image.open('uncensored.jpg')
                img = img.convert("RGB")
                if img.size[0] >= 500:
                    wpercent = (mywidth/float(img.size[0]))
                    hsize = int((float(img.size[1])*float(wpercent)))
                    img = img.resize((mywidth,hsize), PIL.Image.ANTIALIAS)
                img.save("uncensored2.jpg", "JPEG", optimize=True)

                if censorImage():
                    e = discord.Embed(description="", colour=0x000000)
                    f = discord.File("censored.jpg")
                    await client.get_channel(destin_channel_id).send(file=f)
                else:
                    print("Couldn't upload image.")
                    attachment_q.pop(0)
                    await asyncio.sleep(60)
        else:
            print("No images to process.")
        if items != 0:
            attachment_q.pop(0)


client = MyClient()
client.run(token)


