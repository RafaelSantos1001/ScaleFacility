"""
Gera a proposta comercial em PDF no padrão visual da Scale.

Estratégia: as páginas fixas (Missão, Processo, Levantamento in loco, Arquivos,
Contato...) são reaproveitadas IDÊNTICAS das propostas originais feitas no Canva
(arquivo assets/paginas_base.pdf). Só as páginas que mudam a cada orçamento
(Capa, Itens de entrega e Prazo/Investimento) recebem uma camada com os novos
textos por cima, desenhada com ReportLab.
"""
import io
import os
import urllib.request

from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from precos import itens_de_entrega

PASTA = os.path.dirname(os.path.abspath(__file__))
BASE_PDF = os.path.join(PASTA, "assets", "paginas_base.pdf")
PASTA_FONTES = os.path.join(PASTA, "assets", "fonts")

# Índice de cada página dentro de assets/paginas_base.pdf
PAG = {
    "capa": 0, "missao": 1, "importancia": 2, "processo_inloco": 3, "inloco": 4,
    "digital_2d": 5, "arquivos_2d": 6, "itens": 7, "prazo": 8, "contato": 9,
    "digital_3d": 10, "arquivos_3d": 11, "processo_maquete": 12, "elaboracao": 13,
    "arquivos_maquete": 14,
}

# Geometria das páginas originais (1440 x 810 pt, mediabox deslocada 7,92 pt)
W, TOPO = 1440, 817.92

MARROM = Color(0.4353, 0.2471, 0.1882)
MARROM_CAPA = Color(0.4392, 0.2471, 0.1882)
BRANCO = Color(1, 1, 1)

# ---------------------------------------------------------------------------
# FONTES (Montserrat, a mesma das propostas). Se não houver os arquivos .ttf em
# assets/fonts, o app tenta baixar do repositório oficial; sem internet, usa
# Helvetica como reserva.
# ---------------------------------------------------------------------------
_ARQ_FONTES = {
    "Light": "Montserrat-Light.ttf",
    "Regular": "Montserrat-Regular.ttf",
    "Bold": "Montserrat-Bold.ttf",
    "BoldItalic": "Montserrat-BoldItalic.ttf",
    "LightItalic": "Montserrat-LightItalic.ttf",
}
_RESERVA = {
    "Light": "Helvetica", "Regular": "Helvetica", "Bold": "Helvetica-Bold",
    "BoldItalic": "Helvetica-BoldOblique", "LightItalic": "Helvetica-Oblique",
}
_URL_FONTE = "https://raw.githubusercontent.com/JulietaUla/Montserrat/master/fonts/ttf/{}"
F = {}  # estilo -> nome da fonte registrada


def _pasta_fontes_gravavel():
    """assets/fonts se der para gravar; senão uma pasta temporária."""
    import tempfile
    for pasta in (PASTA_FONTES, os.path.join(tempfile.gettempdir(), "scale_fonts")):
        try:
            os.makedirs(pasta, exist_ok=True)
            teste = os.path.join(pasta, ".teste")
            open(teste, "w").close()
            os.remove(teste)
            return pasta
        except OSError:
            continue
    return None


def _carregar_fontes():
    if F:
        return
    destino = None
    for estilo, arq in _ARQ_FONTES.items():
        caminho = os.path.join(PASTA_FONTES, arq)
        if not os.path.exists(caminho):
            destino = destino or _pasta_fontes_gravavel()
            if destino:
                caminho = os.path.join(destino, arq)
                if not os.path.exists(caminho):
                    try:
                        with urllib.request.urlopen(_URL_FONTE.format(arq), timeout=8) as r:
                            dados = r.read()
                        with open(caminho, "wb") as fh:
                            fh.write(dados)
                    except Exception:
                        pass
        try:
            nome = f"Mont-{estilo}"
            pdfmetrics.registerFont(TTFont(nome, caminho))
            F[estilo] = nome
        except Exception:
            F[estilo] = _RESERVA[estilo]


def usando_montserrat() -> bool:
    _carregar_fontes()
    return F["Regular"].startswith("Mont-")


# ---------------------------------------------------------------------------
# Utilitários de desenho
# ---------------------------------------------------------------------------
def _y(base_inferior, tamanho):
    """Converte a posição 'bottom' medida na página original em baseline do ReportLab."""
    return TOPO - base_inferior + 0.25 * tamanho


def _largura(texto, fonte, tamanho, espaco=0.0):
    return pdfmetrics.stringWidth(texto, fonte, tamanho) + espaco * max(len(texto) - 1, 0)


def _texto(c, texto, x, bottom, estilo, tamanho, cor, espaco=0.0, alinhar="esq"):
    fonte = F[estilo]
    if alinhar == "dir":
        x -= _largura(texto, fonte, tamanho, espaco)
    c.setFillColor(cor)
    c.setFont(fonte, tamanho)
    c.drawString(x, _y(bottom, tamanho), texto, charSpace=espaco)


