# Path Engineering

Landing page for the Path Engineering platform (Arabic, RTL) with a demo chatbot, **Engineering Path Advisor**, that gives engineering students a roadmap for their graduation project. The chatbot runs on a **local model through Ollama**: no API key, no cloud, no data leaves your machine.

## What is in this repo

| File | Purpose |
|------|---------|
| `index.html` | The whole website: landing page, registration form (Supabase), and the advisor chatbot section (`#advisor`) |
| `serve.py` | Small local server: serves the site and forwards `/ollama/*` requests to Ollama (no CORS setup needed) |
| `prompts/advisor_system.md` | The advisor's system prompt (rules and the 7-section answer format) |

## Requirements

- Python 3.8+ (standard library only, nothing to `pip install`)
- [Ollama](https://ollama.com)
- A modern browser (Chrome, Firefox, Edge)
- Hardware for the default model `qwen2.5:7b-instruct`: about **8 GB free RAM**, about 5 GB disk. A GPU is optional; on CPU only, expect about 5 tokens/second (a full roadmap takes 2-3 minutes).

## 1. Install Ollama

**Linux**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**macOS / Windows**: download the installer from <https://ollama.com/download> and run it.

Check it works:
```bash
ollama --version
curl http://localhost:11434/api/tags     # should return JSON
```
On Linux the installer starts Ollama as a service. If the `curl` fails, start it manually with `ollama serve`.

## 2. Download a model

```bash
ollama pull qwen2.5:7b-instruct
```

| Model | Size | Notes |
|-------|------|-------|
| `qwen2.5:7b-instruct` | ~4.7 GB | **Recommended.** Best Arabic and best at following the format. Slow on CPU. |
| `qwen2.5:3b-instruct` | ~1.9 GB | About 2x faster, weaker Arabic. Use on low-RAM machines. |
| `gemma3:270m` | ~0.3 GB | Too small: it ignores the prompt and just chats. Not usable for this bot. |

List installed models with `ollama list`.

## 3. Run the website

From the project folder:
```bash
python3 serve.py          # serves on http://localhost:8000
python3 serve.py 8080     # or choose another port
```
Open <http://localhost:8000> and scroll to **مستشار مشروع التخرج** (or click "المستشار" in the nav).

> **Do not open `index.html` by double-clicking it.** A page opened as `file://` is blocked by Ollama (HTTP 403), so the chat cannot connect. Always use `serve.py`.

If port 8000 is busy (`Address already in use`), stop the other server or pass another port as shown above.

## 4. Using the chatbot

1. Wait for the status next to the model dropdown to show **متصل بالنموذج المحلي** (connected).
2. Pick a model in the dropdown. By default the largest installed model is selected, and your choice is remembered in the browser.
3. Type your **major + project idea** in one message, or click an example chip. Optional: add keywords and your skill level.
   - Example: `Computer engineering: face recognition attendance system`
   - Example: `هندسة حاسوب: نظام Smart Home باستخدام ESP32`
4. Press **Enter** to send (**Shift+Enter** for a new line). The answer streams in as it is written.
5. Use **إيقاف** to stop a long answer and **محادثة جديدة** to start over.

### What the advisor answers

If the idea is too vague, it asks up to 3 clarifying questions and stops. Otherwise it replies with these sections, in order:

1. Project Understanding
2. Related Fields and Technologies
3. Prerequisite Knowledge
4. Project Steps (Roadmap)
5. Topics and Courses to Learn
6. Expected Challenges
7. Questions to Discuss with Your Mentor

It replies in the language you write in (Arabic with technical terms in English). It never invents URLs, course titles or prices, and it reminds students to validate decisions with their human mentor.

### Chat history

Chats are **not saved**. The conversation lives only in the page's memory: refreshing or closing the tab erases it. The only thing stored in the browser is the selected model (`localStorage`, key `advisorModel`). Nothing is sent to any server.

## 5. How it works

```
Browser (index.html)  --/ollama/api/chat-->  serve.py  -->  Ollama (localhost:11434)  -->  local model
```

- `serve.py` serves static files and forwards any path starting with `/ollama/` to Ollama, streaming the response back. Same origin means no CORS configuration.
- If the proxy is not found, the page falls back to calling `http://localhost:11434` directly. That only works from a `localhost` page, or when Ollama is started with `OLLAMA_ORIGINS="*" ollama serve`.
- On every message the page sends: the system prompt + a **language rule** (Arabic if the message contains Arabic, otherwise English; small models tend to drift into Chinese without it) + the full conversation so far.
- Settings used: `temperature 0.3`, `num_ctx 8192`.

## 6. Customizing

- **Change the advisor's behavior**: edit `prompts/advisor_system.md`, then paste the same text into the `SYSTEM_PROMPT` constant in `index.html` (the page has its own copy so it also works without fetching files).
- **Change the model**: pull another one (`ollama pull <name>`) and select it in the dropdown. Reload the page if it does not appear.
- **Change temperature or context size**: the `options` object in the `send()` function in `index.html`.
- **Change the example chips**: the `EXAMPLES` array in `index.html`.

## 7. Troubleshooting

| Problem | Fix |
|---------|-----|
| Status "غير متصل" / "تعذر الاتصال بـ Ollama" | Make sure Ollama is running (`ollama serve`) and you opened the site through `serve.py` |
| Message about `file://` | You opened the file directly. Run `python3 serve.py` and use `http://localhost:8000` |
| `Address already in use` | Another server uses the port: `python3 serve.py 8080` |
| Dropdown empty / "لا توجد نماذج" | Run `ollama pull qwen2.5:7b-instruct` |
| Replies are useless chat ("I understand the task...") | The model is too small. Use a 3B or 7B model |
| Reply in Chinese or the wrong language | Start a new chat and write your idea clearly in Arabic or English |
| Very slow replies | Normal on CPU. Try `qwen2.5:3b-instruct`, close other heavy apps, or use a GPU |
| Out-of-memory / model fails to load | Use a smaller model |

## Known limitations

- Each student's browser must reach an Ollama running on **their own machine** (or a shared server you run). A public static host such as GitHub Pages cannot reach a visitor's local Ollama in a useful way; a real deployment needs a server hosting the model plus a small backend.
- No chat history, no login, no mentor matching yet. This is a demo.
- Local models can make mistakes. Answers are guidance only and should be checked with the mentor.
