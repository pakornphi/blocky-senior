import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class CSRFTester:
    def __init__(self, target_url, form_data=None, csrf_token_name='csrf_token'):
        """
        Initializer for CSRFTester class.
        :param target_url: Target URL for the test.
        :param form_data: Optional dictionary to override default form data.
        :param csrf_token_name: Optional custom name for CSRF token field (default: 'csrf_token').
        """
        self.target_url = target_url
        self.session = requests.Session()
        self.form_data = form_data or {'username': 'testuser', 'password': 'testpassword'}
        self.csrf_token_name = csrf_token_name

    def get_csrf_token(self):
        """ดึงโทเค็น CSRF จาก URL เป้าหมาย"""
        try:
            response = self.session.get(self.target_url)
            response.raise_for_status()  # ถ้าหากไม่สามารถเชื่อมต่อได้ จะโยน Exception
            soup = BeautifulSoup(response.text, 'html.parser')

            # ดึงโทเค็นจาก meta หรือ form input
            csrf_token = self._extract_csrf_token(soup)
            form_tag = soup.find('form')
            form_action = urljoin(self.target_url, form_tag['action']) if form_tag else None
            method = form_tag.get('method', 'POST').upper() if form_tag else 'POST'

            return csrf_token, form_action, method

        except Exception as e:
            print(f"[ผิดพลาด] ไม่สามารถดึงโทเค็น CSRF: {e}")
            return None, None, None

    def _extract_csrf_token(self, soup):
        """ดึงโทเค็น CSRF จาก HTML"""
        token_tag = soup.find('meta', {'name': 'csrf-token'})
        if token_tag:
            return token_tag.get('content')

        form_tag = soup.find('form')
        if form_tag:
            csrf_token_input = form_tag.find('input', {'name': self.csrf_token_name})
            if csrf_token_input:
                return csrf_token_input['value']

        return None

    def submit_form(self, form_action, data, method):
        """ส่งข้อมูลฟอร์มด้วย HTTP Method ที่ระบุ"""
        try:
            form_action = urljoin(self.target_url, form_action)
            response = None

            # Using a dictionary to map methods to corresponding requests
            http_methods = {
                'POST': self.session.post,
                'PUT': self.session.put,
                'PATCH': self.session.patch,
            }

            if method in http_methods:
                response = http_methods[method](form_action, data=data)
            else:
                print(f"[ผิดพลาด] HTTP Method {method} ไม่รองรับ")
                return None

            return response

        except requests.exceptions.HTTPError as err:
            print(f"[ผิดพลาด HTTP]: {err}")
            return None

    def check_csrf_protection(self, response, expected_error_message="invalid request"):
        """ตรวจสอบว่ามีการป้องกัน CSRF หรือไม่"""

        if response is None:
            print("[✘] การตอบสนองเป็น None ไม่สามารถตรวจสอบได้")
            return

        # ตรวจสอบกรณีที่เซิร์ฟเวอร์ตอบกลับด้วยสถานะ 400 (Bad Request)
        if response.status_code == 400:
            print("[✔] ระบบป้องกัน CSRF สำเร็จ: ไม่สามารถส่งข้อมูลได้โดยไม่ใช้โทเค็น CSRF")
        
        # กรณีที่ระบบตอบกลับด้วยข้อความที่เกี่ยวข้องกับ CSRF
        elif expected_error_message in response.text.lower():
            print(f"[✘] ระบบป้องกัน CSRF ไม่สำเร็จ: {expected_error_message} - สามารถส่งข้อมูลได้โดยใช้โทเค็น CSRF")

        # กรณีที่ระบบตอบกลับด้วยสถานะ 200
        elif response.status_code == 200 and not "token reuse" in response.text.lower():
            print(f"[✘] ระบบป้องกัน CSRF ไม่สำเร็จ: - สามารถส่งข้อมูลได้โดยใช้โทเค็น CSRF")

        # กรณีการใช้โทเค็นซ้ำ
        elif "token reuse" in response.text.lower() or "csrf token has expired" in response.text.lower():
            print("[✘] ระบบป้องกัน CSRF ไม่สำเร็จ: สามารถส่งข้อมูลได้โดยใช้โทเค็น CSRF")
        
        else:
            print("[✘] ระบบป้องกัน CSRF ล้มเหลว: สามารถส่งข้อมูลได้โดยไม่ใช้โทเค็น CSRF")


    def test_token_reuse(self):
        """ทดสอบการใช้งานโทเค็น CSRF ซ้ำ"""
        print("[*] เริ่มการทดสอบการใช้งานโทเค็น CSRF ซ้ำ")

        csrf_token, form_action, method = self.get_csrf_token()

        if not form_action:
            print("[✘] ไม่พบ URL สำหรับการส่งฟอร์ม ตรวจสอบ HTML ของหน้าเว็บอีกครั้ง")
            return

        # ข้อมูลฟอร์มตัวอย่าง
        form_data = {
            'username': 'testuser',  # ตัวอย่าง ใช้ชื่อฟิลด์จริง
            'password': 'testpassword',  # ตัวอย่าง ใช้ชื่อฟิลด์จริง
            'csrf_token': csrf_token  # ใช้โทเค็นแรกในการส่งฟอร์มครั้งแรก
        }

        
        print("[*] กำลังทดสอบการส่งฟอร์มครั้งแรกด้วยโทเค็น CSRF เดิม")
        response_1 = self.submit_form(form_action, form_data, method) 
        
        if response_1.status_code == 200:
            print("[✘] ระบบป้องกัน CSRF ล้มเหลว: สามารถส่งข้อมูลได้โดยใช้โทเค็น CSRF ซ้ำ")
        else:
            print("[✔] ระบบป้องกัน CSRF สำเร็จ: ไม่สามารถส่งข้อมูลได้โดยใช้โทเค็น CSRF ซ้ำ")


    def perform_test(self):
        """ฟังก์ชันหลักสำหรับการทดสอบ CSRF"""
        print(f"[*] เริ่มการทดสอบ CSRF ที่: {self.target_url}")

        csrf_token, form_action, method = self.get_csrf_token()

        if not form_action:
            print("[✘] ไม่พบ URL สำหรับการส่งฟอร์ม ตรวจสอบ HTML ของหน้าเว็บอีกครั้ง")
            return

        # ส่งฟอร์มพร้อมโทเค็น CSRF ถ้ามี
        form_data = self.form_data.copy()

        if csrf_token:
            print("[✔] พบ token ของหน้าเว็บ")
            # ทดสอบส่งฟอร์มโดยไม่มีโทเค็น CSRF
            print("[*] กำลังทดสอบการส่งฟอร์มโดยไม่มีโทเค็น CSRF...")
            form_data.pop('csrf_token', None)
            response_no_csrf = self.submit_form(form_action, form_data, method)
            self.check_csrf_protection(response_no_csrf)

            # **ทดสอบการใช้โทเค็น CSRF ซ้ำ**
            self.test_token_reuse()
        

        else:
            print("[✘] ไม่พบโทเค็น CSRF: ระบบอาจไม่มีการป้องกัน CSRF")
            # ทดสอบส่งฟอร์มโดยไม่มีโทเค็น CSRF
            print("[*] กำลังทดสอบการส่งฟอร์มโดยไม่มีโทเค็น CSRF...")
            form_data.pop('csrf_token', None)
            response_no_csrf = self.submit_form(form_action, form_data, method)
            self.check_csrf_protection(response_no_csrf)

            # **ทดสอบการใช้โทเค็น CSRF ซ้ำ**
            self.test_token_reuse()
