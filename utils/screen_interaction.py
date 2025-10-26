from pywinauto.application import Application
from pywinauto import Desktop

class ScreenInteraction:
    def __init__(self):
        self.app = None

    def find_window(self, title):
        """Connects to a running application by its window title."""
        try:
            self.app = Desktop(backend="uia").window(title_re=f".*{title}.*")
            if not self.app.exists():
                return f"Application window with title containing '{title}' not found."
            return f"Connected to '{self.app.window_text()}'"
        except Exception as e:
            return f"Failed to connect to application: {e}"

    def minimize_window(self, title):
        """Minimize a window by title."""
        try:
            window = Desktop(backend="uia").window(title_re=f".*{title}.*")
            window.minimize()
            return f"Window '{title}' minimized."
        except Exception as e:
            return f"Failed to minimize window: {e}"

    def close_window(self, title):
        """Close a window by title."""
        try:
            window = Desktop(backend="uia").window(title_re=f".*{title}.*")
            window.close()
            return f"Window '{title}' closed."
        except Exception as e:
            return f"Failed to close window: {e}"

    def click_button(self, window_title, button_name):
        """Click a button inside a window."""
        try:
            app = Desktop(backend="uia").window(title_re=f".*{window_title}.*")
            button = app.child_window(title=button_name, control_type="Button")
            button.click_input()
            return f"Clicked button '{button_name}' in window '{window_title}'."
        except Exception as e:
            return f"Failed to click button: {e}"

    def type_in_textbox(self, window_title, text_to_type):
        """Find a text box and type text into it."""
        try:
            app = Desktop(backend="uia").window(title_re=f".*{window_title}.*")
            edit_control = app.child_window(control_type="Edit")
            edit_control.set_focus()
            edit_control.type_keys(text_to_type, with_spaces=True)
            return f"Typed '{text_to_type}' into the window titled '{window_title}'."
        except Exception as e:
            return f"Failed to type text: {e}"

    def read_text_from_active_window(self):
        """Reads all accessible text from the currently active window."""
        try:
            active_window = Desktop(backend="uia").active()
            text_content = ""
            for child in active_window.descendants():
                if child.element_info.control_type in ["Edit", "Text"]:
                    text = child.window_text()
                    if text:
                        text_content += text + "\n"
            return text_content if text_content else "No text controls found."
        except Exception as e:
            return f"Failed to read text: {e}"
