"""
Tabela de preços da Scale Levantamentos.

Valores em R$ por m², copiados da planilha "MODELO PRECIFICAÇÃO DA SCALE".
Para reajustar preços, basta editar os números abaixo e salvar no GitHub:
o Streamlit Cloud atualiza o app sozinho em ~1 minuto.
"""

IN_LOCO = "LEVANTAMENTO IN LOCO"
D2 = "LEVANTAMENTO DIGITAL 2D"
D3 = "LEVANTAMENTO DIGITAL 3D"
BLOCOS = [IN_LOCO, D2, D3]

ROTULO_BLOCO = {
    IN_LOCO: "Levantamento in loco",
    D2: "Levantamento digital 2D (AutoCAD)",
    D3: "Levantamento digital 3D / Maquete (SketchUp)",
}

FAIXAS = [50, 80, 100, 200, 500, 1000]

# Percentual padrão de "Juros Nota" (a planilha usa 6%)
PERCENTUAL_NOTA_PADRAO = 6.0

# ---------------------------------------------------------------------------
# TABELA R$/m² POR FAIXA
# ---------------------------------------------------------------------------
TABELA = {
    50: {
        IN_LOCO: {"ALVENARIA": 10, "ELÉTRICA": 0.5, "GESSO": 0.5, "ILUMINAÇÃO": 0.5, "HIDRÁULICA E GÁS": 0.5,
                  "MARMORARIA": 0.5, "REVESTIMENTO": 0.5, "MOBILIÁRIO FIXO": 0.5, "MOBILIÁRIO SOLTO": 0.5,
                  "SITUAÇÃO": 0.5, "FACHADAS": 2, "CORTES": 1, "COBERTURA": 0.5, "LEVANTAMENTO FOTOGRÁFICO": 0.5},
        D2: {"ALVENARIA": 4, "ELÉTRICA": 0.3, "GESSO": 0.3, "ILUMINAÇÃO": 0.3, "HIDRÁULICA E GÁS": 0.3,
             "MARMORARIA": 0.3, "REVESTIMENTO": 0.3, "MOBILIÁRIO FIXO": 0.3, "MOBILIÁRIO SOLTO": 0.3,
             "SITUAÇÃO": 0.3, "FACHADAS": 1.2, "CORTES": 0.6, "COBERTURA": 0.3},
        D3: {"ALVENARIA": 8, "ELÉTRICA": 0.3, "GESSO E ILUMINAÇÃO": 0.3, "HIDRÁULICA E GÁS": 0.3,
             "MARMORARIA": 0.3, "REVESTIMENTO": 0.3, "MOBILIÁRIO FIXO": 0.3, "MOBILIÁRIO SOLTO": 0.3,
             "COBERTURA": 0.3},
    },
    80: {
        IN_LOCO: {"ALVENARIA": 9, "ELÉTRICA": 0.45, "GESSO": 0.45, "ILUMINAÇÃO": 0.45, "HIDRÁULICA E GÁS": 0.45,
                  "MARMORARIA": 0.45, "REVESTIMENTO": 0.45, "MOBILIÁRIO FIXO": 0.45, "MOBILIÁRIO SOLTO": 0.45,
                  "SITUAÇÃO": 0.45, "FACHADAS": 1.8, "CORTES": 0.9, "COBERTURA": 0.45,
                  "LEVANTAMENTO FOTOGRÁFICO": 0.45},
        D2: {"ALVENARIA": 3.5, "ELÉTRICA": 0.25, "GESSO": 0.25, "ILUMINAÇÃO": 0.25, "HIDRÁULICA E GÁS": 0.25,
             "MARMORARIA": 0.25, "REVESTIMENTO": 0.25, "MOBILIÁRIO FIXO": 0.25, "MOBILIÁRIO SOLTO": 0.25,
             "SITUAÇÃO": 0.25, "FACHADAS": 0.8, "CORTES": 0.25, "COBERTURA": 0.2},
        D3: {"ALVENARIA": 7.5, "ELÉTRICA": 0.25, "GESSO E ILUMINAÇÃO": 0.25, "HIDRÁULICA E GÁS": 0.25,
             "MARMORARIA": 0.25, "REVESTIMENTO": 0.25, "MOBILIÁRIO FIXO": 0.25, "MOBILIÁRIO SOLTO": 0.25,
             "COBERTURA": 0.25},
    },
    100: {
        IN_LOCO: {"ALVENARIA": 8, "ELÉTRICA": 0.4, "GESSO": 0.4, "ILUMINAÇÃO": 0.4, "HIDRÁULICA E GÁS": 0.4,
                  "MARMORARIA": 0.4, "REVESTIMENTO": 0.4, "MOBILIÁRIO FIXO": 0.4, "MOBILIÁRIO SOLTO": 0.4,
                  "SITUAÇÃO": 0.4, "FACHADAS": 1.6, "CORTES": 0.8, "COBERTURA": 0.4, "LEVANTAMENTO FOTOGRÁFICO": 0.4},
        D2: {"ALVENARIA": 3.25, "ELÉTRICA": 0.25, "GESSO": 0.25, "ILUMINAÇÃO": 0.25, "HIDRÁULICA E GÁS": 0.25,
             "MARMORARIA": 0.25, "REVESTIMENTO": 0.25, "MOBILIÁRIO FIXO": 0.25, "MOBILIÁRIO SOLTO": 0.25,
             "SITUAÇÃO": 0.25, "FACHADAS": 1, "CORTES": 0.5, "COBERTURA": 0.25},
        D3: {"ALVENARIA": 7, "ELÉTRICA": 0.25, "GESSO E ILUMINAÇÃO": 0.25, "HIDRÁULICA E GÁS": 0.25,
             "MARMORARIA": 0.25, "REVESTIMENTO": 0.25, "MOBILIÁRIO FIXO": 0.25, "MOBILIÁRIO SOLTO": 0.25,
             "COBERTURA": 0.25},
    },
    200: {
        IN_LOCO: {"ALVENARIA": 6, "ELÉTRICA": 0.35, "GESSO": 0.35, "ILUMINAÇÃO": 0.35, "HIDRÁULICA E GÁS": 0.35,
                  "MARMORARIA": 0.35, "REVESTIMENTO": 0.35, "MOBILIÁRIO FIXO": 0.35, "MOBILIÁRIO SOLTO": 0.35,
                  "SITUAÇÃO": 0.35, "FACHADAS": 1.4, "CORTES": 0.9, "COBERTURA": 0.45,
                  "LEVANTAMENTO FOTOGRÁFICO": 0.45},
        D2: {"ALVENARIA": 3, "ELÉTRICA": 0.2, "GESSO": 0.2, "ILUMINAÇÃO": 0.2, "HIDRÁULICA E GÁS": 0.2,
             "MARMORARIA": 0.2, "REVESTIMENTO": 0.2, "MOBILIÁRIO FIXO": 0.2, "MOBILIÁRIO SOLTO": 0.2,
             "SITUAÇÃO": 0.2, "FACHADAS": 0.8, "CORTES": 0.4, "COBERTURA": 0.2},
        D3: {"ALVENARIA": 6, "ELÉTRICA": 0.2, "GESSO E ILUMINAÇÃO": 0.2, "HIDRÁULICA E GÁS": 0.2,
             "MARMORARIA": 0.2, "REVESTIMENTO": 0.2, "MOBILIÁRIO FIXO": 0.2, "MOBILIÁRIO SOLTO": 0.2,
             "COBERTURA": 0.2},
    },
    500: {
        IN_LOCO: {"ALVENARIA": 3.2, "ELÉTRICA": 0.3, "GESSO": 0.3, "ILUMINAÇÃO": 0.3, "HIDRÁULICA E GÁS": 0.3,
                  "MARMORARIA": 0.3, "REVESTIMENTO": 0.3, "MOBILIÁRIO FIXO": 0.3, "MOBILIÁRIO SOLTO": 0.3,
                  "SITUAÇÃO": 0.3, "FACHADAS": 1.2, "CORTES": 0.6, "COBERTURA": 0.3, "LEVANTAMENTO FOTOGRÁFICO": 0.3},
        D2: {"ALVENARIA": 1.8, "ELÉTRICA": 0.12, "GESSO": 0.12, "ILUMINAÇÃO": 0.12, "HIDRÁULICA E GÁS": 0.12,
             "MARMORARIA": 0.12, "REVESTIMENTO": 0.12, "MOBILIÁRIO FIXO": 0.12, "MOBILIÁRIO SOLTO": 0.12,
             "SITUAÇÃO": 0.12, "FACHADAS": 0.48, "CORTES": 0.24, "COBERTURA": 0.12},
        D3: {"ALVENARIA": 3, "ELÉTRICA": 0.1, "GESSO E ILUMINAÇÃO": 0.1, "HIDRÁULICA E GÁS": 0.1,
             "MARMORARIA": 0.1, "REVESTIMENTO": 0.1, "MOBILIÁRIO FIXO": 0.1, "MOBILIÁRIO SOLTO": 0.1,
             "COBERTURA": 0.1},
    },
    1000: {
        IN_LOCO: {"ALVENARIA": 2, "ELÉTRICA": 0.15, "GESSO": 0.15, "ILUMINAÇÃO": 0.15, "HIDRÁULICA E GÁS": 0.15,
                  "MARMORARIA": 0.15, "REVESTIMENTO": 0.15, "MOBILIÁRIO FIXO": 0.15, "MOBILIÁRIO SOLTO": 0.15,
                  "SITUAÇÃO": 0.15, "FACHADAS": 0.6, "CORTES": 0.3, "COBERTURA": 0.15,
                  "LEVANTAMENTO FOTOGRÁFICO": 0.15},
        D2: {"ALVENARIA": 0.9, "ELÉTRICA": 0.1, "GESSO": 0.1, "ILUMINAÇÃO": 0.1, "HIDRÁULICA E GÁS": 0.1,
             "MARMORARIA": 0.1, "REVESTIMENTO": 0.1, "MOBILIÁRIO FIXO": 0.1, "MOBILIÁRIO SOLTO": 0.1,
             "SITUAÇÃO": 0.1, "FACHADAS": 0.4, "CORTES": 0.2, "COBERTURA": 0.1},
        D3: {"ALVENARIA": 1.5, "ELÉTRICA": 0.05, "GESSO E ILUMINAÇÃO": 0.05, "HIDRÁULICA E GÁS": 0.05,
             "MARMORARIA": 0.05, "REVESTIMENTO": 0.05, "MOBILIÁRIO FIXO": 0.05, "MOBILIÁRIO SOLTO": 0.05,
             "COBERTURA": 0.05},
    },
}

