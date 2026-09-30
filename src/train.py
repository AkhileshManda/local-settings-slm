import os
import json
import torch
torch.set_num_threads(4)
from datasets import load_dataset
from transformers import TrainingArguments, AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model

def format_prompt(example):
    """
    Format the dataset into the conversational layout expected by the model.
    """
    system = "You are a fast on-device settings agent. Return a JSON dict with the action."
    user = f"Context: {example['system_state']}\\nCommand: {example['input']}"
    assistant = '{"action": "' + example['output_action'] + '"}'
    
    # Simple formatting template
    text = f"<|im_start|>system\\n{system}<|im_end|>\\n<|im_start|>user\\n{user}<|im_end|>\\n<|im_start|>assistant\\n{assistant}<|im_end|>"
    return {"text": text}

def train_slm(data_path: str, model_name: str = "Qwen/Qwen2.5-0.5B-Instruct", output_dir: str = "models/slm_finetuned"):
    print("Loading Dataset...")
    dataset = load_dataset("json", data_files={"train": data_path})["train"]
    dataset = dataset.map(format_prompt)
    
    print("Loading Base Model via Transformers...")
    max_seq_length = 512
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token

    # Using MPS/CPU friendly precision
    device = "cpu"
    print(f"Using device: {device}")
    
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="cpu",
        torch_dtype=torch.float16 if device == "mps" else torch.float32,
    )
    
    # Configure LoRA Adapters using PEFT
    lora_config = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    
    print("Initializing Trainer...")
    from transformers import Trainer, DataCollatorForLanguageModeling
    def tokenize_fn(examples):
        return tokenizer(examples['text'], truncation=True, max_length=512)
    tokenized_dataset = dataset.map(tokenize_fn, batched=True)
    trainer = Trainer(
        model=model,
        data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
        train_dataset=tokenized_dataset,
        args=TrainingArguments(
            per_device_train_batch_size=4,
            gradient_accumulation_steps=2,
            warmup_steps=5,
            max_steps=150, # Very short run for demonstration on Mac
            learning_rate=1e-3,
            fp16=False,
            bf16=False,
            use_cpu=True,
            logging_steps=5,
            output_dir="outputs",
        ),
    )
    
    print("Starting Training Loop...")
    trainer.train() 
    
    print("Saving Fine-Tuned Weights...")
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    print(f"Model saved to {output_dir}. Ready for Evaluation!")

if __name__ == "__main__":
    train_slm("data/teacher_dataset_laya.jsonl")
