import requests
from bs4 import BeautifulSoup
import time
import re

class CSRFTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()

    def _get_form_data(self):
        """Helper method to retrieve form and CSRF token data."""
        response = self.session.get(self.base_url)
        self._check_response(response)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        form = soup.find('form')
        if not form:
            raise Exception("No form found on the page.")
        
        action = form.get('action', '')
        method = form.get('method', 'post').lower()
        inputs = form.find_all('input')
        
        form_data = {}
        for input_tag in inputs:
            name = input_tag.get('name')
            if name:
                form_data[name] = input_tag.get('value', '')
        
        return action, method, form_data

    def _submit_form(self, action, method, form_data):#1
        """Helper method to submit the form and check the response."""
        if method == 'post':
            response = self.session.post(self.base_url + action, data=form_data)
        else:
            response = self.session.get(self.base_url + action, params=form_data)
        
        self._check_response(response)
        return response

    def _check_response(self, response):
        """Check the response status code."""
        if response.status_code != 200:
            raise Exception(f"Request failed with status code {response.status_code}")

    def _get_csrf_token(self):#2
        """Helper method to extract the CSRF token from the form."""
        response = self.session.get(self.base_url)
        self._check_response(response)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token_input = soup.find('input', {'name': 'csrf_token'})
        
        if csrf_token_input:
            return csrf_token_input.get('value', None)
        else:
            raise Exception("No CSRF token found in the form.")

    def check_csrf_token(self):#4
        """Check if the CSRF token exists and is valid."""
        try:
            csrf_token = self._get_csrf_token()
            print(f"CSRF token found: {csrf_token}")
            return "pass", csrf_token
        except Exception as e:
            print(str(e))
            return "fail", None

    def check_csrf_reuse(self):#5
        """Test if the CSRF token is reused across requests."""
        status, csrf_token_before = self.check_csrf_token()
        
        if status == "fail":
            return "fail", None
        
        action, method, form_data = self._get_form_data()
        form_data.pop('csrf_token', None)  # Remove CSRF token for submission

        self._submit_form(action, method, form_data)
        status, csrf_token_after = self.check_csrf_token()

        if csrf_token_before == csrf_token_after:
            print("CSRF token is reused, indicating a potential vulnerability.")
            return "fail", csrf_token_after
        else:
            print("CSRF token is dynamic, no issue detected.")
            return "pass", csrf_token_after

    def check_session_fixation(self):#6
        """Test for session fixation vulnerability by testing session ID before and after form submission."""
        original_session_id = self.session.cookies.get('PHPSESSID')
        print(f"Original session ID: {original_session_id}")

        attacker_session_id = 'attacker_session_id_12345'
        self.session.cookies.set('PHPSESSID', attacker_session_id)
        print(f"Attacker-controlled session ID set: {attacker_session_id}")

        action, method, form_data = self._get_form_data()
        self._submit_form(action, method, form_data)

        new_session_id = self.session.cookies.get('PHPSESSID')
        print(f"Session ID after form submission: {new_session_id}")

        if new_session_id == original_session_id:
            print("Session ID was not changed after form submission. Possible session fixation vulnerability detected.")
            return "fail", new_session_id
        elif new_session_id == attacker_session_id:
            print("Attacker-controlled session ID was reused after form submission. Session fixation vulnerability confirmed.")
            return "fail", new_session_id
        else:
            print("Session ID changed after form submission. No session fixation vulnerability detected.")
            return "pass", new_session_id

    def check_get_request_vulnerable_to_csrf(self):#7
        """Check if any GET request is vulnerable to CSRF."""
        response = self.session.get(self.base_url)
        self._check_response(response)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        forms = soup.find_all('form')
        
        vulnerable_forms = []
        for form in forms:
            method = form.get('method', 'post').lower()
            action = form.get('action', '')
            
            if method == 'get' and ('delete' in action or 'update' in action or 'edit' in action):
                print(f"Warning: GET request to {action} could be vulnerable to CSRF.")
                vulnerable_forms.append(action)
        
        return "fail", vulnerable_forms if vulnerable_forms else "pass", []

    def check_post_without_csrf(self):#8
        """Check if any POST request is missing CSRF protection."""
        response = self.session.get(self.base_url)
        self._check_response(response)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        forms = soup.find_all('form')
        
        vulnerable_forms = []
        for form in forms:
            method = form.get('method', 'post').lower()
            action = form.get('action', '')
            
            if method == 'post' and not form.find('input', {'name': 'csrf_token'}):
                print(f"Warning: POST form at {action} does not have CSRF token protection.")
                vulnerable_forms.append(action)
        
        return "fail", vulnerable_forms if vulnerable_forms else "pass", []

    def check_double_submit_cookies(self):#9
        """Check if Double Submit Cookies protection is implemented."""
        response = self.session.get(self.base_url)
        self._check_response(response)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token_cookie = self.session.cookies.get('csrf_token')
        
        if not csrf_token_cookie:
            print("No CSRF token found in cookies.")
            return "fail", None
        
        print(f"CSRF token in cookies: {csrf_token_cookie}")
        
        forms = soup.find_all('form')
        for form in forms:
            method = form.get('method', 'post').lower()
            action = form.get('action', '')
            
            if method == 'post':
                csrf_token_input = form.find('input', {'name': 'csrf_token'})
                if csrf_token_input:
                    csrf_token_value = csrf_token_input.get('value', None)
                    print(f"CSRF token in form: {csrf_token_value}")
                    
                    if csrf_token_value == csrf_token_cookie:
                        print("Double Submit Cookies protection detected.")
                        return "pass", csrf_token_value
                    else:
                        print("CSRF token mismatch between form and cookie.")
                        return "fail", None
                else:
                    print(f"No CSRF token found in form with action: {action}")
                    return "fail", None
        
        return "fail", None

    def check_csrf_expiration(self):#10
        """Test CSRF token expiration."""
        action, method, form_data = self._get_form_data()
        
        csrf_token = form_data.get('csrf_token', None)
        if not csrf_token:
            print("No CSRF token found in the form.")
            return "fail", None
        
        print(f"CSRF token found: {csrf_token}")
        
        print("Submitting form with valid CSRF token...")
        self._submit_form(action, method, form_data)
        
        print("Waiting for CSRF token to expire...")
        time.sleep(5)  # Simulating token expiration
        
        print("Submitting form again with the same CSRF token (expired)...")
        form_data['csrf_token'] = csrf_token
        
        expired_submission = self._submit_form(action, method, form_data)
        
        if expired_submission == "fail":
            print("CSRF token has expired. The server correctly rejected the request.")
            return "pass", csrf_token
        else:
            print("CSRF token did not expire as expected.")
            return "fail", csrf_token

    def is_token_format_valid(self, token):#11
        """Check if the CSRF token format is valid."""
        pattern = r'^[a-zA-Z0-9]{32}$'
        return bool(re.match(pattern, token))

    def check_incorrect_csrf_format(self):#11
        """Test if CSRF token format is correct."""
        action, method, form_data = self._get_form_data()
        
        csrf_token = form_data.get('csrf_token', None)
        if not csrf_token:
            print("No CSRF token found in the form.")
            return "fail", None
        
        print(f"CSRF token found: {csrf_token}")
        
        if not self.is_token_format_valid(csrf_token):
            print("CSRF token format is invalid.")
            form_data['csrf_token'] = "invalid_format_token"
            submission_result = self._submit_form(action, method, form_data)
            
            if submission_result == "fail":
                print("The server correctly rejected the request with an invalid CSRF token format.")
                return "pass", csrf_token
            else:
                print("The server did not reject the invalid CSRF token format as expected.")
                return "fail", csrf_token
        else:
            print("CSRF token format is valid.")
            return "pass", csrf_token

    def check_dynamic_csrf(self):#12
        """Test dynamic CSRF token generation."""
        action, method, form_data = self._get_form_data()
        
        csrf_token_before = form_data.get('csrf_token', None)
        if not csrf_token_before:
            print("No CSRF token found in the form.")
            return "fail", None
        
        print(f"Original CSRF token: {csrf_token_before}")
        
        print("Submitting form with the current CSRF token...")
        self._submit_form(action, method, form_data)
        
        action, method, form_data_after = self._get_form_data()
        csrf_token_after = form_data_after.get('csrf_token', None)
        
        print(f"CSRF token after form submission: {csrf_token_after}")
        
        if csrf_token_before != csrf_token_after:
            print("CSRF token has changed, indicating dynamic token generation.")
            return "pass", csrf_token_after
        else:
            print("CSRF token did not change, indicating static token.")
            return "fail", csrf_token_before
