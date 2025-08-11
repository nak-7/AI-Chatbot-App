**AI Chatbot MVP**

📌 Overview
This project is a Minimum Viable Product (MVP) for an AI-powered chatbot web application. It enables real-time interaction between users and an AI model, with chat history stored in an SQLite database for persistence. The project follows a frontend-backend architecture, ensuring clean separation of concerns and easy scalability.

The backend is built using FastAPI for handling requests, integrated with the Google Generative AI API for intelligent responses. The frontend is a simple HTML/CSS/JavaScript interface, designed for fast performance and minimal complexity.

**⚙️ How It Works**

User Input – The user enters a message in the chatbot interface.

API Request – The message is sent to the FastAPI backend via a POST request.

AI Processing – The backend communicates with the Google Generative AI model to generate a response.

Display Response – The AI’s reply is sent back to the frontend and displayed in the chat window.

Persistent History – The database ensures chat history is stored and retrievable for future improvements.

**🛠️ Tech Stack**

Frontend: HTML, CSS, JavaScript

Backend: Python, FastAPI

AI Integration: Google Generative AI API

Version Control: Git & GitHub

**🚀 Steps to Implement the Project**

**1️⃣ Clone the Repository**

git clone https://github.com/nak-7/AI-Chatbot-App.git

cd AI Chatbot App

**2️⃣ Setup Backend**

Navigate to the backend folder:

cd backend

Create and activate a virtual environment:

python -m venv venv

source venv/bin/activate   # Mac/Linux

venv\Scripts\activate      # Windows

Install dependencies:

pip install -r requirements.txt

Create a .env file and add your Google API key:

API_KEY=your_google_generative_ai_api_key

Run the FastAPI server:

uvicorn main:app --reload --port 8000

**3️⃣ Setup Frontend**

Navigate to the frontend folder.

Open index.html in your browser OR use a local server (e.g., Live Server in VS Code).

Ensure the backend server is running before sending messages.

**4️⃣ Run the Application**

Open the chatbot page in your browser.

Type a message and press Send.

The AI response will appear in real-time, and chat history will be saved.

**🔮 Future Scope**

User Authentication – Allow multiple users with separate chat histories.

Advanced UI/UX – Improve design with animations, dark mode, and mobile responsiveness.

Conversation Context – Maintain chat context for better AI responses.

Export Chat History – Let users download conversations as text or PDF.

Multi-language Support – Enable conversations in various languages.

**⚠️ Limitations**

No Contextual Memory – Currently, the chatbot treats each query independently.

Single-User Database – All chat history is stored together without user segregation.

API Dependency – Requires an active Google Generative AI API key and internet access.

No authentication — anyone can access and use the chatbot.
