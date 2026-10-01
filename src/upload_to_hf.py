import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import login
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo_id", type=str, required=True, help="Hugging Face repo ID (e.g. AkhileshManda/qwen-android-settings-slm)")
    parser.add_argument("--token", type=str, required=True, help="Hugging Face write token")
    args = parser.parse_args()

    print("Logging into Hugging Face...")
    login(token=args.token)

    base_model_id = "Qwen/Qwen2.5-0.5B-Instruct"
    adapter_dir = "models/slm_finetuned"

    print(f"Loading base model: {base_model_id}")
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_id,
        torch_dtype=torch.float32,
        device_map="cpu"
    )
    tokenizer = AutoTokenizer.from_pretrained(base_model_id)

    print(f"Loading LoRA adapters from {adapter_dir}")
    model = PeftModel.from_pretrained(base_model, adapter_dir)

    print("Merging adapters into base model...")
    merged_model = model.merge_and_unload()

    print(f"Pushing merged model to {args.repo_id}...")
    merged_model.push_to_hub(args.repo_id, private=False)
    tokenizer.push_to_hub(args.repo_id, private=False)

    print(f"Successfully uploaded to https://huggingface.co/{args.repo_id}")

if __name__ == "__main__":
    main()
