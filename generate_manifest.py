import os
import json

# --- CONFIGURACIÓN ---
# Ajusta estas rutas según tu proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "assets.json")

# Extensiones válidas
IMG_EXT = ('.png', '.jpg', '.jpeg')
SND_EXT = ('.wav', '.mp3', '.ogg')

def get_relative_path(full_path):
    """Convierte ruta absoluta en relativa (ej: assets/images/puerta.png)"""
    return os.path.relpath(full_path, BASE_DIR).replace("\\", "/")

def scan_images():
    """Busca imágenes recursivamente y genera IDs con prefijo spr_"""
    textures = {}
    print(f"--- Escaneando Imágenes en {IMAGES_DIR} ---")
    
    if not os.path.exists(IMAGES_DIR):
        print(f"Advertencia: No se encontró la carpeta {IMAGES_DIR}")
        return textures

    for root, _, files in os.walk(IMAGES_DIR):
        for filename in files:
            if filename.lower().endswith(IMG_EXT):
                # ID = spr_ + nombre del archivo (sin extensión)
                # Ej: door_open.png -> spr_door_open
                name_no_ext = os.path.splitext(filename)[0]
                asset_id = f"spr_{name_no_ext}"
                
                # Ruta relativa para el juego
                full_path = os.path.join(root, filename)
                rel_path = get_relative_path(full_path)
                
                # Detectar duplicados
                if asset_id in textures:
                    print(f"[!] DUPLICADO: {asset_id} ya existe. Se sobrescribirá.")
                
                textures[asset_id] = rel_path
                # print(f"  + {asset_id}") # Descomentar para ver lista completa
                
    print(f"Total Texturas encontradas: {len(textures)}")
    return textures

def scan_sounds():
    """Busca sonidos recursivamente y genera IDs con prefijo sfx_"""
    sounds = {}
    print(f"\n--- Escaneando Sonidos en {SOUNDS_DIR} ---")
    
    if not os.path.exists(SOUNDS_DIR):
        print(f"Advertencia: No se encontró la carpeta {SOUNDS_DIR}")
        return sounds

    for root, _, files in os.walk(SOUNDS_DIR):
        for filename in files:
            if filename.lower().endswith(SND_EXT):
                # ID = sfx_ + nombre del archivo
                # Nota: Si es música larga, quizás quieras renombrarlo manualmente a bgm_
                name_no_ext = os.path.splitext(filename)[0]
                asset_id = f"sfx_{name_no_ext}"
                
                full_path = os.path.join(root, filename)
                rel_path = get_relative_path(full_path)
                
                sounds[asset_id] = rel_path
                
    print(f"Total Sonidos encontrados: {len(sounds)}")
    return sounds

def main():
    # 1. Escanear
    textures_data = scan_images()
    sounds_data = scan_sounds()
    
    # 2. Estructura final del JSON
    manifest = {
        "textures": textures_data,
        "sounds": sounds_data
    }
    
    # 3. Guardar en disco
    # Asegurar que la carpeta 'data' exista
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4, sort_keys=True)
        
    print(f"\n[ÉXITO] Manifiesto generado en: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()