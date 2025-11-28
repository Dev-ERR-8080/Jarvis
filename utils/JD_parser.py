# parse_jd.py
import os
from bs4 import BeautifulSoup
import json
from models.model import GeminiModel
from utils.notion_interaction import NotionInteraction
from dotenv import load_dotenv
load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_API_KEY")  
PARENT_PAGE_ID = os.getenv("NOTION_PARENT_PAGE_ID")

try:
    notion = NotionInteraction(token=NOTION_TOKEN, parent_page_id=PARENT_PAGE_ID)
except ValueError as e:
    print(e)
    exit()

def parse_jd_from_file(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "lxml")

    data = {}

    # --- Step 1: Extract data from the main table ---
    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        
        # Check if the row has at least two columns and is not the nested table container
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
                # Get the link from the 'a' tag
                link = tds[1].find('a')
                if link:
                    data["company_website"] = link['href']
            elif "job profile" in label_lower:
                data["job_profile"] = value
            elif "pre-requirements" in label_lower:
                data["pre_requirements"] = value
            elif "tentative date of joining" in label_lower:
                data["tentative_date_of_joining"] = value

    # --- Step 2: Extract salary and location from the nested table ---
    # Find the nested table by its ID
    job_details_table = soup.find("table", {"id": "tblStreamData"})

    if job_details_table:
        # Get the first data row (the second tr, as the first is the header)
        data_row = job_details_table.find_all("tr")[1]
        
        # Get all the td elements in that row
        details_tds = data_row.find_all("td")

        # The order is: Program/Stream, Designation, Eligibility, Salary, Location
        # So we can access them by index
        if len(details_tds) >= 5:
            # Assuming the order is fixed in the table
            data["designation"] = details_tds[1].get_text(strip=True)
            data["eligibility_details"] = details_tds[2].get_text(strip=True)
            data["salary_package"] = details_tds[3].get_text(strip=True)
            data["job_location"] = details_tds[4].get_text(strip=True)
    summary = summerize(data)
    return data


def summerize(jd_data: dict):
    
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
        
        print(notion.add_parsed_jd_to_page(
            gemini_response_json, 
            page_title=gemini_response_json.get("Company", {}).get("Name", "Job Profile")
        ))
        
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse Gemini's JSON response: {e}")
        print("Raw response:", cleaned_response)
        # Fallback to adding raw text if JSON parsing fails
        notion.add_parsed_jd_to_page({"Summary": cleaned_response})
        
    except Exception as e:
        print(f"❌ An error occurred while adding to Notion: {e}")


if __name__ == "__main__":
    result = parse_jd_from_file("C:\\Users\\reddy\\Downloads\\NRNwbOzHTIbgOMzbCMDr4A==.htm")
    print(json.dumps(result, indent=2, ensure_ascii=False))