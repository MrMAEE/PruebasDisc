import discord
from discord.ext import commands
import random
import os
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
import aiohttp
from io import BytesIO

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

# Diccionario de atributos
ATRIBUTOS = {
    "Dark": "AttributeIcon_Dark.png",
    "Flame": "AttributeIcon_Flame.png",
    "Void": "AttributeIcon_Void.png",
    "Aqua": "AttributeIcon_Aqua.png",
    "Light": "AttributeIcon_Light.png",
    "Forest": "AttributeIcon_Forest.png"
}

# Diccionario de discos
DISCOS = {
    "Accel": "Accele.png",
    "Blast": "Blastv.png",
    "Charge": "Charge.png"
}

# Almacenar datos temporales de usuarios
user_data = {}

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name}')
    print(f'ID: {bot.user.id}')
    print('------')

async def descargar_avatar(url):
    """Descarga el avatar del usuario"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.read()
                return Image.open(BytesIO(data))
    return None

def generar_carta(avatar_path, nombre, atributo, discos, rareza):
    """Genera la imagen de la carta"""
    
    # Abrir plantilla
    template = Image.open('assets/templates/star1.jpg')
    
    # Abrir avatar del usuario
    avatar = Image.open(avatar_path).convert("RGBA")
    # Redimensionar avatar a 303x461
    avatar = avatar.resize((303, 461), Image.Resampling.LANCZOS)
    
    # Calcular posición para centrar el avatar
    avatar_x = 175 - 303 // 2
    avatar_y = 242 - 461 // 2
    
    # Pegar avatar (si tiene transparencia, manejarla)
    if avatar.mode == 'RGBA':
        template.paste(avatar, (avatar_x, avatar_y), avatar)
    else:
        template.paste(avatar, (avatar_x, avatar_y))
    
    # Pegar marco según atributo y rareza
    marco_filename = f"{atributo.lower()}_{rareza}.png"
    marco_path = f'assets/frames/{marco_filename}'
    
    try:
        marco = Image.open(marco_path).convert("RGBA")
        # El marco debe ser del mismo tamaño que el avatar (303x461)
        marco = marco.resize((303, 461), Image.Resampling.LANCZOS)
        # Pegar el marco en la misma posición que el avatar
        template.paste(marco, (avatar_x, avatar_y), marco)
    except FileNotFoundError:
        print(f"Advertencia: No se encontró el marco {marco_filename}")
    except Exception as e:
        print(f"Error al cargar marco: {e}")
    
    # Pegar estrellas de rareza (solo si rareza es 2 o más)
    if rareza >= 2:
        # Configuración específica para cada rareza
        stars_config = {
            2: {"x": 824, "y": 10, "w": 74, "h": 48},
            3: {"x": 822, "y": 9, "w": 104, "h": 49},
            4: {"x": 816, "y": 8, "w": 133, "h": 50},
            5: {"x": 827, "y": 10, "w": 153, "h": 47}
        }
        
        config = stars_config[rareza]
        stars_filename = f"stars_{rareza}.png"
        stars_path = f'assets/stars/{stars_filename}'
        
        try:
            stars = Image.open(stars_path).convert("RGBA")
            # Redimensionar según configuración específica
            stars = stars.resize((config["w"], config["h"]), Image.Resampling.LANCZOS)
            # Pegar en posición específica
            template.paste(stars, (config["x"], config["y"]), stars)
        except FileNotFoundError:
            print(f"Advertencia: No se encontró la imagen de estrellas {stars_filename}")
        except Exception as e:
            print(f"Error al cargar estrellas: {e}")
    
    # Abrir y pegar ícono de atributo
    atributo_icon = Image.open(f'assets/attributes/{ATRIBUTOS[atributo]}').convert("RGBA")
    atributo_icon = atributo_icon.resize((45, 45), Image.Resampling.LANCZOS)
    atributo_x = 388 - 45 // 2
    atributo_y = 46 - 45 // 2
    template.paste(atributo_icon, (atributo_x, atributo_y), atributo_icon)
    
    # Pegar discos
    posiciones_discos = [
        (413, 227),
        (518, 226),
        (623, 227),
        (727, 225),
        (833, 225)
    ]
    
    for i, disco_nombre in enumerate(discos):
        disco_icon = Image.open(f'assets/discs/{DISCOS[disco_nombre]}').convert("RGBA")
        disco_icon = disco_icon.resize((105, 107), Image.Resampling.LANCZOS)
        disco_x = posiciones_discos[i][0] - 105 // 2
        disco_y = posiciones_discos[i][1] - 107 // 2
        template.paste(disco_icon, (disco_x, disco_y), disco_icon)
    
    # Agregar nombre del usuario
    draw = ImageDraw.Draw(template)
    
    # Cargar fuente personalizada
    try:
        font = ImageFont.truetype("assets/fonts/OptimusPrincepsSemiBold.ttf", 30)
    except:
        try:
            font = ImageFont.truetype("assets/fonts/OptimusPrinceps.ttf", 30)
        except:
            font = ImageFont.load_default()
    
    # Dibujar nombre centrado en X=486, Y=44
    bbox = draw.textbbox((0, 0), nombre, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    nombre_x = 486 - text_width // 2
    nombre_y = 44 - text_height // 2
    
    # Dibujar texto con borde negro para mejor visibilidad
    # Borde
    for adj_x in range(-2, 3):
        for adj_y in range(-2, 3):
            draw.text((nombre_x + adj_x, nombre_y + adj_y), nombre, font=font, fill=(0, 0, 0))
    # Texto principal
    draw.text((nombre_x, nombre_y), nombre, font=font, fill=(255, 255, 255))
    
    # Guardar imagen
    output_path = f'carta_{nombre}.png'
    template.save(output_path)
    return output_path

@bot.command(name='tirar')
async def tirar_dado(ctx):
    """Inicia el proceso de tirada"""
    
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
        except discord.Forbidden:
            await ctx.send("❌ No tengo permisos para crear roles.")
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
    
    # Guardar rareza del usuario
    user_data[ctx.author.id] = {"rareza": resultado}
    
    # Crear embed con el resultado
    embed = discord.Embed(
        title="🎲 Tirada de Rareza",
        description=f"{ctx.author.mention}\nResultado: **1d5 ({resultado})**\nRareza: **{nombre_rol}**",
        color=color_rol
    )
    embed.set_footer(text="Ahora elige tu atributo usando !elegir_atributo")
    
    await ctx.send(embed=embed)

@bot.command(name='elegir_atributo')
async def elegir_atributo(ctx):
    """Permite al usuario elegir su atributo"""
    
    if ctx.author.id not in user_data:
        await ctx.send("❌ Primero debes usar `!tirar` para obtener una rareza.")
        return
    
    # Crear mensaje con opciones
    opciones = "\n".join([f"{i+1}. {attr}" for i, attr in enumerate(ATRIBUTOS.keys())])
    
    embed = discord.Embed(
        title="🌟 Elige tu Atributo",
        description=f"Responde con el número del atributo:\n\n{opciones}",
        color=discord.Color.blue()
    )
    
    await ctx.send(embed=embed)
    
    # Esperar respuesta
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()
    
    try:
        msg = await bot.wait_for('message', check=check, timeout=60.0)
        opcion = int(msg.content)
        
        if 1 <= opcion <= len(ATRIBUTOS):
            atributo_elegido = list(ATRIBUTOS.keys())[opcion - 1]
            user_data[ctx.author.id]['atributo'] = atributo_elegido
            
            await ctx.send(f"✅ Has elegido: **{atributo_elegido}**\n\nAhora elige tus discos usando `!elegir_discos`")
        else:
            await ctx.send("❌ Opción inválida. Intenta de nuevo con `!elegir_atributo`")
    
    except TimeoutError:
        await ctx.send("⏰ Tiempo agotado. Usa `!elegir_atributo` para intentar de nuevo.")

@bot.command(name='elegir_discos')
async def elegir_discos(ctx):
    """Permite al usuario elegir sus 5 discos"""
    
    if ctx.author.id not in user_data or 'atributo' not in user_data[ctx.author.id]:
        await ctx.send("❌ Primero debes elegir tu atributo usando `!elegir_atributo`")
        return
    
    embed = discord.Embed(
        title="💿 Elige tus 5 Discos",
        description="Escribe 5 discos separados por espacios.\n\nOpciones: **Accel**, **Blast**, **Charge**\n\nEjemplo: `Accel Blast Blast Blast Charge`",
        color=discord.Color.gold()
    )
    
    await ctx.send(embed=embed)
    
    # Esperar respuesta
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    
    try:
        msg = await bot.wait_for('message', check=check, timeout=60.0)
        discos_input = msg.content.split()
        
        # Validar que sean 5 discos
        if len(discos_input) != 5:
            await ctx.send("❌ Debes elegir exactamente 5 discos. Intenta de nuevo con `!elegir_discos`")
            return
        
        # Validar que todos sean discos válidos
        discos_validos = []
        for disco in discos_input:
            disco_capitalizado = disco.capitalize()
            if disco_capitalizado in DISCOS:
                discos_validos.append(disco_capitalizado)
            else:
                await ctx.send(f"❌ '{disco}' no es un disco válido. Opciones: Accel, Blast, Charge")
                return
        
        # Guardar discos
        user_data[ctx.author.id]['discos'] = discos_validos
        
        # Generar carta
        await ctx.send("⏳ Generando tu carta...")
        
        # Descargar avatar
        avatar_url = ctx.author.display_avatar.url
        avatar_img = await descargar_avatar(avatar_url)
        
        if avatar_img:
            # Guardar avatar temporalmente
            avatar_path = f'temp_avatar_{ctx.author.id}.png'
            avatar_img.save(avatar_path)
            
            # Generar carta
            carta_path = generar_carta(
                avatar_path,
                ctx.author.display_name,
                user_data[ctx.author.id]['atributo'],
                user_data[ctx.author.id]['discos'],
                user_data[ctx.author.id]['rareza']
            )
            
            # Enviar carta
            await ctx.send(
                f"🎉 ¡Tu carta está lista, {ctx.author.mention}!",
                file=discord.File(carta_path)
            )
            
            # Limpiar archivos temporales
            os.remove(avatar_path)
            os.remove(carta_path)
            
            # Limpiar datos del usuario
            del user_data[ctx.author.id]
        else:
            await ctx.send("❌ Error al descargar tu avatar. Intenta de nuevo.")
    
    except TimeoutError:
        await ctx.send("⏰ Tiempo agotado. Usa `!elegir_discos` para intentar de nuevo.")

# Ejecutar el bot
bot.run(os.getenv('DISCORD_TOKEN'))