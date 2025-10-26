# --- Imports ---
import argparse
import os
import json
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

# --- Your other modules ---
# Assuming these are in your project
from models.model import GeminiModel
from utils.JD_parser import PARENT_PAGE_ID
from utils.notion_interaction import NotionInteraction
from utils.system_actions import run_shell


# --- Environment Setup ---
load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_API_KEY") 
PARENT_PAGE_ID = os.getenv("NOTION_PARENT_PAGE_ID")

try:
    notion = NotionInteraction(token=NOTION_TOKEN, parent_page_id=PARENT_PAGE_ID)
except ValueError as e:
    print(e)
    exit()

# --- Notion Interaction Class ---
# This class remains the same as your corrected version
print(run_shell('"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222 --user-data-dir=C:\\tmp\\chrome_dev_test'))

def attach_to_chrome(debug_address="127.0.0.1:9222"):
    opts = Options()
    opts.debugger_address = debug_address
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    return driver

def launch_with_profile(user_data_dir, profile_dir="Default", headless=False):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument(f"--user-data-dir={user_data_dir}")
    opts.add_argument(f"--profile-directory={profile_dir}")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    return driver

def parse_drives_from_html(html, base_url=None):
    # This is the corrected function you already have
    soup = BeautifulSoup(html, "html.parser")
    drives = []
    # ... (rest of your drive parsing logic here) ...
    main_table = soup.find("table", {"id": "ctl00_ContentPlaceHolder1_gdvPlacement"})
    if not main_table:
        print("[-] Could not find the main placement drives table.")
        return []
    rows = main_table.find_all("tr", class_=["tabel_grid_white", "tabel_grid_gray"])
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 5:
            continue
        drive_date = cols[0].get_text(strip=True)
        register_by = cols[1].get_text(strip=True)
        company = cols[2].get_text(strip=True)
        status = cols[4].get_text(strip=True).lower()
        registered = cols[5].get_text(strip=True).lower()
        job_link = None
        a_tag = cols[3].find("a", href=True)
        if a_tag:
            job_link = a_tag["href"]
            if base_url:
                job_link = urljoin(base_url, job_link)
        if status == "open" and registered != "click to cancel registration":
            drives.append({
                "drive_date": drive_date,
                "register_by": register_by,
                "company": company,
                "job_link": job_link,
                "status": status
            })
    return drives

# --- Your `JD_parser` Functions (adapted to take HTML string) ---
# This is a key part: The function no longer takes a file path
def parse_jd_from_html(html_content: str):
    soup = BeautifulSoup(html_content, "lxml")
    data = {}
    
    # ... (your parsing logic from parse_jd_from_file goes here) ...
    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) >= 2 and 'colspan' not in tds[0].attrs:
            label = tds[0].get_text(strip=True)
            value = tds[1].get_text(" ", strip=True)
            label_lower = label.lower()
            if "name of company" in label_lower:
                data["company_name"] = value
            elif "name & type of event" in label_lower:
                data["event_type"] = value
            elif "year (passing out)" in label_lower:
                data["passing_out_year"] = value
            elif "venue" in label_lower:
                data["venue"] = value
            elif "drive date" in label_lower:
                data["drive_date"] = value
            elif "last date of registration" in label_lower:
                data["last_date_of_registration"] = value
            elif "eligible gender" in label_lower:
                data["eligible_gender"] = value
            elif "bond details" in label_lower:
                data["bond_details"] = value
            elif "skills required" in label_lower:
                data["skills_required"] = value
            elif "about company" in label_lower:
                data["about_company"] = value
            elif "website" in label_lower:
                link = tds[1].find('a')
                if link:
                    data["company_website"] = link['href']
            elif "job profile" in label_lower:
                data["job_profile"] = value
            elif "pre-requirements" in label_lower:
                data["pre_requirements"] = value
            elif "tentative date of joining" in label_lower:
                data["tentative_date_of_joining"] = value

    job_details_table = soup.find("table", {"id": "tblStreamData"})
    if job_details_table:
        data_row = job_details_table.find_all("tr")[1]
        details_tds = data_row.find_all("td")
        if len(details_tds) >= 5:
            data["designation"] = details_tds[1].get_text(strip=True)
            data["eligibility_details"] = details_tds[2].get_text(strip=True)
            data["salary_package"] = details_tds[3].get_text(strip=True)
            data["job_location"] = details_tds[4].get_text(strip=True)
    return data

