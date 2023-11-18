from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from openai import OpenAI
import sys
import os
from pathlib import Path
from contextlib import closing

openai_client = OpenAI()  # Initialize the OpenAI client

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS

# Check if the API key is provided as a command-line argument
if len(sys.argv) != 2:
    print("Usage: python app.py <OpenAI_API_Key>")
    sys.exit(1)

# Set the OpenAI API key
openai_client.api_key = sys.argv[1]

# Route to serve the HTML page
@app.route('/')
def index():
    return render_template('page.html')

# Endpoint to handle the text-to-speech conversion
@app.route('/tts', methods=['POST'])
def text_to_speech():
    text = request.json.get('text')
    temp_audio_path = Path("temp_audio.mp3")  # Temporary file path

    # Call the OpenAI TTS API
    try:
        response = openai_client.audio.speech.create(
            model="tts-1",
            input=text,
            voice="nova",
        )
        # Stream the audio to a temporary file
        with closing(response):  # Make sure the stream is closed properly
            with open(str(temp_audio_path), 'wb') as audio_file:
                audio_file.write(response.content)
        
        # Send the audio file to the client
        return send_file(str(temp_audio_path), as_attachment=True, mimetype='audio/mpeg')
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Cleanup the temporary file after sending it
        try:
            os.remove(str(temp_audio_path))
        except OSError as e:
            print(f"Error deleting file {temp_audio_path}: {e.strerror}")

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)

