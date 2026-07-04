// AIP-C01 study chat — streaming SSE client with client-side TTFT measurement.

type Role = "user" | "assistant";
interface Turn {
  role: Role;
  text: string;
}
interface Source {
  n: number;
  breadcrumb: string;
  score: number;
}

const messagesEl = document.getElementById("messages") as HTMLElement;
const composerEl = document.getElementById("composer") as HTMLFormElement;
const inputEl = document.getElementById("input") as HTMLInputElement;
const sendEl = document.getElementById("send") as HTMLButtonElement;
const ttftEl = document.getElementById("ttft") as HTMLElement;

const turns: Turn[] = [];
let busy = false;

function addMessage(role: Role): { bubble: HTMLElement; meta: HTMLElement } {
  const wrap = document.createElement("div");
  wrap.className = `msg ${role}`;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  const meta = document.createElement("div");
  meta.className = "meta";
  wrap.append(bubble, meta);
  messagesEl.append(wrap);
  wrap.scrollIntoView({ block: "end" });
  return { bubble, meta };
}

function renderSources(meta: HTMLElement, sources: Source[]): void {
  for (const s of sources) {
    const chip = document.createElement("span");
    chip.className = "chip";
    chip.textContent = `[${s.n}] ${s.breadcrumb}`;
    chip.title = `relevance ${s.score}`;
    meta.append(chip);
  }
}

/** Parse SSE frames out of a streaming fetch body. */
async function* sseEvents(body: ReadableStream<Uint8Array>) {
  const reader = body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    let sep: number;
    while ((sep = buffer.indexOf("\n\n")) >= 0) {
      const frame = buffer.slice(0, sep);
      buffer = buffer.slice(sep + 2);
      let event = "message";
      let data = "";
      for (const line of frame.split("\n")) {
        if (line.startsWith("event: ")) event = line.slice(7).trim();
        else if (line.startsWith("data: ")) data += line.slice(6);
      }
      if (data) yield { event, data: JSON.parse(data) };
    }
  }
}

async function send(message: string): Promise<void> {
  busy = true;
  sendEl.disabled = true;
  ttftEl.textContent = "…";

  addMessage("user").bubble.textContent = message;
  const { bubble, meta } = addMessage("assistant");
  bubble.classList.add("streaming");

  const t0 = performance.now();
  let firstToken = 0;
  let text = "";

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, history: turns }),
    });
    if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`);

    for await (const { event, data } of sseEvents(res.body)) {
      switch (event) {
        case "meta":
          renderSources(meta, (data.sources ?? []) as Source[]);
          break;
        case "token":
          if (!firstToken) {
            firstToken = performance.now() - t0;
            ttftEl.textContent = `TTFT ${Math.round(firstToken)} ms`;
          }
          text += data.t as string;
          bubble.textContent = text;
          messagesEl.lastElementChild?.scrollIntoView({ block: "end" });
          break;
        case "done":
          ttftEl.textContent = `TTFT ${Math.round(firstToken)} ms · total ${(
            (performance.now() - t0) /
            1000
          ).toFixed(1)} s`;
          break;
        case "error":
          throw new Error(data.message as string);
      }
    }
    turns.push({ role: "user", text: message }, { role: "assistant", text });
    if (turns.length > 16) turns.splice(0, turns.length - 16);
  } catch (err) {
    bubble.textContent = text || `Something went wrong: ${(err as Error).message}`;
    bubble.classList.add("error");
  } finally {
    bubble.classList.remove("streaming");
    busy = false;
    sendEl.disabled = false;
    inputEl.focus();
  }
}

composerEl.addEventListener("submit", (e) => {
  e.preventDefault();
  const message = inputEl.value.trim();
  if (!message || busy) return;
  inputEl.value = "";
  void send(message);
});

inputEl.focus();
