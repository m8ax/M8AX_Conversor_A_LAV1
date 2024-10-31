"""
Este Programa Recorre Un Directorio Específico En Busca De Ficheros De Video
Y Los Convierte A MP4 Con El Códec LAV1, Optimizado Para Minimizar Su Tamaño
Sin Comprometer La Calidad Lo Suficiente Como Para Que Pueda Verse Y Oírse 
Decentemente En Dispositivos Móviles O Televisores.

La Conversión Usa LAV1 Para El Video Y OPUS Para El Audio, Generando Archivos 
Con Un Buen Equilibrio Entre Calidad Y Tamaño Reducido. Los Ficheros Resultantes 
Se Guardan En Una Carpeta Destino Específica, Manteniendo La Jerarquía Del 
Directorio De Origen.

Opcionalmente, El Programa También Permite Añadir Metadatos A Los Videos, 
Incluyendo Código QR Con Logo Mediante URL Y Puede Convertir El Audio Del Video 
A Un Formato 3D Para Una Experiencia De Sonido Más Inmersiva.

Programador: MarcoS OchoA DieZ ( Alias: M8AX ) 
Fecha De Programación: 25 De Octubre De 2024 - Viernes - 00:00
Duración De Programación: 2.5h
Dispositivo Utilizado: MvIiIaX - Xiaomi MI 9 Lite ( TerMuX Con PyThoN ) 
Código Formateado Con: BlacK
"""

import os
import time
import re
import random
import subprocess
import qrcode
import shutil
import requests
import hashlib
import base64
import urllib.parse
import multiprocessing
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from sympy import factorint
from mutagen.mp4 import MP4, MP4Cover
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm
from io import BytesIO
from moviepy.editor import VideoFileClip

ffmpeg_cmd_string = ""
mviiiax = multiprocessing.Value("i", 0)  # 'i' Significa Nº Entero

# Sacar Frames Totales De Un Video


def get_video_info(file_path):
    # Cargar El Archivo De Video

    video = VideoFileClip(file_path)

    # Obtener La Duración En Segundos

    duration = video.duration

    # Obtener Los Frames Por Segundo ( FPS )

    fps = video.fps

    # Calcular El Número Total De Frames

    total_frames = int(duration * fps)

    return total_frames, fps


# Convertir Segundos A Días, Horas, Minutos Y Segundos


