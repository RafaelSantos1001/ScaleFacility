"""
Gera a proposta comercial em PDF no padrão visual da Scale.

Nova estratégia (pós-corrupção do paginas_base.pdf):
Em vez de reaproveitar páginas de um único PDF vetorial exportado do Canva
(frágil: qualquer corrupção binária — ex. Git mexendo em quebra de linha —
deixa as páginas em branco), cada página fixa agora é uma imagem PNG/JPG
independente em assets/pages/, extraída em alta resolução das propostas
reais já aprovadas. Imagens são arquivos binários "normais": o Git não tem
motivo para mexer neles, e mesmo que um dia venham a corromper, corrompe
uma página, não o arquivo inteiro.

Páginas 100% estáticas (nunca mudam com o orçamento) entram como imagem de
fundo cheia. Páginas com texto variável (capa, itens de entrega, prazo,
"do papel ao digital" e "quais arquivos vou receber") usam uma imagem de
fundo (quando têm foto) + uma camada de texto desenhada com ReportLab por
cima — a mesma técnica que já existia para capa/itens/prazo.
"""
import io
import os
import urllib.request

from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

from precos import itens_de_entrega

PASTA = os.path.dirname(os.path.abspath(__file__))
PASTA_PAGINAS = os.path.join(PASTA, "assets", "pages")
PASTA_FONTES = os.path.join(PASTA, "assets", "fonts")

# Imagens de fundo de cada página fixa (relativas a assets/pages/)
FUNDOS = {
    "capa": "capa.jpg",
    "prazo": "prazo_bg.jpg",
    "missao": "missao.jpg",
    "importancia": "importancia.png",
    "processo_inloco": "processo_inloco.png",
    "inloco": "inloco.jpg",
    "digital": "digital_bg.jpg",
    "arquivos_inloco": "arquivos_bg.jpg",
    "processo_maquete": "processo_maquete.png",
    "elaboracao": "elaboracao.jpg",
    "arquivos_maquete": "arquivos_maquete_bg.jpg",
    "contato_completo": "contato_completo.jpg",
    "contato_simples": "contato_simples.jpg",
}

# Geometria das páginas originais (1440 x 810 pt, mediabox deslocada 7,92 pt)
W, TOPO = 1440, 817.92

MARROM = Color(0.4353, 0.2471, 0.1882)
MARROM_CAPA = Color(0.4392, 0.2471, 0.1882)
BEGE = Color(232 / 255, 229 / 255, 220 / 255)
BEGE_PILULA = Color(0.902, 0.878, 0.827)
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
    c.setFillColor(cor)
    c.setStrokeColor(cor)
    c.rect(x0, TOPO - bottom, x1 - x0, bottom - top, stroke=0, fill=1)


ALTURA_CONTEUDO = 810  # as páginas originais têm mediabox [0, 7.92, 1440, 817.92]


def _fundo(c, nome_chave):
    """Desenha a imagem de fundo de uma página fixa, alinhada ao mesmo
    mediabox (0, 7.92, 1440, 817.92) usado pelas propostas originais —
    por isso a imagem cobre só os 810pt de conteúdo, começando em y=7.92,
    e não os 817.92pt inteiros do canvas."""
    caminho = os.path.join(PASTA_PAGINAS, FUNDOS[nome_chave])
    c.drawImage(ImageReader(caminho), 0, TOPO - ALTURA_CONTEUDO, width=W, height=ALTURA_CONTEUDO,
                preserveAspectRatio=False, anchor='c')


def _nova_camada():
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(W, TOPO))
    return c, buf


def _fechar_camada(c, buf):
    c.showPage()
    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]


def _pagina_estatica(nome_chave):
    """Página 100% fixa: só a imagem de fundo, sem nenhum texto dinâmico."""
    c, buf = _nova_camada()
    _fundo(c, nome_chave)
    return _fechar_camada(c, buf)


