import subprocess
import time
import xml.etree.ElementTree as ET
import json
import os

ADB_PATH = os.path.expanduser("~/Library/Android/sdk/platform-tools/adb")

EVEN_MORE_PAGES = {
    "storage_settings": "android.settings.INTERNAL_STORAGE_SETTINGS",
    "date_settings": "android.settings.DATE_SETTINGS",
    "language_settings": "android.settings.LOCALE_SETTINGS",
    "keyboard_settings": "android.settings.INPUT_METHOD_SETTINGS",
    "about_phone": "android.settings.DEVICE_INFO_SETTINGS",
    "cast_settings": "android.settings.CAST_SETTINGS",
    "default_apps": "android.settings.MANAGE_DEFAULT_APPS_SETTINGS",
}

def dump_ui(filename="/sdcard/window_dump.xml", local_name="screen.xml"):
    subprocess.run([ADB_PATH, "shell", "uiautomator", "dump", filename], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run([ADB_PATH, "pull", filename, local_name], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return local_name

def parse_settings_screen(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    elements = []
    for elem in root.iter("node"):
        label = elem.attrib.get("text", "") or elem.attrib.get("content-desc", "")
        checkable = elem.attrib.get("checkable") == "true"
        if label or checkable:
            elements.append({
                "label": label,
                "checkable": checkable,
                "checked": elem.attrib.get("checked") == "true",
            })
    return elements

def explore_and_append(output_file="data/raw_device_states.jsonl"):
    with open(output_file, 'a') as f:
        for name, intent in EVEN_MORE_PAGES.items():
            print(f"Exploring {name}...")
            subprocess.run([ADB_PATH, "shell", "am", "force-stop", "com.android.settings"], check=True)
            subprocess.run([ADB_PATH, "shell", "am", "start", "-a", intent], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(3)
            
            try:
                xml_file = dump_ui()
                elements = parse_settings_screen(xml_file)
                state_record = {
                    "page_name": name,
                    "intent": intent,
                    "ui_elements": elements
                }
                f.write(json.dumps(state_record) + "\\n")
                print(f"Found {len(elements)} elements.")
            except Exception as e:
                print(f"Skipping {name}: {e}")

if __name__ == "__main__":
    explore_and_append()
