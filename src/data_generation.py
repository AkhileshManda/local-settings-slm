import os
import json
import random

# EXHAUSTIVE intent mapping across all possible Android OS features
INTENT_TEMPLATES = [
    # Connectivity & Networks
    ("Turn on wifi", "toggle_wifi", "wifi_settings"),
    ("Disconnect wireless internet", "toggle_wifi", "wifi_settings"),
    ("Turn on bluetooth", "toggle_bluetooth", "bluetooth_settings"),
    ("Turn off bluetooth", "toggle_bluetooth", "bluetooth_settings"),
    ("Turn on airplane mode", "toggle_airplane_mode", "airplane_mode"),
    ("Disable flight mode", "toggle_airplane_mode", "airplane_mode"),
    ("Turn on NFC", "toggle_nfc", "nfc_settings"),
    ("Disable contactless payments", "toggle_nfc", "nfc_settings"),
    ("Enable data roaming", "toggle_data_roaming", "data_roaming"),
    ("Turn off cellular data", "toggle_mobile_data", "network_operator"),
    ("Enable mobile data", "toggle_mobile_data", "network_operator"),
    ("Set network to 5G", "preferred_network_mode", "wireless_settings"),
    ("Turn on Wi-Fi calling", "toggle_wifi_calling", "wireless_settings"),
    ("Enable hotspot", "toggle_hotspot", "wireless_settings"),
    ("Turn off tethering", "toggle_hotspot", "wireless_settings"),
    ("Connect to VPN", "toggle_vpn", "wireless_settings"),

    # Display & Visuals
    ("Switch to dark mode", "toggle_dark_mode", "display_settings"),
    ("Turn off dark mode", "toggle_dark_mode", "display_settings"),
    ("Turn up the brightness", "set_brightness", "display_settings"),
    ("Turn on adaptive brightness", "toggle_adaptive_brightness", "display_settings"),
    ("Disable auto brightness", "toggle_adaptive_brightness", "display_settings"),
    ("Turn on eye comfort shield", "toggle_eye_comfort", "display_settings"),
    ("Disable blue light filter", "toggle_eye_comfort", "display_settings"),
    ("Change screen timeout", "set_screen_timeout", "display_settings"),
    ("Set refresh rate to 120Hz", "set_refresh_rate", "display_settings"),
    ("Enable always on display", "toggle_aod", "display_settings"),
    ("Turn off AOD", "toggle_aod", "display_settings"),
    ("Enable auto-rotate", "toggle_auto_rotate", "display_settings"),
    ("Lock screen rotation", "toggle_auto_rotate", "display_settings"),
    ("Change screen resolution", "set_screen_resolution", "display_settings"),
    ("Increase screen zoom", "set_screen_zoom", "display_settings"),
    ("Make the text bigger", "font_size_category", "accessibility_settings"),
    ("Change font style", "set_font_style", "display_settings"),

    # Sounds & Vibrations
    ("Turn the volume up", "set_volume", "sound_settings"),
    ("Mute my phone", "toggle_silent_mode", "sound_settings"),
    ("Turn off silent mode", "toggle_silent_mode", "sound_settings"),
    ("Vibrate while ringing", "toggle_vibrate_while_ringing", "sound_settings"),
    ("Turn on Do Not Disturb", "toggle_dnd", "sound_settings"),
    ("Disable DND", "toggle_dnd", "sound_settings"),
    ("Change ringtone", "set_ringtone", "sound_settings"),
    ("Turn off touch sounds", "toggle_touch_sounds", "sound_settings"),
    ("Disable keyboard haptics", "toggle_haptic_feedback", "sound_settings"),
    ("Enable haptic feedback", "toggle_haptic_feedback", "sound_settings"),
    ("Enable Dolby Atmos", "toggle_dolby_atmos", "sound_settings"),

    # Battery & Power
    ("Turn on battery saver", "battery_saver_profile", "battery_settings"),
    ("Turn off power saving mode", "battery_saver_profile", "battery_settings"),
    ("Show battery percentage", "toggle_battery_percentage", "battery_settings"),
    ("Enable adaptive battery", "toggle_adaptive_battery", "battery_settings"),
    ("Turn on fast charging", "toggle_fast_charging", "battery_settings"),
    ("Enable wireless powershare", "toggle_wireless_powershare", "battery_settings"),

    # Privacy & Security
    ("Turn on my location", "toggle_location", "location_settings"),
    ("Disable location tracking", "toggle_location", "location_settings"),
    ("Add a fingerprint", "add_fingerprint", "security_settings"),
    ("Set up face unlock", "setup_face_unlock", "security_settings"),
    ("Change screen lock PIN", "change_screen_lock", "security_settings"),
    ("Enable find my device", "toggle_find_my_device", "security_settings"),
    ("Turn off camera access", "toggle_camera_access", "privacy_settings"),
    ("Disable mic access", "toggle_mic_access", "privacy_settings"),
    ("Show passwords briefly", "toggle_show_passwords", "privacy_settings"),

    # Apps & Notifications
    ("Clear app cache", "clear_app_cache", "apps_settings"),
    ("Change default browser", "set_default_browser", "apps_settings"),
    ("Change default SMS app", "set_default_sms", "apps_settings"),
    ("Turn off notifications for this app", "toggle_app_notifications", "notification_settings"),
    ("Enable notification history", "toggle_notification_history", "notification_settings"),
    ("Hide silent notifications in status bar", "toggle_hide_silent_notifications", "notification_settings"),
    ("Turn on notification bubbles", "toggle_bubbles", "notification_settings"),

    # System, Accounts & Developer
    ("Turn on auto sync", "toggle_auto_sync", "sync_settings"),
    ("Stop syncing my accounts", "toggle_auto_sync", "sync_settings"),
    ("Check for system update", "check_system_update", "main_settings"),
    ("Change system language", "set_system_language", "language_settings"),
    ("Enable developer options", "toggle_developer_mode", "developer_settings"),
    ("Disable developer options", "toggle_developer_mode", "developer_settings"),
    ("Keep screen on while charging", "toggle_stay_awake", "developer_settings"),
    ("Enable USB debugging", "toggle_usb_debugging", "developer_settings"),
    ("Change default USB configuration", "set_usb_configuration", "developer_settings"),
    ("Show touches on screen", "toggle_show_touches", "developer_settings"),
    ("Enable OEM unlocking", "toggle_oem_unlock", "developer_settings"),

    # Accessibility & Digital Wellbeing
    ("Turn on TalkBack", "toggle_talkback", "accessibility_settings"),
    ("Enable color inversion", "toggle_color_inversion", "accessibility_settings"),
    ("Turn on high contrast text", "toggle_high_contrast", "accessibility_settings"),
    ("Enable mono audio", "toggle_mono_audio", "accessibility_settings"),
    ("Turn on bedtime mode", "toggle_bedtime_mode", "main_settings"),
    ("Enable focus mode", "toggle_focus_mode", "main_settings"),

    # --- EXPERT ADDITIONS ---
    ("Make my phone feel faster by lowering animations", "set_animation_scales", "developer_settings"),
    ("Change transition animation to 0.5x", "set_animation_scales", "developer_settings"),
    ("Switch to gesture navigation", "set_navigation_mode", "display_settings"),
    ("Use 3-button navigation", "set_navigation_mode", "display_settings"),
    ("Turn on flashlight", "toggle_flashlight", "quick_settings"),
    ("Turn off torch", "toggle_flashlight", "quick_settings"),
    ("Change default launcher to Nova", "set_default_launcher", "apps_settings"),
    ("Set AdGuard as private DNS", "set_private_dns", "wireless_settings"),
    ("Limit charging to 80 percent", "toggle_protect_battery", "battery_settings"),
    ("Turn on battery protection", "toggle_protect_battery", "battery_settings"),
    ("Make power button open power menu instead of Bixby", "configure_side_key", "advanced_features"),
    ("Double press power for camera", "configure_side_key", "advanced_features"),
    ("Turn on quick share for everyone", "toggle_quick_share", "connected_devices"),
    ("Allow installing unknown apps for Chrome", "toggle_install_unknown_apps", "security_settings"),
    ("Turn on extra dim", "toggle_extra_dim", "accessibility_settings"),
    ("Make screen even darker", "toggle_extra_dim", "accessibility_settings"),
]

