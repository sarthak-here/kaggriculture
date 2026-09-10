"""Cancel matched opening wheat round trips, preserving net orders and workers."""
import argparse
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WRAPPER = '''
class _OpeningNet:
    def __init__(self, base):
        self.base = base
        self.delay_telemetry = dict(cancelled_pairs=0)

    def __call__(self, obs, configuration=None):
        action = self.base(obs, configuration)
        step = int(obs.get('step', 0))
        if step == 0:
            self.delay_telemetry['cancelled_pairs'] = 0
        # Leave initial capital allocation alone. Only the first day's subsequent
        # wheat round trips are netted; this is NOT a global trading replacement.
        if not 2 <= step < 24:
            return action
        orders = [list(o) for o in action.get('market', [])]
        amounts = {}
        for op in ('SELL', 'BUY_PRODUCT'):
            amounts[op] = sum(int(o[2]) for o in orders
                              if len(o) == 3 and o[:2] == [op, 'WHEAT']
                              and isinstance(o[2], int) and o[2] > 0)
        paired = min(amounts.values())
        if not paired:
            return action
        remaining = {'SELL': paired, 'BUY_PRODUCT': paired}
        result = []
        for order in orders:
            if (len(order) == 3 and order[0] in remaining and order[1] == 'WHEAT'
                    and isinstance(order[2], int) and order[2] > 0):
                n = min(order[2], remaining[order[0]])
                remaining[order[0]] -= n
                order[2] -= n
                if not order[2]:
                    continue
            result.append(order)
        self.delay_telemetry['cancelled_pairs'] += paired
        return dict(action, market=result)

_V44_POLICY = _OpeningNet(_V44_POLICY)
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=ROOT/'variants/w13_crop_demand/main.py')
    parser.add_argument('--output', type=Path, default=ROOT/'variants/w13_opening_net/main.py')
    args = parser.parse_args()
    source = args.source.read_text()
    marker = '\ndef agent(obs, configuration=None):'
    assert source.count(marker) == 1
    candidate = source.replace(marker, '\n'+WRAPPER+marker)
    compile(candidate, str(args.output), 'exec')
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(candidate)
    print({'source_sha256': hashlib.sha256(args.source.read_bytes()).hexdigest(),
           'output_sha256': hashlib.sha256(args.output.read_bytes()).hexdigest()})


if __name__ == '__main__':
    main()
