import docker
from context import build_messages
from flask import Flask, jsonify, request, send_from_directory
from providers import ProviderError, get_provider

app = Flask(__name__, static_folder="static", static_url_path="")

MODES = {"freeform", "copilot", "log_analyst", "tutor"}
TRACKS = ["ssh", "rdp", "web", "remediate"]


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/health")
def health():
    try:
        provider = get_provider()
    except ProviderError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 503
    return jsonify({"ok": True, "provider": type(provider).__name__})


@app.get("/api/tracks")
def tracks():
    return jsonify({"tracks": TRACKS})


@app.get("/api/containers")
def containers():
    try:
        client = docker.from_env()
        names = [c.name for c in client.containers.list()]
    except docker.errors.DockerException as exc:
        return jsonify({"error": str(exc)}), 503
    return jsonify({"containers": sorted(names)})


@app.post("/api/chat")
def chat():
    body = request.get_json(silent=True) or {}
    mode = body.get("mode", "freeform")
    message = (body.get("message") or "").strip()

    raw_history = body.get("history") or []
    if not isinstance(raw_history, list):
        return jsonify({"error": "history must be a list"}), 400

    # Keep the request bounded (prevents unbounded prompt growth / large payloads).
    raw_history = raw_history[-40:]
    history: list[dict[str, str]] = []
    for item in raw_history:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        content = item.get("content")
        if role in ("user", "assistant") and isinstance(content, str):
            history.append({"role": role, "content": content})

    container = body.get("container")
    track = body.get("track")
    if mode not in MODES:
        return jsonify({"error": f"Unknown mode: {mode!r}"}), 400
    if not message:
        return jsonify({"error": "message is required"}), 400

    try:
        messages = build_messages(mode, message, history, container, track)
        provider = get_provider()
        reply = provider.chat(messages)
    except ProviderError as exc:
        return jsonify({"error": str(exc)}), 502
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8700)
