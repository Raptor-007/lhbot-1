# local
from .helpers import config
from .helpers import challenges

import discord
import asyncio

from discord.ext import commands

class Tools(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.command(help='🔧Zeige eine Demo für die Verifizierung an.')
    async def verifydemo(self, ctx):
        challenge = challenges.get_challenge()
        await ctx.send(embed=discord.Embed(title='Verification Challenge Demo', description=challenge[0], color=discord.Color(0x00FFFF)).set_footer(text=f'Richtig wäre: {challenge[1]}'))

    @commands.has_permissions(manage_messages=True)
    @commands.command(help='🔒Löscht eine bestimme Anzahl von Nachrichten im aktuellen Kanal, kein Argument angeben, um alle Nachrichten in dem aktuellen zu löschen. Benötigt die "manage_messages" Berechtigung für sowohl den Bot, als auch für den Nutzer.', aliases=['purge'])
    async def clear(self, ctx, count=999999):
        are_you_sure_message = await ctx.send(delete_after=60, embed=discord.Embed(title='Bist du dir sicher?', description=f'Reagiere, um **{count if count != 999999 else "alle"}** Nachrichten in diesem Kanal zu löschen.\nDieser Vorgang kann nicht rückgängig gemacht werden.', color=discord.Color(0xFFFF00)).set_footer(text='Diese Nachricht wird nach 60 Sekunden gelöscht.'))
        
        await are_you_sure_message.add_reaction('☑️')

        def check(reaction, user): return reaction.message == are_you_sure_message and user == ctx.author

        try:
            await self.client.wait_for('reaction_add', check=check, timeout=60)
        except asyncio.TimeoutError:
            return

        await ctx.channel.purge(limit=count)
        await ctx.send(delete_after=5, embed=discord.Embed(title=':wastebasket: Chat gepurged!', description=f'**{count if count != 999999 else "Alle"}** Nachrichten im Kanal sollten jetzt weg sein! :)', color=discord.Color(0x00FF00)).set_footer(text='Diese Nachricht wird nach 5 Sekunden gelöscht.'))

    @commands.has_permissions(ban_members=True)
    @commands.command(help='🔒Bannt jemanden (Eingabe: ping/name#tag/ID). [Benötigt die "ban_members" Berechtigung für sowohl den Bot, als auch für den Nutzer.]')
    async def ban(self, ctx, member: discord.Member):
        await ctx.guild.ban(user=member, reason=str(ctx.author))
        await ctx.message.add_reaction('👍')

    @commands.has_permissions(ban_members=True)
    @commands.command(help='🔒Entbannt jemanden (Eingabe: ID). [Benötigt die "ban_members" Berechtigung für sowohl den Bot, als auch für den Nutzer.]')
    async def unban(self, ctx, user: discord.User):
        await ctx.guild.unban(user=user, reason=str(ctx.author))
        await ctx.message.add_reaction('👍')

    @commands.command(help='🔧Zeit Infos über Mitglieder der Servers an! (Eingabe: ping/name#tag/ID)')
    async def info(self, ctx, member: discord.Member=None):
        member = ctx.author if not member else member

        custom_status = '*[inaktiv]*'
        activity = '*[inaktiv]*'

        if member.activities:
            for member_activity in member.activities:
                if isinstance(member_activity, discord.CustomActivity):
                    custom_status = member_activity.name
                    continue
                activity = member_activity.name
        
        nick = member.nick if member.nick else '*[Not set]*'

        roles = ' '.join([r.mention for r in member.roles])    

        status = member.status
        created = member.created_at.strftime('%A, %B %d, %Y %H:%M:%S %p %Z')
        joined = member.joined_at.strftime('%A, %B %d, %Y %H:%M:%S %p %Z')
        highest_role = member.top_role.mention

        status_icon = str(member.status).replace('dnd', ':no_entry:').replace('online', ':green_circle:').replace('idle', ':crescent_moon:').replace('offline', ':black_circle:')
        info = f'''
            **ID**
            {member.id}
            **Nickname**
            {nick}
            **Status**
            {status}
            **Custom Status**
            {custom_status}
            **Aktivität**
            {activity}
            **Konto erstellt**
            {created}
            **Server beigetreten**
            {joined}
            **Hauptrolle**
            {highest_role}
            **Alle Rollen**
            {roles}
            '''
        embed = discord.Embed(title=f'{status_icon} {member.name}#{member.discriminator}', color=member.top_role.color, description=info)
        embed.set_thumbnail(url=member.avatar_url)
        
        await ctx.send(embed=embed)

    @commands.command(help='🔧Zeit Infos über den Server an!')
    async def serverinfo(self, ctx):
        created = ctx.guild.created_at.strftime('%A, %B %d, %Y %H:%M:%S %p %Z')

        text = f'''
        **ID**
        {ctx.guild.id}
        **Erstellt**
        {created}
        **Mitgliederanzahl**
        {ctx.guild.member_count}
        **Rollenanzahl**
        {len(ctx.guild.roles)}
        **Kanalanzahl**
        {len(ctx.guild.channels)}
        **Eigentümer**
        {ctx.guild.owner.mention}
        **Nitro Boosts**
        {ctx.guild.premium_subscription_count}
        '''

        embed = discord.Embed(title=ctx.guild.name, color=config.load()['design']['colors']['primary'], description=text)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.send(embed=embed)

    @commands.has_permissions(kick_members=True)
    @commands.command(help='🔒Mute jemanden (Eingabe: ping/name#tag/ID) [Benötigt die "kick_members" Berechtigung für den Nutzer.]')
    async def mute(self, ctx, member: discord.Member):
        roles = []
        for role_id in config.load()['commands']['mute_role_ids']:
            if role_id in [r.id for r in ctx.guild.roles]:
                roles.append(ctx.guild.get_role(role_id))
                await member.add_roles(ctx.guild.get_role(role_id))

        embed = discord.Embed(title=f'{member} wurde gemutet!', color=0xFF0000, description=f'{member.mention} hat die {"folgenden Rollen" if len(roles) > 1 else "folgende Rolle"} bekommen:\n> {" ".join(r.mention for r in roles)}\nund hat ab sofort beschränken Zugriff auf den Server.')
        embed.set_thumbnail(url=member.avatar_url)
        await ctx.send(embed=embed)

    @commands.has_permissions(kick_members=True)
    @commands.command(help='🔒Entmute jemanden (Eingabe: ping/name#tag/ID) [Benötigt die "kick_members" Berechtigung für den Nutzer.]')
    async def unmute(self, ctx, member: discord.Member):
        roles = []
        for role_id in config.load()['commands']['mute_role_ids']:
            if role_id in [r.id for r in ctx.guild.roles]:
                roles.append(ctx.guild.get_role(role_id))
                await member.remove_roles(ctx.guild.get_role(role_id))

        embed = discord.Embed(title=f'{member} wurde entmutet!', color=config.load()['design']['colors']['primary'], description=f'{member.mention} hat die {"folgenden Rollen" if len(roles) > 1 else "folgende Rolle"} entfernt bekommen:\n> {" ".join(r.mention for r in roles)}\nund hat ab sofort wieder normalen Zugriff auf den Server.')
        embed.set_thumbnail(url=member.avatar_url)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Tools(client))