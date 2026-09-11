from flask import Flask, request, jsonify, render_template
from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

print("Loading AI model...")

tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
model = AutoModel.from_pretrained("microsoft/codebert-base")

print("AI model loaded.")

def get_embedding(code):
    inputs = tokenizer(
        code,
        return_tensors="pt",
        truncation=True,
        padding=True
    )

    with torch.no_grad():
        outputs = model(**inputs)

    return outputs.last_hidden_state.mean(dim=1)

def cosine_sim(a, b):
    return F.cosine_similarity(a, b).item() * 100

def detect_logic(code):

    logic = {
        "add": "+" in code,
        "multiply": "*" in code,
        "loop": "for" in code or "while" in code,
        "print": "System.out" in code
    }

    return logic

@app.route("/similarity", methods=["POST"])
def similarity():

    data = request.json

    code1 = data["code1"]
    code2 = data["code2"]
    
    # Convert both programs into embeddings
    emb1 = get_embedding(code1)
    emb2 = get_embedding(code2)

    # Compare the embeddings
    ai_score = cosine_sim(emb1, emb2)

    logic1 = detect_logic(code1)
    logic2 = detect_logic(code2)

    # Apply simple logic-based rules
    penalty = 0

    if logic1["loop"] != logic2["loop"]:
        penalty += 40

    if logic1["add"] != logic2["add"]:
        penalty += 20

    if logic1["multiply"] != logic2["multiply"]:
        penalty += 20

    final_score = max(0, ai_score - penalty)

    # Return the final similarity score
    return jsonify({
        "similarity": round(final_score, 2)
    })

@app.route("/compare", methods=["POST"])
def compare_ui():

    code1 = request.form.get("code1", "").strip()
    code2 = request.form.get("code2", "").strip()

    if not code1 or not code2:
        return render_template("index.html", similarity="Please enter both codes.")

    emb1 = get_embedding(code1)
    emb2 = get_embedding(code2)

    ai_score = cosine_sim(emb1, emb2)

    logic1 = detect_logic(code1)
    logic2 = detect_logic(code2)

    penalty = 0

    if logic1["loop"] != logic2["loop"]:
        penalty += 40

    if logic1["add"] != logic2["add"]:
        penalty += 20

    if logic1["multiply"] != logic2["multiply"]:
        penalty += 20

    final_score = max(0, ai_score - penalty)

    return render_template(
        "index.html",
        similarity=round(final_score, 2)
    )

if __name__ == "__main__":
    app.run(debug=False)