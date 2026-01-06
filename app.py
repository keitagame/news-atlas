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
    try:
        response = requests.get(EARTHQUAKE_API, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception:
        data = []

    earthquakes = []
    for item in data:
        if item.get('code') == 551:
            eq = item.get('earthquake', {})
            hypo = eq.get('hypocenter', {})
            earthquakes.append({
                'time': eq.get('time'),
                'place': hypo.get('name', '不明'),
                'magnitude': hypo.get('magnitude', 0),
                'depth': hypo.get('depth', 0),
                'scale': eq.get('maxScale', 0),
                'tsunami': eq.get('domesticTsunami', 'None')
            })

    return render_template_string(HTML_TEMPLATE, earthquakes=earthquakes)


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
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="300">
<title>地震速報</title>

<style>
:root {
  --bg: #0b0c0f;
  --panel: #16181d;
  --border: #2a2d35;
  --text: #e5e7eb;
  --muted: #9ca3af;
  --accent: #ef4444;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  font-family: "Hiragino Sans", "Noto Sans JP", system-ui;
  background: var(--bg);
  color: var(--text);
}

header {
  padding: 16px 24px;
  border-bottom: 1px solid var(--border);
}

header h1 {
  font-size: 1.6rem;
  letter-spacing: 0.05em;
}

.container {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
  padding: 16px;
}

/* ===== カード ===== */
.eq {
  background: var(--panel);
  border: 1px solid var(--border);
  padding: 16px;
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
}

.eq-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.mag {
  font-size: 1.4rem;
  font-weight: bold;
}

.scale {
  color: var(--accent);
  font-weight: bold;
}

.meta {
  color: var(--muted);
  font-size: 0.9rem;
}

/* ===== ワイド表示 ===== */
@media (min-width: 900px) {
  .container {
    grid-template-columns: 2fr 1fr;
  }

  .eq {
    grid-template-columns: 2fr 1fr;
  }

  .detail {
    border-left: 1px solid var(--border);
    padding-left: 12px;
    font-size: 0.9rem;
  }
}
</style>
</head>

<body>

<header>
  <h1>地震速報</h1>
</header>

<main class="container">

<section>
{% for eq in earthquakes %}
  <article class="eq">
    <div>
      <div class="eq-header">
        <div class="mag">M{{ "%.1f"|format(eq.magnitude) }}</div>
        <div class="scale">震度 {{ eq.scale }}</div>
      </div>
      <div class="meta">{{ eq.time }}</div>
      <div>{{ eq.place }}</div>
    </div>

    <div class="detail">
      <div>深さ: {{ eq.depth }}km</div>
      {% if eq.tsunami != 'None' %}
        <div style="color:#fbbf24;">津波: {{ eq.tsunami }}</div>
      {% endif %}
    </div>
  </article>
{% endfor %}
</section>

<aside>
  <div class="eq">
    <strong>情報について</strong>
    <p class="meta">
      気象庁発表データを元に表示しています。<br>
      5分ごとに自動更新されます。
    </p>
  </div>
</aside>

</main>
</body>
</html>

'''

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)