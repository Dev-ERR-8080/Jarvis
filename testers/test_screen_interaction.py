from utils.notion_interaction import NotionInteraction
from datetime import datetime

def test_notion():
    notion = NotionInteraction(title_re=".*New page.*")

    print("[TEST] Connecting to Notion...")
    print(notion.connect_to_notion())

    print("[TEST] Adding task from email...")
    response = notion.add_task(
        task_text="Follow up on project proposal",
        email_source="manager@company.com",
        due_time=datetime.now().replace(hour=18, minute=0),
        added_to_calendar=True
    )
    print(response)

    

if __name__ == "__main__":
    test_notion()
