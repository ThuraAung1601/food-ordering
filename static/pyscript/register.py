from pyscript import document, window
import js
import asyncio
from js import document, window, console
from pyodide.http import pyfetch
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

class RegisterForm(Widget):
    def __init__(self, element_id):
        super().__init__(element_id)
        self.handle_register_proxy = None

    async def handle_register(self, event):
        event.preventDefault()
        
        form_data = {
            "username": document.getElementById("username").value,
            "password": document.getElementById("password").value,
            "name": document.getElementById("name").value,
            "phone": document.getElementById("phone").value,
            "address": {
                "number": document.getElementById("number").value,
                "street": document.getElementById("street").value,
                "city": document.getElementById("city").value
            }
        }

        try:
            response = await pyfetch(
                "/customers/register",
                method="POST",
                headers={
                    "Content-Type": "application/json",
                },
                body=json.dumps(form_data)
            )

            text = await response.text()
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                console.error("Invalid JSON response:", text)
                data = {}

            if response.ok:
                window.alert("Registration successful! Please login.")
                window.location.href = "/login"
            else:
                error_message = data.get("detail", "Registration failed")
                window.alert(error_message)

        except Exception as error:
            console.error("Registration error:", str(error))
            window.alert("Registration failed. Please try again.")

    def drawWidget(self):
        self.container = document.createElement("div")
        self.container.className = "register-container"
        
        self.h2 = document.createElement("h2")
        self.h2.innerHTML = "Register"
        
        self.form = document.createElement("form")
        self.form.id = "registerForm"
        self.form.setAttribute("action", "javascript:void(0);")
        
        self.username_group = document.createElement("div")
        self.username_group.className = "form-group"
        self.username_label = document.createElement("label")
        self.username_label.setAttribute("for", "username")
        self.username_label.innerHTML = "Username:"
        self.username_input = document.createElement("input")
        self.username_input.type = "text"
        self.username_input.id = "username"
        self.username_input.name = "username"
        self.username_input.required = True
        
        self.password_group = document.createElement("div")
        self.password_group.className = "form-group"
        self.password_label = document.createElement("label")
        self.password_label.setAttribute("for", "password")
        self.password_label.innerHTML = "Password:"
        self.password_input = document.createElement("input")
        self.password_input.type = "password"
        self.password_input.id = "password"
        self.password_input.name = "password"
        self.password_input.required = True
        
        self.name_group = document.createElement("div")
        self.name_group.className = "form-group"
        self.name_label = document.createElement("label")
        self.name_label.setAttribute("for", "name")
        self.name_label.innerHTML = "Full Name:"
        self.name_input = document.createElement("input")
        self.name_input.type = "text"
        self.name_input.id = "name"
        self.name_input.name = "name"
        self.name_input.required = True
        
        self.phone_group = document.createElement("div")
        self.phone_group.className = "form-group"
        self.phone_label = document.createElement("label")
        self.phone_label.setAttribute("for", "phone")
        self.phone_label.innerHTML = "Phone:"
        self.phone_input = document.createElement("input")
        self.phone_input.type = "tel"
        self.phone_input.id = "phone"
        self.phone_input.name = "phone"
        self.phone_input.required = True
        
        self.address_group = document.createElement("div")
        self.address_group.className = "form-group"
        self.address_label = document.createElement("label")
        self.address_label.innerHTML = "Address:"
        
        self.number_input = document.createElement("input")
        self.number_input.type = "text"
        self.number_input.id = "number"
        self.number_input.name = "number"
        self.number_input.placeholder = "House Number"
        self.number_input.required = True
        
        self.street_input = document.createElement("input")
        self.street_input.type = "text"
        self.street_input.id = "street"
        self.street_input.name = "street"
        self.street_input.placeholder = "Street"
        self.street_input.required = True
        
        self.city_input = document.createElement("input")
        self.city_input.type = "text"
        self.city_input.id = "city"
        self.city_input.name = "city"
        self.city_input.placeholder = "City"
        self.city_input.required = True
        
        self.register_btn = document.createElement("button")
        self.register_btn.type = "submit"
        self.register_btn.className = "reg-button"
        self.register_btn.innerHTML = "Register"
        
       
        self.login_text = document.createElement("p")
        self.login_link = document.createElement("a")
        self.login_link.href = "/login"
        self.login_link.innerHTML = "Login here"
        self.login_text.innerHTML = "Already have an account? "
        self.login_text.appendChild(self.login_link)
        
       
        self.username_group.append(self.username_label, self.username_input)
        self.password_group.append(self.password_label, self.password_input)
        self.name_group.append(self.name_label, self.name_input)
        self.phone_group.append(self.phone_label, self.phone_input)
        self.address_group.append(
            self.address_label,
            self.number_input,
            self.street_input,
            self.city_input
        )
        
        self.form.append(
            self.username_group,
            self.password_group,
            self.name_group,
            self.phone_group,
            self.address_group,
            self.register_btn
        )
        
        self.container.append(self.h2, self.form, self.login_text)
        self.element.appendChild(self.container)
        
      
        self.handle_register_proxy = create_proxy(self.handle_register)
        self.form.addEventListener("submit", self.handle_register_proxy)

class RegisterLayout(Widget):
    def __init__(self, element_id):
        super().__init__(element_id)
        self.register_form = RegisterForm(element_id)

    def drawWidget(self):
        try:
            self.register_form.drawWidget()
        except Exception as e:
            console.error("Error in drawWidget:", e)

if __name__ == "__main__":
    register = RegisterLayout("app")
    register.drawWidget()