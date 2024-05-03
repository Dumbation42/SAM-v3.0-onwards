print("SAM V3.1")
print("By Dumbation")
import time
time.sleep(1)
print("loading...")
import subprocess
import requests
import difflib
print("loaded!")
LOCAL_BOT_FILE = "D:/BTI_Programs/bot.py"
REPO_URL = "https://raw.githubusercontent.com/Dumbation42/SAM-v3.0-onwards/main/bot.py"

def fetch_remote_bot():
    print("obtaining online copy of bot.py")
    """Fetch the latest bot.py from the GitHub repository."""
    try:
        response = requests.get(REPO_URL)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Failed to fetch online bot.py: {e}")
        return None

def files_differ(local_text, remote_text):
    print("comparing files")
    """Check if there are differences between the local and remote bot.py."""
    local_lines = local_text.splitlines(keepends=True)
    remote_lines = remote_text.splitlines(keepends=True)
    diff = list(difflib.unified_diff(local_lines, remote_lines))
    return len(diff) > 0

def run_bot():
    print("starting bot.py")
    """Starts the bot.py script."""
    global bot_process
    bot_process = subprocess.Popen(['python', 'bot.py'])

def stop_bot():
    print("stopping bot.py")
    """Stops the bot.py script gracefully."""
    global bot_process
    if bot_process:
        bot_process.terminate()
        bot_process.wait()

def run_update():
    print("updating bot.py")
    """Runs the update.py script."""
    subprocess.run(['python', 'update.py'])
    print("update successful")

def check_and_update():
    """Check for updates and apply them if needed."""
    global bot_process
    try:
        with open(LOCAL_BOT_FILE, 'r', encoding='utf-8') as file:
            local_bot_text = file.read()

        remote_bot_text = fetch_remote_bot()
        if remote_bot_text is None:
            print("couldn't obtain online copy")
            return

        if files_differ(local_bot_text, remote_bot_text):
            stop_bot()
            run_update()
            run_bot()
        else:
            print("bot.py up to date")
    except FileNotFoundError:
        print("local bot.py not found.")

if __name__ == "__main__":
    run_bot()
    while True:
        check_and_update()
        time.sleep(900)
