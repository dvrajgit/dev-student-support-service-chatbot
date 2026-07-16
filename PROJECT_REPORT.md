# Student Support Service Chatbot — Project Report

## 1. Introduction

The **Student Support Service Chatbot** is a lightweight, web-based conversational assistant designed to answer common student service queries. It handles questions about registration, support-desk hours, and general college information through a clean browser interface backed by a Flask API. The bot combines a small scikit-learn intent classifier, rule-based pattern matching, and an optional Google Gemini fallback to provide fast, deterministic responses for known topics while remaining extensible for open-ended questions.

## 2. Objectives

- Provide instant, automated answers to frequently asked student support questions.
- Demonstrate a hybrid NLP approach: local ML classification with deterministic rule-based and third-party LLM fallbacks.
- Deliver a simple, responsive chat interface accessible from any modern browser.
- Keep the deployment footprint small and the code easy to extend.

## 3. Problem Statement

University and college support desks receive repetitive questions ("How do I register?", "What are your hours?", "How do I reset my password?"). Answering each manually consumes staff time and leads to delayed responses. A chatbot that can resolve these routine queries automatically improves response time and frees staff for more complex issues.

## 4. Scope

- **Supported topics:** greetings, support-desk hours, class registration, and fallback routing for unknown questions.
- **Deployment:** Flask backend serving a static HTML/JS/CSS frontend; can run locally or on any platform that supports Python (e.g., Fly.io, Heroku).
- **Extensibility:** New intents can be added by updating the training data and re-running `train_model.py`.

## 5. Technology Stack

| Layer | Technologies |
|-------|--------------|
| Backend | Python, Flask |
| NLP/ML | scikit-learn (TfidfVectorizer + LogisticRegression), joblib |
| External API | Google Generative Language (Gemini) via REST (optional) |
| Frontend | HTML5, CSS3, vanilla JavaScript |
| Testing | Python `unittest` |
| Persistence | joblib model files (`model/pipeline.joblib`, `model/responses.joblib`) |

## 6. System Architecture

```
┌─────────────────┐      POST /api/chat       ┌─────────────────────┐
│  Browser (HTML/ │ ─────────────────────────▶│  Flask App (app.py) │
│  CSS/JS)        │                           │                     │
└─────────────────┘◀────────────────────────│  StudentSupportChatbot
                         JSON reply          │                     │
                                             └──────────┬──────────┘
                                                        │
                            ┌───────────────────────────┼───────────────────────────┐
                            ▼                           ▼                           ▼
                  ┌─────────────────┐        ┌─────────────────┐          ┌─────────────────┐
                  │  ML Pipeline    │        │  Regex Patterns │          │  Gemini API     │
                  │  (joblib)       │        │  (hard-coded)   │          │  (optional)     │
                  └─────────────────┘        └─────────────────┘          └─────────────────┘
```

The chatbot processes every incoming message in three stages:

1. **ML intent classification:** A TF-IDF + Logistic Regression pipeline predicts a label; if the label has a known response, it is returned.
2. **Rule-based pattern matching:** If the ML pipeline is unavailable or fails, regex patterns match common keywords.
3. **Gemini API fallback:** When `GEMINI_API_KEY` is set and the local methods do not match, the prompt is forwarded to Google's Gemini API.
4. **Default fallback:** For unrecognized queries without an API key, the bot suggests contacting the support team.

## 7. Implementation Details

### 7.1 Backend (`app.py`)

Flask serves two responsibilities:
- `GET /` returns `index.html`.
- `POST /api/chat` accepts JSON `{ "message": "..." }`, validates the input, invokes `StudentSupportChatbot.respond()`, and returns `{ "reply": "..." }`.

### 7.2 Core Chatbot (`student_support_chatbot.py`)

- Initializes regex patterns for greetings, hours, and registration.
- Loads the serialized scikit-learn pipeline and response map from `model/` when present.
- Implements the four-stage response strategy described above.
- Includes a CLI mode (`python student_support_chatbot.py`) for terminal interaction.

### 7.3 Training (`train_model.py`)

- Defines 12 training utterances across four labels: `greeting`, `hours`, `registration`, and `unknown`.
- Builds a `Pipeline` with `TfidfVectorizer(ngram_range=(1, 2), stop_words="english")` and `LogisticRegression(max_iter=1000)`.
- Serializes the trained pipeline and a label-to-response dictionary into `model/pipeline.joblib` and `model/responses.joblib`.

### 7.4 Frontend

- `index.html` provides a responsive chat shell with a message list and composer form.
- `styles.css` applies a dark-mode design with accessible contrast and a mobile layout.
- `app.js` manages the chat state, sends messages to `/api/chat`, and renders user/bot messages with a typing indicator.

## 8. Features

| Feature | Description |
|---------|-------------|
| Web chat UI | Clean, responsive interface with bot/user message bubbles. |
| ML intent classification | Local TF-IDF + logistic regression model for intent detection. |
| Rule-based fallback | Regex patterns for quick, deterministic answers. |
| Optional Gemini integration | LLM fallback when `GEMINI_API_KEY` is configured. |
| CLI mode | Run the chatbot from the terminal without the web server. |
| Unit tests | Automated tests for greetings, hours, registration, and unknown intents. |

## 9. Testing

The project includes a `tests/` directory with `unittest` cases covering the four primary response paths.

```
$ python -m unittest discover -s tests -v
test_greeting_response (test_student_support_chatbot.StudentSupportChatbotTests) ... ok
test_hours_response (test_student_support_chatbot.StudentSupportChatbotTests) ... ok
test_registration_response (test_student_support_chatbot.StudentSupportChatbotTests) ... ok
test_unknown_question_response (test_student_support_chatbot.StudentSupportChatbotTests) ... ok

----------------------------------------------------------------------
Ran 4 tests in 1.139s

OK
```

All tests pass. Note: loading the pre-trained model raises `InconsistentVersionWarning` because the saved joblib was produced with scikit-learn 1.9.0 while the current environment runs 1.6.0; the classifier still executes successfully.

## 10. Results

- The chatbot correctly maps greetings, hours, and registration queries to their predefined answers.
- Unknown questions receive a safe fallback directing students to the support team, or a Gemini-generated answer when an API key is available.
- The web frontend successfully exchanges JSON with the Flask backend and displays replies in real time.

## 11. Future Enhancements

- Expand the training corpus and add more intent labels (e.g., financial aid, campus map, transcript requests).
- Replace the static response map with a database-backed FAQ system.
- Add conversation context/memory so multi-turn exchanges remain coherent.
- Add user feedback buttons (thumbs up/down) to improve responses over time.
- Containerize the app with Docker for consistent deployments.

## 12. Conclusion

The Student Support Service Chatbot demonstrates a practical, layered approach to building a small-scale support assistant. By combining a local machine-learning classifier with regex rules and an optional LLM fallback, it balances reliability, speed, and flexibility. The included tests, responsive UI, and minimal dependency set make it a solid foundation for further development in an academic support context.
