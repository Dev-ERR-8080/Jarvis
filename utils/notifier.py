import threading
from plyer import audio, notification
from winotify import Notification

def show_notification(title, message,timeout=5):
    notification.notify(
        title=title,
        message=message,
        timeout=timeout  # seconds
    )
    
def show_status_toast(title, message, sound=True):
    """
    Sends a Windows 10+ native notification (safe from WNDPROC errors).
    """
    try:
        def _notify():
            toast = Notification(
                app_id="Jarvis Assistant",
                title=title,
                msg=message,
                duration="short",
                icon=r"D:\jarvis\assets\jarvis_icon.ico"  # optional path
            )
            if sound:
                toast.set_audio(audio.Default, loop=False)
            toast.show()

        threading.Thread(target=_notify, daemon=True).start()

    except Exception as e:
        print(f"[TOAST ERROR] {e}")
        print(f"[STATUS] {title}: {message}")