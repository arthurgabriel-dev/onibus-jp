import csv, json, re, sys
from collections import Counter

raw_path, out_dir = sys.argv[1], sys.argv[2]
raw = json.load(open(raw_path, encoding='utf-8'))

DIAS = {'dia útil', 'sábado', 'domingo', 'feriado', 'feriados'}


def tokens(html):
    t = re.sub(r'<[^>]+>', '|', html)
    t = t.replace('&nbsp;', ' ').replace('&amp;', '&')
    return [x.strip() for x in t.split('|') if x.strip()]


def parse_ruas(html):
    """{viagem: {sentido: [ruas em ordem]}}"""
    tabs = dict(re.findall(r'href="#(\w+)"[^>]*>\s*([^<]+?)\s*</a>', html))
    out = {}
    for part in re.split(r'<div class="tab-pane', html)[1:]:
        pid = re.search(r'id="(\w+)"', part)
        nome = tabs.get(pid.group(1), pid.group(1)) if pid else 'PRINCIPAL'
        sent = {}
        for tb in re.findall(r'<table.*?</table>', part, re.S):
            th = re.search(r'<th>\s*([^<]+?)\s*</th>', tb)
            if not th:
                continue
            ruas = [re.sub(r'\s+', ' ', r).strip() for r in re.findall(r'<td>\s*([^<]*?)\s*</td>', tb)]
            sent[th.group(1).strip().upper()] = [r for r in ruas if r]
        if sent:
            out[nome] = sent
    return out


def parse_horarios(html):
    toks = tokens(html)
    horarios, obs, dia = {}, [], None
    em_obs = False
    for i, t in enumerate(toks):
        low = t.lower()
        if low.startswith('observa'):
            em_obs = True
            continue
        if em_obs:
            obs.append(t)
            continue
        prox = toks[i + 1].lower() if i + 1 < len(toks) else ''
        m_prox = re.fullmatch(r'(\d+)\s+viagens?', prox)
        if m_prox:  # qualquer título seguido de "N viagens" abre um bloco (Dia útil, Sábado, Domingo, Especial...)
            dia = t
            horarios[dia] = {'viagens': int(m_prox.group(1)), 'partidas': []}
            continue
        if re.fullmatch(r'\d+\s+viagens?', low):
            continue
        if re.fullmatch(r'\d{1,2}:\d{2}', t) and dia:
            horarios[dia]['partidas'].append(t.zfill(5))
    return horarios, ' '.join(obs)


def data_valida(s):
    s = (s or '')[:10].replace('/', '-')
    return s if re.fullmatch(r'\d{4}-\d{2}-\d{2}', s) and s >= '2000' else ''


def numero(cod):
    return cod.lstrip('0') or '0' if cod.isdigit() else cod


linhas, avisos = [], []
for r in raw:
    cod = r['codigo']
    nome = re.sub(r'^\s*' + re.escape(cod) + r'\s*-\s*', '', r['rotulo']).strip()
    feats = (r.get('geojson') or {}).get('features', []) if isinstance(r.get('geojson'), dict) else []
    sentidos, tipo, empresa, atual = [], '', '', ''
    for f in feats:
        p = f.get('properties') or {}
        coords = [[round(y, 5), round(x, 5)] for x, y in f['geometry']['coordinates']]
        tipo = tipo or p.get('TIPO', '')
        empresa = empresa or p.get('EMPRESA', '')
        atual = max(atual, data_valida(p.get('ATUALIZACA')))
        sentidos.append({
            'sentido': p.get('ITINERARIO', ''),
            'extremos': (p.get('ROUTE_LONG') or '').strip(),
            'extensao_km': round(p.get('EXTENSAO') or 0, 2),
            'coords': coords,
        })
    horarios, obs = parse_horarios(r.get('horarioHtml', ''))
    for d, v in horarios.items():
        if v['viagens'] is not None and v['viagens'] != len(v['partidas']):
            avisos.append(f"{cod}: {d} diz {v['viagens']} viagens mas há {len(v['partidas'])} horários")
    if not sentidos:
        avisos.append(f'{cod}: sem trajeto desenhado na Semob')
    if not horarios:
        avisos.append(f'{cod}: sem horários')
    linhas.append({
        'codigo': cod, 'numero': numero(cod), 'nome': nome, 'tipo': tipo, 'empresa': empresa,
        'atualizado_em': atual, 'sentidos': sentidos,
        'ruas': parse_ruas(r.get('itinerarioHtml', '')),
        'horarios': horarios, 'observacoes': obs,
    })

# --- Orientação do desenho --------------------------------------------------------------
# O desenho nem sempre está na mesma ordem da lista de ruas (ex.: ida da 304). Usamos os terminais
# citados nas pontas das listas como âncoras para conferir e, se preciso, inverter o desenho.
import math, unicodedata


def norm(t):
    return unicodedata.normalize('NFD', t).encode('ascii', 'ignore').decode().upper().strip()


