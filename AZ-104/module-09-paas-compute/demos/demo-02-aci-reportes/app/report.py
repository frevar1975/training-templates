import base64
import csv
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import html
import io
import json
import os
from pathlib import Path
import time
import uuid


def analyze(text):
    reader = csv.DictReader(io.StringIO(text))
    required = {'fecha', 'sucursal', 'producto', 'cantidad', 'precio_unitario'}
    if not required.issubset(reader.fieldnames or []):
        raise ValueError('Faltan columnas: ' + ', '.join(sorted(required)))
    branches = defaultdict(Decimal)
    products = defaultdict(Decimal)
    days = defaultdict(Decimal)
    units = 0
    rows = 0
    for line, row in enumerate(reader, 2):
        try:
            datetime.strptime(row['fecha'], '%Y-%m-%d')
            qty = int(row['cantidad'])
            price = Decimal(row['precio_unitario'])
            if qty <= 0 or not price.is_finite() or price < 0:
                raise ValueError('Cantidad/precio fuera de rango')
            branch, product = row['sucursal'].strip(), row['producto'].strip()
            if not branch or not product:
                raise ValueError('Sucursal/producto vacíos')
        except (ValueError, InvalidOperation, TypeError) as exc:
            raise ValueError(f'Fila {line}: {exc}') from exc
        amount = qty * price
        branches[branch] += amount
        products[product] += amount
        days[row['fecha']] += amount
        units += qty
        rows += 1
    if rows == 0:
        raise ValueError('El CSV no tiene ventas')
    return {'total': sum(branches.values()), 'units': units, 'rows': rows,
            'branches': dict(branches), 'products': dict(products), 'days': dict(sorted(days.items()))}


def money(n):
    return 'Bs ' + f'{n:,.2f}'


def render(result, run_id, stamp, digest):
    esc = html.escape
    def bars(mapping):
        maximum = max(mapping.values()) or Decimal(1)
        return ''.join(f'<div class="barrow"><div class="label"><b>{esc(k)}</b><span>{money(v)}</span></div><div class="track"><div class="fill" style="width:{float(v/maximum*100):.2f}%"></div></div></div>' for k,v in sorted(mapping.items(), key=lambda x:x[1], reverse=True))
    leader = max(result['branches'], key=result['branches'].get)
    daily = ''.join(f'<tr><td>{esc(k)}</td><td>{money(v)}</td></tr>' for k,v in result['days'].items())
    return f'''<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Nova · Reporte de ventas</title><style>*{{box-sizing:border-box}}body{{background:#eef2f8;color:#16243e;font:16px system-ui;margin:0}}main{{max-width:1100px;margin:auto;padding:32px}}header{{background:#152540;color:white;padding:32px;border-radius:18px}}h1{{font-size:34px;margin:8px 0}}.eyebrow{{letter-spacing:3px;color:#7edcce}}.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:24px 0}}.card,section{{background:white;padding:24px;border-radius:16px}}.value{{font-size:27px;font-weight:800;margin-top:10px}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}.label{{display:flex;justify-content:space-between;gap:12px;margin-bottom:8px}}.barrow{{margin:22px 0}}.track{{background:#edf1f7;border-radius:10px;height:16px}}.fill{{background:#008b79;border-radius:10px;height:16px}}table{{width:100%;border-collapse:collapse}}td,th{{padding:12px;border-bottom:1px solid #e2e8f0;text-align:left}}.meta{{color:#5a6a82;font-size:13px;overflow-wrap:anywhere}}.note{{margin:20px 0;color:#425572}}@media(max-width:700px){{.kpis,.grid{{grid-template-columns:1fr}}}}</style><main><header><div class="eyebrow">NOVA · OPERACIONES</div><h1>Reporte de ventas</h1><p>Datos ficticios · generado por un trabajo en Azure Container Instances</p><div>Ejecutado: {esc(stamp)} UTC</div></header><div class="kpis"><div class="card">Ventas totales<div class="value">{money(result['total'])}</div></div><div class="card">Unidades<div class="value">{result['units']}</div></div><div class="card">Registros de venta<div class="value">{result['rows']}</div></div><div class="card">Sucursal líder<div class="value">{esc(leader)}</div></div></div><div class="grid"><section><h2>Ventas por sucursal</h2>{bars(result['branches'])}</section><section><h2>Ventas por producto</h2>{bars(result['products'])}</section></div><section style="margin-top:20px"><h2>Evolución diaria</h2><table><thead><tr><th>Fecha</th><th>Ventas</th></tr></thead><tbody>{daily}</tbody></table></section><p class="note">El contenedor finaliza después de generar los archivos. Azure Files conserva el resultado para consultarlo después.</p><footer class="meta">Ejecución: {esc(run_id)}<br>SHA256 del CSV: {esc(digest)}</footer></main></html>'''


def main():
    root = Path(os.environ.get('REPORT_ROOT', '/reports'))
    if not root.is_dir():
        raise RuntimeError('No existe el volumen de reportes: ' + str(root))
    delay = int(os.environ.get('DEMO_DELAY_SECONDS', '60'))
    if not 0 <= delay <= 300:
        raise ValueError('DEMO_DELAY_SECONDS debe estar entre 0 y 300')
    input_path = root / 'ventas.csv'
    if not input_path.exists():
        seed = os.environ.get('SEED_CSV_BASE64')
        if not seed:
            raise ValueError('No existe ventas.csv ni CSV inicial')
        input_path.write_bytes(base64.b64decode(seed, validate=True))
        print('[1/5] CSV inicial creado en Azure Files.', flush=True)
    else:
        print('[1/5] Usando ventas.csv existente: los cambios del archivo se conservan.', flush=True)
    print('[2/5] Pausa didáctica para abrir los logs; no representa tiempo real de procesamiento.', flush=True)
    for remaining in range(delay, 0, -10):
        print(f'       {remaining} segundos restantes...', flush=True)
        time.sleep(min(10, remaining))
    text = input_path.read_text(encoding='utf-8-sig')
    result = analyze(text)
    print(f"[3/5] Procesados {result['rows']} registros, {result['units']} unidades. Total: {money(result['total'])}.", flush=True)
    now = datetime.now(timezone.utc)
    run_id = now.strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]
    digest = hashlib.sha256(input_path.read_bytes()).hexdigest()
    document = render(result, run_id, now.strftime('%Y-%m-%d %H:%M:%S'), digest)
    history = root / ('reporte-' + run_id + '.html')
    history.write_text(document, encoding='utf-8')
    (root / 'reporte-actual.html').write_text(document, encoding='utf-8')
    summary = {'run_id':run_id, 'csv_sha256':digest, **result}
    (root / ('resumen-' + run_id + '.json')).write_text(json.dumps(summary, default=str, ensure_ascii=False, indent=2), encoding='utf-8')
    print('[4/5] Guardados: ' + history.name + ', reporte-actual.html y resumen JSON.', flush=True)
    print('[5/5] Trabajo completado. El proceso termina con código 0. Los archivos permanecen en Azure Files.', flush=True)

if __name__ == '__main__':
    main()
