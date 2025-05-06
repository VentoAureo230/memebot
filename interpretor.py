import aiml
import os
import json


def main():
    kernel = aiml.Kernel()

    try:
        with open("system/memebot.properties", "r", encoding="utf-8") as f:
            properties = json.loads(f.read())

        for prop in properties:
            if len(prop) == 2:
                name, value = prop
                kernel.setBotPredicate(name, value)
    except Exception as e:
        print(f"Error loading properties: {e}")

    if kernel.getBotPredicate("name") == "set_when_loaded":
        kernel.setBotPredicate("name", "MemeBot")

    try:
        with open("substitutions/denormal.substitution", "r", encoding="utf-8") as f:
            substitutions = json.loads(f.read())

        for pattern, replacement in substitutions:
            if hasattr(kernel, "addSubstitution"):
                kernel.addSubstitution(pattern, replacement)
    except Exception as e:
        print(f"Error loading substitutions: {e}")

    kernel.learn("files/udc.aiml")

    learn_file = kernel.getBotPredicate("learn-filename")
    max_size = kernel.getBotPredicate("max-learn-file-size")

    if learn_file != "unknown" and os.path.exists(learn_file):
        try:
            if os.path.getsize(learn_file) <= int(max_size):
                kernel.learn(learn_file)
            else:
                print(f"Learn file too large: {learn_file}")
        except Exception as e:
            print(f"Error loading learn file: {e}")

    print(f"{kernel.getBotPredicate('name')} is ready. Type 'quit' to exit.")
    while True:
        user_input = input("> ")
        if user_input.lower() == "quit":
            break
        response = kernel.respond(user_input)
        print(response)


if __name__ == "__main__":
    main()