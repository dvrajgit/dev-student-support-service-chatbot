# dev-student-support-service-chatbot

## Run

```bash
python app.py
```

Open `http://127.0.0.1:5000/`. If port 5000 is busy, Flask may use the port from the `PORT` environment variable.

## Login

Default username: `student`

Default password: `student123`

You can change them with environment variables:

```bash
set CHATBOT_USERNAME=your_username
set CHATBOT_PASSWORD=your_password
python app.py
```

## Groq API

Academic and Internship modes use Groq. Paste a Groq API key in the app, or set it before starting Flask:

```bash
set GROQ_API_KEY=your_groq_api_key
set GROQ_MODEL=llama-3.1-8b-instant
python app.py
```
