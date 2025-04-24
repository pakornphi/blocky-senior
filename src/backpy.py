# backpy.py
from flask import Flask, request, jsonify
from csrf2 import CSRFTester
from xss import XSSTester

app = Flask(__name__)

# Inline HTML form with checkboxes for test selection
form_html = """
<!doctype html>
<html>
  <head><title>Security Tester</title></head>
  <body>
    <h1>Enter a URL to scan for CSRF or XSS issues</h1>
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
        <input type="checkbox" name="test_type" value="csrf" id="chk_csrf">
        <label for="chk_csrf">CSRF Test</label><br>
        <input type="checkbox" name="test_type" value="xss" id="chk_xss">
        <label for="chk_xss">XSS Test</label><br>
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
        # Run CSRF tests if selected
        if 'csrf' in tests:
            csrf_tester = CSRFTester(
                base_url=target_url,
                csrf_field='csrf_token',
                form_selector='form',
                endpoints=['/', '/login'],
                timeout=5.0,
                headers={'User-Agent': 'BackPy-CSRF-Tester/1.0'},
                max_retries=2
            )
            raw_csrf = csrf_tester.run_all()
            # Format as JSON-able
            results['csrf'] = {
                name: {'vulnerable': v, 'info': info}
                for name, (v, info) in raw_csrf.items()
            }

        # Run XSS tests if selected
        if 'xss' in tests:
            xss_tester = XSSTester(
                base_url=target_url,
                payload_file='payload.txt',
                timeout=3,
                cooldown=0.5,
                workers=10
            )
            raw_xss = xss_tester.run_all(max_workers=xss_tester.workers)
            results['xss'] = {
                test_name: {'count': len(plist), 'payloads': plist}
                for test_name, plist in raw_xss.items()
            }

        return jsonify(results)
    return form_html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1000, debug=True)
