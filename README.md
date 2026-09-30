# On-Device Settings SLM

An offline, on-device Small Language Model (SLM) designed to autonomously control Android system settings through natural language. This project distills complex, context-aware reasoning from a System-1 teacher model (**Laya**) into a blazing fast, quantized 0.5B parameter student model (**Qwen 2.5**).

## Architecture

The pipeline consists of three core components:

1. **Contextual Dataset Generation (`src/data_generation_laya.py`)**: 
   - Uses the Laya 0.4B System-1 model to generate probability distributions for over 70+ Android setting actions.
   - Embeds the physical UI screen state (`visible_ui`) into the prompt so the SLM learns to "see" the screen before deciding on an action.
   - Injects conversational noise ("Hey phone", "ASAP") and indirect phrasing ("My eyes hurt from this white screen").
   - Enforces strict Out-Of-Domain (OOD) boundaries by mapping garbage prompts ("Order a pizza", "Tell me a joke") to a safe `no_action` fallback.

2. **SLM Distillation (`src/train.py`)**:
   - Fine-tunes **Qwen2.5-0.5B-Instruct** using Low-Rank Adaptation (LoRA) via PEFT and Hugging Face `trl`.
   - Tuned to run natively on Apple Silicon (MPS) and CPU environments to ensure fast local training without requiring heavy CUDA GPUs.

3. **Robust Evaluation Suite (`src/eval.py`)**:
   - Tests the fine-tuned SLM against a hardcoded evaluation suite of complex, indirect natural language commands and hallucination traps.
   - Extracts the generated JSON (`{"action": "<output>"}`) and calculates exact routing accuracy.

## Current Model Accuracy

On a rapid, 1,000-step proof-of-concept training loop (taking ~30 minutes on a Mac CPU), the model achieved:
- **Overall Routing Accuracy:** 66.67%
- **OOD Boundary Recall:** 100% (Successfully rejected all hallucinated actions).
- **Contextual NLP Recall:** 100% on tested indirect prompts (e.g. mapping *"Disable all network connections, I'm on a plane"* to `toggle_airplane_mode`).

*Note: For production deployment (95%+ accuracy across all 70+ intents), the model should be trained for 3-5 epochs on the full 15,000 sample dataset.*

## Next Steps: Android App Integration

To deploy this SLM locally to a physical Android device and record the demo video, we will execute the following:

1. **Model Export (ExecuTorch / ONNX)**:
   - Export the fine-tuned LoRA weights and base Qwen model to a mobile-friendly format like **ExecuTorch** or **ONNX Runtime Mobile**.
   - Quantize the model to INT4/INT8 to ensure it fits entirely within the phone's RAM and executes in under 200ms on the NPU/GPU.

2. **Android App Scaffolding**:
   - Build a lightweight Android accessibility service app.
   - The app will capture the user's voice command, dump the current UI layout via `AccessibilityNodeInfo`, and feed both into the local SLM.

3. **Execution Engine**:
   - Parse the SLM's JSON output (`{"action": "toggle_wifi"}`).
   - Execute the action dynamically by finding the corresponding UI element on the screen and injecting a click event.

4. **Record the Demo**:
   - Test offline capabilities (Airplane mode on).
   - Demonstrate conversational settings control and OOD rejection, all running entirely on-device without any cloud APIs!