# ---------------------------------------------------------------------------
# Páginas dinâmicas
# ---------------------------------------------------------------------------
def _camada_capa(tipo, cliente, local):
    c, buf = _nova_camada()
    _fundo(c, "capa")
    _tampar(c, 560, 10, 1330, 56, MARROM_CAPA)
    t = _ajustar(tipo, "Light", 34.2, 740)
    _texto(c, tipo, 1300, 53, "Light", t, BRANCO, alinhar="dir")
    for bottom, valor in ((446, cliente), (532, local)):
        _tampar(c, 940, bottom - 26, 1436, bottom + 44, MARROM_CAPA)
        valor = valor.upper()
        t = _ajustar(valor, "Light", 18, 470, espaco=0.6)
        _texto(c, valor, 947, bottom, "Light", t, BRANCO, espaco=0.6)
    return _fechar_camada(c, buf)


def _camada_digital(paragrafo1, paragrafo2):
    """'Do papel ao digital' — mesma foto/cabeçalho sempre, texto muda com o
    software usado (AutoCAD / AutoCAD e/ou SketchUp / SketchUp)."""
    c, buf = _nova_camada()
    _fundo(c, "digital")
    _tampar(c, 40, 330, 800, 610, BEGE)
    y = 360
    for linha in _quebrar(paragrafo1, "Light", 20, 720, 0.3):
        _texto(c, linha, 57, y, "Light", 20, MARROM, espaco=0.3)
        y += 30
    y += 22
    for linha in _quebrar(paragrafo2, "Light", 20, 720, 0.3):
        _texto(c, linha, 57, y, "Light", 20, MARROM, espaco=0.3)
        y += 30
    return _fechar_camada(c, buf)


def _camada_arquivos(fundo_chave, itens_pills):
    """'Quais arquivos vou receber?' — a lista de pílulas muda com os
    serviços contratados; o resto da página (intro, rodapé, foto) é fixo
    e já está embutido na imagem de fundo escolhida."""
    c, buf = _nova_camada()
    _fundo(c, fundo_chave)
    x0, largura, altura, espaco = 64, 655, 41, 36
    y_topo = 310
    _tampar(c, x0 - 10, y_topo - 10, x0 + largura + 10,
            y_topo + max(len(itens_pills), 1) * (altura + espaco) + 60, BRANCO)
    for i, (titulo, spec) in enumerate(itens_pills):
        y = y_topo + i * (altura + espaco)
        escuro = i % 2 == 0
        cor_fundo = MARROM if escuro else BEGE_PILULA
        cor_titulo = BRANCO if escuro else MARROM
        cor_spec = BRANCO if escuro else MARROM
        c.setFillColor(cor_fundo)
        c.roundRect(x0, TOPO - (y + altura), largura, altura,
                    radius=altura / 2, stroke=0, fill=1)
        cx, cy = x0 + altura / 2, TOPO - (y + altura / 2)
        c.setFillColor(BRANCO if escuro else MARROM)
        c.circle(cx, cy, altura / 2 - 5, stroke=0, fill=1)
        c.setStrokeColor(cor_fundo)
        c.setLineWidth(2)
        c.line(cx - 4, cy + 4, cx + 3, cy)
        c.line(cx - 4, cy - 4, cx + 3, cy)
        _texto(c, titulo, x0 + altura + 6, y + altura / 2 + 6, "Regular", 17, cor_titulo)
        _texto(c, spec, x0 + largura * 0.62, y + altura / 2 + 6, "Light", 16, cor_spec)
    return _fechar_camada(c, buf)


