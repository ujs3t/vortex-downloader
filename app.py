from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vortex DL - محمل الفيديوهات السريع</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #111; color: white; margin: 0; padding: 40px 20px; text-align: center; }
        .container { max-width: 500px; background: #222; padding: 30px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); margin: 0 auto; border: 1px solid #333; }
        input[type="text"] { width: 90%; padding: 12px; margin: 20px 0; border: 1px solid #444; background: #333; color: white; border-radius: 8px; font-size: 16px; text-align: center; }
        button { background-color: #00ff87; color: #111; padding: 12px 25px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: bold; width: 95%; }
        button:hover { background-color: #00df76; }
        #loading { display: none; color: #888; margin-top: 15px; }
        #result { margin-top: 25px; display: none; }
        .download-btn { display: block; background-color: #007bff; color: white; padding: 12px; text-decoration: none; border-radius: 8px; font-weight: bold; margin-top: 10px; }
    </style>
</head>
<body>
<div class="container">
    <h2>📥 Vortex DL Lite</h2>
    <p>ضع رابط الفيديو للتحميل مباشرة من جوالك أو كمبيوترك</p>
    <input type="text" id="videoUrl" placeholder="https://www.youtube.com/watch?v=...">
    <button onclick="getDownloadLink()">استخراج رابط التحميل</button>
    <div id="loading">⏳ جاري جلب الرابط المباشر من السيرفر السحابي...</div>
    <div id="result">
        <h3>🎉 جاهز للتحميل!</h3>
        <a id="downloadLink" href="#" target="_blank" class="download-btn">اضغط هنا لبدء التحميل المباشر</a>
    </div>
</div>
<script>
    async function getDownloadLink() {
        const urlInput = document.getElementById('videoUrl').value;
        const loadingDiv = document.getElementById('loading');
        const resultDiv = document.getElementById('result');
        const downloadLink = document.getElementById('downloadLink');
        if (!urlInput) { alert('ضع الرابط أولاً!'); return; }
        loadingDiv.style.display = 'block'; resultDiv.style.display = 'none';
        try {
            const response = await fetch('/get-link', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: urlInput })
            });
            const data = await response.json();
            if (data.success) {
                downloadLink.href = data.download_url;
                resultDiv.style.display = 'block';
            } else { alert('فشل استخراج الرابط.'); }
        } catch (error) { alert('حدث خطأ في الاتصال بالسيرفر!'); }
        loadingDiv.style.display = 'none';
    }
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/get-link', methods=['POST'])
def get_link():
    data = request.get_json()
    video_url = data.get('url')
    if not video_url:
        return jsonify({'success': False}), 400

    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            download_url = info.get('url')
            if download_url:
                return jsonify({'success': True, 'download_url': download_url})
        return jsonify({'success': False})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Render يطلب تشغيل السيرفر على البورت المعين من قبله تلقائياً
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)