import subprocess
import time
import xml.etree.ElementTree as ET
import json
import os

ADB_PATH = os.path.expanduser("~/Library/Android/sdk/platform-tools/adb")

# A broader list of Android Settings Intents to scrape for an exhaustive SLM
MORE_PAGES = {
    "location_settings": "android.settings.LOCATION_SOURCE_SETTINGS",
    "security_settings": "android.settings.SECURITY_SETTINGS",
    "apps_settings": "android.settings.APPLICATION_SETTINGS",
    "sync_settings": "android.settings.SYNC_SETTINGS",
    "nfc_settings": "android.settings.NFC_SETTINGS",
    "data_roaming": "android.settings.DATA_ROAMING_SETTINGS",
    "network_operator": "android.settings.NETWORK_OPERATOR_SETTINGS",
    "privacy_settings": "android.settings.PRIVACY_SETTINGS",
    "notification_settings": "android.settings.ACTION_APP_NOTIFICATION_SETTINGS"
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
        for name, intent in MORE_PAGES.items():
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
