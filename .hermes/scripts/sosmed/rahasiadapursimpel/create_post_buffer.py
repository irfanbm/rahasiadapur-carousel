import urllib.request, json, sys

TOKEN = "tqjZ794XZr-MkAyDQxCV-wlYnvxfDPWN7JKZOYCtVJA"
URL = "https://api.buffer.com/graphql"
IG_CH = "6aa82720ea19ca0bde3fd956"   # rahasiadapursimpel (instagram)
TT_CH = "6aa84104ea19ca0bde410081"   # cekotpake (tiktok)
BASE = "https://raw.githubusercontent.com/irfanbm/rahasiadapur-carousel/main"

# args: <folder_or_relpath> <caption> <hours_ahead>
folder_in = sys.argv[1] if len(sys.argv) > 1 else "jpg"
caption = sys.argv[2] if len(sys.argv) > 2 else "Rahasia Dapur Simpel"
hours = int(sys.argv[3]) if len(sys.argv) > 3 else 2

from datetime import datetime, timezone, timedelta
due = (datetime.now(timezone.utc) + timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%S.000Z")

# list jpg/png in folder, zero-padded slide_XX.jpg / slide_XX.png
import glob, os, time
files = sorted(glob.glob(os.path.join(folder_in, "slide_*.[jJ][pP][gG]")) + glob.glob(os.path.join(folder_in, "slide_*.[pP][nN][gG]")))

# Determine relative path for GitHub Raw URL
# Rule: If folder_in is e.g. "jpg/2026-09-24-1100/7-trik-dapur/", preserve relative path.
rel_folder = folder_in.replace("\\", "/").strip("/")
# repo root is /home/ubuntu, so committed path has this prefix
import subprocess
rel = rel_folder
for c in (".hermes/scripts/sosmed/rahasiadapursimpel/", "carousel/"):
    rel = rel.replace(c, "", 1)
if subprocess.run(["git", "-C", "/home/ubuntu", "ls-files", "--error-unmatch", ".hermes/scripts/sosmed/rahasiadapursimpel/" + rel_folder]).returncode == 0:
    rel_folder = ".hermes/scripts/sosmed/rahasiadapursimpel/" + rel_folder
else:
    rel_folder = rel_folder
assets = [{"image": {"url": f"{BASE}/{rel_folder}/{os.path.basename(f)}"}} for f in files]
print(f"assets: {len(assets)} from {rel_folder}")

# HTTP 200 verification before submitting to Buffer API
def check_asset(u, retries=10, delay=10):
    for _ in range(retries):
        try:
            req = urllib.request.Request(u, method="GET", headers={"User-Agent": "Mozilla/5.0"})
            resp = urllib.request.urlopen(req, timeout=15)
            if resp.status == 200:
                return True
        except Exception:
            pass
        time.sleep(delay)
    return False

all_ok = True
for a in assets:
    u = a["image"]["url"]
    if check_asset(u):
        print(f"[VERIFIED 200] {u}")
    else:
        print(f"[FAILED 200] {u}")
        all_ok = False

if not all_ok:
    print("ABORT: Asset URLs not return HTTP 200. Buffer post cancelled.")
    sys.exit(1)

def graph(q, variables):
    req = urllib.request.Request(URL, data=json.dumps({"query": q, "variables": variables}).encode(),
                                 headers={"Content-Type": "application/json", "Authorization": "Bearer " + TOKEN})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

CREATE = """
mutation($input:CreatePostInput!){
  createPost(input:$input){
    __typename
    ... on PostActionSuccess { post { id status channel { service name } } }
    ... on InvalidInputError { message }
  }
}
"""

results = {}
for ch, svc in [(IG_CH, "instagram"), (TT_CH, "tiktok")]:
    inp = {
        "channelId": ch,
        "assets": assets,
        "text": caption,
        "mode": "customScheduled",
        "schedulingType": "automatic",
        "dueAt": due,
        "needsApproval": False,
    }
    if svc == "instagram":
        inp["metadata"] = {"instagram": {"type": "post", "shouldShareToFeed": True}}
    variables = {"input": inp}
    r = graph(CREATE, variables)
    results[svc] = r
    print(svc, "->", json.dumps(r.get("data", {}).get("createPost", r.get("errors")))[:200])

print("DUE:", due)
