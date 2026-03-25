# AI Tool Logo Scraper

A set of Python scripts to recover, check, and replace broken Firebase Storage image URLs in `.docx` files — and scrape logos directly from websites.

---

## Project Structure

```
.
├── scrape_logos.py        # Scrape logos from a list of URLs
├── check_and_download.py  # Check Firebase URLs and download working images
├── replace_urls.py        # Replace old Firebase URLs in .docx with new bucket URLs
├── urls.txt               # Input file: one site URL per line
├── requirements.txt       # Python dependencies
└── README.md
```

---

## Scripts

### 1. `scrape_logos.py`
Reads a list of website URLs, scrapes the best available logo for each site, and saves them locally.

**Strategy priority** (mirrors what browsers show in the tab):
1. `<link rel="icon">` — largest PNG/SVG/WebP found in the page `<head>`
2. `<link rel="apple-touch-icon">` — high-res iOS icon
3. Clearbit Logo API
4. `/favicon.ico`
5. Google Favicon Service

**Usage:**
```bash
python scrape_logos.py --input urls.txt --out-dir logos
```

**Output:**
- `logos/<domain>.png` — downloaded logo for each site
- `logos/_logo_map.csv` — mapping of site → logo URL → saved file → strategy used

---

### 2. `check_and_download.py`
Reads all Firebase Storage image URLs from a `.docx` file, checks which are still accessible, downloads the working ones, and lists the broken ones.

**Usage:**
```bash
python check_and_download.py --input your_doc.docx --out-dir downloaded_images
```

**Output:**
- `downloaded_images/<filename>` — all successfully downloaded images
- `downloaded_images/_BROKEN_IMAGES.txt` — list of URLs that failed

---

### 3. `replace_urls.py`
Replaces all old Firebase Storage URLs inside a `.docx` file with a new bucket base URL, preserving original filenames.

**Usage:**
```bash
python replace_urls.py \
  --input  original.docx \
  --output updated.docx \
  --new-base "https://storage.googleapis.com/YOUR-BUCKET-NAME"
```

---

## Setup

### Requirements
```bash
pip install -r requirements.txt
```

> `check_and_download.py` and `replace_urls.py` use Python stdlib only — no extra packages needed for those.

### Python Version
Python 3.6 or newer required.

### Windows / MSYS2 Note
If you see `SSL: CERTIFICATE_VERIFY_FAILED` errors, always use `python` (not `py`) to run scripts inside a virtualenv:
```powershell
python script.py   # ✅ uses venv
py script.py       # ❌ may bypass venv and fail SSL
```

---

## Typical Workflow

1. **Check which Firebase images are still alive and download them:**
   ```bash
   python check_and_download.py --input your_doc.docx --out-dir downloaded_images
   ```

2. **Re-upload downloaded images to your new bucket.**  
   Re-take screenshots for any listed in `_BROKEN_IMAGES.txt`.

3. **Scrape logos for all tools:**
   ```bash
   python scrape_logos.py --input urls.txt --out-dir logos
   ```

4. **Update the .docx with the new bucket URLs:**
   ```bash
   python replace_urls.py --input your_doc.docx --output updated.docx \
     --new-base "https://storage.googleapis.com/YOUR-BUCKET-NAME"
   ```

---

## `urls.txt` Format

One URL per line. Lines starting with `#` are ignored.

```
https://chat.openai.com
https://www.grammarly.com
# this line is a comment and will be skipped
https://huggingface.co
```
