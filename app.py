from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
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

    # إرسال الطلب إلى خوادم معالجة كـوبالت المفتوحة والمحمية ضد الحظر
    cobalt_api_url = "https://api.cobalt.tools/api/json"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": video_url,
        "videoQuality": "720", # جودة مدمجة ممتازة صوت وصورة تلقائياً
        "filenameStyle": "classic"
    }

    try:
        response = requests.post(cobalt_api_url, json=payload, headers=headers, timeout=10)
        result = response.json()
        
        # إذا نجح جلب الرابط من الـ API المشغل
        if response.status_code == 200 and result.get('status') == 'stream':
            return jsonify({'success': True, 'download_url': result.get('url')})
        elif result.get('status') == 'redirect':
            return jsonify({'success': True, 'download_url': result.get('url')})
            
        return jsonify({'success': False, 'message': result.get('text', 'Error from processing server')})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
