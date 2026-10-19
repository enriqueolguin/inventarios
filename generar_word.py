# -*- coding: utf-8 -*-
"""
Genera "Memoria_Tecnica_Servidor.docx" replicando el diseno del
"Manual_Usuario_CRMexline.pdf":

  - Fuente Noto Sans (Regular / Bold) en todo el documento
  - Paleta: #1B2559 (titulos), #3B5BFF (subtitulos), #1E293B (texto),
            #7B849D (gris secundario), #E6EAF2 (lineas divisorias)
  - Portada: logo centrado + titulo 38pt + subtitulo gris 22pt
  - Encabezado: linea divisoria #E6EAF2
  - Pie de pagina: banda degradada #094EF4 -> #05ABF8 con bloque rojo
    #E00B25 y el texto "MEMORIA TECNICA DEL SERVIDOR" + "Pagina N" en blanco
  - Indice con marcadores cuadrados y entradas en azul #3B5BFF
  - Secciones que inician en pagina nueva con titulo 17pt + linea divisoria
"""

import re
from PIL import Image, ImageDraw
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Emu
from docx.enum.text import (
    WD_ALIGN_PARAGRAPH,
    WD_BREAK,
    WD_TAB_ALIGNMENT,
    WD_TAB_LEADER,
)
from docx.oxml import parse_xml
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

RUTA_ESTRUCTURA = "documento/estructura.txt"
RUTA_SALIDA = "Memoria_Tecnica_Servidor_v2.docx"
RUTA_LOGO = "imagenes/logomxln.png"
RUTA_BANDA = "imagenes/banda_footer.png"

_name_idx = [1001]

AZUL_OSCURO = "1B2559"
AZUL_VIVO = "3B5BFF"
TEXTO = "1E293B"
GRIS = "7B849D"
LINEA = "E6EAF2"
ROJO = "E00B25"

FUENTE = "Noto Sans"

TITULO_PIE = "MEMORIA TÉCNICA DEL SERVIDOR"


# ---------------------------------------------------------------- utilidades
def rgb(hexa):
    return RGBColor(int(hexa[0:2], 16), int(hexa[2:4], 16), int(hexa[4:6], 16))


def usar_fuente_noto(run):
    """Fuerza Noto Sans en ascii, hAnsi, cs y eastAsia. Usa get_or_add_rFonts
    para que w:rFonts quede en su posicion correcta del esquema rPr."""
    run.font.name = FUENTE
    rfonts = run._r.get_or_add_rPr().get_or_add_rFonts()
    rfonts.set(qn("w:cs"), FUENTE)
    rfonts.set(qn("w:eastAsia"), FUENTE)


def estilizar_run(run, size=None, color=None, bold=None):
    if size:
        run.font.size = Pt(size)
    if color:
        run.font.color.rgb = rgb(color)
    if bold is not None:
        run.font.bold = bold
    usar_fuente_noto(run)


def agregar_campo_simple(parrafo, instruccion, resultado="1", size=7.5, color="FFFFFF"):
    """Inserta un campo de Word (PAGE, NUMPAGES) con resultado en cache
    para que LibreOffice/Word lo muestren con el formato correcto.
    Usa la estructura canonica de Word: cada fldChar/instrText en su propio run."""
    runs = []
    # begin
    r1 = parrafo.add_run()
    fld_b = OxmlElement("w:fldChar")
    fld_b.set(qn("w:fldCharType"), "begin")
    r1._r.append(fld_b)
    runs.append(r1)
    # instruccion
    r2 = parrafo.add_run()
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = instruccion
    r2._r.append(instr)
    runs.append(r2)
    # separador
    r3 = parrafo.add_run()
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    r3._r.append(fld_sep)
    runs.append(r3)
    # resultado en cache (se actualiza al abrir el documento)
    r4 = parrafo.add_run(resultado)
    runs.append(r4)
    # cierre
    r5 = parrafo.add_run()
    fld_e = OxmlElement("w:fldChar")
    fld_e.set(qn("w:fldCharType"), "end")
    r5._r.append(fld_e)
    runs.append(r5)
    for r in runs:
        estilizar_run(r, size, color, True)
    return r4


