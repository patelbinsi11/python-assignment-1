import os
import pickle
import re
import sys
import zipfile
from collections import defaultdict

TOKEN = re.compile(r"[a-z0-9_]+")       # a token = letters, digits, underscore


def make_demo(folder="logs"):
    """Create a small sample logs folder so you can test without making files."""
    os.makedirs(folder, exist_ok=True)
    samples = {
        "server1.log": "INFO server started\nERROR timeout on db\nINFO request ok\n",
        "server2.log": "WARN disk almost full\nERROR timeout on api\n",
        "server3.log": "INFO user login\nINFO user logout\nERROR crash in worker\n",
    }
    for name, text in samples.items():
        with open(os.path.join(folder, name), "w", encoding="utf-8") as f:
            f.write(text)
    print(f"Created folder '{folder}' with {len(samples)} sample log files.")


def build(folder, zip_name):
    if not os.path.isdir(folder):
        print("Folder not found:", folder)
        return
    index = defaultdict(list)            # token -> [(file name, line number), ...]
    files = lines = 0
    names = sorted(f for f in os.listdir(folder)
                   if os.path.isfile(os.path.join(folder, f)))
    for name in names:
        try:
            with open(os.path.join(folder, name), encoding="utf-8", errors="ignore") as fh:
                files += 1
                for no, line in enumerate(fh, 1):
                    lines += 1
                    for tok in set(TOKEN.findall(line.lower())):
                        if len(tok) <= 50:
                            index[tok].append((name, no))
        except OSError as e:
            print("Skipping", name, "-", e)

    pkl = os.path.splitext(zip_name)[0] + "_index.pkl"
    with open(pkl, "wb") as fh:          # save the index with pickle
        pickle.dump(dict(index), fh)
    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as z:
        for name in names:               # original logs go into the zip
            z.write(os.path.join(folder, name), arcname="logs/" + name)
        z.write(pkl, arcname=os.path.basename(pkl))   # and the index too
    print("FILES", files)
    print("LINES", lines)
    print("TOKENS", len(index))


def search(pkl, queries):
    try:
        with open(pkl, "rb") as fh:
            index = pickle.load(fh)
    except (OSError, pickle.UnpicklingError, EOFError) as e:
        print("Cannot load index:", e)
        return
    for q in queries:
        hits = index.get(q.lower(), [])
        print(f"{q}: {len(hits)} match(es)")
        for name, no in hits:
            print(f"  {name}:{no}")


def main():
    a = sys.argv[1:]
    if a and a[0].upper() == "DEMO":
        make_demo()
    elif len(a) >= 3 and a[0].upper() == "BUILD":
        build(a[1], a[2])
    elif len(a) >= 3 and a[0].upper() == "SEARCH":
        search(a[1], a[2:])
    else:
        print("Usage:")
        print("  DEMO")
        print("  BUILD  <folder> <output.zip>")
        print("  SEARCH <index.pkl> <token> [token ...]")


if __name__ == "__main__":
    main()