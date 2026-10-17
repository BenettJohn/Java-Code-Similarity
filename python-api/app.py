import os
import threading
from flask import Flask, jsonify, render_template, request

os.environ.setdefault("HF_HOME", "/tmp/huggingface")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

app = Flask(__name__)

MODEL_NAME = "microsoft/codebert-base"
MAX_CODE_CHARS = 12000

_tokenizer = None
_model = None
_model_lock = threading.Lock()


def load_model():
    """Load CodeBERT only when the first comparison is requested."""
    global _tokenizer, _model

    if _tokenizer is not None and _model is not None:
        return _tokenizer, _model

    with _model_lock:
        if _tokenizer is None or _model is None:
            from transformers import AutoModel, AutoTokenizer

            print(f"Loading {MODEL_NAME} for the first comparison...")
            tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
            model = AutoModel.from_pretrained(MODEL_NAME)
            model.eval()
            _tokenizer = tokenizer
            _model = model
            print("CodeBERT is ready.")

    return _tokenizer, _model


def get_embedding(code):
    import torch

    tokenizer, model = load_model()
    inputs = tokenizer(
        code,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=512,
    )

    with torch.no_grad():
        outputs = model(**inputs)

    # Mean pooling over token embeddings, matching the original project approach.
    return outputs.last_hidden_state.mean(dim=1)


def detect_logic(code):
    """Small heuristic checks used alongside the embedding score."""
    return {
        "add": "+" in code,
        "multiply": "*" in code,
        "loop": "for" in code or "while" in code,
        "print": "System.out" in code,
    }


def compare_code(code1, code2):
    import torch.nn.functional as functional

    embedding1 = get_embedding(code1)
    embedding2 = get_embedding(code2)
    ai_score = functional.cosine_similarity(embedding1, embedding2).item() * 100

    logic1 = detect_logic(code1)
    logic2 = detect_logic(code2)
    penalty = 0

    if logic1["loop"] != logic2["loop"]:
        penalty += 40
    if logic1["add"] != logic2["add"]:
        penalty += 20
    if logic1["multiply"] != logic2["multiply"]:
        penalty += 20

    # Keep the display in a percentage range.
    final_score = max(0.0, min(100.0, ai_score - penalty))
    return round(final_score, 2)


def validate_code(code1, code2):
    if not isinstance(code1, str) or not isinstance(code2, str):
        return "Please provide both Java code snippets."
    if not code1.strip() or not code2.strip():
        return "Please enter both Java programs before comparing."
    if len(code1) > MAX_CODE_CHARS or len(code2) > MAX_CODE_CHARS:
        return f"Each code snippet must be {MAX_CODE_CHARS:,} characters or fewer."
    return None


def result_label(score):
    if score >= 85:
        return "Highly similar"
    if score >= 50:
        return "Moderately similar"
    return "Lower similarity"


@app.route("/")
def home():
    return render_template("index.html", code1="", code2="")


@app.route("/health")
def health():
    # This endpoint intentionally does not load the model.
    return jsonify({"status": "ok", "model_loaded": _model is not None})


@app.route("/similarity", methods=["POST"])
def similarity():
    data = request.get_json(silent=True) or {}
    code1 = data.get("code1", "")
    code2 = data.get("code2", "")

    validation_error = validate_code(code1, code2)
    if validation_error:
        return jsonify({"error": validation_error}), 400

    try:
        score = compare_code(code1, code2)
        return jsonify({
            "similarity": score,
            "label": result_label(score),
            "note": "This is an experimental estimate, not proof of plagiarism or code ownership.",
        })
    except Exception:
        app.logger.exception("Code comparison failed")
        return jsonify({
            "error": "The comparison could not be completed. The model may still be downloading or the host may have reached a resource limit. Please try again shortly."
        }), 503


@app.route("/compare", methods=["POST"])
def compare_ui():
    code1 = request.form.get("code1", "")
    code2 = request.form.get("code2", "")
    validation_error = validate_code(code1, code2)

    if validation_error:
        return render_template(
            "index.html", code1=code1, code2=code2, error_message=validation_error
        ), 400

    try:
        score = compare_code(code1, code2)
        return render_template(
            "index.html",
            code1=code1,
            code2=code2,
            similarity=score,
            result_label=result_label(score),
        )
    except Exception:
        app.logger.exception("Code comparison failed")
        return render_template(
            "index.html",
            code1=code1,
            code2=code2,
            error_message=(
                "The comparison could not be completed. The model may still be downloading "
                "or the host may have reached a resource limit. Please try again shortly."
            ),
        ), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
