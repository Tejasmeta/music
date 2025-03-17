from flask import Flask, render_template, request, jsonify, send_file, url_for
import requests
import os
from gtts import gTTS  # Google Text-to-Speech

app = Flask(__name__)

# Hugging Face API Key
HUGGING_FACE_API_KEY = "api"

# Hugging Face Models
LYRICS_MODEL = "tiiuae/falcon-7b-instruct"
MUSIC_MODEL = "facebook/musicgen-small"

# API Headers
HEADERS = {"Authorization": f"Bearer {HUGGING_FACE_API_KEY}"}

# File Paths
STATIC_DIR = "static"
MUSIC_FILE = os.path.join(STATIC_DIR, "generated_music.wav")  
LYRICS_FILE = os.path.join(STATIC_DIR, "lyrics.txt")
VOICE_FILE = os.path.join(STATIC_DIR, "lyrics_audio.mp3")
FINAL_SONG_FILE = os.path.join(STATIC_DIR, "final_song.mp3")  

# Ensure static directory exists
os.makedirs(STATIC_DIR, exist_ok=True)

# Generate Lyrics
def generate_lyrics(theme):
    api_url = f"https://api-inference.huggingface.co/models/{LYRICS_MODEL}"
    payload = {"inputs": f"Generate song lyrics based on the theme: {theme}"}

    response = requests.post(api_url, headers=HEADERS, json=payload)

    if response.status_code == 200:
        try:
            data = response.json()
            lyrics = data[0].get("generated_text", "") if isinstance(data, list) else "Lyrics generation failed."
            if lyrics:
                with open(LYRICS_FILE, "w", encoding="utf-8") as f:
                    f.write(lyrics)
            return lyrics
        except Exception as e:
            return f"Error processing lyrics: {str(e)}"
    return f"Error generating lyrics: {response.text}"

# Generate Music
def generate_music(theme):
    api_url = f"https://api-inference.huggingface.co/models/{MUSIC_MODEL}"
    payload = {"inputs": theme}

    response = requests.post(api_url, headers=HEADERS, json=payload)

    if response.status_code == 200:
        with open(MUSIC_FILE, "wb") as f:
            f.write(response.content)
        return MUSIC_FILE
    return None

# Convert Lyrics to Speech
def generate_lyrics_audio():
    if os.path.exists(LYRICS_FILE):
        with open(LYRICS_FILE, "r", encoding="utf-8") as f:
            lyrics = f.read()
        
        tts = gTTS(text=lyrics, lang="en")
        tts.save(VOICE_FILE)  
        return VOICE_FILE
    return None

# Mock: Combine Lyrics Audio and Music
def generate_final_song():
    if os.path.exists(VOICE_FILE) and os.path.exists(MUSIC_FILE):
        os.rename(MUSIC_FILE, FINAL_SONG_FILE)  # Simulating merging
        return FINAL_SONG_FILE
    return None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    theme = request.json.get("theme", "").strip()
    if not theme:
        return jsonify({"error": "Please enter a theme."}), 400

    lyrics = generate_lyrics(theme)
    music = generate_music(theme)
    voice = generate_lyrics_audio()

    if not music:
        return jsonify({"lyrics": lyrics, "music": None, "error": "Music generation failed"}), 500

    return jsonify({
        "lyrics": lyrics,
        "music": url_for('download_file', filename="generated_music.wav"),
        "lyrics_audio": url_for('download_file', filename="lyrics_audio.mp3"),
        "lyrics_file": url_for('download_file', filename="lyrics.txt")
    })

@app.route("/final_song", methods=["GET"])
def final_song():
    final_song = generate_final_song()
    if final_song:
        return jsonify({"final_song": url_for('download_file', filename="final_song.mp3")})
    return jsonify({"error": "Final song creation failed"}), 500

@app.route("/download/<filename>")
def download_file(filename):
    file_path = os.path.join(STATIC_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({"error": "File not found."}), 404

if __name__ == "__main__":
    app.run(debug=True)
