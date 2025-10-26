# from utils.system_actions import open_app
# from pywinauto.keyboard import send_keys
# from pywinauto import Desktop
# from datetime import datetime
# import json

# class NotionInteraction:
#     def __init__(self, page_title=".*"):
#         self.page_title = page_title
#         self.app = None
#         self.task_counter = 1
#         self.notion_path = r"C:\Users\reddy\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Notion.lnk"

#     def launch_notion(self):
#         open_app("notion")
#         return "✅ Launched Notion application"
        
#     def connect_to_notion(self):
#         try:
#             self.app = Desktop(backend="uia").window(title_re=self.page_title)
#             if not self.app.exists():
#                 return f"❌ No Notion page found with pattern: {self.page_title}"
#             return f"✅ Connected to page: {self.app.window_text()}"
#         except Exception as e:
#             return f"❌ Could not connect to Notion page: {e}"
        
#     def add_task(self, task_text, email_source=None, due_time=None, added_to_calendar=False, numbered=True):
#         if not self.app:
#             return "⚠️ Not connected to any Notion page"

#         try:
#             prefix = f"{self.task_counter}. " if numbered else "- "
#             details = f"{prefix}{task_text}\n"
#             if email_source:
#                 details += f"   || From: {email_source}\n"
#             if due_time:
#                 if isinstance(due_time, datetime):
#                     details += f"   || Due: {due_time.strftime('%Y-%m-%d %H:%M')}\n"
#                 else:
#                     details += f"   || Due: {due_time}\n"
#             details += f"   || Calendar: {'Yes' if added_to_calendar else 'No'}"

#             self.app.set_focus()
#             send_keys(details)
#             send_keys("{ENTER}")

#             if numbered:
#                 self.task_counter += 1

#             return f"✅ Task added:\n{details}"
#         except Exception as e:
#             return f"❌ Failed to add task: {e}"

#     def add_parsed_jd_to_page(self, jd_data: dict, page_title=None):
#         """
#         Types a parsed JD dict into the current (or new) Notion page in a nice format.
#         """
#         if not self.app:
#             return "⚠️ Not connected to any Notion page"

#         try:
#             self.app.set_focus()

#             # Optional: create a new page
#             if page_title:
#                 send_keys("^n")  # Ctrl+N to create new page
#                 send_keys(page_title)
#                 send_keys("{ENTER}")
#                 send_keys("{ENTER}")

#             # Type JD details
#             send_keys("# Job Description Summary{ENTER}{ENTER}")

#             for section, value in jd_data.items():
#                 send_keys(f"## {section}{ENTER}")

#                 if isinstance(value, list):
#                     for item in value:
#                         send_keys(f"- {item}{ENTER}")
#                 elif isinstance(value, dict):
#                     for k, v in value.items():
#                         send_keys(f"- {k}: {v}{ENTER}")
#                 else:
#                     send_keys(f"{value}{ENTER}")

#                 send_keys("{ENTER}")

#             return "✅ JD summary typed into Notion page."
#         except Exception as e:
#             return f"❌ Failed to type JD into Notion: {e}"

#     def close_notion(self):
#         if not self.app:
#             return "⚠️ Notion not running"
#         try:
#             self.app.close()
#             return "✅ Notion closed successfully"
#         except Exception as e:
#             return f"❌ Failed to close Notion: {e}"
import os
from notion_client import Client
from dotenv import load_dotenv
load_dotenv()

class NotionInteraction:
    def __init__(self, token=None, parent_page_id=None):
        """
        Initializes the Notion client.

        Args:
            token (str): The Notion API integration token. It's recommended
                         to use an environment variable for this.
            parent_page_id (str): The ID of the parent page where new pages will be created.
                                  This is a required parameter for creating a new page in Notion.
        """
        if token is None or token.strip() == "":
            token = os.getenv("NOTION_API_KEY")

        if not token or token.strip() == "":
            raise ValueError("Notion API token not provided. Set it in the environment variable 'NOTION_API_KEY' or pass it as an argument.")

        self.client = Client(auth=token)
        self.parent_page_id = parent_page_id

    def add_parsed_jd_to_page(self, jd_data: dict, page_title=None):
        """
        Creates a new Notion page and adds the parsed JD data to it.

        Args:
            jd_data (dict): The dictionary containing parsed job description data.
            page_title (str, optional): The title for the new Notion page. 
                                        If not provided, a default title is generated.

        Returns:
            str: A status message indicating success or failure.
        """
        if not self.parent_page_id:
            return "❌ Cannot add page. A parent page ID is required to create a new page."

        if not page_title:
            # Safely get the company name from the nested dictionary
            company_name = jd_data.get("Company", {}).get("Name", "Unknown Company")
            role = jd_data.get("Role", {}).get("Designation", "Job Description")
            page_title = f"{company_name} - {role}"
            
        try:
            new_page = self.client.pages.create(
                parent={"page_id": self.parent_page_id},
                properties={
                    "title": [
                        {
                            "text": {
                                "content": page_title
                            }
                        }
                    ]
                }
            )
            
            new_page_id = new_page["id"]
            blocks = []
            
            blocks.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [
                        {"text": {"content": "Job Description Summary"}}
                    ]
                }
            })

            # Iterate through the JD data to create a structured page
            for section, value in jd_data.items():
                # Add a sub-heading for each section
                blocks.append({
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [
                            {"text": {"content": section.replace('_', ' ').title()}}
                        ]
                    }
                })

                if isinstance(value, list):
                    for item in value:
                        blocks.append({
                            "object": "block",
                            "type": "bulleted_list_item",
                            "bulleted_list_item": {
                                "rich_text": [
                                    {"text": {"content": str(item)}}
                                ]
                            }
                        })
                elif isinstance(value, dict):
                    # Recursively handle nested dictionaries
                    for k, v in value.items():
                        # Handle lists within nested dictionaries (like 'Responsibilities')
                        if isinstance(v, list):
                            blocks.append({
                                "object": "block",
                                "type": "bulleted_list_item",
                                "bulleted_list_item": {
                                    "rich_text": [
                                        {"text": {"content": f"{k.replace('_', ' ').title()}:"}}
                                    ]
                                }
                            })
                            for sub_item in v:
                                blocks.append({
                                    "object": "block",
                                    "type": "bulleted_list_item",
                                    "bulleted_list_item": {
                                        "rich_text": [
                                            {"text": {"content": f"  - {sub_item}"}}
                                        ]
                                    }
                                })
                        else:
                            blocks.append({
                                "object": "block",
                                "type": "bulleted_list_item",
                                "bulleted_list_item": {
                                    "rich_text": [
                                        {"text": {"content": f"{k.replace('_', ' ').title()}: {str(v)}"}}
                                    ]
                                }
                            })
                else:
                    # For simple values, add a paragraph block
                    blocks.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {"text": {"content": str(value)}}
                            ]
                        }
                    })

            self.client.blocks.children.append(
                block_id=new_page_id,
                children=blocks
            )

            page_url = f"https://www.notion.so/{new_page_id.replace('-', '')}"
            return f"✅ JD summary added to Notion page successfully! URL: {page_url}"

        except Exception as e:
            return f"❌ Failed to add JD to Notion page: {e}"