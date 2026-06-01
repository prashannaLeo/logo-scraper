import csv
import argparse
import requests
import re
import os
import urllib3
import mimetypes
# Disable SSL verification warnings to bypass potential local certificate errors
urllib3.disable_warnings()
# Path to the logo with the typo
old_name = os.path.join("logos", "ritesonic.com.png")
new_name = os.path.join("logos", "writesonic.com.png")

if os.path.exists(old_name):
    os.rename(old_name, new_name)
    print(f"✅ Renamed {old_name} to {new_name}")
else:
    print("ℹ️ File 'ritesonic.com.png' not found; it may already be fixed.")

txt_file = "image_list.txt"

if os.path.exists(txt_file):
    with open(txt_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Replace the typo with the correct name
    if "ritesonic.com.png" in content:
        new_content = content.replace("ritesonic.com.png", "writesonic.com.png")
        
        with open(txt_file, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"✅ Updated {txt_file}: 'ritesonic' changed to 'writesonic'")
    else:
        print(f"ℹ️ No typo found in {txt_file}.")
else:
    print(f"❌ {txt_file} not found. Make sure you have run the scraper first.")

def is_local_file(path):
    """
    Checks if a given string is a path to a local file.
    """
    return os.path.isfile(path)

def is_url(path):
    """
    Checks if a given string is a URL.
    """
    try:
        r = requests.head(path)
        return r.status_code == 200
    except requests.exceptions.RequestException:
        return False

def upload_image(file_or_url, upload_api_url):
    """
    Uploads a local image file or an image from a URL to the specified API.
    
    Args:
        file_or_url (str): The local file path or URL of the image.
        upload_api_url (str): The URL of the upload API endpoint.
    
    Returns:
        tuple: (original_path_or_url, download_url, status)
    """
    print(f"\nProcessing image: {file_or_url}")
    
    if is_local_file(file_or_url):
        print(f"  Detected as local file. Reading...")
        # Local file path
        try:
            with open(file_or_url, 'rb') as f:
                image_data = f.read()
                filename = os.path.basename(file_or_url)
                mime_type, _ = mimetypes.guess_type(file_or_url)
                if not mime_type:
                    mime_type = 'application/octet-stream' # Fallback
                files = {'file': (filename, image_data, mime_type)}
                return perform_upload(upload_api_url, files, file_or_url)
        except Exception as e:
            print(f"  ❌ Error opening local file {file_or_url}: {e}")
            return (file_or_url, None, f"Failed: {e}")

    elif is_url(file_or_url):
        print(f"  Detected as URL. Fetching...")
        # URL - needs downloading before uploading
        try:
            r_download = requests.get(file_or_url, stream=True, verify=False, timeout=15)
            if r_download.status_code == 200:
                print(f"  Successfully fetched remote image ({len(r_download.content)} bytes).")
                # Try to guess a filename from the URL, or use a default
                filename_base = file_or_url.split('/')[-1]
                if not filename_base or '?' in filename_base:
                     filename_base = "downloaded_image"
                
                mime_type = r_download.headers.get('content-type', 'application/octet-stream')
                files = {'file': (filename_base, r_download.content, mime_type)}
                return perform_upload(upload_api_url, files, file_or_url)
            else:
                 print(f"  ❌ Error downloading image from URL {file_or_url}: HTTP {r_download.status_code}")
                 return (file_or_url, None, f"Failed: HTTP {r_download.status_code}")
        except Exception as e:
            print(f"  ❌ Error fetching remote image from URL {file_or_url}: {e}")
            return (file_or_url, None, f"Failed: {e}")

    else:
        print(f"  ❌ Invalid path or URL: {file_or_url}")
        return (file_or_url, None, "Invalid path/URL")

def perform_upload(upload_api_url, files_payload, original_path_or_url):
    """
    Actually performs the POST request to upload the image.
    
    Args:
        upload_api_url (str): The URL of the upload API.
        files_payload (dict): The payload containing the file data.
        original_path_or_url (str): The original source path/URL.
    
    Returns:
        tuple: (original_path_or_url, download_url, status)
    """
    try:
        # Construct the full upload URL with the query parameter `file_name`
        # Using a sanitized domain name from the original source as the filename.
        # Let's derive a simple name from the original source for the file_name parameter.
        if is_local_file(original_path_or_url):
            filename_for_api = os.path.basename(original_path_or_url)
        else: # it's a URL
            domain_match = re.search(r'//(www\.)?([^/]+)', original_path_or_url)
            if domain_match:
                filename_for_api = domain_match.group(2)
            else:
                filename_for_api = "image" # fallback

        # Sanitize for filename in the query parameter (simple regex, match what we see in the images)
        filename_for_api = re.sub(r"[^\w\-.]", "_", filename_for_api)
        api_with_params = f"{upload_api_url}?file_name={filename_for_api}"

        print(f"  Uploading to: {api_with_params}...")

        # No custom headers needed, requests will handle content-type with the files param
        response = requests.post(api_with_params, files=files_payload, verify=False, timeout=30)
        
        if response.status_code == 200:
            resp_json = response.json()
            download_url = resp_json.get('downloadUrl')
            print(f"  ✅ Upload successful! Download URL: {download_url}")
            return (original_path_or_url, download_url, "Upload OK")
        else:
            print(f"  ❌ Upload failed: HTTP {response.status_code}. Details: {response.text}")
            return (original_path_or_url, None, f"Upload Failed: HTTP {response.status_code}")
    except requests.exceptions.RequestException as e:
         print(f"  ❌ Request exception during upload for {original_path_or_url}: {e}")
         return (original_path_or_url, None, f"Request Failed: {e}")
    except ValueError:
        print(f"  ❌ Failed to parse JSON response from upload API for {original_path_or_url}. Details: {response.text}")
        return (original_path_or_url, None, "Failed: JSON Parse Error")
def get_successful_uploads(mapping_file):
    """
    Reads the existing CSV and returns a set of filenames 
    that were successfully uploaded.
    """
    successful_files = set()
    if os.path.exists(mapping_file):
        try:
            with open(mapping_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Check if the 'Upload Status' column says 'Upload OK'
                    if row.get('Upload Status') == 'Upload OK':
                        # Get just the filename from the 'Original Source' path
                        filename = os.path.basename(row.get('Original Source', ''))
                        successful_files.add(filename)
        except Exception as e:
            print(f"⚠️ Could not read existing mapping file: {e}")
    return successful_files
def main():
    """
    Main function to process images for uploading and saving download URLs.
    """
    parser = argparse.ArgumentParser(description="Upload images to a public file API.")
    parser.add_argument("image_list", help="A text file containing one image local path or URL per line.")
    # The endpoint URL from the image provided
    api_endpoint = "https://api-dev.futurestore.ai/api/v1/customer/files/upload-file-public"
    
    args = parser.parse_args()

    # Read the list of images
    try:
        with open(args.image_list, 'r', encoding='utf-8') as f:
            images = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
    except FileNotFoundError:
        print(f"Error: The file '{args.image_list}' was not found.")
        return
    except Exception as e:
        print(f"Error reading image list file: {e}")
        return

    if not images:
        print(f"No valid image paths/URLs found in '{args.image_list}'.")
        return
    # Save the mapping of original to download URL to a new file
    output_mapping_file = "uploaded_image_mapping.csv"
    # Process each image and collect results
     # 2. ADD THIS LINE: Get already successful uploads from the CSV
    already_uploaded = get_successful_uploads(output_mapping_file)

    # 3. ADD THIS LINE: Initialize results with existing data if the file exists
    results = []
    if os.path.exists(output_mapping_file):
        with open(output_mapping_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader) # Skip header
            for row in reader:
                results.append(tuple(row))

    print(f"Found {len(images)} images to process. Uploading to API...")    
     # Define the directory where scrape_logos.py saved the files
    LOGOS_DIR = "logos" 
    for filename in images:
        if filename in already_uploaded:
            print(f"⏩ Skipping {filename} (Already exists in mapping with 'Upload OK')")
            continue
        # Join the directory name with the filename to get a valid local path
        full_path = os.path.join(LOGOS_DIR, filename)
        if not os.path.exists(full_path):
            print(f"⚠️ File not found: {full_path}")
            continue
        result = upload_image(full_path, api_endpoint)
        results.append(result)

    try:
        import csv
        with open(output_mapping_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Original Source', 'Download URL', 'Upload Status'])
            for original_path, download_url, status in results:
                writer.writerow([original_path, download_url, status])
        print(f"\nResults saved to '{output_mapping_file}'.")
    except Exception as e:
        print(f"Error saving results to '{output_mapping_file}': {e}")

if __name__ == "__main__":
    main()