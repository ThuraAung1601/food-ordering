from pyscript import document, window
from js import console
import json
import asyncio
from pyodide.http import pyfetch
from pyodide.ffi import create_proxy

class ForgotPassword:
    def __init__(self):
        self.container = document.querySelector("#forgot-password-form")
        self.setup_form()

    def setup_form(self):
        self.container.innerHTML = """
            <div class="forgot-password-container" style="width: 500px;">
                <h2>Reset Password</h2>
                <form id="resetForm" class="reset-form" onsubmit="return false;">
                    <div class="form-group">
                        <label for="username">Username</label>
                        <input type="text" id="username" name="username" required>
                    </div>
                    <div class="form-group">
                        <label for="new_password">New Password</label>
                        <input type="password" id="new_password" name="new_password" required>
                    </div>
                    <div class="form-group">
                        <label for="confirm_password">Confirm Password</label>
                        <input type="password" id="confirm_password" name="confirm_password" required>
                    </div>
                    <button type="button" id="resetBtn" class="reset-btn">Reset Password</button>
                </form>
            </div>
        """
        
        reset_btn = self.container.querySelector("#resetBtn")
        reset_btn.addEventListener("click", create_proxy(self.handle_reset))

    async def handle_reset(self, event):
        event.preventDefault()
        
        username = document.querySelector("#username").value
        new_password = document.querySelector("#new_password").value
        confirm_password = document.querySelector("#confirm_password").value
    
        if not username or not new_password or not confirm_password:
            window.alert("Please fill in all fields")
            return
    
        if new_password != confirm_password:
            window.alert("Passwords do not match!")
            return
    
        try:
            # First request reset token
            token_response = await pyfetch(
                f"/customers/{username}/password-reset/request",
                method="POST",
                headers={"Content-Type": "application/json"}
            )
    
            if not token_response.ok:
                window.alert("User not found!")
                return
    
            token_data = await token_response.json()
            token = token_data.get("reset_token")
    
            if not token:
                window.alert("Failed to generate reset token")
                return
    
            # Complete password reset
            reset_response = await pyfetch(
                "/customers/password-reset/complete",
                method="POST",
                headers={"Content-Type": "application/json"},
                body=json.dumps({
                    "token": token,
                    "new_password": new_password
                })
            )
    
            reset_data = await reset_response.json()
            
            if reset_response.ok:
                window.alert("Password reset successful!")
                window.location.href = "/login"
            else:
                error_message = reset_data.get("detail", "Failed to reset password")
                window.alert(error_message)
    
        except Exception as e:
            console.error("Error:", e)
            window.alert("An error occurred. Please try again.")

if __name__ == "__main__":
    ForgotPassword()