def _ajustar(texto, estilo, tamanho, largura_max, espaco=0.0, minimo=9):
    """Diminui a fonte até o texto caber na largura."""
    while tamanho > minimo and _largura(texto, F[estilo], tamanho, espaco) > largura_max:
        tamanho -= 0.5
    return tamanho


def _quebrar(texto, estilo, tamanho, largura, espaco=0.0):
    linhas, atual = [], ""
    for palavra in texto.split():
        teste = f"{atual} {palavra}".strip()
        if _largura(teste, F[estilo], tamanho, espaco) <= largura or not atual:
            atual = teste
        else:
            linhas.append(atual)
            atual = palavra
    if atual:
        linhas.append(atual)
    return linhas


def _tampar(c, x0, top, x1, bottom, cor):
    """Cobre uma área da página original (coordenadas top/bottom como no original)."""
    c.setFillColor(cor)
    c.setStrokeColor(cor)
    c.rect(x0, TOPO - bottom, x1 - x0, bottom - top, stroke=0, fill=1)


def _nova_camada():
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(W, TOPO))
    return c, buf


def _fechar_camada(c, buf):
    c.showPage()
    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]


# ---------------------------------------------------------------------------
# Páginas dinâmicas
# ---------------------------------------------------------------------------
def _camada_capa(tipo, cliente, local):
    c, buf = _nova_camada()
    # Título do serviço (canto superior direito)
    _tampar(c, 560, 10, 1330, 56, MARROM_CAPA)
    t = _ajustar(tipo, "Light", 34.2, 740)
    _texto(c, tipo, 1300, 53, "Light", t, BRANCO, alinhar="dir")
    # Valores de "Proposto a" e "Local a ser medido"
    for bottom, valor in ((446, cliente), (532, local)):
        _tampar(c, 940, bottom - 24, 1436, bottom + 12, MARROM_CAPA)
        valor = valor.upper()
        t = _ajustar(valor, "Light", 18, 470, espaco=0.6)
        _texto(c, valor, 947, bottom, "Light", t, BRANCO, espaco=0.6)
    return _fechar_camada(c, buf)


def _camada_itens(secoes):
    c, buf = _nova_camada()
    _tampar(c, 42, 100, W, TOPO, BRANCO)

    colunas_x, largura_col = [64, 760], 630
    topo_util, limite = 140, 785

    def montar(escala):
        tam_sec, tam_tit, tam_desc = 16 * escala, 14.5 * escala, 13.5 * escala
        blocos = []  # (altura, lista de comandos)
        for titulo_sec, itens in secoes:
            if titulo_sec:
                blocos.append(("sec", titulo_sec, tam_sec * 2.0))
            for tit, desc in itens:
                linhas = _quebrar(desc, "Light", tam_desc, largura_col - 10, 0.5)
                h = tam_tit * 1.45 + len(linhas) * tam_desc * 1.4 + tam_desc * 0.9
                blocos.append(("item", (tit, linhas), h))
        # distribuir nas colunas (evita partir uma seção se ela cabe inteira na próxima coluna)
        col, y, layout = 0, topo_util, []
        for i, (tipo_b, conteudo, h) in enumerate(blocos):
            prox_h = blocos[i + 1][2] if tipo_b == "sec" and i + 1 < len(blocos) else 0
            if tipo_b == "sec" and col < len(colunas_x) - 1 and y > topo_util:
                h_sec = h
                for b in blocos[i + 1:]:
                    if b[0] == "sec":
                        break
                    h_sec += b[2]
                if y + h_sec > limite and topo_util + h_sec <= limite:
                    prox_h = limite  # força a troca de coluna
            if y + h + prox_h > limite:
                col += 1
                y = topo_util
                if col >= len(colunas_x):
                    return None
            layout.append((col, y, tipo_b, conteudo))
            y += h
        return layout, (tam_sec, tam_tit, tam_desc)

    escala, resultado = 1.0, None
    while escala >= 0.55:
        resultado = montar(escala)
        if resultado:
            break
        escala -= 0.05
    if not resultado:
        resultado = montar(0.55) or ([], (9, 9, 9))
    layout, (tam_sec, tam_tit, tam_desc) = resultado

    for col, y, tipo_b, conteudo in layout:
        x = colunas_x[col]
        if tipo_b == "sec":
            _texto(c, conteudo, x, y + tam_sec, "Bold", tam_sec, MARROM, espaco=0.6)
            c.setStrokeColor(MARROM)
            c.setLineWidth(1)
            ly = TOPO - (y + tam_sec * 1.45)
            c.line(x, ly, x + min(largura_col, _largura(conteudo, F["Bold"], tam_sec, 0.6)), ly)
        else:
            tit, linhas = conteudo
            _texto(c, "•", x + 4, y + tam_tit, "Bold", tam_tit, MARROM)
            _texto(c, tit, x + 20, y + tam_tit, "Bold", tam_tit, MARROM, espaco=0.6)
            yy = y + tam_tit * 1.45
            for ln in linhas:
                yy += tam_desc * 1.4
                _texto(c, ln, x, yy, "Light", tam_desc, MARROM, espaco=0.5)
    return _fechar_camada(c, buf)


