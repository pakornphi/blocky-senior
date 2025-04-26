from flask import Flask, request, jsonify
from sql_injection_tester import SQLInjectionTester

app = Flask(__name__)

# Inline HTML form with checkboxes for test selection
form_html = """
<!doctype html>
<html>
  <head><title>Security Tester</title></head>
  <body>
    <h1>Enter a URL to scan for CSRF, XSS, or SQL Injection issues</h1>
    <form method="post">
      <div>
        <label>URL to test:</label><br>
        <input
          type="url"
          name="url"
          placeholder="https://example.com"
          style="width:300px"
          required
        >
      </div>
      <div>
        <label>Select tests:</label><br>
        <input type="checkbox" name="test_type" value="sql" id="chk_sql">
        <label for="chk_sql">SQL Injection Test</label><br>
      </div>
      <button type="submit">Run Tests</button>
    </form>
  </body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        target_url = request.form.get('url')
        tests = request.form.getlist('test_type')
        # Validation
        errors = []
        if not target_url:
            errors.append('Please enter a URL to test.')
        if not tests:
            errors.append('Please select at least one test.')
        if errors:
            return '<br>'.join(f"<p style='color:red;'>{e}</p>" for e in errors) + form_html, 400

        results = {}
        # Run SQL Injection tests if selected
        if 'sql' in tests:
            sql_tester = SQLInjectionTester(base_url=target_url, endpoints=['/', '/login'])
            sql_result = sql_tester.test_sql_injection()
            results['sql_injection'] = {
                'vulnerable': sql_result[0],
                'info': sql_result[1]
            }

        return jsonify(results)
    return form_html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1000, debug=True)
