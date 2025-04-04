from pyscript import document, window
import js
import asyncio
from js import document, window, console
from pyodide.http import pyfetch 
from pyodide.ffi import to_js
from pyodide.ffi import create_proxy
import json
from abc import ABC, abstractmethod

class Widget(ABC):
    def __init__(self, element_id):
        self.element_id = element_id
        self._element = None

    @property
    def element(self):
        if not self._element:
            self._element = document.querySelector(f"#{self.element_id}")
        return self._element

    @abstractmethod
    def drawWidget(self):
        pass

class LoginForm(Widget):
    def __init__(self, element_id):
        super().__init__(element_id)
        self.handle_login_proxy = None

    async def handle_login(self, event):
        event.preventDefault()
        username = document.getElementById("username").value
        password = document.getElementById("password").value

        if not username or not password:
            window.alert("Please enter both username and password")
            return

        try:
            admin_response = await pyfetch(
                "/admin/login",
                method="POST",
                headers={
                    "Content-Type": "application/json",
                },
                body=json.dumps({
                    "username": username,
                    "password": password
                })
            )

            if admin_response.ok:
                admin_data = await admin_response.json()
                console.log('Admin login successful:', admin_data)
                window.location.href = admin_data.get("redirect_path", "/admin/dashboard")
                return

            customer_response = await pyfetch(
                "/customers/login",
                method="POST",
                headers={
                    "Content-Type": "application/json",
                },
                body=json.dumps({
                    "username": username,
                    "password": password
                })
            )

            customer_text = await customer_response.text()
            try:
                customer_data = json.loads(customer_text)
            except json.JSONDecodeError:
                console.error("Invalid JSON from customer login:", customer_text)
                customer_data = {}

            if customer_response.ok:
                console.log('Customer login successful:', customer_data)
                window.location.href = customer_data.get("redirect_path", f"/customers/{username}/dashboard")
            else:
                error_message = customer_data.get("detail", "Invalid credentials")
                window.alert(error_message)

        except Exception as error:
            console.error("Login error:", str(error))
            window.alert("Login failed. Please try again.")

    def drawWidget(self):
        self.container = document.createElement("div")
        self.container.className = "login-container"
        self.container.style.width = "500px"
        
        self.h2 = document.createElement("h2")
        self.h2.innerHTML = "Login"
        
        self.form = document.createElement("form")
        self.form.id = "loginForm"
        self.form.setAttribute("action", "javascript:void(0);")
        
        self.nameFormGroup = document.createElement("div")
        self.nameFormGroup.className = "form-group"
        self.nameLabel = document.createElement("label")
        self.nameLabel.innerHTML = "Username:"
        self.nameInput = document.createElement("input")
        self.nameInput.type = "text"
        self.nameInput.id = "username"
        self.nameInput.name = "username"
        self.nameInput.required = True
        
        # Password field
        self.passwordFormGroup = document.createElement("div")
        self.passwordFormGroup.className = "form-group"
        self.passwordLabel = document.createElement("label")
        self.passwordLabel.innerHTML = "Password:"
        self.passwordInput = document.createElement("input")
        self.passwordInput.type = "password"
        self.passwordInput.id = "password"
        self.passwordInput.name = "password"
        self.passwordInput.required = True
        
        self.login_btn = document.createElement("button")
        self.login_btn.type = "button"  
        self.login_btn.className = "login-button"
        self.login_btn.innerHTML = "Login"
        
        self.register = document.createElement("p")
        self.register.innerHTML = "Don't have an account?"
        self.regLink = document.createElement("a")
        self.regLink.href = "/register"
        self.regLink.innerHTML = "Register here"
        self.register.appendChild(self.regLink)

        self.forgot = document.createElement("p")
        self.forgot.innerHTML = "Forgot your password? "
        self.forgotLink = document.createElement("a")
        self.forgotLink.href = "/forgot-password"
        self.forgotLink.innerHTML = "Reset here"
        self.forgot.appendChild(self.forgotLink)
        
        self.nameFormGroup.appendChild(self.nameLabel)
        self.nameFormGroup.appendChild(self.nameInput)
        self.passwordFormGroup.appendChild(self.passwordLabel)
        self.passwordFormGroup.appendChild(self.passwordInput)
        
        self.form.appendChild(self.nameFormGroup)
        self.form.appendChild(self.passwordFormGroup)
        self.form.appendChild(self.login_btn)
        
        self.container.appendChild(self.h2)
        self.container.appendChild(self.form)
        self.container.appendChild(self.register)
        self.form.appendChild(self.forgot)
        
        self.element.appendChild(self.container)
        
        self.handle_login_proxy = create_proxy(self.handle_login)
        self.login_btn.addEventListener("click", self.handle_login_proxy)

class LoginLayout(Widget):
    def __init__(self, element_id):
        super().__init__(element_id)
        self.login_form = LoginForm(element_id)

    def drawWidget(self):
        try:
            self.login_form.drawWidget()
        except Exception as e:
            console.error("Error in drawWidget:", e)

if __name__ == "__main__":
    login = LoginLayout("app")
    login.drawWidget()