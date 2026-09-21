"""
Gerador de Orçamentos — Scale Levantamentos
Rode localmente com:  streamlit run app.py
"""
import base64
import hashlib
import json
import os
import re
import urllib.parse

import streamlit as st

import precos as pr
from proposta_pdf import gerar_proposta, usando_montserrat

PASTA = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(page_title="Orçamentos Scale", page_icon="📐", layout="centered")

# ---------------------------------------------------------------------------
# Estilo (identidade Scale: marrom #6F3F30 e bege #E8E5DC)
# ---------------------------------------------------------------------------
with open(os.path.join(PASTA, "assets", "logo.png"), "rb") as f:
    LOGO_B64 = base64.b64encode(f.read()).decode()

st.markdown(f"""
<style>
  .block-container {{ padding-top: 4rem; padding-bottom: 4rem; max-width: 720px; }}
  .scale-topo {{ background:#6F3F30; border-radius:14px; padding:18px 20px; margin-bottom:14px;
                 display:flex; align-items:center; gap:16px; }}
  .scale-topo img {{ height:54px; }}
  .scale-topo div {{ color:#fff; font-size:0.95rem; letter-spacing:.08em; line-height:1.3; }}
  .scale-total {{ background:#6F3F30; color:#fff; border-radius:14px; padding:18px 20px; margin:6px 0 10px; }}
  .scale-total .rot {{ font-size:.8rem; letter-spacing:.15em; opacity:.85; }}
  .scale-total .val {{ font-size:2.1rem; font-weight:700; margin-top:2px; }}
  .scale-total .sub {{ font-size:.85rem; opacity:.85; margin-top:4px; }}
  .scale-linha {{ display:flex; justify-content:space-between; gap:10px; padding:6px 2px;
                  border-bottom:1px solid #E8E5DC; font-size:.95rem; }}
  h3 {{ color:#6F3F30; margin-top:1.2rem !important; }}
  div[data-testid="stExpander"] summary p {{ font-weight:600; }}
  .stButton button, .stDownloadButton button, .stLinkButton a {{ width:100%; min-height:3rem; font-weight:600; }}
</style>
<div class="scale-topo">
  <img src="data:image/png;base64,{LOGO_B64}">
  <div>GERADOR DE<br>ORÇAMENTOS</div>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Estado dos checkboxes / pacotes
# ---------------------------------------------------------------------------
PERSONALIZADO = "Personalizado (marcar manualmente)"


def chave(bloco, item):
    return f"chk|{bloco}|{item}"


def aplicar_pacote():
    pacote = st.session_state["pacote"]
    if pacote == PERSONALIZADO:
        return
    for bloco in pr.BLOCOS:
        for item in pr.ITENS[bloco]:
            st.session_state[chave(bloco, item)] = item in pr.PACOTES[pacote][bloco]


def marcar_bloco(bloco, valor):
    for item in pr.ITENS[bloco]:
        st.session_state[chave(bloco, item)] = valor
    st.session_state["pacote"] = PERSONALIZADO


def virou_personalizado():
    st.session_state["pacote"] = PERSONALIZADO


if "iniciado" not in st.session_state:
    st.session_state["pacote"] = "Levantamento 2D Completo"
    aplicar_pacote()
    st.session_state["iniciado"] = True

# ---------------------------------------------------------------------------
# 1. Cliente
# ---------------------------------------------------------------------------
st.markdown("### 1. Cliente e imóvel")
cliente = st.text_input("Cliente / empresa contratante", placeholder="Ex.: Quinta Arquitetura")
local = st.text_input("Local a ser medido", placeholder="Ex.: Apartamento Ipanema")
metragem = st.number_input("Metragem total (m²)", min_value=0.0, value=None, step=1.0,
                           placeholder="Ex.: 85", format="%.2f")
mostrar_m2_capa = st.checkbox("Mostrar metragem na capa do PDF", value=True)
telefone = st.text_input("WhatsApp do cliente (opcional)", placeholder="(21) 99999-9999")

m = float(metragem or 0)
faixa_auto = pr.faixa_para(m) if m else pr.FAIXAS[0]
opcoes_faixa = ["Automática"] + [f"Até {f} m²" for f in pr.FAIXAS]
escolha_faixa = st.selectbox("Faixa de preço", opcoes_faixa,
                             help="Automática escolhe a faixa pela metragem. Troque só se quiser forçar outra tabela.")
faixa = faixa_auto if escolha_faixa == "Automática" else int(re.findall(r"\d+", escolha_faixa)[0])
if m > pr.FAIXAS[-1] and escolha_faixa == "Automática":
    st.info("Metragem acima de 1.000 m²: usando a tabela 'Até 1000 m²'.")
st.caption(f"Tabela aplicada: **Até {faixa} m²**")

# ---------------------------------------------------------------------------
# 2. Serviços
# ---------------------------------------------------------------------------
st.markdown("### 2. Serviços")
st.selectbox("Pacote pronto", list(pr.PACOTES.keys()), key="pacote", on_change=aplicar_pacote,
             help="O pacote pré-marca os itens. Você pode ajustar item a item abaixo.")

selecao = {}
for bloco in pr.BLOCOS:
    tabela = pr.TABELA[faixa][bloco]
    marcados = [i for i in pr.ITENS[bloco] if st.session_state.get(chave(bloco, i))]
    subtotal = sum(tabela[i] for i in marcados) * m
    rotulo = f"{pr.ROTULO_BLOCO[bloco]} — {len(marcados)} itens · {pr.brl(subtotal)}"
    with st.expander(rotulo, expanded=False):
        c1, c2 = st.columns(2)
        c1.button("Marcar todos", key=f"todos|{bloco}", on_click=marcar_bloco, args=(bloco, True))
        c2.button("Limpar", key=f"limpar|{bloco}", on_click=marcar_bloco, args=(bloco, False))
        for item in pr.ITENS[bloco]:
            st.checkbox(f"{item.capitalize()} · {pr.brl(tabela[item])}/m²", key=chave(bloco, item),
                        on_change=virou_personalizado)
    selecao[bloco] = [i for i in pr.ITENS[bloco] if st.session_state.get(chave(bloco, i))]

tipo = pr.tipo_servico(selecao)
tem_loco = bool(selecao[pr.IN_LOCO])

# ---------------------------------------------------------------------------
# 3. Ajustes de valor
# ---------------------------------------------------------------------------
st.markdown("### 3. Ajustes de valor")
desconto_pct = st.number_input("Desconto (%)", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
col_a, col_b = st.columns(2)
usar_nota = col_a.toggle("Juros nota fiscal", value=True)
nota_pct = col_b.number_input("% nota", min_value=0.0, max_value=50.0, value=pr.PERCENTUAL_NOTA_PADRAO,
                              step=0.5, disabled=not usar_nota)
calc = pr.calcular(m, faixa, selecao, desconto_pct, nota_pct if usar_nota else 0.0)

usar_manual = st.toggle("Definir valor final manualmente", value=False,
                        help="Use para arredondar ou negociar. O PDF e o WhatsApp usam este valor.")
valor_final = calc["valor_final"]
if usar_manual:
    valor_final = st.number_input("Valor final (R$)", min_value=0.0, value=round(calc["valor_final"], 2), step=10.0)

# ---------------------------------------------------------------------------
# 4. Prazo e pagamento
# ---------------------------------------------------------------------------
st.markdown("### 4. Prazo e pagamento")
c1, c2 = st.columns(2)
dias_entrega = c1.number_input("Entrega (dias úteis)", min_value=1, max_value=90,
                               value=5 if tipo == "MAQUETE 3D" else 7, step=1)
dias_inloco = c2.number_input("Dias de visita in loco", min_value=0, max_value=30,
                              value=1 if tem_loco else 0, step=1, disabled=not tem_loco)

pag_5050 = st.checkbox("50% na contratação + 50% na entrega", value=True)
pag_cartao = st.checkbox("Cartão de crédito", value=True)
parcelas = 12
if pag_cartao:
    parcelas = st.slider("Parcelamento em até", 1, 12, 12, format="%dx")
incluir_itens = st.checkbox("Incluir página 'Itens de entrega' no PDF", value=True)

pagamentos = []
if pag_5050:
    pagamentos.append(("Contratação + entrega", ["50% na contratação e 50% na entrega do levantamento"]))
if pag_cartao:
    txt = "Pagamento à vista no cartão." if parcelas == 1 else f"Parcelamento em até {parcelas}x."
    pagamentos.append(("Cartão de crédito", [txt, "*O pagamento deverá ser efetuado integralmente na contratação."]))

# ---------------------------------------------------------------------------
# 5. Resultado
# ---------------------------------------------------------------------------
st.markdown("### 5. Orçamento")
st.markdown(f"""
<div class="scale-total">
  <div class="rot">VALOR DO INVESTIMENTO · {tipo}</div>
  <div class="val">{pr.brl(valor_final)}</div>
  <div class="sub">{pr.fmt_m2(m)} m² · tabela até {faixa} m² · {pr.brl(valor_final / m if m else 0)}/m²</div>
</div>
""", unsafe_allow_html=True)

with st.expander("Ver composição do valor"):
    html = ""
    for bloco in pr.BLOCOS:
        if calc["subtotais"][bloco]:
            html += f'<div class="scale-linha"><span>{pr.ROTULO_BLOCO[bloco]}</span><b>{pr.brl(calc["subtotais"][bloco])}</b></div>'
    html += f'<div class="scale-linha"><span>Total do levantamento</span><b>{pr.brl(calc["total_levantamento"])}</b></div>'
    if calc["desconto"]:
        html += f'<div class="scale-linha"><span>Desconto ({desconto_pct:g}%)</span><b>− {pr.brl(calc["desconto"])}</b></div>'
    if calc["nota"]:
        html += f'<div class="scale-linha"><span>Juros nota ({nota_pct:g}%)</span><b>+ {pr.brl(calc["nota"])}</b></div>'
    if usar_manual:
        html += f'<div class="scale-linha"><span>Valor calculado (antes do ajuste manual)</span><b>{pr.brl(calc["valor_final"])}</b></div>'
    st.markdown(html, unsafe_allow_html=True)
    for bloco in pr.BLOCOS:
        itens_b = [l for l in calc["linhas"] if l["bloco"] == bloco]
        if itens_b:
            st.caption(pr.ROTULO_BLOCO[bloco].upper())
            st.markdown("".join(
                f'<div class="scale-linha"><span>{l["item"].capitalize()} '
                f'<small>({pr.brl(l["taxa"])} × {pr.fmt_m2(m)} m²)</small></span>'
                f'<span>{pr.brl(l["valor"])}</span></div>' for l in itens_b), unsafe_allow_html=True)

# Validação
problemas = []
if not cliente.strip():
    problemas.append("preencha o nome do cliente")
if not local.strip():
    problemas.append("preencha o local a ser medido")
if m <= 0:
    problemas.append("informe a metragem")
if not any(selecao.values()):
    problemas.append("selecione pelo menos um serviço")
if not pagamentos:
    problemas.append("escolha pelo menos uma forma de pagamento")

if problemas:
    st.warning("Para gerar a proposta: " + "; ".join(problemas) + ".")
    st.stop()

# ---------------------------------------------------------------------------
# 6. PDF
# ---------------------------------------------------------------------------
local_capa = f"{local.strip()} - {pr.fmt_m2(m)}M²" if mostrar_m2_capa else local.strip()
valor_txt = pr.brl(valor_final)
parametros = dict(tipo=tipo, cliente=cliente.strip(), local=local_capa, selecao=selecao, valor_txt=valor_txt,
                  dias_entrega=int(dias_entrega), dias_inloco=int(dias_inloco), pagamentos=pagamentos,
                  incluir_itens=incluir_itens)
assinatura = hashlib.md5(json.dumps(parametros, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

st.markdown("### 6. Enviar")
if st.button("📄 Gerar proposta em PDF", type="primary"):
    with st.spinner("Montando a proposta..."):
        st.session_state["pdf"] = gerar_proposta(**parametros)
        st.session_state["pdf_assinatura"] = assinatura

if st.session_state.get("pdf") and st.session_state.get("pdf_assinatura") == assinatura:
    nome_arquivo = re.sub(r'[\\/:*?"<>|]', "", f"PROPOSTA {tipo} - {cliente.strip().upper()}.pdf")
    st.download_button("⬇️ Baixar PDF", data=st.session_state["pdf"], file_name=nome_arquivo,
                       mime="application/pdf")
elif st.session_state.get("pdf"):
    st.caption("Os dados mudaram. Toque em **Gerar proposta em PDF** de novo para atualizar.")


# ---------------------------------------------------------------------------
# 7. WhatsApp
# ---------------------------------------------------------------------------
def montar_mensagem():
    primeiro = cliente.strip().split()[0].capitalize()
    titulo = tipo.title().replace("In Loco", "in loco")
    linhas = [
        f"Olá, {primeiro}! Tudo bem?",
        "",
        f"Segue o orçamento da *Scale Levantamentos* para o *{titulo}*:",
        "",
        f"📍 *Local:* {local.strip()}",
        f"📐 *Metragem:* {pr.fmt_m2(m)} m²",
        "",
        "*Escopo:*",
    ]
    for bloco in pr.BLOCOS:
        if selecao[bloco]:
            linhas.append(f"• {pr.ROTULO_BLOCO[bloco]}: " + ", ".join(i.lower() for i in selecao[bloco]))
    linhas.append("")
    if tem_loco:
        visita = f" (necessário {dias_inloco} dia{'s' if dias_inloco > 1 else ''} de visita)" if dias_inloco else ""
        linhas.append(f"⏱️ *Prazo:* {dias_entrega} dias úteis após o levantamento in loco{visita}")
    else:
        linhas.append(f"⏱️ *Prazo:* {dias_entrega} dias úteis após o recebimento da planta e fotos")
    linhas += [f"💰 *Investimento:* {valor_txt}", "", "*Formas de pagamento:*"]
    if pag_5050:
        linhas.append("• 50% na contratação e 50% na entrega")
    if pag_cartao:
        linhas.append("• Cartão de crédito à vista" if parcelas == 1
                      else f"• Cartão de crédito em até {parcelas}x (pagamento integral na contratação)")
    linhas += [
        "",
        "A entrega é 100% digital, em uma pasta no Google Drive. A proposta completa em PDF segue em anexo.",
        "",
        "Fico à disposição para qualquer dúvida!",
        "*Scale Levantamentos* · @scalevantamentos",
    ]
    return "\n".join(linhas)


mensagem = st.text_area("Mensagem do WhatsApp (pode editar antes de enviar)", value=montar_mensagem(), height=320)

digitos = re.sub(r"\D", "", telefone)
if len(digitos) in (10, 11):
    digitos = "55" + digitos
url_wa = f"https://wa.me/{digitos}?text={urllib.parse.quote(mensagem)}"
st.link_button("💬 Abrir no WhatsApp", url_wa, type="primary")
st.caption("O WhatsApp não permite anexar arquivos por link: baixe o PDF acima e anexe na conversa. "
           "Sem número preenchido, o WhatsApp pede para você escolher o contato.")

if not usando_montserrat():
    st.caption("⚠️ PDF usando fonte reserva (Helvetica). Veja o README para instalar a Montserrat.")
