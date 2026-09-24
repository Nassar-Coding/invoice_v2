# Pinned challenge snapshot

- Repository: https://github.com/majedzahrani3/invoice-auditing-level-2
- Commit: `aef4924dc32506b4587de8b788b5a947e6beffec` (the only authoritative input)
- Expected local path: `../majedzahrani3/invoice-auditing-level-2` relative to this repo, or set `INVOICE_SNAPSHOT`.

Obtain it with:

```
git clone https://github.com/majedzahrani3/invoice-auditing-level-2 ../majedzahrani3/invoice-auditing-level-2
git -C ../majedzahrani3/invoice-auditing-level-2 checkout aef4924dc32506b4587de8b788b5a947e6beffec
python tools/snapshot.py verify
```

Frozen files (regenerate only with `python tools/snapshot.py freeze` against the pinned commit):

| File | Content |
|---|---|
| `manifest.tsv` | 10,330 tracked files: path, SHA-256, git blob SHA-1, bytes. `verify` also compares every blob with `git ls-tree -r <commit>`. |
| `pdf_pages.json` | Both contracts: page count, no text layer, one 1654×2338 DeviceGray image per page, SHA-256 of each page's decoded samples. This is the identity of "the scan" for G1. |
| `inventory.json` | CSV schemas and row counts, ID uniqueness and header/line/template joins, distinct codes and units, record counts/bytes, contract-reference variants, zero adjustment fields, missing civil record IDs, same-day submissions relevant to A3. These are observations, not invoice outcomes. |
