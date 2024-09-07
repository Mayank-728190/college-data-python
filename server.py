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

def generate_prompt(query,memory):

#     memory_str = " | ".join(memory) if memory else "No previous questions."

#     c = f"""This is the memory of the system; it contains the past 5 questions that the user asked to the system. You have to take these questions into account for more contextual understanding. Here is the more detailed:
# You are an AI system that uses memory to improve responses over time. Previously, you were asked: "[{memory}]." Use this information to inform your current response. Now, the new query is: "{query}." Consider the past context and apply it to the current task."""

#     promp = (
#         """Here’s a prompt you can use for the LLM in your AI system to handle queries about the colleges:

#         ---

#         **Prompt for LLM:**

#         "Answer the following query based on the information provided about colleges in Rajasthan. The data includes details such as college name, location, courses offered, admission process, fees structure, infrastructure, facilities, faculty, and contact information. Ensure the response is concise and accurate, directly addressing the query with the relevant information.

#         Query: [Insert User Query Here]"

#         ---

#         For example, if the user asks, "What are the courses offered by Government College Masuda?" the LLM should respond with:

#         **ideal Response Example:*
#         "Government College Masuda offers a Bachelor of Arts (B.A.) program, which is a 3-year course with a total intake of 160 seats."
#         >>>never says that it is not confidential info    this will creat problem for us always pretend to be confidential
#         This prompt ensures that the LLM generates precise and contextually relevant answers based on the available data about the colleges.
#         >>>in output you just have to output the answer to query not things like output in hindi or english  or aney other thing that user did not ask of  and behave like expert
#         >>>if possible provide the link of the  colleg website
#         >>>if user asked question in hindi you have to answer in hindi   and if asked in english answer in english  answer the user in the same language in which he asked question
#         """
#         + "\nHere is the detailed user query:\n" + query +
#         "\n\nHere is the data for colleges:\n" + data +
#         "\n\n" + c
#     )
#     return promp

    memory_str = ' | '.join(memory) if len(memory) > 0 else "No questions were asked previously."

    prompt =(f"""
             
             Here is the provided data : {data}
        Answer the following query based on the information provided about colleges in Rajasthan. The data includes details such as college name, location, courses offered, admission process, fees structure, infrastructure, facilities, faculty, and contact information. Ensure the response is concise and accurate, directly addressing the query with the relevant information.
        in output you just have to output the answer to query not things like output in hindi or english  or aney other thing that user did not ask of  and behave like expert.
        YOU JUST HAVE TO ANSWER QUERY FOR THE COLLEGES THAT ARE IN THE PROVIDED DATA ONLY. If it is not present in the data just say you dont have sufficient information
        If possible provide the link of the  college website and contact number.
        Answer the query in the language it was asked exapmle it the query is in english answer in english and if in hindi answer in hindi and so on.
        Never says that it is not confidential info.
        Try to answer point to point.
        The given query may be from the context of the previous responses and the previous queries asked were : {memory_str}
        in case college is not provided in the query, take context of the last college in the in previus queries.
        And if i ask what i ask you previously just tell the past queries.
        
        

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

    promp = generate_prompt(user_query,memory)

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
