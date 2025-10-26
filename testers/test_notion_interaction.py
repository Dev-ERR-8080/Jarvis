from utils.notion_interaction import NotionInteraction
from datetime import datetime

def test_notion():
    notion = NotionInteraction(page_title=".*Gmails.*")

    print("[TEST] Connecting to Notion...")
    print(notion.launch_notion())
    print(notion.connect_to_notion())

    print("[TEST] Adding task from email...")
    print(notion.add_task(
        task_text="Follow up on project proposal",
        email_source="manager@company.com",
        due_time=datetime.now().replace(hour=18, minute=0),
        added_to_calendar=True
    ))
    print("[TEST] Adding simple task...")
    print(notion.add_task(
        task_text="Prepare for the meeting",
        numbered=False
    ))
    print("[TEST] Closing Notion...")
    print(notion.close_notion())

if __name__ == "__main__":
    test_notion()