def summarize_and_save(jd_data: dict):
    gemini_model = GeminiModel()
    prompt = f"""
    You are an assistant helping a student with placement preparation.
    Summarize the following job description in a clean, structured way.
    
    {json.dumps(jd_data, indent=2)}
    
    Format the summary as a JSON object with the following keys:
    "Company", "type of event","Role", "Eligibility", "Package_Stipend", "Important_Dates", "Job Location", "Key_Notes", "LinkedIn", "What Company Do", "Size of the Company".
    Ensure the response is only the JSON object, with no introductory text or markdown.
    """
    
    gemini_response_text = gemini_model.generate_text(prompt)
    cleaned_response = gemini_response_text.strip().lstrip("```json").rstrip("```")
    
    try:
        gemini_response_json = json.loads(cleaned_response)
        if not isinstance(gemini_response_json, dict):
            raise TypeError("Gemini response is not a valid JSON object.")
        company_data = gemini_response_json.get("Company", "Job Profile")
        if isinstance(company_data, dict):
            page_title = company_data.get("Name", "Job Profile")
        else:
            # If it's not a dict, treat it as a simple string
            page_title = company_data
        print(notion.add_parsed_jd_to_page(
            gemini_response_json,
            page_title=page_title
        ))
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse Gemini's JSON response: {e}")
        print("Raw response:", cleaned_response)
        notion.add_parsed_jd_to_page({"Summary": cleaned_response})
    except Exception as e:
        print(f"❌ An error occurred while adding to Notion: {e}")


# --- The Main Orchestration Logic ---
def main_pipeline(drives_url, selenium_mode="attach", **kwargs):
    driver = None
    try:
        if selenium_mode == "attach":
            print(f"[+] Attaching to Chrome at {kwargs.get('debug_address')} ...")
            driver = attach_to_chrome(kwargs.get('debug_address'))
        else:
            if not kwargs.get("user_data_dir"):
                raise ValueError("user_data_dir is required in launch mode")
            print(f"[+] Launching Chrome with profile {kwargs.get('profile_dir')} (user_data_dir={kwargs.get('user_data_dir')}) ...")
            driver = launch_with_profile(**kwargs)
        
        print(f"[+] Opening drives URL: {drives_url}")
        driver.get(drives_url)
        try:
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "tr.tabel_grid_white, tr.tabel_grid_gray")))
        except:
            print("[-] Timed out waiting for table data. Parsing what's available...")

        drives_html = driver.page_source
        drives_list = parse_drives_from_html(drives_html, drives_url)
        print(f"✅ Found {len(drives_list)} open drives.")

        for drive in drives_list:
            
            print(f"[+] Processing JD for {drive['company']}...")
            if drive['job_link']:
                try:
                    driver.get(drive['job_link'])
                    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "tblStreamData")))
                    jd_html = driver.page_source
                    parsed_data = parse_jd_from_html(jd_html)
                    if parsed_data:
                        summarize_and_save(parsed_data)
                    else:
                        print(f"❌ Failed to parse JD for {drive['company']}.")
                except Exception as e:
                    print(f"❌ An error occurred while processing {drive['company']}'s JD: {e}")
            else:
                print(f"❌ No job link found for {drive['company']}.")
    
    finally:
        if driver and selenium_mode == "launch":
            driver.quit()

if __name__ == "__main__":
    # You must have your .env file with NOTION_API_KEY and NOTION_PARENT_PAGE_ID
    if not NOTION_TOKEN or not PARENT_PAGE_ID:
        print("❌ Please set NOTION_API_KEY and NOTION_PARENT_PAGE_ID in your .env file.")
        exit()

    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["attach", "launch"], default="attach")
    parser.add_argument("--debug-address", default="127.0.0.1:9222")
    parser.add_argument("--drives-url", required=True)
    parser.add_argument("--user-data-dir", help="Path to Chrome User Data directory")
    parser.add_argument("--profile-dir", default="Default")
    parser.add_argument("--headless", action="store_true")
    args = parser.parse_args()

    # The shell command is outside the main function, so it runs when the script starts
    # This is useful for 'attach' mode to ensure the browser is open
    run_shell(f'"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port={args.debug_address} --user-data-dir={args.user_data_dir}')
    
    # Wait for the browser to open before starting the pipeline
    time.sleep(5) 
    
    main_pipeline(
        drives_url=args.drives_url,
        selenium_mode=args.mode,
        debug_address=args.debug_address,
        user_data_dir=args.user_data_dir,
        profile_dir=args.profile_dir,
        headless=args.headless
    )