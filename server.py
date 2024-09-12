from flask import Flask, request, jsonify
from groq import Groq
import os

app = Flask(__name__)

# Initialize Groq client
client = Groq(api_key="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")

# Read the college data from the file
file_path = "collegedata.txt"
with open(file_path, 'r') as file:
    data = file.read()

memory = []

def generate_prompt(query, memory):
    memory_str = ' | '.join(memory) if len(memory) > 0 else "No questions were asked previously."

    prompt = (
        f"""
        Here is the provided data: {data}
        Answer the following query based on the information provided about colleges in Rajasthan. The data includes details such as college name, location, courses offered, admission process, fees structure, infrastructure, facilities, faculty, and contact information. Ensure the response is concise and accurate, directly addressing the query with the relevant information.
        in output you just have to output the answer to query not things like output in hindi or english  or any other thing that user did not ask of and behave like expert.
        YOU JUST HAVE TO ANSWER QUERY FOR THE COLLEGES THAT ARE IN THE PROVIDED DATA ONLY. You can answer by search if the college is present in provided data else if the college is not present in the college list just say you don't have sufficient information about that college.
        If possible provide the link of the college website and contact number.
        Answer the query in the language it was asked (for example, if the query is in English, answer in English; if in Hindi, answer in Hindi).
        Never say that it is not confidential info.
        Try to answer point to point.
        The given query may be from the context of the previous responses, and the previous queries asked were: {memory_str}.
        If the user asks what they asked previously, just tell the past queries.

        Here is the detailed query: {query}
        """
    )
    return prompt

@app.route('/query', methods=['POST'])
def handle_query():
    user_query = request.json.get('query')
    memory = request.json.get('memory')

    if not user_query:
        return jsonify({"error": "Query is required"}), 400
    if not memory:
        memory = []

    promp = generate_prompt(user_query, memory)

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": promp
                }
            ],
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

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
