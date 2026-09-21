# Gerador de Orçamentos — Scale Levantamentos

App web (feito para celular) que calcula o orçamento pela tabela de preços da Scale,
gera a proposta em PDF no mesmo visual das propostas do Canva e monta a mensagem
pronta para o WhatsApp.

## Arquivos

```
app.py                  → a tela do app
precos.py               → TABELA DE PREÇOS, pacotes e textos (edite aqui para reajustar)
proposta_pdf.py         → monta o PDF
assets/paginas_base.pdf → páginas originais das propostas (missão, processo, contato...)
assets/logo.png         → logo usada no topo do app
assets/fonts/           → (opcional) fonte Montserrat
.streamlit/config.toml  → cores do app (marrom/bege)
requirements.txt        → bibliotecas que o Streamlit Cloud instala
```

## Publicar no Streamlit Community Cloud (gratuito)

**1. Crie uma conta no GitHub** em https://github.com (se ainda não tiver).

**2. Crie um repositório**
- Clique em **New repository**, dê um nome (ex.: `orcamentos-scale`).
- Recomendo marcar **Private**, para que sua tabela de preços não fique pública.
- Clique em **Create repository**.

**3. Envie os arquivos**
- No repositório, clique em **Add file → Upload files**.
- Descompacte o `.zip` no computador e arraste **todo o conteúdo** da pasta
  (arquivos `.py`, `requirements.txt` e as pastas `assets` e `.streamlit`).
- Clique em **Commit changes**.
- No Mac, a pasta `.streamlit` fica oculta: aperte `Cmd + Shift + .` no Finder para vê-la.
  Se ela não subir, o app funciona igual, só que com as cores padrão.

**4. Publique**
- Acesse https://share.streamlit.io e entre com sua conta do GitHub.
- Clique em **Create app → Deploy a public app from GitHub** (ou equivalente).
- Escolha o repositório, branch `main` e arquivo principal `app.py`.
- Em **App URL**, escolha um endereço fácil, ex.: `orcamentos-scale`.
- Clique em **Deploy**. Em 2–3 minutos o app fica no ar em
  `https://orcamentos-scale.streamlit.app`.
- Se o repositório for privado, o app também fica privado: em **Share**, adicione o
  e-mail de quem pode acessar (você e sua sócia).

**5. No celular**
- Abra o link no navegador e use **Adicionar à tela inicial** (Safari: botão Compartilhar;
  Chrome: menu ⋮). Ele passa a abrir como um aplicativo.
- Apps gratuitos "dormem" depois de alguns dias sem uso. Se aparecer a tela de
  "app is asleep", toque no botão para acordar e aguarde cerca de 1 minuto.

## Como usar

1. Preencha cliente, local e metragem (a faixa de preço é escolhida sozinha).
2. Escolha um pacote pronto e ajuste os itens se precisar.
3. Confira desconto, juros de nota (6% por padrão, como na planilha) e, se quiser,
   defina o valor final manualmente para arredondar.
4. Toque em **Gerar proposta em PDF** → **Baixar PDF**.
5. Toque em **Abrir no WhatsApp**, confira a mensagem e anexe o PDF baixado.

## Reajustar preços

Abra `precos.py` no GitHub, clique no lápis (✏️), altere os valores de R$/m² da faixa
desejada e clique em **Commit changes**. O app se atualiza sozinho em cerca de 1 minuto.
Os pacotes prontos (`PACOTES`) e os textos da página "Itens de entrega" também ficam
nesse arquivo.

## Fonte do PDF

As propostas usam a fonte **Montserrat**. Na primeira geração de PDF o app tenta baixá-la
automaticamente. Para garantir, baixe em https://fonts.google.com/specimen/Montserrat e
coloque na pasta `assets/fonts/` os arquivos `Montserrat-Light.ttf`, `Montserrat-Regular.ttf`,
`Montserrat-Bold.ttf`, `Montserrat-BoldItalic.ttf` e `Montserrat-LightItalic.ttf`
(ficam na pasta `static` do .zip).

## Rodar no computador (opcional)

```
pip install -r requirements.txt
streamlit run app.py
```