# Lista de itens de cada bloco (na ordem da planilha)
ITENS = {bloco: list(TABELA[50][bloco].keys()) for bloco in BLOCOS}

# ---------------------------------------------------------------------------
# PACOTES PRONTOS (pré-selecionam os itens; tudo pode ser ajustado depois)
# ---------------------------------------------------------------------------
_BASE_2D = ["ALVENARIA", "ELÉTRICA", "GESSO", "ILUMINAÇÃO", "HIDRÁULICA E GÁS",
            "MARMORARIA", "REVESTIMENTO", "MOBILIÁRIO FIXO"]
_BASE_3D = ["ALVENARIA", "ELÉTRICA", "GESSO E ILUMINAÇÃO", "REVESTIMENTO",
            "MOBILIÁRIO FIXO", "MOBILIÁRIO SOLTO"]
_INLOCO_3D = ["ALVENARIA", "ELÉTRICA", "GESSO", "ILUMINAÇÃO", "REVESTIMENTO",
              "MOBILIÁRIO FIXO", "MOBILIÁRIO SOLTO", "LEVANTAMENTO FOTOGRÁFICO"]

PACOTES = {
    "Levantamento 2D Completo": {
        IN_LOCO: _BASE_2D + ["LEVANTAMENTO FOTOGRÁFICO"],
        D2: _BASE_2D,
        D3: [],
    },
    "Levantamento 3D Completo": {
        IN_LOCO: _INLOCO_3D,
        D2: [],
        D3: _BASE_3D,
    },
    "Levantamento 2D + 3D": {
        IN_LOCO: sorted(set(_BASE_2D + _INLOCO_3D), key=ITENS[IN_LOCO].index),
        D2: _BASE_2D,
        D3: _BASE_3D,
    },
    "Maquete 3D (a partir de planta e fotos)": {
        IN_LOCO: [],
        D2: [],
        D3: ["ALVENARIA", "ELÉTRICA", "GESSO E ILUMINAÇÃO", "REVESTIMENTO", "MOBILIÁRIO FIXO"],
    },
    "Somente Levantamento in loco": {
        IN_LOCO: _BASE_2D + ["LEVANTAMENTO FOTOGRÁFICO"],
        D2: [],
        D3: [],
    },
    "Personalizado (marcar manualmente)": {IN_LOCO: [], D2: [], D3: []},
}

