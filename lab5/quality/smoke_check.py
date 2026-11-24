#!/usr/bin/env python3
"""Сравнивает два stats_*.json и проверяет деградацию объёма/полноты."""
import json
import sqlite3
import sys
from pathlib import Path

def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def main(previous, current, db_path="data/crawl.db"):
    old, new = load(previous), load(current)
    old_count = int(old.get("item_scraped_count", 0))
    new_count = int(new.get("item_scraped_count", 0))
    if old_count and new_count < old_count * 0.8:
        print(f"WARNING: число элементов упало более чем на 20% ({old_count} -> {new_count})")
    else:
        print(f"OK: динамика элементов: {old_count} -> {new_count}")

    conn = sqlite3.connect(db_path)
    total = conn.execute("SELECT COUNT(*) FROM quotes").fetchone()[0]
    empty = conn.execute("""
        SELECT
          SUM(CASE WHEN quote IS NULL OR trim(quote)='' THEN 1 ELSE 0 END) +
          SUM(CASE WHEN author IS NULL OR trim(author)='' THEN 1 ELSE 0 END) +
          SUM(CASE WHEN tags IS NULL OR trim(tags)='' THEN 1 ELSE 0 END) +
          SUM(CASE WHEN author_url IS NULL OR trim(author_url)='' THEN 1 ELSE 0 END)
        FROM quotes
    """).fetchone()[0] or 0
    required_cells = total * 4
    ratio = empty / required_cells if required_cells else 0
    print(f"Записей в БД: {total}; пустых обязательных значений: {ratio:.2%}")
    if ratio > 0.05:
        print("WARNING: доля пустых обязательных полей превышает 5%")
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Использование: python quality/smoke_check.py data/stats_001.json data/stats_002.json")
    main(sys.argv[1], sys.argv[2])
