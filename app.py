from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# قائمة خوادم معالجة متباعدة ومحدثة لضمان استقرار الخدمة وتجنب الضغط
COBALT_INSTANCES = [
    "https://api.cobalt.tools/api/json",
    "https://cobalt.0x97.cf/api/json",
    "https://api.cobalt.lol/api/json"
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get-link', methods=['POST'])
def get_link():
    data = request.get_json()
    video_url = data.get('url')
    if not video_url:
        return jsonify({'success': False, 'message': 'No URL provided'}), 400

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    payload = {
        "url": video_url,
        "videoQuality": "720",  # جودة مدمجة ممتازة جاهزة للتحميل المباشر
        "filenameStyle": "classic"
    }

    # المحاولة عبر الخوادم المتاحة بالتوالي في حال كان أحدها تحت الضغط
    for api_url in COBALT_INSTANCES:
        try:
            response = requests.post(api_url, json=payload, headers=headers, timeout=8)
            
            if response.status_code == 200:
                result = response.json()
                status = result.get('status')
                
                if status in ['stream', 'redirect'] and result.get('url'):
                    return jsonify({'success': True, 'download_url': result.get('url')})
                elif status == 'picker' and result.get('picker'):
                    # في حال وجود جودات متعددة اختر الأولى تلقائياً
                    return jsonify({'success': True, 'download_url': result['picker'][0]['url']})
                    
        except Exception:
            continue  # الانتقال للخادم التالي مباشرة في حال حدوث timeout أو خطأ

    # إذا فشلت جميع الخوادم المتاحة بسبب حظر الـ IP أو الضغط
    return jsonify({
        'success': False, 
        'message': 'جميع خوادم المعالجة السحابية مزدحمة حالياً، يرجى إعادة المحاولة بعد ثوانٍ.'
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
