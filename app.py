
from flask import Flask, request, send_file
from flask_cors import CORS
import yt_dlp
import openai
import os
import uuid

app = Flask(__name__)
CORS(app)

openai.api_key = 'YOUR_OPENAI_API_KEY'

@app.route('/translate', methods=['POST'])
def translate_audio():
    data = request.json
    video_url = data.get("url")
    target_lang = data.get("lang", "ru")

    filename = f"audio_{uuid.uuid4()}.mp3"

    # Скачиваем аудио
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': filename,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3'
        }]
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    # Распознавание речи
    with open(filename, 'rb') as f:
        transcript = openai.Audio.transcribe("whisper-1", f)

    # Перевод текста
    translated = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"Переведи это на язык {target_lang}"},
            {"role": "user", "content": transcript["text"]}
        ]
    )

    translated_text = translated['choices'][0]['message']['content']
    tts_file = f"tts_{uuid.uuid4()}.mp3"

    os.system(f'gtts-cli "{translated_text}" --lang {target_lang} --output {tts_file}')

    return send_file(tts_file, mimetype='audio/mpeg')

if __name__ == '__main__':
    app.run(port=5000)

