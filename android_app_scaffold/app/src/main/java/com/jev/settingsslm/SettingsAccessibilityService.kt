package com.jev.settingsslm

import android.accessibilityservice.AccessibilityService
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import android.util.Log
import org.json.JSONObject

class SettingsAccessibilityService : AccessibilityService() {
    private val TAG = "JevSLM"

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        // Triggered when UI changes. In a real app, this would be gated by a Voice trigger.
    }

    override fun onInterrupt() {}

    /**
     * Called when the user issues a voice command.
     */
    fun onUserVoiceCommand(voiceCommand: String) {
        val rootNode = rootInActiveWindow
        if (rootNode == null) {
            Log.e(TAG, "Cannot access screen content")
            return
        }

        // 1. Build the visible UI state just like in the Python training data
        val visibleUi = mutableListOf<String>()
        val nodeMap = mutableMapOf<String, AccessibilityNodeInfo>()
        traverseAndBuildUI(rootNode, visibleUi, nodeMap)

        // 2. Format the prompt for the SLM
        val systemState = JSONObject().apply {
            put("prompt", voiceCommand)
            put("visible_ui", visibleUi)
        }
        val prompt = "Context: $systemState\nCommand: $voiceCommand"

        // 3. Call the Local LLM (llama.cpp or MLC)
        Log.d(TAG, "Sending to Local SLM: $prompt")
        val jsonResponse = runLocalLLMInference(prompt) // Pseudo-function for JNI call
        
        // 4. Parse action and execute
        try {
            val responseObj = JSONObject(jsonResponse)
            val action = responseObj.getString("action")
            
            if (action == "no_action") {
                Log.d(TAG, "SLM rejected action (OOD boundary).")
                return
            }
            
            executeAction(action, nodeMap)
        } catch (e: Exception) {
            Log.e(TAG, "Failed to parse SLM output: $jsonResponse")
        }
    }

    private fun traverseAndBuildUI(
        node: AccessibilityNodeInfo, 
        uiList: MutableList<String>, 
        nodeMap: MutableMap<String, AccessibilityNodeInfo>
    ) {
        if (node.text != null || node.isCheckable) {
            val label = node.text?.toString() ?: node.contentDescription?.toString() ?: "element"
            val state = "${label} (checked=${node.isChecked})"
            uiList.add(state)
            
            // Map common actions to UI nodes based on intent mapping heuristics
            nodeMap[label.lowercase()] = node
        }

        for (i in 0 until node.childCount) {
            val child = node.getChild(i)
            if (child != null) traverseAndBuildUI(child, uiList, nodeMap)
        }
    }

    private fun executeAction(action: String, nodeMap: Map<String, AccessibilityNodeInfo>) {
        Log.d(TAG, "Executing Action: $action")
        
        // This is a simplified heuristic. In production, the model would output the target text,
        // or we'd map "toggle_wifi" -> searching for the node containing "Wi-Fi".
        val targetTerm = action.replace("toggle_", "").replace("_", " ")
        
        for ((label, node) in nodeMap) {
            if (label.contains(targetTerm)) {
                node.performAction(AccessibilityNodeInfo.ACTION_CLICK)
                Log.d(TAG, "Clicked node: $label")
                return
            }
        }
        Log.e(TAG, "Could not find UI element matching action: $action")
    }

    private fun runLocalLLMInference(prompt: String): String {
        // TODO: Call llama.cpp Android JNI binding here.
        // Returning mock for scaffold.
        return "{\"action\": \"toggle_wifi\"}"
    }
}