def borde_inferior(parrafo, color=LINEA, sz="6"):
    """Aplica borde inferior fino a un parrafo."""
    ppr = parrafo._p.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), sz)
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), color)
    pbdr.append(bottom)
    ppr.insert_element_before(
        pbdr,
        "w:shd", "w:tabs", "w:suppressAutoHyphens", "w:kinsoku", "w:wordWrap",
        "w:overflowPunct", "w:topLinePunct", "w:autoSpaceDE", "w:autoSpaceDN",
        "w:bidi", "w:adjustRightInd", "w:snapToGrid", "w:spacing", "w:ind",
        "w:contextualSpacing", "w:mirrorIndents", "w:suppressOverlap", "w:jc",
        "w:textDirection", "w:textAlignment", "w:textboxTightWrap",
        "w:outlineLvl", "w:divId", "w:cnfStyle", "w:rPr", "w:sectPr",
        "w:pPrChange",
    )


def agregar_linea_divisoria(doc, despues=14):
    """Parrafo vacio que dibuja una linea #E6EAF2 a lo ancho."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(despues)
    borde_inferior(p)
    estilizar_run(p.add_run(""), 2, LINEA)
    return p


def nueva_entrada_indice(doc, nivel, texto):
    """Entrada del indice con marcador cuadrado y linea de puntos al margen."""
    pe = doc.add_paragraph()
    pf = pe.paragraph_format
    pf.space_after = Pt(16)
    pf.line_spacing = 1.0
    pf.tab_stops.add_tab_stop(Cm(15.5), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
    if nivel == 1:
        pf.left_indent = Cm(0.25)
        pf.first_line_indent = Cm(-0.25)
        r0 = pe.add_run("\u25AA ")
        estilizar_run(r0, 13, TEXTO, True)
        r = pe.add_run(texto)
        estilizar_run(r, 13, AZUL_VIVO, True)
        rt = pe.add_run("\t")
        estilizar_run(rt, 13, TEXTO)
    else:
        pf.left_indent = Cm(1.0)
        r = pe.add_run(texto)
        estilizar_run(r, 11, GRIS, False)
        rt = pe.add_run("\t")
        estilizar_run(rt, 11, GRIS)
    return pe


def agregar_salto_pagina(doc):
    p = doc.add_paragraph()
    r = p.add_run()
    r.font.size = Pt(2)
    usar_fuente_noto(r)
    r.add_break(WD_BREAK.PAGE)


def generar_banda_footer():
    """Banda degradada #094EF4 -> #05ABF8 (83% del ancho) + bloque rojo #DF0A25
    (17%), como el Manual_Usuario_CRMexline.pdf.
    Tamano: ancho de pagina A4 (21 cm) x 0.93 cm a 300 dpi."""
    W, H = 2480, 110
    img = Image.new("RGB", (W, H))
    dr = ImageDraw.Draw(img)
    c1 = (9, 78, 244)   # 094EF4
    c2 = (5, 171, 248)  # 05ABF8
    red_w = int(W * 0.17)
    for x in range(0, W - red_w):
        t = x / max(1, W - red_w - 1)
        col = tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))
        dr.line([(x, 0), (x, H)], fill=col)
    dr.rectangle([W - red_w, 0, W, H], fill=(223, 10, 37))
    img.save(RUTA_BANDA)


def agregar_banda_flotante(parrafo, ruta_imagen, cx, cy, pos_v, name="banda footer"):
    """Inserta una imagen anclada al fondo de la pagina, detras del texto
    (misma tecnica que las marcas de agua de Word)."""
    parte = parrafo.part
    r_id, _ = parte.get_or_add_image(ruta_imagen)
    xml = (
        '<w:drawing \n'
        ' xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"\n'
        ' xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"\n'
        ' xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"\n'
        ' xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"\n'
        ' xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f'<wp:anchor distT="0" distB="0" distL="0" distR="0" simplePos="0" relativeHeight="{251658240 + _name_idx[0]}" behindDoc="1" locked="0" layoutInCell="1" allowOverlap="1">'
        '<wp:simplePos x="0" y="0"/>'
        '<wp:positionH relativeFrom="page"><wp:posOffset>0</wp:posOffset></wp:positionH>'
        f'<wp:positionV relativeFrom="page"><wp:posOffset>{pos_v}</wp:posOffset></wp:positionV>'
        f'<wp:extent cx="{cx}" cy="{cy}"/>'
        '<wp:effectExtent l="0" t="0" r="0" b="0"/>'
        '<wp:wrapNone/>'
        f'<wp:docPr id="{_name_idx[0]}" name="{name}"/>'
        '<wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr>'
        '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        '<pic:pic>'
        f'<pic:nvPicPr><pic:cNvPr id="{_name_idx[0]}" name="{name}"/><pic:cNvPicPr/></pic:nvPicPr>'
        f'<pic:blipFill><a:blip r:embed="{r_id}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
        f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
        '</pic:pic></a:graphicData></a:graphic></wp:anchor></w:drawing>'
    )
    _name_idx[0] += 1
    run = parrafo.add_run()
    run._r.append(parse_xml(xml))


# ---------------------------------------------------------------- documento
doc = Document()

# --- estilos base
normal = doc.styles["Normal"]
normal.font.name = FUENTE
normal.font.size = Pt(13)
normal.paragraph_format.space_after = Pt(10)
normal.paragraph_format.line_spacing = 1.0
rfonts = normal.element.get_or_add_rPr().get_or_add_rFonts()
rfonts.set(qn("w:cs"), FUENTE)
rfonts.set(qn("w:eastAsia"), FUENTE)

h1 = doc.styles["Heading 1"]
h1.font.name = FUENTE
h1.font.size = Pt(17)
h1.font.bold = True
h1.font.color.rgb = rgb(AZUL_OSCURO)
h1rfonts = h1.element.get_or_add_rPr().get_or_add_rFonts()
h1rfonts.set(qn("w:cs"), FUENTE)
h1rfonts.set(qn("w:eastAsia"), FUENTE)

h2 = doc.styles["Heading 2"]
h2.font.name = FUENTE
h2.font.size = Pt(13)
h2.font.bold = True
h2.font.color.rgb = rgb(AZUL_VIVO)
h2rfonts = h2.element.get_or_add_rPr().get_or_add_rFonts()
h2rfonts.set(qn("w:cs"), FUENTE)
h2rfonts.set(qn("w:eastAsia"), FUENTE)

# --- seccion: A4, margenes como el manual (45 pt ~ 1.59 cm)
seccion = doc.sections[0]
seccion.page_width = Cm(21.0)
seccion.page_height = Cm(29.7)
seccion.top_margin = Cm(2.0)
seccion.bottom_margin = Cm(2.2)
seccion.left_margin = Cm(1.59)
seccion.right_margin = Cm(1.59)
seccion.header_distance = Cm(1.0)
seccion.footer_distance = Cm(0.3)
# primera pagina (portada) con encabezado propio, sin logo
seccion.different_first_page_header_footer = True

# --- encabezado general (todas las paginas menos la portada):
# logo centrado + linea divisoria #E6EAF2 a lo ancho util
encabezado = seccion.header
encabezado.is_linked_to_previous = False
parrafo_enc = encabezado.paragraphs[0]
parrafo_enc.text = ""
parrafo_enc.alignment = WD_ALIGN_PARAGRAPH.CENTER
parrafo_enc.paragraph_format.space_before = Pt(0)
parrafo_enc.paragraph_format.space_after = Pt(0)
run_logo_enc = parrafo_enc.add_run()
run_logo_enc.add_picture(RUTA_LOGO, width=Cm(3.6))

# --- encabezado de la primera pagina (portada): solo la linea divisoria
encabezado_portada = seccion.first_page_header
parrafo_enc1 = encabezado_portada.paragraphs[0]
parrafo_enc1.alignment = WD_ALIGN_PARAGRAPH.LEFT
parrafo_enc1.paragraph_format.space_after = Pt(0)
borde_inferior(parrafo_enc1)
estilizar_run(parrafo_enc1.add_run(""), 2, LINEA)

# --- pie de pagina: banda degradada flotante (como el manual) + texto blanco
# en una linea centrada sobre la banda

# medidas de la banda (tomadas del Manual_Usuario_CRMexline.pdf):
# - alto 0.93 cm (26.3 pt)
# - borde inferior de la banda a 0.52 cm del borde de la pagina (14.8 pt)
# - bloque rojo 17% del ancho (x >= 494.3 pt de 595.9 pt)
ANCHO_PAGINA_EMU = int(21.0 * 360000)
ALTO_BANDA_EMU = int(0.93 * 360000)
OFFSET_Y_EMU = int((29.7 - 0.93 - 0.52) * 360000)

generar_banda_footer()

def llenar_pie(pie_container):
    """Pie como el del manual: banda flotante + tabla invisible de 2 columnas
    (titulo del documento a la izquierda, 'Pagina N' a la derecha)."""
    parrafo = pie_container.paragraphs[0]

    # 1) banda degradada anclada al fondo, igual en todas las paginas
    p_banda = parrafo.insert_paragraph_before()
    p_banda.paragraph_format.space_before = Pt(0)
    p_banda.paragraph_format.space_after = Pt(0)
    p_banda.paragraph_format.line_spacing = 1.0
    r_banda = p_banda.add_run()
    r_banda.font.size = Pt(2)
    usar_fuente_noto(r_banda)
    agregar_banda_flotante(p_banda, RUTA_BANDA, ANCHO_PAGINA_EMU, ALTO_BANDA_EMU, OFFSET_Y_EMU)

    # 2) linea de texto en 2 columnas: titulo (izq) + Pagina N (der)
    tbl = pie_container.add_table(rows=1, cols=2, width=Cm(17.82))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    # sin bordes visibles
    tblPr = tbl._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "none")
        el.set(qn("w:sz"), "0")
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), "auto")
        borders.append(el)
    tblPr.insert_element_before(
        borders, "w:shd", "w:tblLayout", "w:tblCellMar", "w:tblLook",
        "w:tblCaption", "w:tblDescription",
    )
    # margenes de celda en 0 para que el texto quede exactamente en los
    # margenes de la pagina, como en el manual (x=45 pt)
    cellmar = OxmlElement("w:tblCellMar")
    for side, val in (("top", "0"), ("left", "0"), ("bottom", "0"), ("right", "0")):
        m = OxmlElement(f"w:{side}")
        m.set(qn("w:w"), val)
        m.set(qn("w:type"), "dxa")
        cellmar.append(m)
    tblPr.insert_element_before(
        cellmar, "w:tblLook", "w:tblCaption", "w:tblDescription",
    )
    # anchos de columna: 15.41 cm (titulo) + 2.41 cm (pagina) = 17.82 cm utiles
    for idx, ancho in enumerate((Cm(15.41), Cm(2.41))):
        # python-docx crea un unico w:tcW en la posicion correcta de tcPr
        tbl.rows[0].cells[idx].width = ancho

    c_izq = tbl.rows[0].cells[0].paragraphs[0]
    c_izq.paragraph_format.space_before = Pt(2)
    c_izq.paragraph_format.space_after = Pt(0)
    r = c_izq.add_run(TITULO_PIE)
    estilizar_run(r, 7.5, "FFFFFF", True)

    c_der = tbl.rows[0].cells[1].paragraphs[0]
    c_der.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    c_der.paragraph_format.space_before = Pt(2)
    c_der.paragraph_format.space_after = Pt(0)
    r = c_der.add_run("Página ")
    estilizar_run(r, 7.5, "FFFFFF", True)
    agregar_campo_simple(c_der, "PAGE")

    # 3) parrafo de relleno tras la tabla: centra verticalmente la linea de
    # texto sobre la banda (interlineado exacto, independiente de la fuente)
    p_pad = pie_container.add_paragraph()
    p_pad.paragraph_format.space_before = Pt(0)
    p_pad.paragraph_format.space_after = Pt(0)
    p_pad.paragraph_format.line_spacing = Pt(13.0)
    r_pad = p_pad.add_run("")
    estilizar_run(r_pad, 2, "FFFFFF")

llenar_pie(seccion.footer)

# pie de la portada: misma banda, para que la portada tambien la tenga
pie_portada = seccion.first_page_footer
llenar_pie(pie_portada)


# ---------------------------------------------------------------- lectura de estructura
def leer_estructura(ruta):
    """Lee el txt y devuelve bloques {'titulo': str, 'lineas': [str]}."""
    with open(ruta, "r", encoding="utf-8") as f:
        texto = f.read()

    bloques = []
    titulo_actual = None
    lineas_actuales = []

    for linea in texto.splitlines():
        linea = linea.rstrip()
        m = re.match(r"^(\d+)\.\s+(.+)$", linea)
        if m:
            if titulo_actual is not None:
                bloques.append({"titulo": titulo_actual, "lineas": lineas_actuales})
            titulo_actual = linea
            lineas_actuales = []
        elif linea.strip() == "":
            continue
        else:
            if titulo_actual is not None:
                lineas_actuales.append(linea.strip())

    if titulo_actual is not None:
        bloques.append({"titulo": titulo_actual, "lineas": lineas_actuales})

    # Secciones finales sin numerar (p. ej. "Recomendaciones")
    finales = []
    for bloque in bloques:
        if "Recomendaciones" in bloque["lineas"]:
            idx = bloque["lineas"].index("Recomendaciones")
            bloque["lineas"] = bloque["lineas"][:idx]
            finales.append({"titulo": "Recomendaciones", "lineas": bloque["lineas"][idx + 1:]})
    bloques.extend(finales)

    return bloques


bloques = leer_estructura(RUTA_ESTRUCTURA)
bloque_control = bloques[0]          # "1. Control del documento"
cuerpo_bloques = bloques[1:]         # del 2 en adelante

# --- pagina 1: portada
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(70)
p.paragraph_format.space_after = Pt(4)
run_img = p.add_run()
run_img.add_picture(RUTA_LOGO, width=Cm(7.0))

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(30)
p.paragraph_format.space_after = Pt(6)
r = p.add_run("MEMORIA TÉCNICA DEL SERVIDOR")
estilizar_run(r, 38, AZUL_OSCURO, True)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_after = Pt(40)
r = p.add_run("Documento de control y especificaciones")
estilizar_run(r, 22, GRIS, False)

# --- tabla de control del documento (campos en dos columnas)
tabla = doc.add_table(rows=0, cols=2)
tabla.style = "Table Grid"
tabla.alignment = WD_TABLE_ALIGNMENT.CENTER

campos_portada = bloque_control["lineas"]
for linea in campos_portada:
    items = [x.strip() for x in linea.split(",")] if len(linea) > 40 else [linea]
    for item in items:
        item = item.rstrip(".")
        fila = tabla.add_row().cells
        p0 = fila[0].paragraphs[0]
        r = p0.add_run(item)
        estilizar_run(r, 13, TEXTO, True)
        p1 = fila[1].paragraphs[0]
        r = p1.add_run("")
        estilizar_run(r, 13, TEXTO)

# pie de portada
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(30)
r = p.add_run("Versión 1.0")
estilizar_run(r, 13, TEXTO, True)

agregar_salto_pagina(doc)

# --- pagina 2: indice de contenidos
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_after = Pt(14)
r = p.add_run("Índice de Contenidos")
estilizar_run(r, 17, AZUL_OSCURO, True)

# campo TOC real: Word lo rellena al abrir (updateFields)
p = doc.add_paragraph()
run = p.add_run()
fld_b = OxmlElement("w:fldChar")
fld_b.set(qn("w:fldCharType"), "begin")
run._r.append(fld_b)
run2 = p.add_run()
instr = OxmlElement("w:instrText")
instr.set(qn("xml:space"), "preserve")
instr.text = 'TOC \\o "1-2" \\h \\z \\u'
run2._r.append(instr)
run3 = p.add_run()
fld_sep = OxmlElement("w:fldChar")
fld_sep.set(qn("w:fldCharType"), "separate")
run3._r.append(fld_sep)

# vista previa del indice (Word la reemplaza al actualizar campos)
p.paragraph_format.tab_stops.add_tab_stop(Cm(15.5), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
primera = True
for bloque in cuerpo_bloques:
    if primera:
        r = p.add_run(bloque["titulo"])
        estilizar_run(r, 13, AZUL_VIVO, True)
        rt = p.add_run("\t")
        estilizar_run(rt, 13, TEXTO)
        primera = False
    else:
        nueva_entrada_indice(doc, 1, bloque["titulo"])
    for linea in bloque["lineas"]:
        nueva_entrada_indice(doc, 2, linea)

# cierre del campo TOC en el ultimo parrafo
r_fin = doc.paragraphs[-1].add_run()
fld_end = OxmlElement("w:fldChar")
fld_end.set(qn("w:fldCharType"), "end")
r_fin._r.append(fld_end)

agregar_salto_pagina(doc)

# --- cuerpo: cada seccion inicia en pagina nueva (como el manual)
for bloque in cuerpo_bloques:
    p = doc.add_paragraph(style="Heading 1")
    p.paragraph_format.page_break_before = True
    p.paragraph_format.space_after = Pt(14)
    p.add_run(bloque["titulo"])

    for linea in bloque["lineas"]:
        p = doc.add_paragraph(style="Heading 2")
        p.paragraph_format.space_before = Pt(18)
        p.add_run(linea)

doc.save(RUTA_SALIDA)
print(f"Documento generado: {RUTA_SALIDA}")

# Hacer que Word actualice el indice y la numeracion al abrir.
# settings.xml exige orden de esquema: zoom, ..., updateFields va ANTES
# de defaultTabStop; por eso se inserta al inicio, no con append.
from docx.settings import Settings
_elem = doc.settings.element
if _elem.find(qn("w:updateFields")) is None:
    _uf = OxmlElement("w:updateFields")
    _uf.set(qn("w:val"), "true")
    _ref = _elem.find(qn("w:defaultTabStop"))
    if _ref is not None:
        _ref.addprevious(_uf)
    else:
        _elem.insert(0, _uf)

import os
_docx = os.path.abspath(RUTA_SALIDA)
try:
    import win32com.client as win32
    word = win32.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    _doc = word.Documents.Open(_docx, ConfirmConversions=False, ReadOnly=False,
                               AddToRecentFiles=False)
    try:
        _doc.Fields.Update()
        _toc = _doc.TablesOfContents(1)
        _toc.Update()
        _doc.Save()
    finally:
        _doc.Close(SaveChanges=0)
        word.Quit()
    print("Indice y campos actualizados con Microsoft Word (COM)")
except Exception as e:
    print(f"Aviso: no se pudo automatizar Word ({e}); el .docx queda valido")
    print("y el indice se actualizara al abrirlo en Word.")
