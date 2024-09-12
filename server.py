from flask import Flask, request, jsonify
from groq import Groq
import os
import speech_recognition as sr

app = Flask(__name__)

# Initialize Groq client
try:
    client = Groq(api_key=os.getenv("GROQ_API_KEY", "your_default_groq_api_key"))
except Exception as e:
    print(f"Error initializing Groq client: {e}")
    client = None

# Load college data from the file
file_path = "collegedata.txt"
try:
    with open(file_path, 'r') as file:
        data = file.read()
except FileNotFoundError:
    data = ""

memory = []

def generate_prompt(query, memory):
    memory_str = ' | '.join(memory) if len(memory) > 0 else "No previous questions."

    prompt = (
        f"""
        Here is the provided data: {data}
        Answer the following query based on the information provided about colleges in Rajasthan. The data includes details such as college name, location, courses offered, admission process, fees structure, infrastructure, facilities, faculty, and contact information. Ensure the response is concise and accurate, directly addressing the query with the relevant information.
        YOU JUST HAVE TO ANSWER QUERY FOR THE COLLEGES THAT ARE IN THE PROVIDED DATA ONLY. If the college is not present in the data, just say you don't have sufficient information.
        If possible, provide the link of the college website and contact number.
        Answer in the language the query is asked.
        The previous queries were: {memory_str}
        Here is the detailed query: {query}
        """
    )
    return prompt

# Function to handle voice recognition
def recognize_speech_from_mic():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for query...")
        audio = recognizer.listen(source)
        try:
            print("Recognizing speech...")
            text = recognizer.recognize_google(audio, language="en-US")
            print(f"Recognized Text: {text}")
            return text
        except sr.UnknownValueError:
            return "Sorry, I could not understand the audio."
        except sr.RequestError as e:
            return f"Could not request results from Google Speech Recognition service; {e}"

@app.route('/query', methods=['POST'])
def handle_query():
    user_query = request.json.get('query')
    memory = request.json.get('memory', [])

    if not user_query:
        return jsonify({"error": "Query is required"}), 400

    promp = generate_prompt(user_query, memory)

    try:
        if client:
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": promp}],
                temperature=0.2,
                max_tokens=724,
                top_p=0.2,
                stream=True,
                stop=None,
            )

            response_text = ""
            for chunk in completion:
                response_text += chunk.choices[0].delta.content or ""

            return jsonify({"response": response_text})

        else:
            return jsonify({"error": "Groq client is not initialized."}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/speech_to_text', methods=['GET'])
def handle_speech_to_text():
    # Handle speech-to-text conversion
    recognized_text = recognize_speech_from_mic()
    return jsonify({"recognized_text": recognized_text})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
