# Ônibus JP

**Qual ônibus pegar em João Pessoa?** Diga de onde você sai e para onde vai. O site mostra as linhas que passam perto dos dois pontos, **onde subir**, **onde descer**, quanto andar a pé e os horários de saída do dia.

Funciona no navegador e pode ser **instalado no celular** como app (iPhone e Android), sem loja de aplicativos.

> **Projeto independente e gratuito, sem ligação com a Semob, a NuBus ou as empresas de ônibus.** Trajetos e horários vêm de dados públicos e podem estar desatualizados. Confira sempre no ponto.

## Objetivo

O projeto nasceu da insatisfação do autor com o aplicativo oficial do NuBus, que, na opinião dele, é cheio de anúncios e mostra as linhas, mas deixa o passageiro sem saber onde subir e onde descer. A ideia é ter uma alternativa simples, leve e gratuita. **Esta versão não tem anúncios.**

## Autor e contato

**Arthur Gabriel**, aluno de Ciência da Computação da UFPB.
Erros, paradas fora do lugar ou linhas que faltam: <gabrielarthurg81010@gmail.com> ou a aba *Issues* deste repositório.

## O que faz

- Sugestões enquanto você digita, com **tolerância a erros de digitação** e **pontos de referência** (bairros, universidades, hospitais, shoppings, terminais, comércio e serviços).
- Lugares conhecidos que o mapa livre não tem, como a Casa NuBus, são achados pelo endereço.
- Considera **todas as linhas** e mostra primeiro as de menor caminhada, na ordem certa de embarque e desembarque.
- Mostra as paradas próximas no mapa. Toque em uma para **subir ou descer nela**; dá para cadastrar paradas que faltam.
- **Aprende com o seu uso**: lembra lugares e trajetos recentes, oferece atalhos ("Casa → CI UFPB") e destaca as linhas que você costuma pegar.
- Botão "Onde estou" e "Marcar no mapa".

## Instalar no celular

- **Android (Chrome/Edge):** abra o site e toque em **Instalar** na faixa verde (ou menu ⋮ → *Instalar app*).
- **iPhone/iPad (Safari):** abra o site, toque em **Compartilhar** (quadrado com seta) → **Adicionar à Tela de Início**. O iOS não oferece botão de instalar; esse é o caminho oficial.

O app abre em tela cheia, com ícone próprio. Os arquivos ficam guardados no aparelho; o mapa, as buscas de endereço e a localização dos lugares precisam de internet.

## Publicar na internet (GitHub Pages, grátis)

1. Crie um repositório **vazio** no GitHub (por exemplo `onibus-jp`).
2. Envie **o conteúdo desta pasta** para a raiz do repositório (pelo site: *Add file → Upload files*; ou por `git`).
3. No repositório: **Settings → Pages → Build and deployment → Deploy from a branch → `main` / `(root)` → Save**.
4. Em cerca de 1 minuto o site abre em `https://SEU-USUARIO.github.io/onibus-jp/`. Esse endereço usa **https**, necessário para a localização e para instalar como app.

Ao publicar uma versão nova, aumente `VERSION` em `sw.js` para os celulares baixarem os arquivos novos.

## Rodar no seu computador

```bash
python3 -m http.server 8000
# abra http://localhost:8000
```

Abrir o `index.html` com dois cliques funciona, mas o navegador pode bloquear a localização e o mapa padrão.

## De onde vêm os dados

| Dado | Fonte | Licença / observação |
|---|---|---|
| Trajetos, ruas e horários de saída das linhas | Semob-JP, <https://servicos.semobjp.pb.gov.br/linhas-de-onibus/> (coletado em 26/11/2026) | Informação pública. A Semob não publicou licença de reuso; para uso comercial, peça confirmação por escrito. A Semob **não publica a posição das paradas**. |
| Mapa, paradas e pontos de referência | © colaboradores do [OpenStreetMap](https://www.openstreetmap.org/copyright) | [ODbL](https://opendatacommons.org/licenses/odbl/). A atribuição aparece no mapa e no rodapé. |
| Endereços | Nominatim (OpenStreetMap) e Photon | Uso leve, pedido a pedido, conforme as [políticas de uso](https://operations.osmfoundation.org/policies/nominatim/). |
| Mapa de fundo | tile.openstreetmap.org | Sujeito à [política de tiles](https://operations.osmfoundation.org/policies/tiles/): uso pesado exige outro provedor. |
| Biblioteca de mapas | [Leaflet](https://leafletjs.com) 1.9.4 (BSD-2-Clause), em `lib/leaflet/` | |

Os arquivos em `dados/` (JSON e CSV) são a versão organizada dos dados da Semob.

### Limitações conhecidas

- Sem a lista oficial de paradas, o embarque usa paradas do OpenStreetMap quando existem; senão, um ponto aproximado na rua. Corrija pelo mapa.
- O desenho de cada linha é o publicado pela Semob (de 2017 a 2026) e pode não seguir o sentido das ruas nem ter mudanças recentes. O aviso aparece no cartão quando o trajeto é antigo.
- O horário mostrado é o de **saída do terminal**, não o de passagem na sua parada. Não há tempo real.
- Em 26 sentidos de linha não foi possível confirmar a orientação do desenho; o sentido vem da lista de ruas.

## Privacidade

Não há servidor nem conta. Histórico, lugares e paradas marcadas ficam **só no seu aparelho** (armazenamento do navegador) e podem ser apagados no rodapé. Ao usar o site, o navegador consulta serviços do OpenStreetMap (mapa, busca de endereços, lugares), que recebem seu endereço de IP e o que você pesquisa. A posição do aparelho só é lida se você tocar em "Onde estou" e fica no navegador. Para escrever o nome das ruas dos pontos de embarque e desembarque, o site envia as coordenadas desses pontos (não a sua posição exata) ao Nominatim.

## Atualizar os dados

```bash
# 1) com os dados brutos coletados (lista de {codigo, rotulo, geojson, itinerarioHtml, horarioHtml}):
python3 -I tools/build.py raw.json dados/
# 2) gerar o arquivo que a página carrega:
python3 tools/gerar_js.py
```

A coleta no site da Semob não está automatizada aqui: o site bloqueia acessos de servidores, então foi feita pelo navegador.

## Estrutura

```
index.html              página (HTML, CSS e JavaScript)
sobre.html              objetivo, autor, licença e créditos
dados-semob.js          dados das linhas carregados pela página
manifest.webmanifest    informações do app instalável
sw.js                   service worker (abrir sem internet)
icons/                  ícones do app
lib/leaflet/            biblioteca de mapas
dados/                  dados organizados (JSON e CSV)
tools/                  scripts para atualizar os dados
```

## Licença

Código: [MIT](LICENSE), © 2026 Arthur Gabriel. Os dados têm as licenças da tabela acima.
