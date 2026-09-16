# Cloning V45 snapshot

Imported unchanged from the Desktop notebook on 2026-09-16. Kept separate from
our existing agents. Original source notices and notebook are preserved.

The importer extracts Python byte literals without executing notebook cells.
Both the source and the deterministic tar.gz match the notebook's pinned hashes.
The archive contains main.py at the root. See manifest.json and UPSTREAM_NOTICES.md.

Source SHA-256: 2536d41ed5a00c75204b6350f1c76c54259c774cb065ba2a3a0072eedf210d94

The notebook's performance claims are upstream claims, not independently
reproduced results. Local smoke results, when complete, are saved at
analysis/cloning_v45_smoke_20260916.json. Two games are not a promotion panel.
Local smoke completed: 2 wins, zero losses/ties/failures against submitted
Shop0909 tomato432, seed39166000 both seats. Scores120948 versus117648 in each
seat (+3300). This validates execution, not broad superiority.
No Kaggle submission was made by this import.

Rebuild in a fresh checkout (requires the original Desktop notebook):
`.venv/Scripts/python.exe analysis/import_desktop_cloning_v45.py`
The importer refuses to overwrite an existing snapshot directory.