# ---------------------------------------------------------------------------
# TEXTOS DA PÁGINA "ITENS DE ENTREGA" DO PDF
# ---------------------------------------------------------------------------
DESCRICAO_2D = {
    "ALVENARIA": ("PLANTA BAIXA", "Esta planta deverá conter todos os elementos construtivos presentes no projeto."),
    "ELÉTRICA": ("PLANTA DE PONTOS ELÉTRICOS", "Esta planta deverá conter todos os tipos de pontos elétricos presentes no projeto."),
    "GESSO": ("PLANTA DE GESSO", "Esta planta deverá conter todos os tipos de detalhes feitos no gesso."),
    "ILUMINAÇÃO": ("PLANTA DE ILUMINAÇÃO", "Esta planta deverá conter todos os tipos de luminárias presentes no projeto."),
    "HIDRÁULICA E GÁS": ("PLANTA DE HIDRÁULICA, GÁS E BACIAS SANITÁRIAS", "Esta planta deverá conter os pontos hidráulicos, de gás e todos os tipos de bacias sanitárias presentes no projeto."),
    "MARMORARIA": ("PLANTA DE MARMORARIA", "Esta planta deverá conter todas as pedras presentes no projeto."),
    "REVESTIMENTO": ("PLANTA DE REVESTIMENTOS", "Esta planta deverá conter todos os revestimentos aplicados no projeto. Dimensionamento do revestimento (piso) hachurado com cor aproximada; indicação de revestimentos de piso, parede e teto."),
    "MOBILIÁRIO FIXO": ("PLANTA DE MOBILIÁRIO FIXO", "Esta planta deverá conter os mobiliários fixos que o contratante selecionou previamente."),
    "MOBILIÁRIO SOLTO": ("PLANTA DE MOBILIÁRIO SOLTO", "Esta planta deverá conter os mobiliários soltos presentes no imóvel."),
    "SITUAÇÃO": ("PLANTA DE SITUAÇÃO", "Implantação do imóvel em relação ao terreno e ao entorno."),
    "FACHADAS": ("FACHADAS", "Vistas das fachadas com aberturas, elementos e alturas."),
    "CORTES": ("CORTES", "Cortes com pés-direitos, níveis e alturas relevantes."),
    "COBERTURA": ("PLANTA DE COBERTURA", "Telhados, lajes, caimentos e demais elementos da cobertura."),
}

