from pyscript import document, window
import js,json
from js import console, JSON
from pyodide.http import pyfetch
from pyodide.ffi import create_proxy
from abc import ABC, abstractmethod
import asyncio

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

class CustomerDashboard(Widget):
    def __init__(self, element_id):
        super().__init__(element_id)
        self.pathSegments = window.location.pathname.split('/')
        self.username = self.pathSegments[2]
        self.cart_items = []
    
    def drawWidget(self):
        self.container = document.createElement("div")
        self.container.className = "dashboard-container"
        
        # Create navigation
        nav = document.createElement("nav")
        nav.className = "customer-nav"
        
        nav_header = document.createElement("div")
        nav_header.className = "nav-header"
        nav_header.innerHTML = f"""
            <i class='bx bx-restaurant logo-icon'></i>
            <h1>Silver Leaf</h1>
        """
        
        nav_links = document.createElement("ul")
        nav_links.className = "nav-links"
        
        # Create navigation links
        links_data = [
            {"id": "orders", "icon": "bx-food-menu", "text": "Orders", "handler": self.showOrders},
            {"id": "menu", "icon": "bx-restaurant", "text": "Menu", "handler": self.showMenu},
            {"id": "cart", "icon": "bx-cart", "text": "My Cart", "handler": self.showCart},
            {"id": "logout", "icon": "bx-log-out", "text": "Logout", "handler": self.handleLogout}
        ]
        
        for link in links_data:
            li = document.createElement("li")
            a = document.createElement("a")
            a.href = "javascript:void(0);"
            a.dataset.section = link["id"]
            handler = create_proxy(link["handler"])
            a.onclick = handler
            
            icon = document.createElement("i")
            icon.className = f'bx {link["icon"]}'
            span = document.createElement("span")
            span.innerHTML = link["text"]
            
            a.appendChild(icon)
            a.appendChild(span)
            li.appendChild(a)
            nav_links.appendChild(li)
        
        # Create main content sections
        sections_data = [
            {"id": "menu", "title": "Our Menu", "class": "menu-grid"},
            {"id": "cart", "title": "My Cart", "class": "cart-grid"},
            {"id": "orders", "title": "Your Orders", "class": "orders-list"}
        ]
        
        main_content = document.createElement("div")
        main_content.className = "content"
        
        header = document.createElement("div")
        header.className = "header"
        header.innerHTML = f"""
            <h2>Welcome Back!</h2>
            <div class="user-info">
                <i class='bx bx-user-circle'></i>
                <span id="customerName">{self.username}</span>
            </div>
        """
        main_content.appendChild(header)
        
        for section in sections_data:
            section_elem = document.createElement("section")
            section_elem.id = section["id"]
            section_elem.className = "dashboard-section"
            section_elem.innerHTML = f"""
                <div class="section-header">
                    <h2>{section["title"]}</h2>
                </div>
                <div id="{section['id']}List" class="{section['class']}"></div>
            """
            main_content.appendChild(section_elem)
        
      
        nav.appendChild(nav_header)
        nav.appendChild(nav_links)
        self.container.appendChild(nav)
        self.container.appendChild(main_content)
        self.element.appendChild(self.container)
    
        self.showMenu(None)
    
    async def loadMenuSection(self):
            try:
                response = await pyfetch(
                    f"/customers/{self.username}/menus",
                    method="GET",
                    headers={
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                        "X-Requested-With": "XMLHttpRequest"
                    }
                )

                menuList = document.getElementById('menuList')
                menuList.innerHTML = ''  

                if response.ok:
                    data = await response.json()
                    # console.log('Menu data:', data)  

                    menus = data.get('menus', {})  

                    if menus:
                        for menu_name, items in menus.items():  
                            menuCard = document.createElement('div')
                            menuCard.className = 'menu-card'
                            menuCard.innerHTML = f"<h3>{menu_name}</h3>"

                            if items: 
                                itemsContainer = document.createElement('div')
                                itemsContainer.className = 'menu-actions'

                                for item in items:
                                    itemCard = self.createItemCard(item)
                                    itemsContainer.appendChild(itemCard)

                                menuCard.appendChild(itemsContainer)
                            else:
                                menuCard.innerHTML += '<p>No items available in this menu.</p>'

                            menuList.appendChild(menuCard)
                    else:
                        menuList.innerHTML = '<p>No menus available.</p>'
                else:
                    console.error('Failed to load menus:', response.status)
                    menuList.innerHTML = '<p>Error loading menus. Please try again later.</p>'

            except Exception as e:
                console.error('Error loading menus:', str(e))
                document.getElementById('menuList').innerHTML = '<p>Error loading menus. Please try again later.</p>'

    def createItemCard(self, item):
        itemCard = document.createElement('div')
        itemCard.className = 'item-card'
        itemCard.innerHTML = f"""
            <img src="{item.get('photo_url', '/static/style/img/burger.png')}"
                alt="{item['name']}"
                style="width: 50%; height: 50%;" />
            <div class="item-details">
                <h4>{item['name']}</h4>
                <p>{item.get('description', 'No description available')}</p>
                <p>Price: ${item['price']:.2f}</p>
                <button class="add-to-cart-btn" data-item-name="{item['name']}">
                    Add to Cart
                </button>
            </div>
        """
        
        addBtn = itemCard.querySelector('.add-to-cart-btn')
        if addBtn:
            async def add_to_cart_handler(event):
                event.preventDefault()
                name = item['name'] 
                console.log(f"Adding to cart: {name}")
                await self.addToCart(name)
            
            handler = create_proxy(add_to_cart_handler)
            addBtn.onclick = handler

        return itemCard

    async def addToCart(self, item_name):
        try:
            cart_data = {
                "item_name": item_name,
                "quantity": 1
            }
            
            json_str = f'{{"item_name": "{item_name}", "quantity": 1}}'
            
            console.log("Sending cart data:", json_str)
            
            response = await pyfetch(
                f"/customers/{self.username}/cart/add",
                method="POST",
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },
                body=json_str
            )
            
            if response.ok:
                console.log('Item added to cart successfully')
                window.alert(f"Added {item_name} to your cart!")
                await self.loadCartItems()
            else:
                error_text = await response.text()
                console.error('Failed to add item to cart:', error_text)
                window.alert("Failed to add item to cart. Please try again.")
        except Exception as e:
            console.error('Error adding to cart:', str(e))
            window.alert("Error adding item to cart. Please try again.")

    async def loadCartItems(self):
        try:
            response = await pyfetch(
                f"/customers/{self.username}/cart",
                method="GET",
                headers={"Accept": "application/json"}
            )
            
            if response.ok:
                cart_items = await response.json()
                console.log('Cart items:', cart_items)
                self.updateCartDisplay(cart_items)
            else:
                console.error('Failed to load cart items:', await response.text())
                document.getElementById('cartList').innerHTML = '<p>Failed to load cart items</p>'
        except Exception as e:
            console.error('Error loading cart:', str(e))
            document.getElementById('cartList').innerHTML = '<p>Error loading cart items</p>'

    def updateCartDisplay(self, cart_items):
        cartList = document.getElementById('cartList')
        if not cartList:
            console.error('Cart list container not found')
            return
            
        cartList.innerHTML = ''
        
        if cart_items and len(cart_items) > 0:
            total = 0
            
            for item in cart_items:
                itemElem = document.createElement('div')
                itemElem.className = 'cart-item-card'
                price = item.get('price', 0)
                quantity = item.get('quantity', 1)
                item_total = price * quantity
                total += item_total
                
                item_name = item.get('item_name', item.get('name', 'Unknown Item'))
                photo_url = item.get('photo_url', '/static/style/img/burger.png')
                description = item.get('description', 'No description available')
                
                itemElem.innerHTML = f"""
                    <div class="cart-item">
                        <img src="{photo_url}" 
                             alt="{item_name}" 
                             style="width: 100px; height: 100px;" />
                        <div class="cart-item-details">
                            <h4>{item_name}</h4>
                            <p>{description}</p>
                            <p>Price: ${price:.2f}</p>
                            <p>Quantity: {quantity}</p>
                            <button class="remove-from-cart-btn" data-item-name="{item_name}">
                                Remove
                            </button>
                        </div>
                    </div>
                """
                
                cartList.appendChild(itemElem)
            
            checkoutSection = document.createElement('div')
            checkoutSection.className = 'cart-total'
            checkoutSection.innerHTML = f"""
                <div class="total-info">
                    <h3>Total: ${total:.2f}</h3>
                    <p>Items: {len(cart_items)}</p>
                </div>
                <button id="checkoutBtn" class="checkout-btn">Proceed to Checkout</button>
            """
            cartList.appendChild(checkoutSection)
            
            checkoutBtn = checkoutSection.querySelector('#checkoutBtn')
            if checkoutBtn:
                handler = create_proxy(self.proceedToCheckout)
                checkoutBtn.onclick = handler
            
            removeButtons = cartList.querySelectorAll('.remove-from-cart-btn')
            for btn in removeButtons:
                async def remove_handler(event):
                    name_to_remove = event.target.dataset.itemName
                    await self.removeFromCart(name_to_remove)
                
                handler = create_proxy(remove_handler)
                btn.onclick = handler
        else:
            cartList.innerHTML = '<p class="empty-cart-message">Your cart is empty</p>'

    async def removeFromCart(self, item_name):
        try:
            json_str = f'{{"item_name": "{item_name}", "quantity": 1}}'
            
            response = await pyfetch(
                f"/customers/{self.username}/cart/remove",
                method="DELETE",
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },
                body=json_str
            )
            
            if response.ok:
                console.log('Item removed from cart successfully')
                await self.loadCartItems()
            else:
                error_text = await response.text()
                console.error('Failed to remove item from cart:', error_text)
                window.alert("Failed to remove item from cart")
        except Exception as e:
            console.error('Error removing from cart:', str(e))
            window.alert("Error removing item from cart")

    async def proceedToCheckout(self, event):
        try:
            response = await pyfetch(
                f"/customers/{self.username}/order/create",
                method="POST",
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                }
            )
            
            if response.ok:
                order_data = await response.json()
                console.log('Order created successfully:', order_data)
                
                window.alert("Order created successfully! Your order will be delivered soon.")
               
                await self.loadCartItems()
                await self.loadOrders()
               
                self.showSection('orders')
            else:
                error_text = await response.text()
                console.error('Failed to create order:', error_text)
                window.alert("Failed to create order. Please try again.")
        except Exception as e:
            console.error('Error creating order:', str(e))
            window.alert("Error creating order. Please try again.")

    async def loadOrders(self):
        try:
            response = await pyfetch(
                f"/customers/{self.username}/orders",
                method="GET",
                headers={"Accept": "application/json"}
            )
            
            if response.ok:
                orders = await response.json()
                console.log('Orders:', orders)
                
                ordersList = document.getElementById('ordersList')
                if ordersList:
                    ordersList.innerHTML = ''
                    
                    if orders and len(orders) > 0:
                        for order in orders:
                            orderCard = document.createElement('div')
                            orderCard.className = 'order-card'
                            
                            order_date = order.get('created_at', 'Unknown date')
                            estimated_delivery = order.get('estimated_delivery', '')
                            status = order.get('status', 'Processing')
                            total = order.get('total_price', 0)
                            address = order.get('delivery_address', 'No address provided')
                            order_id = order.get('order_id', 'Unknown')[:8]  # Get first 8 chars of order ID
                            
                            items_html = ""
                            for item in order.get('items', []):
                                items_html += f"""
                                    <div class="order-item">
                                        <span class="item-name">{item.get('name', 'Unknown Item')}</span>
                                        <span class="item-price">${item.get('price', 0):.2f}</span>
                                    </div>
                                """
                            
                            delivery_html = f"""
                                <p>Estimated Delivery: {estimated_delivery}</p>
                            """ if estimated_delivery else ""
                            
                            orderCard.innerHTML = f"""
                                <div class="order-header">
                                    <h3>Order #{order_id}</h3>
                                    <span class="status {status.lower()}">{status}</span>
                                </div>
                                <div class="order-details">
                                    <div class="items-list">
                                        {items_html}
                                    </div>
                                    <div class="order-summary">
                                        <p>Total: ${total:.2f}</p>
                                        <p>Delivery to: {address}</p>
                                        <p>Ordered: {order_date}</p>
                                        {delivery_html}
                                    </div>
                                </div>
                            """
                            
                            ordersList.appendChild(orderCard)
                    else:
                        ordersList.innerHTML = '<p>No orders found</p>'
                else:
                    console.error('Orders container not found')
            else:
                console.error('Failed to load orders:', await response.text())
                if document.getElementById('ordersList'):
                    document.getElementById('ordersList').innerHTML = '<p>Error loading orders. Please try again later.</p>'
        except Exception as e:
            console.error('Error loading orders:', str(e))
            if document.getElementById('ordersList'):
                document.getElementById('ordersList').innerHTML = '<p>Error loading orders. Please try again later.</p>'

    def showMenu(self, event):
        if event:
            event.preventDefault()
        self.showSection('menu')
        asyncio.ensure_future(self.loadMenuSection())

    def showCart(self, event):
        event.preventDefault()
        self.showSection('cart')
        asyncio.ensure_future(self.loadCartItems())

    def showOrders(self, event):
        event.preventDefault()
        self.showSection('orders')
        asyncio.ensure_future(self.loadOrders())

    def showSection(self, section_id):
        sections = document.querySelectorAll('.dashboard-section')
        for section in sections:
            section.style.display = 'none'
        
        target_section = document.getElementById(section_id)
        if target_section:
            target_section.style.display = 'block'
        
        links = document.querySelectorAll('.nav-links a')
        for link in links:
            link.classList.remove('active')
            if link.dataset.section == section_id:
                link.classList.add('active')

    def handleLogout(self, event):
        event.preventDefault()
        asyncio.ensure_future(self.logout())

    async def logout(self):
        try:
            response = await pyfetch("/customers/logout", method="POST")
            if response.ok:
                window.location.href = "/"
            else:
                console.error('Logout failed')
        except Exception as e:
            console.error('Error during logout:', str(e))

if __name__ == "__main__":
    cus = CustomerDashboard("app")
    cus.drawWidget()