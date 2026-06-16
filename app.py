from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pytubefix import YouTube
from pytubefix.cli import on_progress
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get-link', methods=['POST'])
def get_link():
    data = request.get_json()
    video_url = data.get('url')
    if not video_url:
        return jsonify({'success': False, 'message': 'No URL provided'}), 400

    try:
        # استخدام كود تشغيلي يحاكي متصفح الجوال لتفادي حظر سيرفرات الاستضافة
        yt = YouTube(video_url, client='ANDROID_TESTSUITE')
        
        # جلب أعلى جودة MP4 تحتوي على صوت وصورة مسبقاً (مدمجة جاهزة)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').get_highest_resolution()
        
        if stream and stream.url:
            return jsonify({'success': True, 'download_url': stream.url})
            
        return jsonify({'success': False, 'message': 'Progressive stream not found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