DESCRICAO_3D = {
    "ALVENARIA": ("ALVENARIA E ESQUADRIAS", "Paredes, vãos, portas e janelas modelados em 3D."),
    "ELÉTRICA": ("PONTOS ELÉTRICOS", "Deverá conter todos os tipos de pontos elétricos presentes no projeto."),
    "GESSO E ILUMINAÇÃO": ("GESSO E PONTOS DE ILUMINAÇÃO", "Deverá conter todos os detalhes feitos no gesso e todos os tipos de luminárias presentes no projeto."),
    "HIDRÁULICA E GÁS": ("PONTOS HIDRÁULICOS E DE GÁS", "Deverá conter os pontos hidráulicos e de gás presentes no projeto."),
    "MARMORARIA": ("MARMORARIA", "Deverá conter todas as pedras presentes no projeto."),
    "REVESTIMENTO": ("REVESTIMENTOS", "Deverá conter todo tipo de revestimentos presentes no projeto."),
    "MOBILIÁRIO FIXO": ("MOBILIÁRIO FIXO (MARCENARIA)", "Conterá todos os mobiliários fixos aplicados no projeto."),
    "MOBILIÁRIO SOLTO": ("MEMORIAL DESCRITIVO DE MOBILIÁRIO SOLTO", "Este memorial deverá conter todos os mobiliários soltos presentes no projeto."),
    "COBERTURA": ("COBERTURA", "Modelagem da cobertura, telhados e lajes."),
}

DESCRICAO_IN_LOCO = {
    "LEVANTAMENTO FOTOGRÁFICO": ("LEVANTAMENTO FOTOGRÁFICO", "Entregaremos todas as mídias feitas no projeto."),
}