def _camada_prazo(valor_txt, dias_entrega, dias_inloco, tem_inloco, pagamentos):
    c, buf = _nova_camada()

    # --- Prazo ---
    _tampar(c, 0, 97, 985, 258, BRANCO)
    bottom = 128
    if tem_inloco and dias_inloco:
        plural = "dia" if dias_inloco == 1 else "dias"
        _texto(c, f"*Necessitaremos de {dias_inloco} {plural} de levantamento in loco.",
               57, bottom, "BoldItalic", 22, MARROM, espaco=1.0)
        bottom = 175
    prefixo = "Os arquivos serão entregues em "
    dias_txt = f"{dias_entrega:02d} dias úteis." if dias_entrega > 1 else "01 dia útil."
    _texto(c, prefixo, 54, bottom, "Light", 22, MARROM, espaco=1.0)
    x2 = 54 + _largura(prefixo, F["Light"], 22, 1.0) + 1.0
    _texto(c, dias_txt, x2, bottom, "Bold", 22, MARROM, espaco=1.0)
    obs = ("*Esse prazo é referente após a conclusão do levantamento in loco." if tem_inloco
           else "*Esse prazo é referente após o recebimento da planta e fotos.")
    _texto(c, obs, 54, bottom + 32, "LightItalic", 22, MARROM, espaco=1.0)

    # --- Valor ---
    _tampar(c, 480, 290, 985, 390, MARROM)
    t = _ajustar(valor_txt, "Bold", 31.3, 470, 1.0)
    largura = _largura(valor_txt, F["Bold"], t, 1.0)
    x = min(698, 975 - largura)
    _texto(c, valor_txt, x, 355, "Bold", t, BRANCO, espaco=1.0)

    # --- Forma de pagamento ---
    _tampar(c, 0, 562, 985, TOPO, BRANCO)
    y = 592
    for titulo, linhas in pagamentos:
        _texto(c, "•", 80, y, "Bold", 21, MARROM)
        _texto(c, titulo.upper(), 99, y, "Bold", 21, MARROM, espaco=1.2)
        y += 40
        for ln in linhas:
            for sub in _quebrar(ln, "Light", 21, 900, 1.0):
                _texto(c, sub, 64, y, "Light", 21, MARROM, espaco=1.0)
                y += 29
        y += 22
    return _fechar_camada(c, buf)


# ---------------------------------------------------------------------------
# Montagem
# ---------------------------------------------------------------------------
def gerar_proposta(*, tipo, cliente, local, selecao, valor_txt, dias_entrega,
                   dias_inloco, pagamentos, incluir_itens=True) -> bytes:
    """
    pagamentos: lista de (titulo, [linhas]) — ex.:
        [("Contratação + entrega", ["50% na contratação e 50% na entrega do levantamento"])]
    Retorna os bytes do PDF.
    """
    _carregar_fontes()
    from precos import IN_LOCO, D2, D3

    tem_loco = bool(selecao.get(IN_LOCO))
    tem_2d = bool(selecao.get(D2))
    tem_3d = bool(selecao.get(D3))

    ordem = ["capa"]
    if tem_loco:
        ordem += ["missao", "importancia", "processo_inloco", "inloco"]
    elif tem_3d:
        ordem += ["processo_maquete", "elaboracao"]
    else:
        ordem += ["missao", "importancia"]
    if tem_2d:
        ordem.append("digital_2d")
    if tem_3d and tem_loco:
        ordem.append("digital_3d")
    if tem_2d:
        ordem.append("arquivos_2d")
    if tem_3d:
        ordem.append("arquivos_3d" if tem_loco else "arquivos_maquete")
    if incluir_itens:
        ordem.append("itens")
    ordem += ["prazo", "contato"]

    base = PdfReader(BASE_PDF)
    saida = PdfWriter()
    for nome in ordem:
        pagina = saida.add_page(base.pages[PAG[nome]])
        if nome == "capa":
            pagina.merge_page(_camada_capa(tipo, cliente, local))
        elif nome == "itens":
            pagina.merge_page(_camada_itens(itens_de_entrega(selecao)))
        elif nome == "prazo":
            pagina.merge_page(_camada_prazo(valor_txt, dias_entrega, dias_inloco, tem_loco, pagamentos))

    saida.add_metadata({"/Title": f"Proposta {tipo.title()} - {cliente}", "/Author": "Scale Levantamentos"})
        saida.add_metadata({"/Title": f"Proposta {tipo.title()} - {cliente}", "/Author": "Scale Levantamentos"})
    out = io.BytesIO()
    saida.write(out)
    return out.getvalue()
    out = io.BytesIO()
    saida.write(out)
    return out.getvalue()
