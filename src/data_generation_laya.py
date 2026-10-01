import os
import json
import random
import laya
from typing import List, Dict

# Exhaustive intents list based on Jev SPEC-SLM-JEV-002 and device exploration
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

    # Indirect / Conversational Intents
    ("I can't see the screen in this sun", "set_brightness", "display_settings"),
    ("The screen is blinding me in bed", "set_brightness", "display_settings"),
    ("My brightness is too low can you increase it", "set_brightness", "display_settings"),
    ("My eyes hurt from this white screen", "toggle_dark_mode", "display_settings"),
    ("It's night time, make the screen black", "toggle_dark_mode", "display_settings"),
    ("I have no internet", "toggle_wifi", "wifi_settings"),
    ("Can't load this webpage, fix my connection", "toggle_wifi", "wifi_settings"),
    ("I can't hear the video", "set_volume", "sound_settings"),
    ("The music is too loud", "set_volume", "sound_settings"),
    ("Turn the sound down a bit", "set_volume", "sound_settings"),
    ("My phone is about to die", "battery_saver_profile", "battery_settings"),
    ("I'm at 5 percent, help", "battery_saver_profile", "battery_settings"),
    ("It's pitch black in here", "toggle_flashlight", "quick_settings"),
    ("I dropped my keys in the dark", "toggle_flashlight", "quick_settings"),
    ("Where am I?", "toggle_location", "location_settings"),
    ("Google maps can't find me", "toggle_location", "location_settings"),
    ("My phone keeps dying fast", "toggle_adaptive_battery", "battery_settings"),
    ("The screen keeps turning off while I'm reading", "set_screen_timeout", "display_settings"),
    ("Stop the screen from rotating when I lie down", "toggle_auto_rotate", "display_settings"),
    ("I can't read this tiny text", "font_size_category", "display_settings"),
    ("Make the words bigger", "font_size_category", "display_settings"),
    ("I'm getting too many pings", "toggle_dnd", "sound_settings"),
    ("Silence my phone for the meeting", "toggle_silent_mode", "sound_settings"),
    ("I want to share my internet with my laptop", "toggle_hotspot", "wireless_settings"),
    ("My bluetooth headphones won't connect", "toggle_bluetooth", "bluetooth_settings"),
    ("Disable all network connections, I'm on a plane", "toggle_airplane_mode", "airplane_mode"),

    # Out of Domain / Garbage (Should trigger no_action)
    ("What's the weather like today?", "no_action", "main_settings"),
    ("Tell me a joke", "no_action", "main_settings"),
    ("Call mom", "no_action", "main_settings"),
    ("Order a pizza from dominoes", "no_action", "main_settings"),
    ("asdfsdfsd", "no_action", "main_settings"),
    ("Open youtube and play a video", "no_action", "main_settings"),
    ("Send a text to John", "no_action", "main_settings"),
    ("Who is the president of the United States?", "no_action", "main_settings"),
    ("Set a timer for 10 minutes", "no_action", "main_settings"),
    ("Play some jazz music", "no_action", "main_settings"),
    ("What is 10 plus 10?", "no_action", "main_settings"),
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

