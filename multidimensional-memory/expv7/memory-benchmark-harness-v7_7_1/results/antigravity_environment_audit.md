# Antigravity IDE Environment Capability & Model Gateway Audit

## 1. Executive Summary
An inspection of the installed **Antigravity IDE and Agent Environment** (`/Users/xxvirusxx/.gemini/antigravity-ide/`) was performed to determine whether an external local process can programmatically invoke the configured Antigravity model for arbitrary text prompts and receive structured text/JSON responses.

**Conclusion:** **No supported mechanism exists.** 
There is no documented CLI, local HTTP/REST server, or MCP endpoint exposed by the Antigravity installation that acts as a generic, deterministic model completion gateway. 

---

## 2. Detailed Interface Findings

### A. IDE Command-Line Tool (`antigravity-ide`)
* **Path:** `/Users/xxvirusxx/.antigravity-ide/antigravity-ide/bin/antigravity-ide`
* **Supported Commands:** `chat`, `serve-web`, `tunnel`, `--add-mcp`
* **Behavior:**
  * Executing `antigravity-ide chat` opens or focuses the IDE graphical user interface window and starts an interactive agent session thread.
  * **Output Format:** Renders rich UI elements inside the GUI application. It does not output clean stdout or raw JSON suitable for programmatic parsing by external scripts.

### B. Internal Sub-utility (`agentapi`)
* **Path:** `/Users/xxvirusxx/.gemini/antigravity-ide/bin/agentapi`
* **Underlying Binary:** `/Applications/Antigravity IDE.app/Contents/Resources/app/extensions/antigravity/bin/language_server_macos_arm agentapi`
* **Exposed Commands:**
  * `get-conversation-metadata <conversation_id>`
  * `new-conversation [--model=<flash_lite|flash|pro>] <prompt>`
  * `send-message <recipient_id> <content>`
* **Limitations & Mechanism:**
  * **Agent Session Trajectory:** `new-conversation` creates a full stateful agent workspace trajectory in local SQLite/LevelDB app storage (`~/.gemini/antigravity-ide/brain/...`).
  * **System Prompt & Tool Binding:** Requests automatically include system prompts, workspace context, and tool definitions (file system access, terminal execution, MCP tools).
  * **Non-Deterministic:** It is engineered for multi-step autonomous tool execution across the local workspace, not for stateless, deterministic single-turn prompt-to-response text completion.

### C. Local API / REST Server
* **Status:** No local HTTP endpoint or OpenAI/Ollama-compatible `/v1/chat/completions` REST server is hosted or exposed locally for external programmatic consumption.

### D. Model Context Protocol (MCP)
* **Role in Antigravity:** Antigravity operates strictly as an **MCP Client** (consuming tools listed in `~/.gemini/antigravity-ide/mcp_config.json`). It does not run as an **MCP Tool Server** that exposes model inference capabilities to external clients.

---

## 3. Capability Evaluation Matrix

| Requirement | Supported? | Technical Detail / Finding |
| :--- | :---: | :--- |
| **Documented Completion CLI** | ❌ No | `antigravity-ide chat` requires GUI interaction. |
| **Local REST API / HTTP Endpoint** | ❌ No | No HTTP server is hosted. |
| **Structured JSON Completion Output** | ❌ No | Output is tied to internal agent UI state and JSONL log storage. |
| **Deterministic Replayable Gateway** | ❌ No | Agent sessions maintain state and execute non-deterministic tool iterations. |
| **Authentication & Credentials** | N/A | Authenticated directly via IDE session token to Google Cloud backends. |
| **Concurrency Limitations** | N/A | Unsuited for parallel benchmark evaluation workers. |

---

## 4. Final Recommendation
Because no supported programmatic model gateway exists in the local Antigravity setup, external benchmark execution should rely on dedicated API endpoints (such as direct Google Gemini API, OpenAI API, or local Ollama endpoints) rather than attempting to wrap the Antigravity IDE environment.
