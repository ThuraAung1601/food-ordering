from pyscript import document, window
import js
import json
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

class AdminDashboard(Widget):
    def __init__(self, element_id):
        super().__init__(element_id)
    
    def drawWidget(self):
        self.container = document.createElement("div")
        self.container.className = "admin-container"
        
        # Create navigation
        nav = document.createElement("nav")
        nav.className = "admin-nav"
        nav.innerHTML = """
            <h1>Admin Dashboard</h1>
            <ul>
                <li><a href="#menus" data-section="menus">Manage Menus</a></li>
                <li><a href="#customerList" data-section="customerList">View Customers</a></li>
                <li><a href="#" id="logoutLink">Logout</a></li>
            </ul>
        """
        
       
        content = document.createElement("div")
        content.className = "content"
        
        menus_section = document.createElement("section")
        menus_section.id = "menus"
        menus_section.className = "dashboard-section"
        menus_section.innerHTML = """
            <h2>Menu Management</h2>
            <div class="action-buttons">
                <button id="createMenuBtn">Create New Menu</button>
            </div>
            <div id="createMenuForm" class="menu-form" style="display: none;">
                <form id="menuForm">
                    <div class="form-group">
                        <label for="menuName">Menu Name:</label>
                        <input type="text" id="menuName" required>
                    </div>
                    <div class="form-actions">
                        <button type="submit" class="submit-btn">Create Menu</button>
                        <button type="button" class="cancel-btn" id="cancelMenuBtn">Cancel</button>
                    </div>
                </form>
            </div>
            <div id="addItemForm" class="menu-form" style="display: none;">
                <h3>Add Item to <span id="currentMenuName"></span></h3>
                <form id="itemForm">
                    <div class="form-group">
                        <label for="itemType">Item Type:</label>
                        <select id="itemType" required>
                            <option value="main">Main Dish</option>
                            <option value="side">Side Dish</option>
                            <option value="drink">Drink</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="itemName">Item Name:</label>
                        <input type="text" id="itemName" required>
                    </div>
                    <div class="form-group">
                        <label for="price">Price:</label>
                        <input type="number" id="price" step="0.01" required>
                    </div>
                    <div class="form-group">
                        <label for="description">Description:</label>
                        <textarea id="description" required></textarea>
                    </div>
                    <div class="form-actions">
                        <button type="submit" class="submit-btn">Add Item</button>
                        <button type="button" class="done-btn" id="doneItemBtn">Done</button>
                    </div>
                </form>
            </div>
            <div id="menuItemsView" class="menu-items-view" style="display: none;">
                <h3 id="selectedMenuName"></h3>
                <div id="menuItemsList"></div>
                <button id="backToMenusBtn" class="back-btn">Back to Menus</button>
            </div>
            <div id="menuList">
                <!-- Menus will be loaded here -->
            </div>
        """
        
       
        customers_section = document.createElement("section")
        customers_section.id = "customerList"
        customers_section.className = "dashboard-section"
        customers_section.innerHTML = """
            <h2 class="customer-heading">Customer List</h2>
            <div id="customersList">
                
            </div>
        """
        
        
        content.appendChild(menus_section)
        content.appendChild(customers_section)
        self.container.appendChild(nav)
        self.container.appendChild(content)
        self.element.appendChild(self.container)
        
       
        self.setupEventListeners()
        
       
        asyncio.ensure_future(self.loadMenus())
        asyncio.ensure_future(self.loadCustomers())
        
        
        self.showSection('menus')

    def setupEventListeners(self):
       
        links = self.container.querySelectorAll('nav a[data-section]')
        for link in links:
            def nav_handler(event):
                event.preventDefault()
                section = event.target.dataset.section
                self.showSection(section)
            
            handler = create_proxy(nav_handler)
            link.onclick = handler
        
      
        logout_link = self.container.querySelector('#logoutLink')
        if logout_link:
            handler = create_proxy(self.handleLogout)
            logout_link.onclick = handler
        
       
        create_btn = self.container.querySelector('#createMenuBtn')
        if create_btn:
            handler = create_proxy(self.showCreateMenuForm)
            create_btn.onclick = handler
        
        cancel_btn = self.container.querySelector('#cancelMenuBtn')
        if cancel_btn:
            handler = create_proxy(self.hideCreateMenuForm)
            cancel_btn.onclick = handler
        
        menu_form = self.container.querySelector('#menuForm')
        if menu_form:
            handler = create_proxy(self.handleCreateMenu)
            menu_form.onsubmit = handler
        
       
        item_form = self.container.querySelector('#itemForm')
        if item_form:
            handler = create_proxy(self.handleAddMenuItem)
            item_form.onsubmit = handler
        
        done_btn = self.container.querySelector('#doneItemBtn')
        if done_btn:
            handler = create_proxy(self.hideAddItemForm)
            done_btn.onclick = handler
        
       
        back_btn = self.container.querySelector('#backToMenusBtn')
        if back_btn:
            handler = create_proxy(self.hideMenuItems)
            back_btn.onclick = handler
        
       

    def showSection(self, section_id):
        sections = self.container.querySelectorAll('.dashboard-section')
        for section in sections:
            section.style.display = 'none'
        
        target_section = self.container.querySelector(f'#{section_id}')
        if target_section:
            target_section.style.display = 'block'
            
            # Load appropriate data based on section
            if section_id == 'customerList':
                asyncio.ensure_future(self.loadCustomers())
            elif section_id == 'menus':
                asyncio.ensure_future(self.loadMenus())

    async def loadMenus(self):
        try:
            response = await pyfetch(
                "/admin/menus",
                method="GET",
                headers={"Accept": "application/json"}
            )
            
            if response.ok:
                data = await response.json()
                menuList = document.getElementById('menuList')
                
                if data.get('menus'):
                    html = ""
                    for menu in data['menus']:
                        html += f"""
                            <div class="menu-card">
                                <h3>{menu['name']}</h3>
                                <p>Total Items: {menu['total_items']}</p>
                                <p>Total Price: ${menu['total_price']:.2f}</p>
                                <div class="menu-actions">
                                    <button class="add-btn" data-menu-name="{menu['name']}">Add Item</button>
                                    <button class="view-btn" data-menu-name="{menu['name']}">View Items</button>
                                    <button class="delete-btn delete" data-menu-name="{menu['name']}">Delete Menu</button>
                                </div>
                            </div>
                        """
                    
                    menuList.innerHTML = html
                    
                    for btn in menuList.querySelectorAll('.add-btn'):
                        handler = create_proxy(lambda e: self.showAddItemForm(e.target.dataset.menuName))
                        btn.onclick = handler
                    
                    for btn in menuList.querySelectorAll('.view-btn'):
                        handler = create_proxy(lambda e: asyncio.ensure_future(self.viewMenuItems(e.target.dataset.menuName)))
                        btn.onclick = handler
                    
                    for btn in menuList.querySelectorAll('.delete-btn'):
                        handler = create_proxy(lambda e: asyncio.ensure_future(self.deleteMenu(e.target.dataset.menuName)))
                        btn.onclick = handler
                else:
                    menuList.innerHTML = '<p>No menus available.</p>'
            else:
                console.error('Failed to load menus:', response.status)
                document.getElementById('menuList').innerHTML = '<p>Error loading menus. Please try again later.</p>'
        
        except Exception as e:
            console.error('Error loading menus:', str(e))
            document.getElementById('menuList').innerHTML = '<p>Error loading menus. Please try again later.</p>'

    async def loadCustomers(self):
        try:
            response = await pyfetch(
                "/admin/customers",
                method="GET",
                headers={"Accept": "application/json"}
            )
            
            if response.ok:
                data = await response.json()
                customersList = document.getElementById('customersList')
                
                if data.get('customers'):
                    html = ""
                    for customer in data['customers']:
                        html += f"""
                            <div class="customer-card" style="border: 1px solid black; width:50%;">
                                <h3>{customer['name']}</h3>
                                <p>Username: {customer['username']}</p>
                                <p>Active Orders: {customer['active_orders']}</p>
                                <p>Address: {customer['default_address']}</p>
                            </div>
                        """
                    customersList.innerHTML = html
                else:
                    customersList.innerHTML = '<p>No customers found.</p>'
            else:
                console.error('Failed to load customers:', response.status)
                document.getElementById('customersList').innerHTML = '<p>Error loading customers. Please try again later.</p>'
        
        except Exception as e:
            console.error('Error loading customers:', str(e))
            document.getElementById('customersList').innerHTML = '<p>Error loading customers. Please try again later.</p>'

    def showCreateMenuForm(self, event):
        if event:
            event.preventDefault()
        document.getElementById('createMenuForm').style.display = 'block'

    def hideCreateMenuForm(self, event):
        if event:
            event.preventDefault()
        document.getElementById('createMenuForm').style.display = 'none'
        document.getElementById('menuForm').reset()

    async def handleCreateMenu(self, event):
        event.preventDefault()
        menu_name = document.getElementById('menuName').value
        
        try:
            response = await pyfetch(
                f"/admin/menu/create?name={window.encodeURIComponent(menu_name)}",
                method="POST",
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },
                body=JSON.stringify({"name": menu_name})
            )
            
            if response.ok:
                self.hideCreateMenuForm(None)
                await self.loadMenus()
            else:
                error = await response.json()
                window.alert(error.get('detail', 'Failed to create menu'))
        except Exception as e:
            console.error('Error creating menu:', str(e))
            window.alert('Failed to create menu')

    def showAddItemForm(self, menu_name):
        document.getElementById('menuList').style.display = 'none'
        document.getElementById('currentMenuName').textContent = menu_name
        document.getElementById('addItemForm').style.display = 'block'

    def hideAddItemForm(self, event):
        if event:
            event.preventDefault()
        
        document.getElementById('menuList').style.display = 'block'
        document.getElementById('addItemForm').style.display = 'none'
        document.getElementById('itemForm').reset()
        asyncio.ensure_future(self.loadMenus())

    async def handleAddMenuItem(self, event):
        event.preventDefault()
        menu_name = document.getElementById('currentMenuName').textContent
        item_type = document.getElementById('itemType').value
        item_name = document.getElementById('itemName').value
        price = document.getElementById('price').value
        description = document.getElementById('description').value
        
        if item_type == 'main':
            default_image = '/static/style/img/burger.png'
        elif item_type == 'side':
            default_image = '/static/style/img/salad.png'
        elif item_type == 'drink':
            default_image = '/static/style/img/noodle.png'
        
        item_data = {
            "name": item_name,
            "price": float(price),
            "description": description,
            "photo_url": default_image
        }
        
        if item_type == 'main':
            item_data["cooking_time"] = 15
        elif item_type == 'side':
            item_data["is_vegetarian"] = True
        elif item_type == 'drink':
            item_data["temperature"] = "COLD"
        
        try:
            response = await pyfetch(f"/admin/menu/{window.encodeURIComponent(menu_name)}/items?item_type={item_type}", 
                       method="POST",
                       headers={"Content-Type": "application/json", "Accept": "application/json"},
                       body=json.dumps(item_data))
            
            if response.ok:
                document.getElementById('itemForm').reset()
                self.hideAddItemForm(None)
                await self.loadMenus()
                await self.viewMenuItems(menu_name)
            else:
                error_data = await response.json()
                console.error('Server error:', error_data)
                window.alert(error_data.get('detail', 'Failed to add item'))
        except Exception as e:
            console.error('Error adding menu item:', e)
            window.alert('Failed to add item')


    async def viewMenuItems(self, menu_name):
        try:
            response = await pyfetch(
                f"/admin/menu/{window.encodeURIComponent(menu_name)}/items",
                method="GET",
                headers={"Accept": "application/json"}
            )
            
            if response.ok:
                data = await response.json()
                document.getElementById('selectedMenuName').textContent = menu_name
                menuItemsList = document.getElementById('menuItemsList')
                
                items = data.get('items', [])
                
                if not items:
                    menuItemsList.innerHTML = '<p>No items in this menu yet.</p>'
                else:
                    html = '' 
                    for item in items:
                        if 'cooking_time' in item:
                            default_image = '/static/style/img/burger.png'
                        elif 'is_vegetarian' in item:
                            default_image = '/static/style/img/salad.png'
                        elif 'temperature' in item:
                            default_image = '/static/style/img/noodle.png'
                        else:
                            default_image = '/static/style/img/pizza.png'
                        
                        specific_props = ""
                        if 'cooking_time' in item:
                            specific_props += f"<p>Cooking Time: {item['cooking_time']} mins</p>"
                        if 'is_vegetarian' in item:
                            specific_props += f"<p>Vegetarian: {'Yes' if item['is_vegetarian'] else 'No'}</p>"
                        if 'temperature' in item:
                            specific_props += f"<p>Temperature: {item['temperature']}</p>"
                        
                        html += f"""
                            <div class="item-card">
                                <img src="{item.get('photo_url', default_image)}" 
                                     alt="{item['name']}"
                                     onerror="this.src='{default_image}'">
                                <div class="item-details">
                                    <h4>{item['name']}</h4>
                                    <p>{item['description']}</p>
                                    <p>Price: ${item['price']:.2f}</p>
                                    {specific_props}
                                </div>
                                <div class="item-actions">
                                    <button class="delete-btn" data-menu-name="{menu_name}" 
                                            data-item-name="{item['name']}">Delete</button>
                                </div>
                            </div>
                        """
                    
                    menuItemsList.innerHTML = html  
                    
                    
                    for btn in menuItemsList.querySelectorAll('.delete-btn'):
                        handler = create_proxy(
                            lambda e: asyncio.ensure_future(
                                self.deleteMenuItem(
                                    e.target.dataset.menuName,
                                    e.target.dataset.itemName
                                )
                            )
                        )
                        btn.onclick = handler
                
                document.getElementById('menuList').style.display = 'none'
                document.getElementById('menuItemsView').style.display = 'block'
                
            else:
                error_data = await response.json()
                console.error('Failed to load menu items:', error_data.get('detail', 'Unknown error'))
                window.alert('Failed to load menu items')
        
        except Exception as e:
            console.error('Error loading menu items:', str(e))
            window.alert('Error loading menu items')

    def hideMenuItems(self, event):
            if event:
                event.preventDefault()
            document.getElementById('menuList').style.display = 'block'
            document.getElementById('menuItemsView').style.display = 'none'
            document.getElementById('menuItemsList').innerHTML = ''

    async def deleteMenuItem(self, menu_name, item_name):
        if window.confirm(f'Are you sure you want to delete {item_name}?'):
            try:
                response = await pyfetch(
                    f"/admin/menu/{window.encodeURIComponent(menu_name)}/items/{window.encodeURIComponent(item_name)}",
                    method="DELETE",
                    headers={"Accept": "application/json"}
                )
                
                if response.ok:
                    menu_response = await pyfetch(
                        f"/admin/menu/{window.encodeURIComponent(menu_name)}",
                        method="GET",
                        headers={"Accept": "application/json"}
                    )
                    
                    menu_data = await menu_response.json()
                    if not menu_data.get('items'):
                        self.hideMenuItems(None)
                    else:
                        await self.viewMenuItems(menu_name)
                    
                    await self.loadMenus()
                else:
                    window.alert('Failed to delete menu item')
            except Exception as e:
                console.error('Error deleting menu item:', str(e))
                window.alert('Failed to delete menu item')

    async def deleteMenu(self, menu_name):
        if window.confirm(f'Are you sure you want to delete {menu_name}?'):
            try:
                response = await pyfetch(
                    f"/admin/menu/{window.encodeURIComponent(menu_name)}",
                    method="DELETE",
                    headers={"Accept": "application/json"}
                )
                
                if response.ok:
                    await self.loadMenus()
                else:
                    window.alert('Failed to delete menu')
            except Exception as e:
                console.error('Error deleting menu:', str(e))
                window.alert('Failed to delete menu')

    async def handleLogout(self, event):
        event.preventDefault()
        try:
            response = await pyfetch(
                "/admin/logout",
                method="POST",
                headers={"Accept": "application/json"}
            )
            
            if response.ok:
                window.location.href = "/"
            else:
                console.error('Logout failed')
        except Exception as e:
            console.error('Error during logout:', str(e))

   
    

if __name__ == "__main__":
    admin = AdminDashboard("app")
    admin.drawWidget()