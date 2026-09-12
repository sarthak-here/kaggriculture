"""Build a bounded waiting-stock sales probe from the submitted opening guard."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
HELPER='''
def sell_waiting_stock(action, view, tape, step):
    """Add held-stock sales. Later requests stay intact; this is not an exact shift."""
    if not 144 <= step < 648 or step % 4 == 0:
        return
    if any(o and (o[0].startswith("BUY") or o[0] == "HIRE") for o in action["market"]):
        return
    planned = {}
    for future in range(step + 2, step + 4):
        if future // 24 != step // 24 or future >= 648:
            continue
        for order in tape[future].get("market", []):
            if len(order) >= 3 and order[0] == "SELL":
                planned[order[1]] = planned.get(order[1], 0) + max(0, int(order[2]))
    stock = projected_shed(action, view)
    selling = {o[1] for o in action["market"] if len(o) >= 2 and o[0] == "SELL"}
    for item in PRODUCTS:
        if item in ("WHEAT", "FERTILIZER") or item in selling:
            continue
        quantity = min(stock.get(item, 0), planned.get(item, 0))
        if quantity > 0 and view.prices.get(item, 0) >= 2 and len(action["market"]) < MAX_ORDERS:
            action["market"].append(["SELL", item, quantity])

'''
def main():
    out=ROOT/'variants/shop0909_waiting_h3'
    if out.exists():raise FileExistsError(out)
    archive=ROOT/'analysis/shop0909_opening_panel_20260912/candidate.zip'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()=='a63d56e478203b281b9560df3224abef322f34fcb81dee812f707720593758fb'
    with zipfile.ZipFile(archive) as z:files={n:z.read(n) for n in ('main.py','actions.json','LICENSE.txt')}
    source=files['main.py'].decode();assert source.count('class Policy:')==1
    source=source.replace('class Policy:',HELPER+'class Policy:')
    anchor='        advance_sales(action, view, state, tape, step)'
    assert source.count(anchor)==1
    source=source.replace(anchor,anchor+'\n        sell_waiting_stock(action, view, tape, step)')
    compile(source,'main.py','exec');files['main.py']=source.encode()
    out.mkdir(parents=True)
    for n,b in files.items():(out/n).write_bytes(b)
    (out/'provenance.json').write_text(json.dumps(dict(base_submission=56182426,
        files={n:hashlib.sha256(b).hexdigest() for n,b in files.items()}),indent=2)+'\n')
    print(out)
if __name__=='__main__':main()
