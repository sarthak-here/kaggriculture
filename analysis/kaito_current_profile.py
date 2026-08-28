"""Profile the complete current loss corpus of the Kaito-based submission."""

import argparse
import collections
import json
from pathlib import Path
import statistics

from pfall_clone_profile import distance
from v46_loss_pattern import profile


def family(side):
    animals = side["animal_mix"]
    return "%dq-%dc-%ds-%dg" % (
        side["quads"], animals.get("COW", 0), animals.get("SHEEP", 0),
        animals.get("GOOSE", 0))


def clone_stats(path):
    replay = json.load(open(path, encoding="utf-8"))
    values = []
    for index in range(120, min(681, len(replay.get("steps") or []))):
        obs = replay["steps"][index][0].get("observation")
        if isinstance(obs, dict):
            values.append(distance(obs))
    counts = {threshold: sum(value <= threshold for value in values)
              for threshold in (2, 6, 12)}
    streak = current = 0
    for value in values:
        current = current + 1 if value <= 2 else 0
        streak = max(streak, current)
    return {
        "min": min(values),
        "mean": statistics.mean(values),
        "turns": counts,
        "streak2": streak,
    }


def summarize(label, rows):
    if not rows:
        return
    print("\n%s %d" % (label, len(rows)))
    print(" buckets", dict(collections.Counter(row["bucket"] for row in rows)))
    print(" seats", dict(collections.Counter(row["seat"] for row in rows)))
    print(" opponents", collections.Counter(row["opponent"] for row in rows).most_common(8))
    print(" families", collections.Counter(row["op_family"] for row in rows).most_common(8))
    print(" persistent clone", sum(row["clone"]["streak2"] >= 24 for row in rows))
    for key in ("income", "spend", "feed_units", "weed_burden",
                "ready_value", "quads", "animals", "crops"):
        ours = statistics.mean(row["us"][key] for row in rows)
        theirs = statistics.mean(row["op"][key] for row in rows)
        print(" %-12s us %9.1f op %9.1f delta %+9.1f" %
              (key, ours, theirs, ours - theirs))
    for key in ("day12_gap", "day18_gap", "final_gap", "margin"):
        print(" %-12s %+9.1f" %
              (key, statistics.mean(row[key] for row in rows)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path,
                        default=Path("loss_analysis/kaito_current"))
    args = parser.parse_args()
    manifest = json.load(open(args.corpus / "manifest.json", encoding="utf-8"))
    metadata = {row["episode"]: row for row in manifest}
    rows = []
    paths = sorted(args.corpus.glob("episode-*-replay.json"))
    for number, path in enumerate(paths, 1):
        row = profile(str(path))
        row.update(metadata.get(row["episode"], {}))
        row["op_family"] = family(row["op"])
        row["clone"] = clone_stats(path)
        rows.append(row)
        if number % 10 == 0 or number == len(paths):
            print("profiled %d/%d" % (number, len(paths)), flush=True)
    target = args.corpus / "profiles.json"
    target.write_text(json.dumps(rows, indent=2), encoding="utf-8")

    close = [row for row in rows if row["margin"] >= -2500]
    severe = [row for row in rows if row["margin"] <= -8000]
    clone = [row for row in rows if row["clone"]["streak2"] >= 24]
    structural = [row for row in rows if row["clone"]["turns"][6] == 0]
    recent = sorted(rows, key=lambda row: row.get("end", ""))[-20:]
    for label, group in (
        ("ALL", rows), ("CLOSE", close), ("SEVERE", severe),
        ("PERSISTENT_CLONE", clone), ("NO_CLONE_CONTACT", structural),
        ("RECENT_20_LOSSES", recent),
    ):
        summarize(label, group)

    print("\nWORST")
    for row in sorted(rows, key=lambda item: item["margin"])[:20]:
        print("%d s%d %8.0f %-9s %-14s clone min%2d streak%3d %s" % (
            row["episode"], row["seat"], row["margin"], row["bucket"],
            row["op_family"], row["clone"]["min"], row["clone"]["streak2"],
            row["opponent"][:24]))
    print("wrote", target)


if __name__ == "__main__":
    main()