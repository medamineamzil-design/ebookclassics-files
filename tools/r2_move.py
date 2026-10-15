#!/usr/bin/env python3
"""Move the paid ebook files (PDF, EPUB) of every book to the private R2 bucket.

Each public file <slug>/<stem>.pdf|.epub is uploaded to R2 under text/<slug>/<stem>.<ext>, checked,
then replaced in the repository by a short notice (kept above 1000 bytes so manifest.json is unchanged).
Print files (interieur, couverture, bv) are never touched. Usage: r2_move.py <repo_dir>
"""
import os, re, sys
import boto3

root = sys.argv[1] if len(sys.argv) > 1 else "."
MARK = b"BOOKCLASSICS-PAID-FILE"
s3 = boto3.client("s3", endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
                  aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"], aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
                  region_name="auto")
bucket = os.environ["R2_BUCKET"]
TYPES = {"pdf": "application/pdf", "epub": "application/epub+zip"}
moved = skipped = 0
for slug in sorted(os.listdir(root)):
    d = os.path.join(root, slug)
    if slug.startswith((".", "_")) or not os.path.isdir(d):
        continue
    for f in sorted(os.listdir(d)):
        m = re.match(re.escape(slug) + r"(?:-([a-z]{2}(?:-[a-z]{2})?))?\.(epub|pdf)$", f)
        if not m:
            continue
        p = os.path.join(d, f)
        data = open(p, "rb").read()
        if MARK in data[:400]:
            skipped += 1
            continue
        key = f"text/{slug}/{f}"
        s3.put_object(Bucket=bucket, Key=key, Body=data, ContentType=TYPES[m.group(2)])
        if s3.head_object(Bucket=bucket, Key=key)["ContentLength"] != len(data):
            print("!! upload check failed:", key); continue
        note = (MARK + b"\nThis ebook file is sold on BookClassics (reading online stays free):\n"
                + f"https://bookclassics.org/books/{slug}/\n".encode())
        open(p, "wb").write(note + b" " * max(0, 1200 - len(note)) + b"\n")
        moved += 1
print(f"moved to R2: {moved} | already moved: {skipped}")