def convertir_segundos_a_dhms(segundos):
    dias = int(segundos // (24 * 3600))  # Calcular Días
    segundos %= 24 * 3600  # Obtener Los Segundos Restantes Después De Calcular Días
    horas = int(segundos // 3600)  # Calcular Horas
    segundos %= 3600  # Obtener Los Segundos Restantes Después De Calcular Horas
    minutos = int(segundos // 60)  # Calcular Minutos
    segundos = segundos % 60  # Obtener Los Segundos Restantes
    return dias, horas, minutos, segundos


# Comprobar Dirección Web Válida


def es_direccion_web_valida(direccion):
    resultado = urlparse(direccion)
    return all([resultado.scheme, resultado.netloc])


# Pedir Dirección URL Directa A Imágen


def solicitar_direccion_web():
    direccion_default = "https://yt3.googleusercontent.com/ytc/AIdro_kbQO4N_i3ddLrouqOb1lhgx72WQITlLn6t2D1WaSR29Q=s900-c-k-c0x00ffffff-no-rj"
    while True:
        direccion = input(
            "\nM8AX - Introduce Una Dirección Web, Que Apunte A Un Fichero Gráfico, jpg, bmp, png, webp, Etc... Para Añadir La Imágen Al Código QR. ( Deja Vacío Para Usar URL Con Tu Logo ): "
        )

        if not direccion:  # Si Está Vacío, Usar La Dirección Por Defecto
            return direccion_default

        if es_direccion_web_valida(direccion):
            return direccion
        else:
            print(
                "\nM8AX - La Dirección Web No Es Válida. Por Favor, Inténtalo De Nuevo."
            )


# Descargar Imágen Dada Una URL


def download_image(url):
    response = requests.get(url)
    response.raise_for_status()  # Lanza Un Error Si La Respuesta No Es 200
    img = Image.open(BytesIO(response.content))

    # Guardar La Imagen Como PNG

    img.save("m8ax.png", "PNG")


# Calcula El Hash SHA-256 De Un Archivo


def calculate_hash(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):  # Leer El Archivo En Bloques De 8192 Bytes
            sha256.update(chunk)
    return sha256.hexdigest()


# Factoriza Número Aleatorio De 50 Cifras... Tontería Para Los Metadatos... ( Propia De Mí, Pero Me Identifica. )


def generar_y_factorizar():
    max_cifras = 50

    numero = random.randint(10 ** (max_cifras - 1), 10**max_cifras - 1)

    # Factorizar El Número

    factores = factorint(numero)

    # Construir La Cadena De Descomposición

    descomposicion = " * ".join(
        [f"{p}^{e}" if e > 1 else str(p) for p, e in factores.items()]
    )

    # Formatear La Salida

    resultado = f"M8AX - Número: 🔢 {numero} 🔢, Descompuesto En Factores Primos Es: ( ▶︎ {descomposicion} ◀︎ )."

    return resultado


# Fecha A Mi Gusto


def obtener_fecha_formateada():
    # Diccionarios Para Traducir Días Y Meses Al Español

    dias_semana = {
        0: "Lunesito",
        1: "Martesito",
        2: "Miércolesito",
        3: "Juevesito",
        4: "Viernesito",
        5: "Sábadocito",
        6: "Dominguito",
    }

    meses = {
        1: "Enerito",
        2: "Febrerito",
        3: "Marzito",
        4: "Abrilito",
        5: "Mayito",
        6: "Junito",
        7: "Julito",
        8: "Agostito",
        9: "Septiembrito",
        10: "Octubrito",
        11: "Noviembrito",
        12: "Diciembrito",
    }

    # Obtener La Fecha Y Hora Actual

    fecha_actual = datetime.now()

    # Obtener Los Componentes Traducidos De La Fecha

    dia_semana = dias_semana[
        fecha_actual.weekday()
    ]  # Obtener El Día De La Semana Como Índice (0=Lunes)
    mes = meses[fecha_actual.month]  # Obtener El Mes Usando El Número Del Mes

    # Formatear La Fecha En El Formato Requerido

    fecha_formateada = f"El {dia_semana}, {fecha_actual.day} De {mes} De {fecha_actual.year} A Las {fecha_actual.strftime('%H:%M:%S')}"

    return fecha_formateada


# Función Para Recibir Una Imágen Y Grabar Otra Con Modificaciones


def add_text_to_image(input_image_path, output_image_path, text):
    # Abrir La Imágen

    with Image.open(input_image_path) as img:
        # Obtener Las Dimensiones De La Imágen Original

        width, height = img.size

        # Crear Una Nueva Imágen Con Espacio Adicional Para El Texto

        new_height = height + 80  # Aumentar La Altura En 80 Píxeles
        new_img = Image.new("RGB", (width, new_height), color="black")

        # Pegar La Imágen Original En La Nueva Imágen

        new_img.paste(img, (0, 0))

        # Crear Un Objeto Para Dibujar

        draw = ImageDraw.Draw(new_img)

        # Usar Una Fuente Por Defecto

        font_size = 20
        font = ImageFont.load_default()

        # Dibujar El Texto Centrado

        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_position = ((width - text_width) // 2, height + (80 - text_height) // 2)

        # Dibujar El Texto

        draw.text(text_position, text, font=font, fill="white")

        # Guardar La Imágen Resultante

        new_img.save(output_image_path)


# Función Para Limpiar La Pantalla


def clear_screen():
    if os.name == "nt":  # Para Windows
        subprocess.run("cls", shell=True)
    else:  # Para Unix/Linux/Mac
        subprocess.run("clear")


# Función Para Solicitar Paneo Dinámico


def ask_for_paneo():
    alehz = 0
    while True:
        choice = (
            input(
                "\nM8AX - ¿ Deseas Un Paneo Dinámico Para Todos Los Videos ?, ale Implica Si, Pero La Duración Del Paneo Será Aleatoria En Cada Video De 33s A 8s... ( Escribe 'si', 'no' O 'ale' ): "
            )
            .strip()
            .lower()
        )

        # Si La Opción Es Válida, Se Devuelve Esa Opción

        if choice in ["si", "no", "ale"]:
            if choice == "ale":
                alehz = 1
            else:
                alehz = 0
            return choice, alehz
        else:
            print("\nM8AX - Error: Debes Escribir 'si', 'no' O 'ale' ...")


# Función Para Solicitar Si Eco En Paneo Dinámico


def ask_for_ecopane():
    while True:
        choice = (
            input("\nM8AX - ¿ Eco En Paneo Dinámico ? ( Escribe 'si' O 'no' ): ")
            .strip()
            .lower()
        )

        # Si La Opción Es Válida, Se Devuelve Esa Opción

        if choice in ["si", "no"]:
            return choice
        else:
            print("\nM8AX - Error: Debes Escribir 'si' O 'no'...")


# Función Para Solicitar Si Añadimos MetaTags


def ask_for_meta():
    while True:
        choice = (
            input(
                "\nM8AX - ¿ Añadir MetaTags A Los Videos ? si = Añade MetaTags no = Deja Como Están... ( Escribe 'si' O 'no' ): "
            )
            .strip()
            .lower()
        )

        # Si La Opción Es Válida, Se Devuelve Esa Opción

        if choice in ["si", "no"]:
            return choice
        else:
            print("\nM8AX - Error: Debes Escribir 'si' O 'no'...")


# Función Para Preguntar El Número De Núcleos A Usar En La Compresión De Video


def ask_for_cores():
    num_cores = multiprocessing.cpu_count()
    while True:
        entrada = input(
            "\nM8AX- Introduce El Número De Núcleos A Usar En La Compresión A MP4... Cuantos Más Núcleos Tenga Tu CPU, Más Rápido Terminará El Proceso, A Cada Núcleo Se Le Asignará A Comprimir Una Video. ¿ Cuántos Núcleos Usamos ?: "
        )

        try:
            xnum_coress = int(entrada)
            if xnum_coress >= 1 and xnum_coress <= num_cores:
                return xnum_coress
            else:
                print(
                    f"\nM8AX - Debes Introducir Un Número Mayor O Igual A 1 Y Menor O Igual A {num_cores}..."
                )
        except ValueError:
            print(
                "\nM8AX - Entrada No Válida. Asegúrate De Introducir Un Número Válido..."
            )


# Aumentar Variable mviiiax En 1


def modificar_variable():
    # Modificar La Variable Compartida

    with mviiiax.get_lock():  # Aseguramos Que Solo Un Proceso Acceda A La Variable A La Vez
        mviiiax.value += 1


# Función Para Convertir Archivos A MP4 Usando FFmpeg


def convert_to_MP4(file_path):
    relative_path = os.path.relpath(file_path, input_dir)
    output_file_path = os.path.join(
        output_dir, relative_path.rsplit(".", 1)[0] + ".Mp4"
    )
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    # Calcular HASH SHA-256 Del Fichero De Video Original M8AXHash256VideoOriginalM8AX

    hash_value = calculate_hash(file_path)

    # Comando Para Convertir A MP4 Con Metadatos

    ffmpeg_cmd = [
        "ffmpeg",
        "-i",
        file_path,  # Archivo De Video De Entrada
        "-ar",
        "24000",
        "-vf",
        "scale='if(gt(a,448/252),448,-2)':'if(gt(a,448/252),-2,252)',scale=trunc(iw/4)*4:trunc(ih/4)*4, drawtext=text='M8AX':fontfile='arial.ttf':fontcolor=white:fontsize=h/20:x=W-tw-5:y=H-th-5,unsharp=5:5:0.5",  # Escalado, Texto Y Nitidez
        "-map",
        "0:v?",
        "-map",
        "0:a?",
    ]

    # Paneo Dinámico

    if alehz == 1:
        hz_value = random.uniform(0.03, 0.15)
    else:
        hz_value = 0.1

    if haypaneo == "si" or haypaneo == "ale":
        if paneco == "si":
            ffmpeg_cmd += [
                "-af",
                f"apulsator=mode=sine:hz={hz_value:.2f}:amount=0.90, aecho=0.8:0.4:150:0.4,volume=3.52dB",
            ]  # Paneo Dinámico Con Eco
        else:
            ffmpeg_cmd += [
                "-af",
                f"apulsator=mode=sine:hz={hz_value:.2f}:amount=0.90,volume=3.52dB",
            ]  # Paneo Dinámico Sin Eco

    ffmpeg_cmd += [
        "-c:v",
        "libsvtav1",  # Codec De Video
        "-b:v",
        "100k",  # Tasa De Bits De Video
        "-preset",
        "7",  # Velocidad De Codificación
        "-c:a",
        "libopus",  # Codec De Audio
        "-b:a",
        "32k",  # Tasa Objetivo De Bits Para El Audio ( VBR )
    ]
    if haypaneo == "no":
        ffmpeg_cmd += [
            "-filter:a",
            "volume=3.52dB",  # Aumentar Un Poco El Volumen
        ]

    ffmpeg_cmd += [
        "-vbr",
        "constrained",  # Habilitar VBR
        "-ac",
        "2",  # Estéreo
        "-compression_level",
        "10",  # Nivel De Compresión
    ]

    # Agregar MetaTags

    if metetag == "si":
        ffmpeg_cmd += [
            "-metadata",
            f"episode_id=ORIGEN - {os.path.basename(file_path)} | DESTINO - {os.path.basename(output_file_path)} | Hash SHA-256 Original {hash_value}.",  # ID Del Episodio
            "-metadata",
            r"copyright=-///📷\\\ --- MvIiIaX & M8AX 2025 - 2050 --- ///📷\\\-",  # Copyright
            "-metadata",
            r"artist=-///🎹\\\ --- ░M░A░R░C░O░S░ --- ///🎹\\\-",  # Artist
            "-metadata",
            r"album=-///🎸\\\ --- ＊*•̩̩͙✩•̩̩͙*˚ᛖ𝐯ᎥᎥᎥⱥx*•̩̩͙✩•̩̩͙*˚＊ --- ///🎸\\\-",  # Album
            "-metadata",
            r"genre=-///₿\\\ --- | ★ https://oncyber.io/@m8ax ★ | --- ///₿\\\-",  # Género
            "-metadata",
            r"MarcosOchoaDiez=🧑‍💻 🢂 @-📱-@ Programar No Es Solo Resolver Problemas, Es Transformar Ideas En Soluciones Que Cambian El Mundo... @-📱-@ 🢀 💻🧑‍",  # MarcosOchoaDiez
            "-metadata",
            r"MvIiIaX=----- | ★ https://opensea.io/es/m8ax ★ | -----",  # NFTS
            "-metadata",
            r"BitcoinWallet=-/// ⚡LeD⚡ \\\ - ********** - /// ⚡GeR⚡ \\\-",  # Wallet Bitcoin
            "-metadata",
            r"author=--- MarcoS OchoA DieZ -► ( ★ ********** ★, ★ +34********* ★ ) ---",  # Autor
            "-metadata",
            r"show=Mi Canal De YouTube - ((( ★ http://youtube.com/m8ax ★ )))",  # Show
            "-metadata",
            r"grouping=Mi Blog - ((( ★ http://mviiiaxm8ax.blogspot.com ★ )))",  # Agrupación Blog
            "-metadata",
            r"comment=1 - Por Muchas Vueltas Que Demos, Siempre Tendremos El Culo Atrás... 2 - El Futuro... No Está Establecido, No Hay Destino, Sólo Existe El Que Nosotros Hacemos... 3 - El Miedo Es El Camino Hacia El Lado Oscuro, El Miedo Lleva A La Ira, La Ira Lleva Al Odio, El Odio Lleva Al Sufrimiento... 4 - Video Compilado En Honor A MDDD...",  # Comentario
            "-metadata",
            r"M8AX=Yo He Visto Cosas Que Vosotros No Creeríais. Atacar Naves En Llamas Más Alla De Orión. He Visto Rayos-C Brillar En La Oscuridad Cerca De La Puerta De Tannhäuser. Todos Esos Momentos Se Perderán En El Tiempo, Como Lágrimas En La Lluvia. Es Hora De Morir...",  # Frase M8AX
            "-metadata",
            f"title={os.path.basename(output_file_path)}",  # Título
            "-metadata",
            f"ImoD=----- The Algorithm Man -► ( AND NOT OR ) ( E=MC^2 ) ( Ax=b ) -----",  # M8AX Programmer
            "-metadata",
            f"MvIiIaX_M8AX=Mi CPU Procesa En Red Neural, Es De Aprendizaje... Pero Skynet Solo Lee, Cuando Nos Envían Solos A Una Misión...",  # Frasecilla
            "-metadata",
            f"M8AX_MvIiIaX=No Soy Una Máquina, Ni Un Hombre. Soy Más...",  # Frasecilla
            "-metadata",
            r"handler_name=--- -🇪🇸- MarcoS OchoA DieZ -► ( M8AX ◀️👨‍💻▶️ MvIiIaX ) -🇪🇸- ---",  # Nombre Del Compresor
            "-metadata",
            f"EHD_MDDD=.•♫•♬•🔥Ｍ𝚟ıııคx🔥•♬•♫•. X∀8ꟽ ⌘•⌘ ꧁☆❤️🅼8🅰🆇❤️☆꧂ ⌘•⌘",  # M8AX Programmer EHDMDDD
            "-metadata",
            f"fingerprint=1003197777913001",  # M8AX FingerPrint
            "-metadata",
            f"GualoMajanDuchi=M2O-MAR-POR",  # RISAS
            "-metadata",
            r"ImoDTroN=Nunca Dejes Que Nadie Te Diga Que No Puedes Hacer Algo. Ni Siquiera Yo. Si Tienes Un Sueño, Tienes Que Protegerlo. Las Personas Que No Son Capaces De Hacer Algo Por Ellas Mismas, Te Dirán Que Tú Tampoco Puedes Hacerlo. ¿ Quieres Algo ? Ve Por Ello Y Punto...",  # Frasecilla
        ]

    # Agregar El Archivo De Salida Al Final Del Comando

    ffmpeg_cmd.append(output_file_path)  # Último Comando

    if mviiiax.value == 0:
        # Abro El Archivo En Modo Escritura

        with open("M8AX-Lista-FFmpeg.TxT", "w", encoding="utf-8") as f:
            f.write(" ".join(ffmpeg_cmd))

    modificar_variable()

    # Ejecutar El Comando FFmpeg Y Mostrar La Salida En Tiempo Real

    result = subprocess.run(
        ffmpeg_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="latin-1",
    )

    # Mostrar La Salida De FFmpeg

    return result.stdout


# Función Para Obtener La Duración De Un Archivo De Video


def get_Video_duration(file_path):
    audio = MP4(file_path)
    return audio.info.length  # Devuelve La Duración En Segundos


# Función Para Obtener El Tamaño De Un Archivo En MB


def get_file_size_mb(file_path):
    return os.path.getsize(file_path) / (1024 * 1024)


# Función Para Solicitar Un Directorio Existente


def get_existing_directory(prompt):
    while True:
        directory = input(prompt).strip()
        if os.path.exists(directory):
            return directory
        else:
            print(
                f"\nM8AX - El Directorio '{directory}' No Existe. Por Favor, Verifica La Ruta...\n"
            )


# Comenzando

clear_screen()

haypaneo = "no"
total_duration = 0
paneco = "no"
hz_value = 0.1
alehz = 0
markitosfac = "No Se Ha Factorizado Nada, Ha Habido Errores Para Bajar Una Imágen De Internet Y Adornar El Código QR... Todo Lo Demás, Correcto."

print(f"--------  M8AX - PROGRAMA PARA CONVERTIR VIDEO A FORMATO MP4 - M8AX --------")
print(f"")
input_dir = get_existing_directory(
    "M8AX - Introduce El Directorio De Origen ( Donde Están Los Archivos A Convertir ): "
)

# Solicitar Directorio De Destino Y Crearlo Si No Existe

output_dir = input(
    "\nM8AX - Introduce El Directorio De Destino ( Donde Se Guardarán Los Archivos Convertidos ): "
).strip()
os.makedirs(output_dir, exist_ok=True)

# Solicitar Paneo Dinámico

haypaneo, alehz = ask_for_paneo()
if haypaneo == "si" or haypaneo == "ale":
    paneco = ask_for_ecopane()

# Solicitar Si Añadimos MetaTags

metetag = ask_for_meta()

if metetag == "si":
    # Solicitar Dirección Web Directa A Una Imágen

    direimagenqr = solicitar_direccion_web()

# Preguntar Número De Núcleos A Usar

xnum_cores = ask_for_cores()

# Lista De Extensiones De Video A Convertir

Video_extensions = (
    ".mp4",
    ".avi",
    ".mkv",
    ".mov",
    ".wmv",
    ".flv",
    ".mpeg",
    ".mpg",
    ".webm",
    ".3gp",
    ".h264",
    ".vob",
    ".ts",
    ".m4v",
    ".rmvb",
)

# Limpiar La Pantalla Al Comienzo Del Programa

clear_screen()

# Crear Una Lista De Archivos Para Convertir

files_to_convert = []
initial_total_size = 0
for root, _, files in os.walk(input_dir):
    for file in files:
        if file.lower().endswith(Video_extensions):
            file_path = os.path.join(root, file)
            files_to_convert.append(file_path)
            initial_total_size += get_file_size_mb(file_path)

# Detectar El Número De Núcleos De La CPU

num_cores = multiprocessing.cpu_count()
print(
    f"------------ Usando {xnum_cores} De {num_cores} Núcleos Para La Conversión Al Codec LAV1 ------------\n"
)

# Medir El Tiempo Total Para La Conversión

start_time = time.time()

antes = obtener_fecha_formateada()

# Crear La Barra De Progreso Total

fill_color = ["blue", "cyan", "green", "magenta", "red", "yellow", "white"]

fill_color = random.choice(fill_color)

with tqdm(
    total=len(files_to_convert),
    desc="M8AX - Paso 1/2 - ",
    ncols=80,
    colour=fill_color,
) as pbar_total:

    # Usar Un Executor Para Convertir En Paralelo, Con El Número De Núcleos Que Hemos Elegido

    with ThreadPoolExecutor(max_workers=xnum_cores) as executor:

        # Convertir Los Archivos Y Actualizar El Progreso

        for _ in executor.map(convert_to_MP4, files_to_convert):
            pbar_total.update(1)


# Calcular El Tamaño Total Después De La Conversión Y Alguna Cosilla Más

final_total_size = 0
pelidura = 0
peliocupa = 0
m8axframes = 0
m8axtframes = 0
ffppss = 0
cadenaqr = ""

# Recorre El Directorio Para Contar Archivos

total_files = sum(len(files) for _, _, files in os.walk(output_dir))

print("\n")

fill_color = ["blue", "cyan", "green", "magenta", "red", "yellow", "white"]

fill_color = random.choice(fill_color)

# Barra De Progreso Para Procesos Finales Del Cálculo Y Añadir QRCODE A MetaTags Si Así Lo Queremos...

with tqdm(
    total=total_files,
    desc="M8AX - Paso 2/2 - ",
    colour=fill_color,
) as pbar:
    for root, _, files in os.walk(output_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(".Mp4"):
                # Sumar Duración De Los Ficheros De Video Y Peso

                pelidura = get_Video_duration(file_path)
                peliocupa = get_file_size_mb(file_path)
                m8axframes, ffppss = get_video_info(file_path)
                m8axtframes += m8axframes
                total_duration += pelidura
                final_total_size += peliocupa
                xdias, xhoras, xminutos, xsegundos = convertir_segundos_a_dhms(pelidura)
                cadenaqr = f"Duración Del Video: {xdias} Días, {xhoras} Horas, {xminutos} Minutos Y {xsegundos:.4f} Segundos.\nOcupa: {peliocupa:.4f} MB.\nFPS: {ffppss:.4f}.\nNúmero De Frames: {m8axframes}."

                # Crear Un Objeto QRCode

                if metetag == "si":
                    if not os.path.isfile("m8ax.png"):
                        try:
                            continua = 1
                            download_image(direimagenqr)
                        except Exception:
                            continua = 0
                            pass  # Ignora El Error Y Continúa Sin Hacer Nada
                    else:
                        continua = 1
                    if continua == 1:
                        markitosfac = generar_y_factorizar()
                        year = datetime.now().year
                        nombrefi = os.path.basename(file_path)
                        titulo_codificado = urllib.parse.quote(nombrefi)
                        link_busqueda = (
                            f"https://www.google.com/search?q={titulo_codificado}"
                        )

                        colors = [
                            "cyan",
                            "red",
                            "white",
                            "#3B5998",
                            "brown",
                            "orange",
                            "magenta",
                            "#FF5733",
                            "#ECC420",
                            "#9DB8EC",
                            "#F38F6D",
                            "#999594",
                            "#90D6C4",
                            "#D69097",
                            "#06FB25",
                        ]

                        fill_colo = random.choice(colors)
                        qr = qrcode.QRCode(
                            version=2,
                            error_correction=qrcode.constants.ERROR_CORRECT_L,
                            box_size=8,
                            border=2,
                        )

                        qr.add_data(
                            f"Título: {nombrefi}\n{cadenaqr}\nLink: {link_busqueda}\n\nWeb 1: https://youtube.com/m8ax\nWeb 2: https://opensea.io/es/m8ax\nMail: **********\nTlf: +34*********\n\nPor Muchas Vueltas Que Demos, Siempre Tendremos El Culo Atrás...\n\n{markitosfac}\n"
                            + "\n.•♫•♬•🔥Ｍ𝚟ıııคx🔥•♬•♫•.\nX∀8ꟽ\n⌘•⌘ ꧁☆❤️🅼8🅰🆇❤️☆꧂ ⌘•⌘"
                        )

                        qr.make(fit=True)
                        img = qr.make_image(fill_color=fill_colo, back_color="black")
                        img.save("mddd-cover.jpg")

                        # Abre Las Imágenes De Fondo Y Superposición

                        background = Image.open("mddd-cover.jpg")
                        overlay = Image.open("m8ax.png")

                        # Asegúrate De Que Las Imágenes Tengan El mismo Tamaño, Si No, Redimensiona La De Superposición

                        overlay = overlay.resize(background.size)

                        # Aplica La Opacidad A La Imagen De Superposición ( 0 Es Completamente Transparente, 255 Es Opaco )

                        opacity = 65  # 65% De Opacidad
                        overlay = overlay.convert("RGBA")
                        alpha = overlay.split()[3]  # Extrae El Canal Alfa
                        alpha = alpha.point(
                            lambda p: p * (opacity / 255)
                        )  # Ajusta El Canal Alfa Según La Opacidad
                        overlay.putalpha(
                            alpha
                        )  # Aplica El Nuevo Canal Alfa A La Imágen De Superposición

                        # Superpone La Imágen Con Opacidad Sobre La De Fondo

                        combined = Image.alpha_composite(
                            background.convert("RGBA"), overlay
                        )

                        # Guarda El Resultado

                        combined.save("mviiiax-cover.png")
                        input_image = "mviiiax-cover.png"
                        output_image = "g8alax-cover.png"

                        text_to_add = f"{nombrefi}\nMvIiIaX - The Algorithm Man - MvIiIaX\nEl Futuro... No Esta Establecido, No Hay Destino, Solo Existe El Que Nosotros Hacemos...\nhttp://youtube.com/m8ax\n--- En Honor De M8AX-MDDD ---"

                        add_text_to_image(input_image, output_image, text_to_add)
                        main_image = Image.open("g8alax-cover.png")
                        small_image = Image.open("m8ax.png")
                        small_image = small_image.resize((75, 75))
                        width, height = main_image.size
                        main_image.paste(small_image, (0, height - 75))  # (X, Y)
                        main_image.paste(
                            small_image, (width - 75, height - 75)
                        )  # (X, Y)

                        main_image.save(
                            "m8ax-cover.webp", format="WEBP", optimize=True, quality=75
                        )

                        audio_file = file_path
                        cover_file = "m8ax-cover.webp"
                        audio = MP4(audio_file)

                        # Leer La Imágen De Portada

                        current_time = obtener_fecha_formateada() + " ⌚ "
                        current_time += datetime.now(timezone.utc).strftime(
                            "%Y-%m-%dT%H:%M:%S.%fZ"
                        )

                        with open(cover_file, "rb") as f:
                            cover_data = f.read()
                        audio["covr"] = [
                            MP4Cover(cover_data, imageformat=MP4Cover.FORMAT_PNG)
                        ]
                        comment = (
                            "🎶 ----- {nombrefi} ----- 🎶 ----- M8AX . Portada Con Código QR Incorporada . M8AX ----- 💻 ----- "
                            "{markitosfac} ----- 💻 1 - Por Muchas Vueltas Que Demos, Siempre Tendremos El Culo Atrás... "
                            "2 - El Futuro... No Está Establecido, No Hay Destino, Sólo Existe El Que Nosotros Hacemos... "
                            "3 - El Miedo Es El Camino Hacia El Lado Oscuro, El Miedo Lleva A La Ira, La Ira Lleva Al Odio, "
                            "El Odio Lleva Al Sufrimiento... 4 - Yo He Visto Cosas Que Vosotros No Creeríais. Atacar Naves En "
                            "Llamas Más Alla De Orión. He Visto Rayos-C Brillar En La Oscuridad Cerca De La Puerta De Tannhäuser. "
                            "Todos Esos Momentos Se Perderán En El Tiempo, Como Lágrimas En La Lluvia. Es Hora De Morir... "
                            "5 - No Soy Una Máquina, Ni Un Hombre. Soy Más... 6 - Mi CPU Procesa En Red Neural, Es De Aprendizaje... "
                            "Pero Skynet Solo Lee, Cuando Nos Envían Solos A Una Misión... 7 - Nunca Dejes Que Nadie Te Diga Que "
                            "No Puedes Hacer Algo. Ni Siquiera Yo. Si Tienes Un Sueño, Tienes Que Protegerlo. Las Personas Que No "
                            "Son Capaces De Hacer Algo Por Ellas Mismas, Te Dirán Que Tú Tampoco Puedes Hacerlo. ¿ Quieres Algo ? Ve "
                            "Por Ello Y Punto... 8 - Video Compilado En Honor A MDDD... 🧑‍💻 🢂 @-📱-@ Programar No Es Solo Resolver "
                            "Problemas, Es Transformar Ideas En Soluciones Que Cambian El Mundo... @-📱-@ 🢀 💻🧑 Mi Blog - "
                            "((( ★ http://mviiiaxm8ax.blogspot.com ★ )))‍ ----- | Mi OpenSea - ★ https://opensea.io/es/m8ax ★ ----- | Mi Canal De YouTube - ((( ★ http://youtube.com/m8ax ★ ))) ----- | Mi OnCyber - ★ https://oncyber.io/@m8ax ★ ----- | "
                            "-⌘•⌘ ⚡LeD⚡ ⌘•⌘ - ********** - ⌘•⌘ ⚡GeR⚡ ⌘•⌘- --- MarcoS OchoA DieZ "
                            "-► ( ★ ********** ★, ★ +34********* ★ ) --- ----- The Algorithm Man -► ( AND NOT OR ) "
                            "( E=MC^2 ) ( Ax=b ) ----- --- -🇪🇸- MarcoS OchoA DieZ -► ( M8AX ◀️👨‍💻▶️ MvIiIaX ) -🇪🇸- --- "
                            ".•♫•♬•🔥Ｍ𝚟ıııคx🔥•♬•♫•. X∀8ꟽ ⌘•⌘ ꧁☆❤️🅼8🅰🆇❤️☆꧂ ⌘•⌘ 1003197777913001 "
                            "GualoMajanDuchi - M2O-MAR-POR - "
                            "Fecha De Compresión De Video - {current_time}."
                        )
                        audio["\xa9cmt"] = comment.format(
                            nombrefi=nombrefi,
                            markitosfac=markitosfac,
                            current_time=current_time,
                        )
                        audio["\xa9des"] = (
                            "**********\n"
                            "**********\n"
                            "**********\n"
                            "**********\n"
                            "ESPAÑA"
                        )
                        audio["trkn"] = [(1, 103)]  # Track Number And Total Tracks
                        audio["\xa9day"] = str(year)  # Year
                        audio["disk"] = [(1, 103)]  # Disk Number And Total Disks
                        audio["\xa9wrt"] = "🤖🔹 𝙈𝙖𝙧𝙘𝙤𝙎 𝙊𝙘𝙝𝙤𝘼 𝘿𝙞𝙚𝙕 🔹🤖"  # Composer

                        # Guardar Los Cambios

                        audio.save()

                        # Borrar Temporales, El QR Ya Está Metido En El Fichero MP4

                        os.remove("m8ax-cover.webp")
                        os.remove("mviiiax-cover.png")
                        os.remove("g8alax-cover.png")
                        os.remove("mddd-cover.jpg")

            # Actualiza La Barra De Progreso

            pbar.update(1)

# Calcular El Tiempo Total De Conversión

end_time = time.time()
elapsed_time = end_time - start_time

# Borrar Imágen Descargada De URL

if os.path.isfile("m8ax.png"):
    os.remove("m8ax.png")

despues = obtener_fecha_formateada()

# Convertir El Tiempo Total De Conversión A Días, Horas, Minutos Y Segundos

conversion_seconds = int(elapsed_time)
conv_days = conversion_seconds // (24 * 3600)
conv_hours = (conversion_seconds % (24 * 3600)) // 3600
conv_minutes = (conversion_seconds % 3600) // 60
conv_seconds = conversion_seconds % 60

# Convertir La Duración Total De Archivos A Días, Horas, Minutos Y Segundos

total_seconds = int(total_duration)
days = total_seconds // (24 * 3600)
hours = (total_seconds % (24 * 3600)) // 3600
minutes = (total_seconds % 3600) // 60
seconds = total_seconds % 60

# Calcular La Duración Media Por Archivo

average_duration = total_duration / len(files_to_convert) if files_to_convert else 0
avg_seconds = int(average_duration)
avg_days = avg_seconds // (24 * 3600)
avg_hours = (avg_seconds % (24 * 3600)) // 3600
avg_minutes = (avg_seconds % 3600) // 60
avg_seconds = avg_seconds % 60

# Calcular El Porcentaje De Compresión

compression_percentage = (
    (1 - (final_total_size / initial_total_size)) * 100 if initial_total_size > 0 else 0
)

# Calcular Archivos Convertidos Por Segundo

files_per_second = len(files_to_convert) / elapsed_time if elapsed_time > 0 else 0

# Mostrar Resultados Finales

clear_screen()

print(
    f"-----  M8AX - PROGRAMA FINALIZADO CON ÉXITO ( -- TODO CORRECTO -- ) - M8AX -----"
)
print(f"\nM8AX - Directorio De Entrada: {input_dir}")
print(f"\nM8AX - Directorio De Salida: {output_dir}")

print(
    f"\nM8AX - Se Han Convertido {mviiiax.value} Videos Y Ocupan {final_total_size:.5f} MB."
)
if haypaneo == "si":
    print("\nM8AX - Paneo Dinámico Aplicado A 0.1 Hz...")
    if paneco == "si":
        print("\nM8AX - Paneo Dinámico Aplicado Con Eco...")
    if paneco == "no":
        print("\nM8AX - Paneo Dinámico Aplicado Sin Eco...")
if haypaneo == "ale":
    print("\nM8AX - Paneo Dinámico Aplicado Aleatoriamente A Cada Canción...")
    if paneco == "si":
        print("\nM8AX - Paneo Dinámico Aplicado Con Eco...")
    if paneco == "no":
        print("\nM8AX - Paneo Dinámico Aplicado Sin Eco...")
if metetag == "si":
    print("\nM8AX - MetaTags Añadidos Correctamente...")
else:
    print("\nM8AX - MetaTags Originales Mantenidos Correctamente...")
if metetag == "si":
    print(
        f"\nM8AX - Código QRCODE Añadido Correctamente, Como Portada De Cada Fichero De Video... Adornado Con La Imágen De Este Link - {direimagenqr}."
    )
print(
    f"\nM8AX - Tiempo Total De Conversión A MP4: {elapsed_time:.5f} Segundos. | {conv_days} Días, {conv_hours} Horas, {conv_minutes} Minutos Y {conv_seconds} Segundos."
)
print(
    f"\nM8AX - Duración Total De Todos Los Archivos De Video: {days} Días, {hours} Horas, {minutes} Minutos Y {seconds} Segundos."
)
print(
    f"\nM8AX - Duración Media De Cada Archivo De Video: {avg_days} Días, {avg_hours} Horas, {avg_minutes} Minutos Y {avg_seconds} Segundos."
)
print(
    f"\nM8AX - Frames Totales Codificados A LAV1: {m8axtframes}, Lo Que Hace Que En {elapsed_time:.5f} Segundos, Que Ha Tardado La Codificación, Tu CPU Ha Codificado A LAV1, A La Friolera De... {m8axtframes/elapsed_time:.5f} FPS."
)
print(
    f"\nM8AX - La Media De Frames Por Video Es De {m8axtframes/mviiiax.value:.5f} Frames."
)
print(
    f"\nM8AX - He Usado {xnum_cores} De Los {num_cores} Núcleos De La CPU, Que Podría Usar..."
)
print(f"\nM8AX - Archivos Convertidos Por Segundo: {files_per_second:.5f} Arch/s.")
print(f"\nM8AX - Archivos Convertidos Por Minuto: {(files_per_second)*60:.5f} Arch/m.")
print(f"\nM8AX - Archivos Convertidos Por Hora: {(files_per_second)*3600:.5f} Arch/h.")
print(f"\nM8AX - Archivos Convertidos Por Día: {(files_per_second)*86400:.5f} Arch/d.")
print(
    f"\nM8AX - Archivos Convertidos Por Semana: {(files_per_second)*604800:.5f} Arch/sem."
)
print(
    f"\nM8AX - Archivos Convertidos Por Mes: {(files_per_second)*2592000:.5f} Arch/mes."
)
print(
    f"\nM8AX - Archivos Convertidos Por Año: {(files_per_second)*31536000:.5f} Arch/año."
)
print(f"\nM8AX - Tamaño Total Antes De La Conversión: {initial_total_size:.5f} MB.")
print(f"\nM8AX - Tamaño Total Después De La Conversión: {final_total_size:.5f} MB.")
print(f"\nM8AX - Porcentaje De Compresión Conseguido: {compression_percentage:.5f} %.")
print(
    f"\nM8AX - Segundos De Video Por Segundo Procesados: {total_duration/elapsed_time:.5f} TimeVid(s)/s..."
)
print(
    f"\nM8AX - Minutos De Video Por Segundo Procesados: {(total_duration/elapsed_time)/60:.5f} TimeVid(m)/s..."
)
print(
    f"\nM8AX - Horas De Video Por Segundo Procesadas: {(total_duration/elapsed_time)/3600:.5f} TimeVid(h)/s..."
)
print(
    f"\nM8AX - Horas De Video Por Hora Procesadas: {((total_duration/elapsed_time)*3600)/3600:.5f} TimeVid(h)/h..."
)
print(
    f"\nM8AX - En Un Año 24/7, Tu Dispositivo Sería Capaz De Comprimir A MP4: {((31536000*len(files_to_convert))/elapsed_time):.5f} Ficheros De Video, Que A Una Media De {(average_duration):.5f} Segundos Por Fichero, Nos Darían {((((31536000*len(files_to_convert))/elapsed_time)*average_duration)/86400):.5f} Días De Reproducción Continua O Lo Que Es Lo Mismo {(((((31536000*len(files_to_convert))/elapsed_time)*average_duration)/86400)/365):.5f} Años... Una Locura...\n"
)
print(
    f"---------- M8AX - CADENA DE FFMPEG UTILIZADA PARA LA CONVERSIÓN - M8AX ----------\n"
)

with open("M8AX-Lista-FFmpeg.TxT", "r", encoding="utf-8") as f:
    ffmpeg_cmd_string = f.read()  # Leo El Archivo

if os.path.exists("M8AX-Lista-FFmpeg.TxT"):
    os.remove("M8AX-Lista-FFmpeg.TxT")  # Borra El Archivo

print(ffmpeg_cmd_string)
if metetag == "si":
    print(f"\nM8AX - Último Número Factorizado Metido En MetaData: {markitosfac}")
print(f"\nM8AX - El Trabajo Comenzó {antes} Y Terminó {despues}.")
print(
    f"\nM8AX - Número De Ficheros Procesados: {mviiiax.value}, El Cual Coincide Con Los Convertidos... ((( TODO OK )))."
)
print(f"\nBy MarcoS OchoA DieZ - http://youtube.com/m8ax\n")

# Ruta Del Directorio Que Contiene Los Archivos De Video

directorio_video = output_dir

# Lista Todos Los Archivos En El Directorio

for archivo in os.listdir(directorio_video):
    # Verifica Si El Archivo Tiene Una Extensión De Video

    if archivo.lower().endswith(
        (
            ".mp4",
            ".avi",
            ".mkv",
            ".mov",
            ".wmv",
            ".flv",
            ".mpeg",
            ".mpg",
            ".webm",
            ".3gp",
            ".h264",
            ".vob",
            ".ts",
            ".m4v",
            ".rmvb",
        )
    ):  # Agrega Más Extensiones Si Es Necesario
        ruta_archivo = os.path.join(directorio_video, archivo)
        print(
            f"🎹 M8AX 🎹 - Ctrl+Z Para Abortar. Reproduciendo: ((( ▶︎ {ruta_archivo} ◀︎ ))) - 🎹 M8AX 🎹"
        )
        subprocess.run(
            ["ffplay", "-nodisp", "-autoexit", ruta_archivo],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )