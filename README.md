# Site Logo Scraper

A lightweight Python script that reads a list of website URLs and automatically downloads the best available logo for each site.

---

## Project Structure

```
.
├── scrape_logos.py   # Main scraper script
├── urls.txt          # Input file: one site URL per line
├── requirements.txt  # Python dependencies
└── README.md
```

---

## How It Works

For each URL, the script fetches the homepage and tries the following strategies in order, stopping at the first success:

| Priority | Strategy | Description |
|----------|----------|-------------|
| 1 | `<link rel="icon">` | Largest PNG/SVG/WebP from page `<head>` — same icon browsers show in the tab |
| 2 | `<link rel="apple-touch-icon">` | High-res iOS home screen icon |
| 3 | Clearbit Logo API | Clean brand logo from Clearbit |
| 4 | `/favicon.ico` | Classic root favicon fallback |
| 5 | Google Favicon Service | Last resort at 128px |

---

## Setup

### 1. Clone the repo and create a virtual environment

```bash
git clone <repo-url>
cd site-logo-scraper

python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your URLs to `urls.txt`

One URL per line. Lines starting with `#` are ignored:

```
https://chat.openai.com
https://www.grammarly.com
# this line is a comment
https://huggingface.co
```

---

## Usage

```bash
python scrape_logos.py --input urls.txt --out-dir logos
```

| Argument | Default | Description |
|----------|---------|-------------|
| `--input` | required | Path to the URLs text file |
| `--out-dir` | `logos` | Folder to save downloaded logos |

---

## Output

```
logos/
├── grammarly.com.png
├── huggingface.co.ico
├── openai.com.png
├── ...
└── _logo_map.csv
```

**`_logo_map.csv` columns:**

| Column | Description |
|--------|-------------|
| `site` | Original URL from input file |
| `domain` | Extracted domain |
| `logo_url` | The URL the logo was fetched from |
| `saved_file` | Local path of the saved file |
| `status` | `ok:<strategy>` or `failed` |

---

## Requirements

- Python 3.6+
- `requests`
- `beautifulsoup4`

### Windows / MSYS2 Note
Always use `python` instead of `py` inside a virtualenv to avoid SSL errors:

```powershell
python scrape_logos.py --input urls.txt --out-dir logos   # correct
py scrape_logos.py --input urls.txt --out-dir logos       # may bypass venv
```