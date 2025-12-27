import discord
from discord.ext import commands
import random
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)


# Diccionario de rarezas
RAREZAS = {
    1: {"nombre": "★", "color": discord.Color.light_grey()},
    2: {"nombre": "★★", "color": discord.Color.green()},
    3: {"nombre": "★★★", "color": discord.Color.blue()},
    4: {"nombre": "★★★★", "color": discord.Color.purple()},
    5: {"nombre": "★★★★★", "color": discord.Color.gold()}
}

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name}')
    print(f'ID: {bot.user.id}')
    print('------')

@bot.command(name='tirar')
async def tirar_dado(ctx):
    """Tira un dado de 5 caras y asigna un rol de rareza"""
    
    # Tirar el dado
    resultado = random.randint(1, 5)
    
    # Obtener información de la rareza
    rareza = RAREZAS[resultado]
    nombre_rol = rareza["nombre"]
    color_rol = rareza["color"]
    
    # Buscar si el rol ya existe
    rol_existente = discord.utils.get(ctx.guild.roles, name=nombre_rol)
    
    # Si no existe, crearlo
    if not rol_existente:
        try:
            rol_existente = await ctx.guild.create_role(
                name=nombre_rol,
                color=color_rol,
                reason="Rol de rareza generado automáticamente"
            )
            print(f"Rol '{nombre_rol}' creado exitosamente")
        except discord.Forbidden:
            await ctx.send("❌ No tengo permisos para crear roles.")
            return
        except Exception as e:
            await ctx.send(f"❌ Error al crear el rol: {e}")
            return
    
    # Remover roles de rareza anteriores del usuario
    roles_a_remover = [rol for rol in ctx.author.roles if rol.name in [r["nombre"] for r in RAREZAS.values()]]
    if roles_a_remover:
        try:
            await ctx.author.remove_roles(*roles_a_remover)
        except discord.Forbidden:
            await ctx.send("❌ No tengo permisos para remover roles.")
            return
    
    # Asignar el nuevo rol
    try:
        await ctx.author.add_roles(rol_existente)
    except discord.Forbidden:
        await ctx.send("❌ No tengo permisos para asignar roles.")
        return
    except Exception as e:
        await ctx.send(f"❌ Error al asignar el rol: {e}")
        return
    
    # Crear embed con el resultado
    embed = discord.Embed(
        title="🎲 Tirada de Rareza",
        description=f"{ctx.author.mention}",
        color=color_rol
    )
    embed.add_field(name="Resultado", value=f"1d5 ({resultado})", inline=False)
    embed.add_field(name="Total", value=f"{resultado}", inline=False)
    embed.add_field(name="✨ Rareza obtenida", value=f"**{nombre_rol}**", inline=False)
    embed.set_footer(text=f"¡Felicidades ahora eres de rareza {nombre_rol}!")
    
    await ctx.send(embed=embed)

@bot.command(name='reset')
async def reset_rareza(ctx):
    """Remueve todos los roles de rareza del usuario"""
    
    roles_a_remover = [rol for rol in ctx.author.roles if rol.name in [r["nombre"] for r in RAREZAS.values()]]
    
    if not roles_a_remover:
        await ctx.send("❌ No tienes ningún rol de rareza.")
        return
    
    try:
        await ctx.author.remove_roles(*roles_a_remover)
        await ctx.send(f"✅ {ctx.author.mention} Se han removido tus roles de rareza.")
    except discord.Forbidden:
        await ctx.send("❌ No tengo permisos para remover roles.")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

@bot.command(name='rareza')
async def ver_rareza(ctx):
    """Muestra la rareza actual del usuario"""
    
    roles_rareza = [rol for rol in ctx.author.roles if rol.name in [r["nombre"] for r in RAREZAS.values()]]
    
    if not roles_rareza:
        await ctx.send(f"{ctx.author.mention} No tienes ninguna rareza asignada. Usa `!tirar` para obtener una.")
    else:
        rol = roles_rareza[0]
        await ctx.send(f"{ctx.author.mention} Tu rareza actual es: **{rol.name}**")

# Ejecutar el bot
bot.run(os.getenv('DISCORD_TOKEN'))