def dist(a, b):
    R = 6371000
    dl, dn = math.radians(b[0] - a[0]), math.radians(b[1] - a[1])
    h = math.sin(dl / 2) ** 2 + math.cos(math.radians(a[0])) * math.cos(math.radians(b[0])) * math.sin(dn / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


def pontas_lista(l, sentido):
    tab = next(iter(l['ruas'].values()), {})
    r = tab.get(sentido, [])
    return (norm(r[0]), norm(r[-1])) if r else (None, None)


cand = {}
for l in linhas:
    for s in l['sentidos']:
        f, u = pontas_lista(l, s['sentido'])
        for nome in (f, u):
            if nome and 'TERMINAL' in nome:
                cand.setdefault(nome, []).extend([s['coords'][0], s['coords'][-1]])
ancora = {}
for nome, pts in cand.items():
    melhor = max(pts, key=lambda p: sum(1 for q in pts if dist(p, q) < 400))
    apoio = sum(1 for q in pts if dist(melhor, q) < 400)
    if apoio >= 4:
        ancora[nome] = melhor
corrigidas, verificadas, sem_ancora = [], 0, 0
for l in linhas:
    for s in l['sentidos']:
        f, u = pontas_lista(l, s['sentido'])
        if not f or f == u or (f not in ancora and u not in ancora):
            s['orientacao'] = 'nao_verificada'
            sem_ancora += 1
            continue
        ini, fim = s['coords'][0], s['coords'][-1]
        def custo(a, b):
            c = 0
            if f in ancora: c += dist(ini if a else fim, ancora[f])
            if u in ancora: c += dist(fim if a else ini, ancora[u])
            return c
        direto, inverso = custo(True, True), custo(False, False)
        if inverso + 300 < direto:
            s['coords'].reverse()
            s['orientacao'] = 'corrigida'
            corrigidas.append(f"{l['codigo']} {s['sentido']}")
        else:
            s['orientacao'] = 'ok'
            verificadas += 1
print('âncoras de terminais:', len(ancora), '| orientação conferida e ok:', verificadas, '| invertidas:', corrigidas, '| sem âncora para conferir:', sem_ancora)

# Conferência: todos os pontos dentro da região de João Pessoa
for l in linhas:
    for s in l['sentidos']:
        fora = [c for c in s['coords'] if not (-7.30 < c[0] < -7.00 and -35.05 < c[1] < -34.75)]
        if fora:
            avisos.append(f"{l['codigo']} {s['sentido']}: {len(fora)} pontos fora da região de João Pessoa")

out = {
    'fonte': 'SEMOB-JP, servicos.semobjp.pb.gov.br/linhas-de-onibus/',
    'coletado_em': '2026-11-26',
    'observacao': 'A Semob publica o trajeto, as ruas e os horários de partida. Não publica as paradas com localização. coords = [latitude, longitude].',
    'linhas': linhas,
}
json.dump(out, open(out_dir + '/semob_linhas_organizado.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))

with open(out_dir + '/semob_resumo.csv', 'w', encoding='utf-8-sig', newline='') as fh:
    w = csv.writer(fh, delimiter=';')
    w.writerow(['codigo', 'numero', 'nome', 'tipo', 'empresa', 'sentidos', 'extensao_ida_km', 'extensao_volta_km',
                'viagens_dia_util', 'viagens_sabado', 'viagens_domingo', 'primeira_partida_dia_util', 'ultima_partida_dia_util',
                'atualizado_em', 'tem_trajeto'])
    for l in linhas:
        ext = {s['sentido']: s['extensao_km'] for s in l['sentidos']}
        hu = l['horarios'].get('Dia útil', {})
        pu = hu.get('partidas', [])
        w.writerow([l['codigo'], l['numero'], l['nome'], l['tipo'], l['empresa'], len(l['sentidos']),
                    ext.get('IDA', ''), ext.get('VOLTA', ''), hu.get('viagens', ''),
                    l['horarios'].get('Sábado', {}).get('viagens', ''), l['horarios'].get('Domingo', {}).get('viagens', ''),
                    pu[0] if pu else '', pu[-1] if pu else '', l['atualizado_em'], 'sim' if l['sentidos'] else 'não'])

print(len(linhas), 'linhas organizadas')
print('com trajeto:', sum(1 for l in linhas if l['sentidos']), '| com horários:', sum(1 for l in linhas if l['horarios']),
      '| com ruas:', sum(1 for l in linhas if l['ruas']))
print('tipos:', dict(Counter(l['tipo'] for l in linhas)))
print('empresas:', dict(Counter(l['empresa'] for l in linhas)))
datas = sorted(l['atualizado_em'] for l in linhas if l['atualizado_em'])
print('atualização do trajeto: de', datas[0], 'a', datas[-1], '| sem data válida:', sum(1 for l in linhas if l['sentidos'] and not l['atualizado_em']))
print('trajetos atualizados em 2026:', sum(1 for l in linhas if l['atualizado_em'].startswith('2026')),
      '| em 2025:', sum(1 for l in linhas if l['atualizado_em'].startswith('2025')),
      '| 2024 ou antes:', sum(1 for l in linhas if l['atualizado_em'] and l['atualizado_em'] < '2025'))
print('blocos de horário:', dict(Counter(d for l in linhas for d in l['horarios'])))
print('avisos:', len(avisos))
for a in avisos:
    print(' -', a)
