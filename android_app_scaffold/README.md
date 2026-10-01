# Android On-Device Settings SLM App

This scaffold provides the core Android components to intercept the OS screen state, feed it to our quantized Qwen 0.5B model locally, and execute actions.

## 1. Local LLM Inference Engine

To run the fine-tuned model entirely on-device, you should use **llama.cpp** or **MLC LLM**. 

**If using llama.cpp:**
1. Export the merged Hugging Face model to GGUF format:
   ```bash
   python -m llama_cpp.convert_hf_to_gguf --model models/merged_slm --outfile slm.gguf --outtype q4_k_m
   ```
2. Push `slm.gguf` to the Android device storage.
3. Import the `llama.cpp` Android AAR bindings into this project.

## 2. Core Components Included
- `SettingsAccessibilityService.kt`: Traverses the UI tree to generate the `visible_ui` array, builds the JSON prompt, calls the LLM, and clicks the target toggle.
- `AndroidManifest.xml`: Requests `BIND_ACCESSIBILITY_SERVICE`.
- `accessibility_service_config.xml`: Configures the service to listen to window state changes.
