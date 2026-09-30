import subprocess
import time
import xml.etree.ElementTree as ET
import json
import os

ADB_PATH = os.path.expanduser("~/Library/Android/sdk/platform-tools/adb")

# A list of standard Android Settings Intents to scrape
SETTINGS_PAGES = {
    "main_settings": "android.settings.SETTINGS",
    "wifi_settings": "android.settings.WIFI_SETTINGS",
    "bluetooth_settings": "android.settings.BLUETOOTH_SETTINGS",
    "display_settings": "android.settings.DISPLAY_SETTINGS",
    "sound_settings": "android.settings.SOUND_SETTINGS",
    "developer_settings": "android.settings.APPLICATION_DEVELOPMENT_SETTINGS",
    "battery_settings": "android.intent.action.POWER_USAGE_SUMMARY",
    "wireless_settings": "android.settings.WIRELESS_SETTINGS",
    "accessibility_settings": "android.settings.ACCESSIBILITY_SETTINGS",
    "airplane_mode": "android.settings.AIRPLANE_MODE_SETTINGS"
}

def dump_ui(filename="/sdcard/window_dump.xml", local_name="screen.xml"):
    """Dumps the UI XML using UIAutomator and pulls it."""
    subprocess.run([ADB_PATH, "shell", "uiautomator", "dump", filename], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run([ADB_PATH, "pull", filename, local_name], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return local_name

def parse_settings_screen(xml_file):
    """Parses the accessibility tree specifically looking for settings toggles and values."""
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    elements = []
    for elem in root.iter("node"):
        text = elem.attrib.get("text", "")
        desc = elem.attrib.get("content-desc", "")
        res_id = elem.attrib.get("resource-id", "")
        checkable = elem.attrib.get("checkable") == "true"
        checked = elem.attrib.get("checked") == "true"
        clickable = elem.attrib.get("clickable") == "true"
        
        label = text or desc
        
        if label or checkable:
            elements.append({
                "id": res_id if res_id else f"node_{len(elements)}",
                "label": label,
                "checkable": checkable,
                "checked": checked,
                "clickable": clickable
            })
            
    return elements

def collect_data(output_file="data/raw_device_states.jsonl"):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w') as f:
        for name, intent in SETTINGS_PAGES.items():
            print(f"Opening {name} ({intent})...")
            # Force stop settings to ensure clean start
            subprocess.run([ADB_PATH, "shell", "am", "force-stop", "com.android.settings"], check=True)
            # Launch intent
            subprocess.run([ADB_PATH, "shell", "am", "start", "-a", intent], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            time.sleep(3) # Wait for screen to render and settle
            
            print(f"Dumping UI for {name}...")
            try:
                xml_file = dump_ui()
                elements = parse_settings_screen(xml_file)
                
                state_record = {
                    "page_name": name,
                    "intent": intent,
                    "ui_elements": elements
                }
                
                f.write(json.dumps(state_record) + "\\n")
                print(f"Collected {len(elements)} elements for {name}.")
            except Exception as e:
                print(f"Failed to collect {name}: {e}")
                
if __name__ == "__main__":
    collect_data()
