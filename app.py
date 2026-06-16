from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import yt_dlp
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

    # إعدادات ذكية تجلب الصيغ الجاهزة مباشرة (صوت وصورة معاً) دون الحاجة لـ ffmpeg
    ydl_opts = {
        'format': 'best[ext=mp4]/best',  # جلب أفضل جودة MP4 تحتوي على الصوت والصورة مسبقاً
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            download_url = info.get('url')
            
            if download_url:
                return jsonify({'success': True, 'download_url': download_url})
                
        return jsonify({'success': False, 'message': 'Could not extract URL'})
    except Exception as e:
        # إرجاع الخطأ الحقيقي للمساعدة في التشخيص إذا حدث شيء آخر
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
