import ollama



def ask_ai(prompt):

    response = ollama.chat(

        model="gemma3:latest",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]

    )


    return response["message"]["content"]



if __name__ == "__main__":


    question = """
    Explain what SQL is in simple words.
    """


    answer = ask_ai(question)


    print(answer)