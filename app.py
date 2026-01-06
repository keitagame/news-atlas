from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
import requests
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

# 気象庁の地震情報API（P2P地震情報のAPIを使用）
EARTHQUAKE_API = "https://api.p2pquake.net/v2/history?codes=551&limit=20"

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/earthquakes')
def get_earthquakes():
    try:
        response = requests.get(EARTHQUAKE_API, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        earthquakes = []
        for item in data:
            if item.get('code') == 551:  # 地震情報
                eq_data = item.get('earthquake', {})
                earthquakes.append({
                    'id': item.get('id'),
                    'time': eq_data.get('time'),
                    'hypocenter': eq_data.get('hypocenter', {}).get('name', '不明'),
                    'magnitude': eq_data.get('hypocenter', {}).get('magnitude', 0),
                    'depth': eq_data.get('hypocenter', {}).get('depth', 0),
                    'maxScale': eq_data.get('maxScale', 0),
                    'domesticTsunami': eq_data.get('domesticTsunami', 'Unknown')
                })
        
        return jsonify({'success': True, 'data': earthquakes})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>地震速報</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', 'Hiragino Sans', Meiryo, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .update-info {
            font-size: 0.9em;
            opacity: 0.9;
        }
        
        .refresh-btn {
            background: white;
            color: #667eea;
            border: none;
            padding: 12px 30px;
            font-size: 1em;
            border-radius: 25px;
            cursor: pointer;
            margin: 20px 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
            transition: all 0.3s;
        }
        
        .refresh-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.3);
        }
        
        .earthquake-list {
            display: grid;
            gap: 20px;
        }
        
        .earthquake-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }
        
        .earthquake-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 30px rgba(0,0,0,0.15);
        }
        
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 15px;
        }
        
        .magnitude {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        
        .scale-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 1.1em;
        }
        
        .scale-1 { background: #4ade80; color: white; }
        .scale-2 { background: #fbbf24; color: white; }
        .scale-3 { background: #fb923c; color: white; }
        .scale-4 { background: #f97316; color: white; }
        .scale-5 { background: #ef4444; color: white; }
        .scale-6 { background: #dc2626; color: white; }
        .scale-7 { background: #991b1b; color: white; }
        
        .card-body {
            display: grid;
            gap: 10px;
        }
        
        .info-row {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .info-label {
            font-weight: bold;
            color: #666;
            min-width: 80px;
        }
        
        .info-value {
            color: #333;
        }
        
        .loading {
            text-align: center;
            color: white;
            font-size: 1.2em;
            padding: 40px;
        }
        
        .error {
            background: #fee;
            color: #c00;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        
        .tsunami-warning {
            background: #fef3c7;
            color: #92400e;
            padding: 10px;
            border-radius: 8px;
            margin-top: 10px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌍 地震速報</h1>
            <div class="update-info">最新の地震情報</div>
            <button class="refresh-btn" onclick="loadEarthquakes()">🔄 更新</button>
        </header>
        
        <div id="content">
            <div class="loading">読み込み中...</div>
        </div>
    </div>

    <script>
        function getScaleText(scale) {
            const scales = {
                10: '震度1',
                20: '震度2',
                30: '震度3',
                40: '震度4',
                45: '震度5弱',
                50: '震度5強',
                55: '震度6弱',
                60: '震度6強',
                70: '震度7'
            };
            return scales[scale] || '震度不明';
        }
        
        function getScaleClass(scale) {
            if (scale <= 20) return 'scale-1';
            if (scale <= 30) return 'scale-2';
            if (scale <= 40) return 'scale-3';
            if (scale <= 45) return 'scale-4';
            if (scale <= 55) return 'scale-5';
            if (scale <= 60) return 'scale-6';
            return 'scale-7';
        }
        
        function formatDate(dateStr) {
            const date = new Date(dateStr);
            return date.toLocaleString('ja-JP', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
        
        function getTsunamiText(tsunami) {
            const texts = {
                'None': '津波の心配なし',
                'Unknown': '不明',
                'Checking': '調査中',
                'NonEffective': '若干の海面変動',
                'Watch': '津波注意報',
                'Warning': '津波警報'
            };
            return texts[tsunami] || tsunami;
        }
        
        async function loadEarthquakes() {
            const content = document.getElementById('content');
            content.innerHTML = '<div class="loading">読み込み中...</div>';
            
            try {
                const response = await fetch('/api/earthquakes');
                const result = await response.json();
                
                if (!result.success) {
                    throw new Error(result.error);
                }
                
                const earthquakes = result.data;
                
                if (earthquakes.length === 0) {
                    content.innerHTML = '<div class="loading">地震情報がありません</div>';
                    return;
                }
                
                let html = '<div class="earthquake-list">';
                
                earthquakes.forEach(eq => {
                    const hasTsunami = eq.domesticTsunami !== 'None' && eq.domesticTsunami !== 'Unknown';
                    
                    html += `
                        <div class="earthquake-card">
                            <div class="card-header">
                                <div class="magnitude">M${eq.magnitude.toFixed(1)}</div>
                                <div class="scale-badge ${getScaleClass(eq.maxScale)}">
                                    ${getScaleText(eq.maxScale)}
                                </div>
                            </div>
                            <div class="card-body">
                                <div class="info-row">
                                    <span class="info-label">📅 発生時刻:</span>
                                    <span class="info-value">${formatDate(eq.time)}</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">📍 震源地:</span>
                                    <span class="info-value">${eq.hypocenter}</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">🔽 深さ:</span>
                                    <span class="info-value">${eq.depth}km</span>
                                </div>
                                ${hasTsunami ? `
                                    <div class="tsunami-warning">
                                        ⚠️ ${getTsunamiText(eq.domesticTsunami)}
                                    </div>
                                ` : ''}
                            </div>
                        </div>
                    `;
                });
                
                html += '</div>';
                content.innerHTML = html;
                
            } catch (error) {
                content.innerHTML = `
                    <div class="error">
                        エラーが発生しました: ${error.message}
                    </div>
                `;
            }
        }
        
        // 初回読み込み
        loadEarthquakes();
        
        // 5分ごとに自動更新
        setInterval(loadEarthquakes, 300000);
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
