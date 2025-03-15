import requests
from bs4 import BeautifulSoup
import time
import re

class CSRFTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()

    def get_form(self):
        # Send a GET request to the page with the form
        response = self.session.get(self.base_url)
        if response.status_code != 200:
            raise Exception("Failed to load the form page.")
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the form element
        form = soup.find('form')
        if not form:
            raise Exception("No form found on the page.")
        
        # Extract form action URL and method
        action = form.get('action', '')
        method = form.get('method', 'post').lower()
        
        # Find form input fields
        inputs = form.find_all('input')
        form_data = {}
        
        for input_tag in inputs:
            name = input_tag.get('name')
            if name:
                form_data[name] = input_tag.get('value', '')
        
        return action, method, form_data
    
    def submit_form(self, action, method, form_data):
        # Submit the form without CSRF token
        if method == 'post':
            response = self.session.post(self.base_url + action, data=form_data)
        else:
            response = self.session.get(self.base_url + action, params=form_data)
        
        # Check the status code and return the result (pass or fail)
        if response.status_code == 200:
            print("Form submitted successfully without CSRF token.")
            return "fail"  # Pass if status code is 200
        else:
            print(f"Form submission failed with status code {response.status_code}.")
            return "pass"  # Fail if status code is not 200

    def check_csrf_token(self):
        # Send a GET request to the page with the form
        response = self.session.get(self.base_url)
        if response.status_code != 200:
            raise Exception("Failed to load the form page.")
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for hidden input field named csrf_token (common name, adjust if needed)
        csrf_token_input = soup.find('input', {'name': 'csrf_token'})  # Modify the token name if needed
        
        if csrf_token_input:
            csrf_token = csrf_token_input.get('value', '')
            if csrf_token:
                print("CSRF token found:", csrf_token)
                return "pass", csrf_token
            else:
                print("CSRF token input field found, but no value provided.")
                return "fail", None
        else:
            print("No CSRF token found in the form.")
            return "fail", None
        
    def check_csrf_reuse(self):
        # Get the CSRF token before submission
        status, csrf_token_before = self.check_csrf_token()

        if status == "fail":
            print("No CSRF token found. Cannot check for reuse.")
            return "fail", None

        # Submit the form without the CSRF token
        action, method, form_data = self.get_form()
        form_data.pop('csrf_token', None)  # Remove CSRF token if present
        
        # Submit the form
        self.submit_form(action, method, form_data)
        
        # Get the CSRF token after submission
        status, csrf_token_after = self.check_csrf_token()
        
        # Compare the tokens before and after submission
        if csrf_token_before == csrf_token_after:
            print("CSRF token is reused, indicating a potential vulnerability.")
            return "fail", csrf_token_after
        else:
            print("CSRF token is not reused, no issue detected.")
            return "pass", csrf_token_after

    def check_session_fixation(self):
        # Step 1: Store the current session ID before performing the test
        original_session_id = self.session.cookies.get('PHPSESSID')  # Adjust for session cookie name

        print(f"Original session ID: {original_session_id}")

        # Step 2: Simulate an attacker-controlled session by setting a custom session ID
        attacker_session_id = 'attacker_session_id_12345'
        self.session.cookies.set('PHPSESSID', attacker_session_id)

        print(f"Attacker-controlled session ID set: {attacker_session_id}")

        # Step 3: Get the form and check for CSRF token
        action, method, form_data = self.get_form()
        csrf_token = form_data.get('csrf_token', None)

        # Step 4: Submit the form using the attacker-controlled session
        form_submission_result = self.submit_form(action, method, form_data)

        # Step 5: Check the session ID after form submission
        new_session_id = self.session.cookies.get('PHPSESSID')  # Get new session ID

        print(f"Session ID after form submission: {new_session_id}")

        # Step 6: Analyze session ID reuse
        if new_session_id == original_session_id:
            print("Session ID was not changed after form submission. Possible session fixation vulnerability detected.")
            return "fail", new_session_id
        elif new_session_id == attacker_session_id:
            print("Attacker-controlled session ID was reused after form submission. Session fixation vulnerability confirmed.")
            return "fail", new_session_id
        else:
            print("Session ID changed after form submission. No session fixation vulnerability detected.")
            return "pass", new_session_id

    def check_get_request_vulnerable_to_csrf(self):
        # Send a GET request to the page with the form
        response = self.session.get(self.base_url)
        if response.status_code != 200:
            raise Exception("Failed to load the page.")
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all forms on the page
        forms = soup.find_all('form')
        
        vulnerable_forms = []
        
        for form in forms:
            method = form.get('method', 'post').lower()
            action = form.get('action', '')
            
            # Check if the method is GET and it performs an action (like deleting, updating)
            if method == 'get':
                print(f"Found GET method form with action: {action}")
                
                # Check if form contains any action that could modify data
                # Example: Check if the action URL contains delete, update, etc.
                if 'delete' in action or 'update' in action or 'edit' in action:
                    print(f"Warning: GET request to {action} could be vulnerable to CSRF.")
                    vulnerable_forms.append(action)
        
        # Return a list of vulnerable GET forms
        if vulnerable_forms:
            return "fail", vulnerable_forms
        else:
            print("No GET request forms found that could be vulnerable to CSRF.")
            return "pass", []
        
    def check_post_without_csrf(self):
        # Send a GET request to the page with the form
        response = self.session.get(self.base_url)
        if response.status_code != 200:
            raise Exception("Failed to load the form page.")
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all forms on the page
        forms = soup.find_all('form')
        
        vulnerable_forms = []
        
        for form in forms:
            method = form.get('method', 'post').lower()
            action = form.get('action', '')
            
            # Check for POST method forms
            if method == 'post':
                print(f"Found POST method form with action: {action}")
                
                # Check if the form has a CSRF token input field (common name 'csrf_token', modify as needed)
                csrf_token_input = form.find('input', {'name': 'csrf_token'})
                if not csrf_token_input:
                    print(f"Warning: POST form at {action} does not have CSRF token protection.")
                    vulnerable_forms.append(action)
        
        # Return a list of vulnerable POST forms
        if vulnerable_forms:
            return "fail", vulnerable_forms
        else:
            print("All POST forms have CSRF protection.")
            return "pass", []
    
    def check_double_submit_cookies(self):
        # Send a GET request to the page with the form
        response = self.session.get(self.base_url)
        if response.status_code != 200:
            raise Exception("Failed to load the form page.")
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check if the CSRF token is set as a cookie
        csrf_token_cookie = self.session.cookies.get('csrf_token')
        if not csrf_token_cookie:
            print("No CSRF token found in cookies.")
            return "fail", None
        
        print(f"CSRF token in cookies: {csrf_token_cookie}")
        
        # Find all forms on the page
        forms = soup.find_all('form')
        
        for form in forms:
            method = form.get('method', 'post').lower()
            action = form.get('action', '')
            
            # Check for POST method forms
            if method == 'post':
                print(f"Found POST method form with action: {action}")
                
                # Check if the form contains a CSRF token input field
                csrf_token_input = form.find('input', {'name': 'csrf_token'})
                if csrf_token_input:
                    csrf_token_value = csrf_token_input.get('value', None)
                    print(f"CSRF token in form: {csrf_token_value}")
                    
                    # Compare the token in the cookie with the token in the form
                    if csrf_token_value == csrf_token_cookie:
                        print("Double Submit Cookies protection detected.")
                        return "pass", csrf_token_value
                    else:
                        print("CSRF token mismatch between form and cookie.")
                        return "fail", None
                else:
                    print(f"No CSRF token found in form with action: {action}")
                    return "fail", None
        
        print("No POST forms with CSRF token protection found.")
        return "fail", None
    
    def check_csrf_expiration(self):
        # Step 1: Get the form and CSRF token
        action, method, form_data = self.get_form()
        
        # Step 2: Check the CSRF token in the form
        csrf_token = form_data.get('csrf_token', None)
        if not csrf_token:
            print("No CSRF token found in the form.")
            return "fail", None
        
        print(f"CSRF token found: {csrf_token}")
        
        # Step 3: Submit the form with the valid CSRF token
        print("Submitting form with valid CSRF token...")
        valid_submission = self.submit_form(action, method, form_data)
        
        # Simulate waiting for the token to expire (this would usually take time, e.g., 30 minutes)
        print("Waiting for CSRF token to expire...")
        time.sleep(5)  # Sleep for 5 seconds to simulate token expiration (this is for testing purposes)
        
        # Step 4: Try submitting the form again with the same CSRF token
        print("Submitting form again with the same CSRF token (expired)...")
        form_data['csrf_token'] = csrf_token  # Reuse the original token for testing
        
        expired_submission = self.submit_form(action, method, form_data)
        
        # Step 5: Check the result
        if expired_submission == "fail":
            print("CSRF token has expired. The server correctly rejected the request.")
            return "pass", csrf_token
        else:
            print("CSRF token did not expire as expected.")
            return "fail", csrf_token
        
    def is_token_format_valid(self, token):
        # Define the expected format for the CSRF token (e.g., alphanumeric with length 32)
        # For example: The token should be 32 characters long and consist of letters and numbers
        pattern = r'^[a-zA-Z0-9]{32}$'
        
        if re.match(pattern, token):
            return True
        else:
            return False

    def check_incorrect_csrf_format(self):
        # Step 1: Get the form and CSRF token
        action, method, form_data = self.get_form()
        
        # Step 2: Check the CSRF token in the form
        csrf_token = form_data.get('csrf_token', None)
        if not csrf_token:
            print("No CSRF token found in the form.")
            return "fail", None
        
        print(f"CSRF token found: {csrf_token}")
        
        # Step 3: Check if the CSRF token is valid
        if not self.is_token_format_valid(csrf_token):
            print("CSRF token format is invalid.")
            
            # Step 4: Submit the form with the invalid token format
            form_data['csrf_token'] = "invalid_format_token"  # Simulate invalid token format
            submission_result = self.submit_form(action, method, form_data)
            
            if submission_result == "fail":
                print("The server correctly rejected the request with an invalid CSRF token format.")
                return "pass", csrf_token
            else:
                print("The server did not reject the invalid CSRF token format as expected.")
                return "fail", csrf_token
        else:
            print("CSRF token format is valid.")
            return "pass", csrf_token
        
    def check_dynamic_csrf(self):
        # Step 1: Get the form and CSRF token
        action, method, form_data = self.get_form()
        
        # Step 2: Retrieve the CSRF token from the form data
        csrf_token_before = form_data.get('csrf_token', None)
        if not csrf_token_before:
            print("No CSRF token found in the form.")
            return "fail", None
        
        print(f"Original CSRF token: {csrf_token_before}")
        
        # Step 3: Submit the form with the current CSRF token
        print("Submitting form with the current CSRF token...")
        self.submit_form(action, method, form_data)
        
        # Step 4: Get the CSRF token again after the form submission
        action, method, form_data_after = self.get_form()
        csrf_token_after = form_data_after.get('csrf_token', None)
        
        print(f"CSRF token after form submission: {csrf_token_after}")
        
        # Step 5: Compare the tokens before and after the submission
        if csrf_token_before != csrf_token_after:
            print("CSRF token has changed, indicating dynamic token generation.")
            return "pass", csrf_token_after
        else:
            print("CSRF token did not change, indicating static token.")
            return "fail", csrf_token_before