def _camada_itens(secoes):
    c, buf = _nova_camada()
    _tampar(c, 42, 100, W, TOPO, BRANCO)

    colunas_x, largura_col = [64, 760], 630
    topo_util, limite = 140, 785

    def montar(escala):
        tam_sec, tam_tit, tam_desc = 16 * escala, 14.5 * escala, 13.5 * escala
        blocos = []
        for titulo_sec, itens in secoes:
            if titulo_sec:
                blocos.append(("sec", titulo_sec, tam_sec * 2.0))
            for tit, desc in itens:
                linhas = _quebrar(desc, "Light", tam_desc, largura_col - 10, 0.5)
                h = tam_tit * 1.45 + len(linhas) * tam_desc * 1.4 + tam_desc * 0.9
                blocos.append(("item", (tit, linhas), h))
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
                    prox_h = limite
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
    _fundo(c, "prazo")

    _tampar(c, 0, 90, 985, 265, BRANCO)
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
    if tem_inloco:
        obs = "*Esse prazo é referente após a conclusão do levantamento in loco."
        _texto(c, obs, 54, bottom + 32, "LightItalic", 22, MARROM, espaco=1.0)

    _tampar(c, 480, 288, 985, 392, MARROM)
    t = _ajustar(valor_txt, "Bold", 31.3, 470, 1.0)
    largura = _largura(valor_txt, F["Bold"], t, 1.0)
    x = min(698, 975 - largura)
    _texto(c, valor_txt, x, 355, "Bold", t, BRANCO, espaco=1.0)

    _tampar(c, 0, 560, 985, TOPO, BRANCO)
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
# Textos que variam conforme o software / combinação de serviços
# ---------------------------------------------------------------------------
def _texto_digital(tem_2d, tem_3d):
    if tem_2d and tem_3d:
        software = "AutoCAD e/ou SketchUp"
    elif tem_3d:
        software = "SketchUp"
    else:
        software = "AutoCAD"
    p1 = (f"Após concluir o levantamento IN LOCO, transferimos todas as informações "
          f"coletadas para o software {software}.")
    if tem_2d:
        p2 = ("Utilizamos o CTB da sua empresa. Aplicamos ele ao desenho para garantir "
              "que as cores e espessuras das linhas estejam de acordo com suas preferências.")
    else:
        p2 = ("Utilizamos o template da sua empresa. Aplicamos ele ao desenho para garantir "
              "que os parâmetros da modelagem estejam de acordo com suas preferências.")
    return p1, p2


def _pilulas_arquivos(tem_2d, tem_3d, tem_loco):
    pills = []
    if tem_2d:
        pills.append(("Levantamento Digital 2D", ".dwg (utilizando seu ctb)"))
    if tem_3d:
        rotulo = "Levantamento Digital 3D" if tem_loco else "MAQUETE 3D"
        pills.append((rotulo, ".skp"))
    if tem_2d:
        pills.append(("PDFS", "Pranchas plotadas em .pdf"))
    if tem_loco:
        pills.append(("Levantamento Fotográfico", "fotos e vídeos do espaço medido"))
    return pills


# ---------------------------------------------------------------------------
# Montagem
# ---------------------------------------------------------------------------
def gerar_proposta(*, tipo, cliente, local, selecao, valor_txt, dias_entrega,
                    dias_inloco, pagamentos, incluir_itens=True,
                    fechamento="completo") -> bytes:
    """
    pagamentos: lista de (titulo, [linhas]).
    fechamento: "completo" (foto + cartão de crédito) ou "simples" (só texto
        de agradecimento, sem parcelamento) — os dois modelos usados hoje
        pela Scale.
    Retorna os bytes do PDF.
    """
    _carregar_fontes()
    from precos import IN_LOCO, D2, D3

    tem_loco = bool(selecao.get(IN_LOCO))
    tem_2d = bool(selecao.get(D2))
    tem_3d = bool(selecao.get(D3))

    saida = PdfWriter()

    def add(pagina):
        saida.add_page(pagina)

    add(_camada_capa(tipo, cliente, local))

    if tem_loco:
        for chave in ("missao", "importancia", "processo_inloco", "inloco"):
            add(_pagina_estatica(chave))
        p1, p2 = _texto_digital(tem_2d, tem_3d)
        add(_camada_digital(p1, p2))
        pills = _pilulas_arquivos(tem_2d, tem_3d, tem_loco=True)
        add(_camada_arquivos("arquivos_inloco", pills))
    elif tem_3d:
        add(_pagina_estatica("processo_maquete"))
        add(_pagina_estatica("elaboracao"))
        pills = _pilulas_arquivos(tem_2d=False, tem_3d=True, tem_loco=False)
        add(_camada_arquivos("arquivos_maquete", pills))
    else:
        for chave in ("missao", "importancia"):
            add(_pagina_estatica(chave))

    if incluir_itens:
        add(_camada_itens(itens_de_entrega(selecao)))

    add(_camada_prazo(valor_txt, dias_entrega, dias_inloco, tem_loco, pagamentos))

    chave_contato = "contato_completo" if fechamento == "completo" else "contato_simples"
    add(_pagina_estatica(chave_contato))

    saida.add_metadata({"/Title": f"Proposta {tipo.title()} - {cliente}", "/Author": "Scale Levantamentos"})
    out = io.BytesIO()
    saida.write(out)
    return out.getvalue()
