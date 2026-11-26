"""Refresh the HTML and CSV after editing data/menu.json."""
import csv
import json
import re
from datetime import date
from pathlib import Path

root = Path(__file__).resolve().parents[1]
catalog = json.loads((root / "data/menu.json").read_text(encoding="utf-8"))
items = catalog["items"]
stamp = date.fromisoformat(catalog["checked_on"])
page_path = root / "index.html"
page = page_path.read_text(encoding="utf-8")
embedded = json.dumps(catalog, ensure_ascii=False).replace("<", r"\u003c")
page = re.sub(
    r'(<script id="catalog" type="application/json">).*?(</script>)',
    lambda match: match[1] + embedded + match[2],
    page,
    count=1,
    flags=re.S,
)
page = re.sub(r'(<time datetime=")[^"]*(">).*?(</time>)',
              lambda match: match[1] + stamp.isoformat() + match[2] + stamp.strftime("%Y.%m.%d") + match[3],
              page, count=1)
page_path.write_text(page, encoding="utf-8")

fields = list(dict.fromkeys(key for item in items for key in item))
with (root / "data/menu.csv").open("w", encoding="utf-8-sig", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=[*fields, "checked_on"])
    writer.writeheader()
    for item in items:
        row = {key: " / ".join(value) if isinstance(value, list) else value for key, value in item.items()}
        writer.writerow({**row, "checked_on": stamp.isoformat()})