# Item de in loco que já aparece representado num bloco digital
_EQUIVALENTE_3D = {"GESSO": "GESSO E ILUMINAÇÃO", "ILUMINAÇÃO": "GESSO E ILUMINAÇÃO"}


# ---------------------------------------------------------------------------
# CÁLCULO
# ---------------------------------------------------------------------------
def faixa_para(metragem: float) -> int:
    """Retorna a faixa ('Até X m²') correspondente à metragem."""
    for f in FAIXAS:
        if metragem <= f:
            return f
    return FAIXAS[-1]


def calcular(metragem: float, faixa: int, selecao: dict, desconto_pct: float = 0.0,
             nota_pct: float = 0.0) -> dict:
    """
    selecao = {bloco: [itens marcados]}
    Regra da planilha: valor de cada etapa = R$/m² x m²; total = soma das etapas.
    Depois aplica desconto (opcional) e acrescenta Juros Nota (opcional).
    """
    tabela = TABELA[faixa]
    linhas, subtotais = [], {}
    for bloco in BLOCOS:
        soma = 0.0
        for item in selecao.get(bloco, []):
            taxa = tabela[bloco][item]
            valor = taxa * metragem
            soma += valor
            linhas.append({"bloco": bloco, "item": item, "taxa": taxa, "valor": valor})
        subtotais[bloco] = soma
    total = sum(subtotais.values())
    desconto = total * desconto_pct / 100
    base = total - desconto
    nota = base * nota_pct / 100
    return {
        "linhas": linhas,
        "subtotais": subtotais,
        "total_levantamento": total,
        "desconto": desconto,
        "nota": nota,
        "valor_final": base + nota,
        "taxa_m2": (base + nota) / metragem if metragem else 0,
    }


def tipo_servico(selecao: dict) -> str:
    """Título do serviço usado na capa, no nome do arquivo e no WhatsApp."""
    tem_loco, tem_2d, tem_3d = (bool(selecao.get(b)) for b in BLOCOS)
    if tem_2d and tem_3d:
        return "LEVANTAMENTO 2D + 3D"
    if tem_2d:
        return "LEVANTAMENTO 2D"
    if tem_3d and tem_loco:
        return "LEVANTAMENTO 3D"
    if tem_3d:
        return "MAQUETE 3D"
    if tem_loco:
        return "LEVANTAMENTO IN LOCO"
    return "LEVANTAMENTO"


def itens_de_entrega(selecao: dict) -> list:
    """
    Monta as seções da página 'Itens de entrega':
    [(titulo_secao, [(titulo_item, descricao), ...]), ...]
    """
    secoes = []
    loco = selecao.get(IN_LOCO, [])
    d2 = selecao.get(D2, [])
    d3 = selecao.get(D3, [])

    if d2:
        secoes.append(("LEVANTAMENTO DIGITAL 2D (AUTOCAD)", [DESCRICAO_2D[i] for i in d2]))
    if d3:
        secoes.append(("MAQUETE EM 3D NO SOFTWARE SKETCHUP", [DESCRICAO_3D[i] for i in d3]))

    # Itens medidos in loco que não aparecem em nenhum bloco digital
    cobertos = set(d2) | set(d3) | {k for k, v in _EQUIVALENTE_3D.items() if v in d3}
    extras = [i for i in loco if i not in cobertos and i != "LEVANTAMENTO FOTOGRÁFICO"]
    if extras:
        titulo = "LEVANTAMENTO IN LOCO" if not (d2 or d3) else "MEDIÇÕES COMPLEMENTARES IN LOCO"
        secoes.append((titulo, [(i, f"Medição e registro in loco de {i.lower()}.") for i in extras]))

    if "LEVANTAMENTO FOTOGRÁFICO" in loco:
        secoes.append((None, [DESCRICAO_IN_LOCO["LEVANTAMENTO FOTOGRÁFICO"]]))
    return secoes


def brl(valor: float) -> str:
    """Formata número como moeda brasileira: 1234.5 -> 'R$ 1.234,50'."""
    s = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"


def fmt_m2(m: float) -> str:
    return f"{int(m)}" if float(m).is_integer() else f"{m:.2f}".replace(".", ",")
