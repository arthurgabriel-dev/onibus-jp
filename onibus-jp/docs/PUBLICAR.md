# Como publicar (GitHub Pages, grátis)

O site é estático: basta enviar os arquivos para um repositório público e ativar o GitHub Pages. Ele fica no ar o tempo todo, sem precisar de servidor seu.

## 1. Criar o repositório

1. Entre em <https://github.com/new>.
2. **Repository name:** `onibus-jp`.
3. **Description:** `Qual ônibus pegar em João Pessoa: linhas, onde subir e onde descer.`
4. Marque **Public**.
5. **Não** marque "Add a README", ".gitignore" nem "license": o projeto já tem os seus.
6. Clique em **Create repository**.

## 2. Enviar os arquivos

1. Descompacte o `.zip` e abra a pasta `onibus-jp`.
2. Na página do repositório vazio, clique em **uploading an existing file**.
3. Selecione **tudo o que está dentro** da pasta `onibus-jp` (arquivos e subpastas, não a pasta em si) e arraste para a janela do navegador.
4. Espere terminar de enviar (aparece a lista de arquivos), escreva em *Commit message*: `Primeira versão` e clique em **Commit changes**.

Confira se na raiz do repositório aparecem `index.html`, `sobre.html`, `sw.js`, `manifest.webmanifest`, `dados-semob.js`, `README.md`, `LICENSE` e as pastas `icons`, `lib`, `dados`, `tools` e `docs`.

## 3. Ativar o site

1. No repositório: **Settings → Pages**.
2. Em **Build and deployment**, **Source: Deploy from a branch**.
3. **Branch:** `main`, pasta `/(root)`. Clique em **Save**.
4. Espere cerca de 1 minuto e atualize a página. O endereço do site aparece no topo:
   `https://arthurgabriel-dev.github.io/onibus-jp/`

## 4. Testar

- Abra o endereço no computador e no celular.
- Teste a busca ("Casa NuBus", "Mangabeira") e o botão **Onde estou**.
- Android: deve aparecer o botão **Instalar**. iPhone: Compartilhar → Adicionar à Tela de Início.

## 5. Deixar o repositório bonito

- Na página inicial do repositório, clique na engrenagem ao lado de **About** e preencha: descrição, **Website** (o endereço do site) e **Topics** (por exemplo `onibus`, `joao-pessoa`, `transporte-publico`, `pwa`, `leaflet`, `openstreetmap`).

## Atualizar depois

1. Troque os arquivos no GitHub (*Add file → Upload files*, ou edite pelo navegador).
2. Se mudou qualquer arquivo do app, aumente `VERSION` em `sw.js` (por exemplo `v2` para `v3`). Assim os celulares baixam a versão nova.
3. Em 1 minuto o site atualiza.
