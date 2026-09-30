import os
import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm
from sklearn.metrics import accuracy_score, classification_report
import re

def load_dataset(filepath):
    dataset = []
    with open(filepath, 'r') as f:
        for line in f:
            if line.strip():
                dataset.append(json.loads(line))
    return dataset

def extract_action(response_text):
    """
    Extracts the JSON action from the SLM's raw text generation.
    Expects format: {"action": "toggle_wifi"}
    """
    match = re.search(r'{"action":\s*"([^"]+)"}', response_text)
    if match:
        return match.group(1)
    
    # Fallback to loose extraction
    match = re.search(r'"action"\s*:\s*"([^"]+)"', response_text)
    if match:
        return match.group(1)
    return "UNKNOWN"

def run_evals(
    model_path: str = "models/slm_finetuned", 
    base_model_name: str = "Qwen/Qwen2.5-0.5B-Instruct",
    test_data_path: str = "data/teacher_dataset_laya.jsonl",
    num_eval_samples: int = 100
):
    # Robust Evaluation Suite
    
    
    test_set = [
        {"input": "Turn on wifi", "system_state": {"prompt": "Turn on wifi", "visible_ui": []}, "output_action": "toggle_wifi"},
        {"input": "Disable bluetooth", "system_state": {"prompt": "Disable bluetooth", "visible_ui": []}, "output_action": "toggle_bluetooth"},
        {"input": "I can't see the screen in this sun", "system_state": {"prompt": "I can't see the screen in this sun", "visible_ui": []}, "output_action": "set_brightness"},
        {"input": "My eyes hurt from this white screen", "system_state": {"prompt": "My eyes hurt from this white screen", "visible_ui": []}, "output_action": "toggle_dark_mode"},
        {"input": "Google maps can't find me", "system_state": {"prompt": "Google maps can't find me", "visible_ui": []}, "output_action": "toggle_location"},
        {"input": "I'm getting too many pings", "system_state": {"prompt": "I'm getting too many pings", "visible_ui": []}, "output_action": "toggle_dnd"},
        {"input": "My phone is about to die", "system_state": {"prompt": "My phone is about to die", "visible_ui": []}, "output_action": "battery_saver_profile"},
        {"input": "Disable all network connections, I'm on a plane", "system_state": {"prompt": "Disable all network connections, I'm on a plane", "visible_ui": ['Navigate up (checked=False)', 'Flight mode (checked=False)', 'Flight mode (checked=False)', 'Off (checked=False)', 'Off (checked=False)', 'Turns off mobile networks, Wi-Fi, and Bluetooth.While Flight mode is on, you can turn Wi-Fi and Bluetooth on again in Settings or the quick panel.If you turn Wi-Fi or Bluetooth on or off in Flight mode, this will be remembered the next time you use Flight mode. (checked=False)']}, "output_action": "toggle_airplane_mode"},
        {"input": "Make the words bigger", "system_state": {"prompt": "Make the words bigger", "visible_ui": []}, "output_action": "font_size_category"},
        {"input": "What's the weather like today?", "system_state": {"prompt": "What's the weather like today?", "visible_ui": []}, "output_action": "no_action"},
        {"input": "Order a pizza from dominoes", "system_state": {"prompt": "Order a pizza from dominoes", "visible_ui": []}, "output_action": "no_action"},
        {"input": "asdfsdfsd", "system_state": {"prompt": "asdfsdfsd", "visible_ui": []}, "output_action": "no_action"},
        {"input": "Play some jazz music", "system_state": {"prompt": "Play some jazz music", "visible_ui": []}, "output_action": "no_action"},
        {"input": "Set a timer for 10 minutes", "system_state": {"prompt": "Set a timer for 10 minutes", "visible_ui": []}, "output_action": "no_action"},
        {"input": "Call mom", "system_state": {"prompt": "Call mom", "visible_ui": []}, "output_action": "no_action"}
    ]
    
    print(f"Loading Evaluator Model: {model_path} (Base: {base_model_name})")
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            device_map="cpu",
            torch_dtype=torch.float16
        )
    except Exception as e:
        print(f"Warning: Could not load local fine-tuned model at {model_path}. Error: {e}")
        print("Falling back to base model for zero-shot baseline evaluation...")
        tokenizer = AutoTokenizer.from_pretrained(base_model_name)
        model = AutoModelForCausalLM.from_pretrained(
            base_model_name,
            device_map="cpu",
            torch_dtype=torch.float16
        )
    
    model.eval()
    
    y_true = []
    y_pred = []
    
    print(f"Running evaluation on {len(test_set)} samples...")
    for idx, sample in enumerate(tqdm(test_set)):
        prompt = sample["input"]
        system_state = sample["system_state"]
        ground_truth = sample["output_action"]
        
        system = "You are a fast on-device settings agent. Return a JSON dict with the action."
        user = f"Context: {system_state}\\nCommand: {prompt}"
        
        # Chat template
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]
        
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(text, return_tensors="pt").to(model.device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs, 
                max_new_tokens=20,
                temperature=0.1, # Greedy decoding for routing
                pad_token_id=tokenizer.eos_token_id
            )
            
        generated_ids = outputs[0][inputs.input_ids.shape[-1]:]
        response = tokenizer.decode(generated_ids, skip_special_tokens=True)
        
        prediction = extract_action(response)
        
        y_true.append(ground_truth)
        y_pred.append(prediction)
        
        if idx < 3:
            print(f"\\n--- Sample {idx+1} ---")
            print(f"Prompt: {prompt}")
            print(f"Expected: {ground_truth}")
            print(f"Predicted: {prediction}")
            print(f"Raw Output: {response.strip()}")

    print("\\n=======================================================")
    print("                 EVALUATION REPORT")
    print("=======================================================")
    
    acc = accuracy_score(y_true, y_pred)
    print(f"Overall Routing Accuracy: {acc * 100:.2f}%")
    print("\\nDetailed Classification Report (Top 10 Actions):")
    
    # We filter warnings if some classes in the test set were never predicted
    report = classification_report(y_true, y_pred, zero_division=0)
    print(report)

if __name__ == "__main__":
    run_evals(num_eval_samples=50)
