# Java Code Intent Similarity Detector

## Project Overview

This project compares two Java programs and measures how similar their implementation logic is. Instead of comparing only the source code text, the system uses AI to understand the intent of the programs.

The project combines Java, Python and CodeBERT to calculate the similarity score between two Java methods.

---

## Features

- Extracts Java methods using JavaParser
- Converts code into embeddings using CodeBERT
- Compares embeddings using Cosine Similarity
- Applies additional rule-based logic checks
- Displays similarity score through a web interface

---

## Technologies Used

- Java
- Maven
- JavaParser
- Python
- Flask
- PyTorch
- Hugging Face Transformers
- CodeBERT
- HTML
- CSS

---

## Project Structure

```text
intent-sim/
│
├── src/
│   └── main/
│       └── java/
│           └── com/intentsim/
│               ├── App.java
│               └── MethodExtractor.java
│
├── python-api/
│   ├── app.py
│   └── templates/
│       └── index.html
│
├── pom.xml
└── README.md
```

---

## How to Run

### Start the Python Server

```bash
cd python-api
python app.py
```

### Run the Java Application

```bash
mvn clean compile
mvn exec:java "-Dexec.mainClass=com.intentsim.App"
```

---

## Sample Output

```
CASE 1: SAME LOGIC
Similarity: 99.90%

CASE 2: DIFFERENT LOGIC
Similarity: 59.88%

CASE 3: COMPLETELY DIFFERENT
Similarity: 38.37%
```

---

## Future Improvements

- Support multiple programming languages
- Compare entire Java files instead of a single method
- Improve the UI
- Generate similarity reports

---

## License

This project was developed for academic learning purposes.