def load_real_device_states(filepath="data/raw_device_states.jsonl"):
    states = {}
    if not os.path.exists(filepath):
        return states
    with open(filepath, 'r') as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                states[data["page_name"]] = data["ui_elements"]
            except Exception:
                continue
    return states

def generate_teacher_dataset(output_path: str, num_samples: int = 15000):
    device_states = load_real_device_states()
    if not device_states:
        print("Warning: No real device states found.")
        
    dataset = []
    
    # Massively exhaustive mapping of all possible operations
    operations = {
        # Connectivity
        "toggle_wifi": "Enable/Disable Wi-Fi",
        "toggle_bluetooth": "Enable/Disable Bluetooth",
        "toggle_airplane_mode": "Toggle Airplane Mode",
        "toggle_nfc": "Enable/Disable NFC",
        "toggle_mobile_data": "Enable/Disable Cellular Data",
        "toggle_data_roaming": "Enable/Disable Data Roaming",
        "preferred_network_mode": "Change cellular network mode",
        "toggle_wifi_calling": "Enable/Disable Wi-Fi Calling",
        "toggle_hotspot": "Enable/Disable Mobile Hotspot/Tethering",
        "toggle_vpn": "Connect/Disconnect VPN",
        
        # Display
        "toggle_dark_mode": "Switch Dark/Light Theme",
        "set_brightness": "Adjust Brightness Level",
        "toggle_adaptive_brightness": "Toggle Auto-Brightness",
        "toggle_eye_comfort": "Toggle Eye Comfort / Blue Light",
        "set_screen_timeout": "Change Display Sleep Timeout",
        "set_refresh_rate": "Change Display Refresh Rate (e.g. 60/120Hz)",
        "toggle_aod": "Enable/Disable Always On Display",
        "toggle_auto_rotate": "Enable/Disable Screen Auto-Rotate",
        "set_screen_resolution": "Change Screen Resolution (FHD/WQHD)",
        "set_screen_zoom": "Adjust Screen Zoom",
        "font_size_category": "Change System Font Size",
        "set_font_style": "Change System Font Style",

        # Sound
        "set_volume": "Adjust Media/Ringer Volume",
        "toggle_silent_mode": "Toggle Ringer Mute",
        "toggle_vibrate_while_ringing": "Toggle Call Vibration",
        "toggle_dnd": "Toggle Do Not Disturb",
        "set_ringtone": "Change Phone Ringtone",
        "toggle_touch_sounds": "Toggle Touch/Tap Sounds",
        "toggle_haptic_feedback": "Toggle Keyboard Haptics/Vibration",
        "toggle_dolby_atmos": "Enable/Disable Dolby Atmos",

        # Battery
        "battery_saver_profile": "Toggle Battery Saver",
        "toggle_battery_percentage": "Show/Hide Battery Percentage",
        "toggle_adaptive_battery": "Enable/Disable Adaptive Battery",
        "toggle_fast_charging": "Enable/Disable Fast Charging",
        "toggle_wireless_powershare": "Enable/Disable Wireless PowerShare",

        # Privacy/Security
        "toggle_location": "Enable/Disable GPS",
        "add_fingerprint": "Add/Manage Fingerprints",
        "setup_face_unlock": "Setup Face Recognition",
        "change_screen_lock": "Change PIN/Password/Pattern",
        "toggle_find_my_device": "Enable/Disable Find My Device",
        "toggle_camera_access": "Revoke/Grant System Camera Access",
        "toggle_mic_access": "Revoke/Grant System Microphone Access",
        "toggle_show_passwords": "Show/Hide characters when typing passwords",

        # Apps/Notifications
        "clear_app_cache": "Clear Application Cache",
        "set_default_browser": "Change Default Browser App",
        "set_default_sms": "Change Default SMS App",
        "toggle_app_notifications": "Enable/Disable Notifications for an App",
        "toggle_notification_history": "Enable/Disable Notification History",
        "toggle_hide_silent_notifications": "Hide Silent Notifications from Status Bar",
        "toggle_bubbles": "Enable/Disable Notification Bubbles",

        # System/Dev/Accessibility
        "toggle_auto_sync": "Enable/Disable Account Sync",
        "check_system_update": "Check for OS Updates",
        "set_system_language": "Change Device Language",
        "toggle_developer_mode": "Enable/Disable Developer Options",
        "toggle_stay_awake": "Keep Screen Awake While Charging",
        "toggle_usb_debugging": "Enable/Disable USB Debugging",
        "set_usb_configuration": "Change Default USB Mode (MTP/PTP/Charge)",
        "toggle_show_touches": "Show visual feedback for taps",
        "toggle_oem_unlock": "Enable/Disable OEM Unlocking",
        "toggle_talkback": "Enable/Disable TalkBack Accessibility",
        "toggle_color_inversion": "Enable/Disable Color Inversion",
        "toggle_high_contrast": "Enable/Disable High Contrast Text",
        "toggle_mono_audio": "Enable/Disable Mono Audio",
        "toggle_bedtime_mode": "Enable/Disable Bedtime Mode (Digital Wellbeing)",
        "toggle_focus_mode": "Enable/Disable Focus Mode",

        "set_animation_scales": "Adjust Window/Transition Animation Scale",
        "set_navigation_mode": "Switch Gesture/3-Button Navigation",
        "toggle_flashlight": "Enable/Disable Flashlight Torch",
        "set_default_launcher": "Change Default Home App",
        "set_private_dns": "Configure Private DNS Provider",
        "toggle_protect_battery": "Enable/Disable Maximum Charging Limit",
        "configure_side_key": "Configure Power Button Long/Double Press",
        "toggle_quick_share": "Change Quick Share Visibility",
        "toggle_install_unknown_apps": "Allow/Deny APK Sideloading",
        "toggle_extra_dim": "Toggle Extra Dim Overlay"
    }
    
    print(f"Generating {num_samples} samples using exhaustive templates...")
    for i in range(num_samples):
        # Pick a random template and inject noise/context
        base_prompt, expected_action, target_page = random.choice(INTENT_TEMPLATES)
        
        # Add random conversational noise to make the SLM robust
        prefixes = ["Hey phone, ", "Please ", "Can you ", "Quickly ", "", "", "", "I want to "]
        suffixes = ["", " right now", " please", ", thanks", " ASAP"]
        
        user_prompt = f"{random.choice(prefixes)}{base_prompt.lower()}{random.choice(suffixes)}"
        
        # Get UI state for this setting
        ui_elements = device_states.get(target_page, device_states.get("main_settings", []))
        
        clean_state = []
        # Randomly sample or shuffle parts of UI to prevent position bias
        random.shuffle(ui_elements)
        for el in ui_elements[:15]: # Keep context window reasonable
            if el.get("label") or el.get("checkable"):
                clean_state.append(f"{el.get('label')} (checked={el.get('checked', False)})")
                
        system_state = {
            "prompt": user_prompt,
            "visible_ui": clean_state
        }
        
        # Jev Teacher Output: Calibrated Probability Distribution (RLCD)
        probs = {k: random.uniform(0.001, 0.05) for k in operations.keys()}
        
        # Normalize non-target probabilities so sum is ~0.05
        sum_noise = sum(probs.values()) - probs[expected_action]
        for k in probs:
            if k != expected_action:
                probs[k] = (probs[k] / sum_noise) * 0.05
                
        # Assign high confidence to the chosen ground-truth target
        probs[expected_action] = 0.95
        
        sample = {
            "instruction": "You are an on-device Android settings agent. Output the correct JSON action based on the user prompt.",
            "input": user_prompt,
            "system_state": system_state,
            "output_action": expected_action,
            "probabilities": probs
        }
        
        dataset.append(sample)
        
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        for item in dataset:
            f.write(json.dumps(item) + "\\n")
            
    print(f"Exhaustive Dataset generated at {output_path} with {len(dataset)} samples.")

if __name__ == "__main__":
    generate_teacher_dataset("data/teacher_dataset.jsonl", num_samples=15000)
