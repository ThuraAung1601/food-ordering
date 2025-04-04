import js
from pyscript import document, window
from js import console
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

class Header(Widget):
    def __init__(self, element_id):
        Widget.__init__(self,element_id)
    
    def drawWidget(self):
        self.header = document.createElement("header")
        self.header.className = "l-header"
        self.header.id = "header"
        self.header.style.marginLeft = "80px"
        self.header.innerHTML = """
            <nav class=nav bd-container>
                 <a href="#" class="nav__logo"><h1>Mingalar</h1></a>
                <div class="nav__menu" id="nav-menu">
                    <ul class="nav__list">
                        <li class="nav__item"><a href="#home" class="nav__link active">Home</a></li>
                        <li class="nav__item"><a href="#about" class="nav__link">About</a></li>
                        
                        <li class="nav__item"><a href="/login" class="nav__link">Login</a></li>
                        <li class="nav__item"><a href="/register" class="nav__link">Register</a></li>
                        <li class="nav__item"><a href="#contact" class="nav__link">Contact us</a></li>
                    </ul>
                </div>

                <div class="nav__toggle" id="nav__toggle">
                    <i class="bx bx-menu"></i>
                </div>
            </nav>
        """
        self.element.appendChild(self.header)
        


class MainContent(Widget):
    def __init__(self, element_id):
        Widget.__init__(self,element_id)

    def drawWidget(self):
        self.main = document.createElement("main")
        self.main.className = "main"
        self.main.innerHTML = """
            <section class="home" id="home">
                <div class="home__container bd-container bd-grid">
                    <div class="home__data">
                        <h1 class="home__title">Welcome! <br>Try Our Food</br></h1>
                        <h3 class="home__subtitle">Every good food brings people together</h3>
                        <p class="home__description">
                            Experience the best cuisine in town with our carefully crafted dishes.
                        </p>
                        <a href="" class="button">View Menu</a>
                    </div>
                    <img src="/static/style/img/home.png" alt="" class="home__img">
                </div>
            </section>
            
            <section class="about section bd-container" id="about">
                <div class="about__container bd-grid">
                    <div class="about__data">
                        <span class="section-subtitle about__initial">About us</span>
                        <h2 class="section__title about__initial">We cook the best <br> tasty food</h2>
                        <p class="about__description">
                            We are dedicated to providing the finest dining experience in the entire city, with excellent customer service, the best meals and at the best price, visit us.
                        </p>
                    </div>
                    <img src="/static/style/img/about.jpg" alt="" class="about__img"/>
                </div>
            </section>
            
           
        """
        self.element.appendChild(self.main)

class Contact(Widget):
    def __init__(self, element_id):
        Widget.__init__(self,element_id)
    
    def drawWidget(self):
        self.contact = document.createElement("section")
        self.contact.className = "contact section bd-container"
        self.contact.id = "contact"
        self.contact.innerHTML = """
             <div class="contact__container bd-grid">
                    <div class="contact__data">
                        <span class="section-subtitle contact__initial">Let's talk</span>
                        <h2 class="section-title contact__initial">Contact us</h2>
                        <p class="contact__description">We would love to hear from you!<br> For any queries, please contact us.<br>Feel free to contact and suggest the improvements that are required for this website</p>
                    </div>

                    <div class="contact__button">
                        <a href="#" class="button">Contact us now</a>
                    </div>
                </div>
        """
        self.element.appendChild(self.contact)

class Footer(Widget):
    def __init__(self, element_id):
        Widget.__init__(self,element_id)

    def drawWidget(self):
        self.footer = document.createElement("footer")
        self.footer.className = "footer section bd-container"
        self.footer.innerHTML = """
            <div class="footer__container bd-grid">
                <div class="footer__content">
                    <a href="#" class="footer__logo">Mingalar</a>
                    <span class="footer__description">Restaurant</span>
                    <div>
                        <a href="#" class="footer__social"><i class='bx bxl-facebook'></i></a>
                        <a href="#" class="footer__social"><i class='bx bxl-instagram'></i></a>
                        <a href="#" class="footer__social"><i class='bx bxl-twitter'></i></a>
                    </div>
                </div>

                <div class="footer__content">
                    <h3 class="footer__title">Services</h3>
                    <ul>
                        <li><a href="table.html" class="footer__link">Table Reservation</a></li>
                        <li><a href="menu.html" class="footer__link">Order Food</a></li>
                        <li><a href="#" class="footer__link">Delivery Tracking</a></li>
                    </ul>
                </div>
                <div class="footer__content">
                    <h3 class="footer__title">Information</h3>
                    <ul>
                        <li><a href="#" class="footer__link">Event</a></li>
                        <li><a href="#" class="footer__link">Contact us</a></li>
                        <li><a href="#" class="footer__link">Privacy policy</a></li>
                        <li><a href="#" class="footer__link">Terms of services</a></li>
                    </ul>
                </div>

                <div class="footer__content">
                    <h3 class="footer__title">Address</h3>
                    <ul>
                        <li>Chalong Krung</li>
                        <li>Lat Krabang, Bangkok</li>
                        <li>09-123-456</li>
                        <li>mingalar@gmail.com</li>
                    </ul>
                </div>
             </div>

            <p class="footer__copy">&#169; 2024 TEAM TEN. All rights reserved</p>

        """
        self.element.appendChild(self.footer)

class HomeLayout(Widget):
    def __init__(self, element_id):
        super().__init__(element_id)
        
        self.container = document.createElement("main")
        self.container.className = "l-main"
        
        self.header = Header(element_id)   
        self.main_content = MainContent(element_id)
        self.contact = Contact(element_id)
        self.footer = Footer(element_id)

    def drawWidget(self):
        try:
            self.header.drawWidget()
            self.main_content.drawWidget()
            self.contact.drawWidget()
            self.footer.drawWidget()
            self.element.appendChild(self.container)

           
            self._setup_navigation()
        except Exception as e:
            console.error("Error in drawWidget:", e)

    def _setup_navigation(self):
        
        nav_links = document.querySelectorAll('.nav__link')
        for link in nav_links:
            link.addEventListener('click', self._handle_navigation)

    def _handle_navigation(self, event):
        href = event.target.getAttribute('href')
        if href.startswith('/'):
            event.preventDefault()
            window.location.href = href


if __name__ == "__main__":
    home = HomeLayout("app")
    home.drawWidget()