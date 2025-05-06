import aiml
import os
import json
import re
import requests
from PIL import Image
from io import BytesIO

def is_valid_url(url):
    url_pattern = re.compile(r'https?://\S+\.\S+')
    return bool(url_pattern.match(url))

def interpret_url(url):
    try:
        response = requests.head(url, timeout=5)
        content_type = response.headers.get('Content-Type', '')

        if 'image' in content_type:
            return f"Je vois que tu as partagé une image. [IMG:{url}]"
        elif 'html' in content_type:
            return f"C'est un lien vers une page web: {url}"
        else:
            return f"Tu as partagé un lien: {url}"
    except:
        return f"Je ne peux pas interpréter ce lien: {url}"

def display_image(image_url):
    try:
        if os.path.exists(image_url):  # Local file
            image = Image.open(image_url)
            image.show()
            return True
        elif is_valid_url(image_url):  # Remote URL
            response = requests.get(image_url)
            image = Image.open(BytesIO(response.content))
            image.show()
            return True
        return False
    except Exception as e:
        print(f"Couldn't display image: {e}")
        return False

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

        url_match = re.search(r'(https?://\S+)', user_input)
        if url_match:
            url = url_match.group(1)
            interpretation = interpret_url(url)
            kernel.setPredicate("url_interpretation", interpretation)
            kernel.setPredicate("last_url", url)

        response = kernel.respond(user_input)

        img_match = re.search(r'\[IMG:(.*?)\]', response)
        if img_match:
            image_path = img_match.group(1)
            plain_text = response.replace(img_match.group(0), "")
            if plain_text.strip():
                print(plain_text)

            if display_image(image_path):
                print(f"[Displaying image: {image_path}]")
            else:
                print(f"Could not display image: {image_path}")
        else:
            print(response)


if __name__ == "__main__":
    main()