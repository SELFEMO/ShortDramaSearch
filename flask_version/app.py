from flask import Flask, render_template, request, jsonify
import requests
import json

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    search_name = request.form.get('search_name', '').strip()

    if not search_name:
        return jsonify({'error': '请输入搜索关键词'})

    try:
        # 调用API进行搜索
        api_url = "https://api.kuleu.com/api/bddj"
        params = {
            "text": search_name
        }

        response = requests.get(api_url, params=params)
        response.raise_for_status()

        # 解析API返回的JSON数据
        result_data = response.json()

        # 检查API返回状态
        if result_data.get("code") == 200:
            return jsonify({
                'success': True,
                'search_name': search_name,
                'dramas': result_data.get("data", []),
                'result_count': len(result_data.get("data", []))
            })
        else:
            error_msg = result_data.get("msg", "API返回错误")
            return jsonify({'error': error_msg})

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f"网络请求失败: {str(e)}"})
    except json.JSONDecodeError:
        return jsonify({'error': "API返回数据格式错误"})


if __name__ == '__main__':
    app.run(debug=True)
