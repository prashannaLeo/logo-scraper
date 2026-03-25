"""
scrape_logos.py
---------------
Reads a list of URLs from a text file, scrapes each site for its best
logo/favicon, downloads it, and saves a mapping of site -> logo file.

Strategy priority (what browsers show in the tab):
  1. <link rel="icon"> — largest PNG/SVG/WebP (tab favicon, highest quality)
  2. <link rel="apple-touch-icon"> — high-res square icon
  3. Clearbit Logo API — clean brand logos
  4. /favicon.ico — classic fallback
  5. Google Favicon Service — last resort

URL file format (one URL per line, # lines ignored):
    https://chat.openai.com
    https://www.grammarly.com

Usage:
    python scrape_logos.py --input urls.txt --out-dir logos

Requirements:
    pip install requests beautifulsoup4
"""

import argparse
import csv
import os
import re
import urllib.parse
import urllib.request
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependencies. Run:  pip install requests beautifulsoup4")
    raise

# Disable SSL warnings (Windows MSYS2 cert issue fix)
requests.packages.urllib3.disable_warnings()
SESSION = requests.Session()
SESSION.verify = False
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
})


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_domain(url: str) -> str:
    return urlparse(url).netloc.lstrip("www.")


def safe_filename(domain: str) -> str:
    return re.sub(r"[^\w\-.]", "_", domain)


def download(url: str, dest: str, timeout=15) -> bool:
    try:
        r = SESSION.get(url, timeout=timeout, stream=True)
        if r.status_code == 200 and len(r.content) > 100:
            with open(dest, "wb") as f:
                f.write(r.content)
            return True
    except Exception:
        pass
    return False


def guess_ext(url: str, default=".png") -> str:
    ext = os.path.splitext(urlparse(url).path)[-1].lower()
    return ext if ext in (".png", ".jpg", ".jpeg", ".ico", ".svg", ".webp") else default


# ── Strategies ────────────────────────────────────────────────────────────────

def strategy_link_icon(html: str, base_url: str):
    """
    <link rel='icon'> — exactly what browsers show in the tab.
    Prefers PNG/SVG/WebP over ICO, and picks the largest declared size.
    """
    soup = BeautifulSoup(html, "html.parser")
    tags = soup.find_all("link", rel=lambda r: r and "icon" in r)

    PREFERRED = (".png", ".svg", ".webp")
    best_url, best_size, best_preferred = None, 0, False

    for tag in tags:
        href = tag.get("href", "").strip()
        if not href:
            continue
        full_url = urljoin(base_url, href)
        ext = os.path.splitext(urlparse(full_url).path)[-1].lower()
        is_preferred = ext in PREFERRED

        sizes = tag.get("sizes", "0x0")
        try:
            size = int(sizes.split("x")[0])
        except Exception:
            size = 1

        # Upgrade if: better format, or same format but bigger
        if (is_preferred and not best_preferred) or \
           (is_preferred == best_preferred and size > best_size):
            best_url = full_url
            best_size = size
            best_preferred = is_preferred

    return best_url


def strategy_apple_touch_icon(html: str, base_url: str):
    soup = BeautifulSoup(html, "html.parser")
    for rel in ["apple-touch-icon-precomposed", "apple-touch-icon"]:
        tag = soup.find("link", rel=rel)
        if tag and tag.get("href"):
            return urljoin(base_url, tag["href"].strip())
    return None


def strategy_clearbit(domain: str) -> str:
    return f"https://logo.clearbit.com/{domain}"


def strategy_favicon_ico(base_url: str) -> str:
    p = urlparse(base_url)
    return f"{p.scheme}://{p.netloc}/favicon.ico"


def strategy_google_favicon(domain: str) -> str:
    return f"https://www.google.com/s2/favicons?domain={domain}&sz=128"


# ── Main scraper ──────────────────────────────────────────────────────────────

def scrape_logo(site_url: str, out_dir: str) -> dict:
    domain = get_domain(site_url)
    fname_base = safe_filename(domain)
    result = {"site": site_url, "domain": domain, "logo_url": "", "saved_file": "", "status": ""}

    print(f"\n🔍 {domain}")

    # Fetch homepage HTML
    html, final_url = "", site_url
    try:
        r = SESSION.get(site_url, timeout=15)
        html = r.text
        final_url = r.url
        print(f"   Homepage fetched (HTTP {r.status_code})")
    except Exception as e:
        print(f"   ⚠ Could not fetch homepage: {e}")

    # Build candidate list — priority order matches browser tab behaviour
    candidates = []

    if html:
        link_icon = strategy_link_icon(html, final_url)
        if link_icon:
            candidates.append(("link-icon (tab favicon)", link_icon))

        apple = strategy_apple_touch_icon(html, final_url)
        if apple:
            candidates.append(("apple-touch-icon", apple))

    candidates.append(("clearbit",        strategy_clearbit(domain)))
    candidates.append(("favicon.ico",     strategy_favicon_ico(final_url)))
    candidates.append(("google-favicon",  strategy_google_favicon(domain)))

    # Try each in order — stop at first success
    for strategy_name, logo_url in candidates:
        ext  = guess_ext(logo_url)
        dest = os.path.join(out_dir, f"{fname_base}{ext}")
        print(f"   Trying [{strategy_name}]: {logo_url[:90]}...")
        if download(logo_url, dest):
            size_kb = os.path.getsize(dest) / 1024
            print(f"   ✅ Saved → {os.path.basename(dest)} ({size_kb:.1f} KB)")
            result.update(logo_url=logo_url, saved_file=dest, status=f"ok:{strategy_name}")
            return result
        print(f"   ✗ Failed")

    print(f"   ❌ All strategies failed for {domain}")
    result["status"] = "failed"
    return result


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",   required=True, help="Text file with one URL per line")
    parser.add_argument("--out-dir", default="logos", help="Folder to save logos")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        urls = [
            line.strip() for line in f
            if line.strip() and not line.strip().startswith("#")
        ]

    if not urls:
        print("No URLs found in input file.")
        return

    os.makedirs(args.out_dir, exist_ok=True)
    print(f"Found {len(urls)} URLs. Saving logos to: {args.out_dir}/\n")

    results = []
    for url in urls:
        results.append(scrape_logo(url, args.out_dir))

    # Save CSV
    csv_path = os.path.join(args.out_dir, "_logo_map.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["site", "domain", "logo_url", "saved_file", "status"])
        writer.writeheader()
        writer.writerows(results)

    ok   = [r for r in results if r["status"].startswith("ok")]
    fail = [r for r in results if r["status"] == "failed"]
    print(f"\n{'='*60}")
    print(f"✅ {len(ok)} logos downloaded   ❌ {len(fail)} failed")
    if fail:
        print("\nFailed sites:")
        for r in fail:
            print(f"  • {r['site']}")
    print(f"\nMapping saved to: {csv_path}")


if __name__ == "__main__":
    main()