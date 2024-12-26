from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def identify_wordpress_theme_and_plugins(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('link', href=True)
        scripts = soup.find_all('script', src=True)
        theme_info = None
        plugins = set()

        for link in links:
            href = link['href']
            if 'wp-content/themes/' in href:
                theme_start = href.find('wp-content/themes/') + len('wp-content/themes/')
                theme_end = href.find('/', theme_start)
                theme_name = href[theme_start:theme_end]
                theme_info = theme_name
                break

        for tag in links + scripts:
            attr = tag.get('href') or tag.get('src')
            if 'wp-content/plugins/' in attr:
                plugin_start = attr.find('wp-content/plugins/') + len('wp-content/plugins/')
                plugin_end = attr.find('/', plugin_start)
                plugin_name = attr[plugin_start:plugin_end]
                plugins.add(plugin_name)

        return {"theme": theme_info, "plugins": list(plugins)}
    except Exception as e:
        return {"error": str(e)}

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        url = request.form.get('url')
        result = identify_wordpress_theme_and_plugins(url)
        return jsonify(result)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