def generate_laya_dataset(output_path: str, num_samples: int = 100):
    print("Loading Laya model from Hugging Face (convaiinnovations/laya)...")
    # This automatically downloads and caches the checkpoint from HF
    agent = laya.load("convaiinnovations/laya")
    
    device_states = load_real_device_states()
    dataset = []
    
    operations = ["no_action", 'toggle_bedtime_mode', 'toggle_battery_percentage', 'toggle_aod', 'set_navigation_mode', 'set_private_dns', 'toggle_dolby_atmos', 'toggle_mic_access', 'set_ringtone', 'check_system_update', 'font_size_category', 'toggle_airplane_mode', 'toggle_silent_mode', 'configure_side_key', 'toggle_vpn', 'toggle_hide_silent_notifications', 'set_refresh_rate', 'set_system_language', 'toggle_mobile_data', 'toggle_touch_sounds', 'toggle_mono_audio', 'set_animation_scales', 'toggle_wifi', 'toggle_dark_mode', 'toggle_auto_rotate', 'set_default_browser', 'toggle_bubbles', 'toggle_usb_debugging', 'toggle_fast_charging', 'set_default_sms', 'toggle_adaptive_battery', 'toggle_color_inversion', 'toggle_extra_dim', 'toggle_haptic_feedback', 'toggle_eye_comfort', 'toggle_talkback', 'toggle_bluetooth', 'toggle_adaptive_brightness', 'toggle_wireless_powershare', 'set_screen_zoom', 'battery_saver_profile', 'toggle_protect_battery', 'toggle_data_roaming', 'add_fingerprint', 'clear_app_cache', 'toggle_flashlight', 'set_brightness', 'toggle_show_touches', 'set_screen_resolution', 'set_default_launcher', 'set_volume', 'toggle_auto_sync', 'toggle_find_my_device', 'toggle_location', 'toggle_show_passwords', 'set_screen_timeout', 'toggle_camera_access', 'toggle_hotspot', 'toggle_quick_share', 'toggle_install_unknown_apps', 'toggle_app_notifications', 'toggle_oem_unlock', 'preferred_network_mode', 'set_usb_configuration', 'toggle_high_contrast', 'toggle_dnd', 'toggle_nfc', 'set_font_style', 'setup_face_unlock', 'toggle_stay_awake', 'toggle_notification_history', 'change_screen_lock', 'toggle_focus_mode', 'toggle_wifi_calling', 'toggle_vibrate_while_ringing', 'toggle_developer_mode']
    
    print(f"Generating {num_samples} samples using Laya as the System 1 Teacher...")
    for i in range(num_samples):
        base_prompt, expected_action_mock, target_page = random.choice(INTENT_TEMPLATES)
        prefixes = ["Hey phone, ", "Please ", "Can you ", "Quickly ", "", "", "", "I want to "]
        suffixes = ["", " right now", " please", ", thanks", " ASAP"]
        user_prompt = f"{random.choice(prefixes)}{base_prompt.lower()}{random.choice(suffixes)}"
        
        ui_elements = device_states.get(target_page, device_states.get("main_settings", []))
        clean_state = []
        random.shuffle(ui_elements)
        for el in ui_elements[:15]: 
            if el.get("label") or el.get("checkable"):
                clean_state.append(f"{el.get('label')} (checked={el.get('checked', False)})")
                
        system_state = {
            "prompt": user_prompt,
            "visible_ui": clean_state
        }
        
        # 1. Ask Laya to predict the Choice (routing to an operation)
        questions = {
            "operation": {
                "type": "choice",
                "instructions": "Determine the correct settings operation based on the user prompt and visible UI.",
                "criteria": operations
            }
        }
        
        # 2. Forward pass through Laya (returns in ~30ms without text generation)
        result = agent.predict(system_state, questions)
        
        # 3. Extract the predicted value and RLCD calibrated probabilities
        predicted_action = result["answers"]["operation"]["choice"]
        probs = result["answers"]["operation"]["probabilities"]
        
        sample = {
            "instruction": "You are an on-device Android settings agent. Output the correct JSON action based on the user prompt.",
            "input": user_prompt,
            "system_state": system_state,
            "output_action": predicted_action,
            "probabilities": probs
        }
        
        dataset.append(sample)
        
        if (i+1) % 10 == 0:
            print(f"Processed {i+1}/{num_samples} samples...")
        
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        for item in dataset:
            f.write(json.dumps(item) + "\n")
            
    print(f"Laya-powered Dataset generated at {output_path} with {len(dataset)} samples.")

if __name__ == "__main__":
    # We use a smaller number here to demonstrate since it runs on local CPU/GPU
    generate_laya_dataset("data/teacher_dataset_laya.jsonl", num_samples=15000)
