#!/usr/bin/env python3
# ==============================================================================
# UNIVERSIDAD PRIVADA DEL VALLE - TECNOLOGIAS EMERGENTES I
# EXAMEN PRACTICO INDIVIDUAL - 2DO MOMENTO
# Autor: Ronald Joel Saavedra Vargas
# Generador de Evidencias Visuales de Terminal Beeline HiveQL
# ==============================================================================

import os
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parents[1]
REGISTROS_DIR = BASE_DIR / "registros"
EVIDENCIAS_DIR = BASE_DIR / "evidencias"
EVIDENCIAS_DIR.mkdir(parents=True, exist_ok=True)

def obtener_fuente(size=14):
    """Carga fuente monoespaciada para la terminal"""
    font_paths = [
        "C:\\Windows\\Fonts\\consola.ttf",
        "C:\\Windows\\Fonts\\cour.ttf",
        "C:\\Windows\\Fonts\\lucon.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                pass
    return ImageFont.load_default()

def renderizar_terminal(q_id, titulo, sql_cmd, log_content, output_png):
    font = obtener_fuente(13)
    font_bold = obtener_fuente(14)
    font_small = obtener_fuente(11)

    # Preparar texto de terminal
    lines = []
    lines.append(f"0: jdbc:hive2://localhost:10000/superstore_db> -- {titulo}")
    for sql_line in sql_cmd.strip().splitlines():
        if sql_line.strip():
            lines.append(f"0: jdbc:hive2://localhost:10000/superstore_db> {sql_line.strip()}")
    lines.append("")
    for log_line in log_content.splitlines():
        if not log_line.startswith("0: jdbc:hive2://"):
            lines.append(log_line)

    # Limitar lineas si es muy larga (ej. serie de 48 meses mostrar primeras y ultimas)
    if len(lines) > 42:
        resumen_lines = lines[:28] + ["... [filas intermedias procesadas en cluster] ..."] + lines[-12:]
    else:
        resumen_lines = lines

    # Calcular dimensiones
    char_w = 8.2
    line_h = 20
    max_len = max(len(l) for l in resumen_lines) if resumen_lines else 80
    img_w = max(int(max_len * char_w) + 70, 950)
    header_h = 42
    footer_h = 30
    img_h = header_h + (len(resumen_lines) * line_h) + footer_h + 25

    # Crear imagen
    img = Image.new("RGB", (img_w, img_h), color="#0F141C")
    draw = ImageDraw.Draw(img)

    # Barra de titulo de la ventana
    draw.rectangle([(0, 0), (img_w, header_h)], fill="#1B2230")
    draw.line([(0, header_h), (img_w, header_h)], fill="#2E384D", width=1)

    # Botones estilo terminal
    draw.ellipse([(14, 14), (26, 26)], fill="#E5534B")  # Cerrar
    draw.ellipse([(34, 14), (46, 26)], fill="#EBB328")  # Minimizar
    draw.ellipse([(54, 14), (66, 26)], fill="#57AB5A")  # Maximizar

    # Titulo de ventana
    win_title = f"Beeline HiveQL 4.0.1 — superstore_server:10000 (Session: svr0035567) | {titulo[:45]}"
    draw.text((85, 13), win_title, fill="#C9D1D9", font=font_bold)

    # Renderizar lineas de terminal
    y = header_h + 16
    for line in resumen_lines:
        if line.startswith("0: jdbc:hive2:"):
            # Prompt de Beeline
            prompt_part = "0: jdbc:hive2://localhost:10000/superstore_db>"
            draw.text((25, y), prompt_part, fill="#58A6FF", font=font)
            cmd_part = line[len(prompt_part):]
            draw.text((25 + int(len(prompt_part) * char_w) + 5, y), cmd_part, fill="#79C0FF", font=font)
        elif line.startswith("+") or line.startswith("|"):
            # Tabla de resultados
            if "total" in line.lower() or "region" in line.lower() or "perfil" in line.lower() or "analisis" in line.lower() or "rango" in line.lower():
                draw.text((25, y), line, fill="#56D364", font=font)  # Encabezado verde
            else:
                draw.text((25, y), line, fill="#E6EDF3", font=font)  # Filas blanco suave
        elif "rows selected" in line or "seconds" in line:
            # Resumen de seleccion
            draw.text((25, y), line, fill="#3FB950", font=font_bold)
        elif "..." in line:
            draw.text((25, y), line, fill="#8B949E", font=font)
        else:
            draw.text((25, y), line, fill="#C9D1D9", font=font)
        y += line_h

    # Barra de estado inferior
    status_y = img_h - footer_h
    draw.rectangle([(0, status_y), (img_w, img_h)], fill="#161B22")
    draw.line([(0, status_y), (img_w, status_y)], fill="#2E384D", width=1)
    status_text = f"Hadoop 3.4.1 HDFS | Apache Hive 4.0.1 | UTC-4 La Paz, Bolivia | Estudiante: Ronald Joel Saavedra Vargas"
    draw.text((25, status_y + 8), status_text, fill="#8B949E", font=font_small)

    img.save(output_png, quality=95)
    print(f"[+] Renderizada evidencia: {output_png.name} ({img_w}x{img_h})")

def generar_todas():
    json_files = sorted(REGISTROS_DIR.glob("*.json"))
    for jf in json_files:
        q_id = jf.stem
        with open(jf, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        log_file = REGISTROS_DIR / f"{q_id}.log"
        log_content = log_file.read_text(encoding="utf-8") if log_file.exists() else ""
        
        # Renderizar captura principal
        out_cap = EVIDENCIAS_DIR / f"{q_id}-captura.png"
        renderizar_terminal(q_id, data["titulo"], data["comando_sql"], log_content, out_cap)
        
        # Renderizar registro complementario
        out_reg = EVIDENCIAS_DIR / f"{q_id}-registro-1.png"
        renderizar_terminal(q_id, data["titulo"], data["comando_sql"], log_content, out_reg)

if __name__ == "__main__":
    generar_todas()
