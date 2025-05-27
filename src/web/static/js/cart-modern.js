// Modern Cart Manager - Handles cart operations, checkout, and persistence
// Integrates with backend API and provides smooth user experience

class CartManager {
  constructor() {
    this.cart = {
      items: [],
      subtotal: 0,
      total: 0,
      itemCount: 0
    };
    this.isOpen = false;
    this.deliveryFee = 0; // Free delivery
    this.taxRate = 0.08; // 8% tax
  }

  // Initialize cart manager
  init() {
    this.loadCartFromStorage();
    this.setupEventListeners();
    this.updateCartDisplay();
    
    console.log('Cart manager initialized');
    
    // Add test function to window for debugging
    window.testCart = () => this.testCartFunctionality();
  }

  // Test cart functionality (for debugging)
  testCartFunctionality() {
    console.log('Testing cart functionality...');
    
    // Add a test item
    const testItem = {
      id: 'test-pizza',
      name: 'Test Pizza',
      price: 12.99,
      image_url: '/static/images/placeholder.jpg',
      available: true,
      category: 'Pizza'
    };
    
    this.cart.items.push({
      id: testItem.id,
      name: testItem.name,
      price: testItem.price,
      image_url: testItem.image_url,
      quantity: 1,
      category: testItem.category
    });
    
    this.calculateTotals();
    this.updateCartDisplay();
    this.saveCartToStorage();
    
    console.log('Test item added to cart:', this.cart);
    console.log('Opening cart sidebar...');
    this.open();
  }

  // Setup event listeners
  setupEventListeners() {
    // Cart toggle button
    const cartToggle = document.getElementById('cart-toggle');
    const cartClose = document.getElementById('cart-close');
    const cartSidebar = document.getElementById('cart-sidebar');

    console.log('Setting up cart event listeners...');
    console.log('Cart toggle element:', cartToggle);
    console.log('Cart close element:', cartClose);
    console.log('Cart sidebar element:', cartSidebar);

    if (cartToggle) {
      console.log('Cart toggle button found, attaching event listener');
      cartToggle.addEventListener('click', (e) => {
        console.log('Cart toggle clicked!');
        e.preventDefault();
        this.toggle();
      });
    } else {
      console.error('Cart toggle button not found!');
    }

    if (cartClose) {
      console.log('Cart close button found, attaching event listener');
      cartClose.addEventListener('click', () => this.close());
    } else {
      console.warn('Cart close button not found');
    }

    // Close cart when clicking outside
    document.addEventListener('click', (e) => {
      if (this.isOpen && cartSidebar && !cartSidebar.contains(e.target) && 
          !e.target.closest('#cart-toggle')) {
        this.close();
      }
    });

    // Checkout button
    const checkoutBtn = document.getElementById('checkout-btn');
    if (checkoutBtn) {
      checkoutBtn.addEventListener('click', () => this.initiateCheckout());
    }

    // Setup checkout modal
    this.setupCheckoutModal();

    // Listen for language changes
    window.addEventListener('languageChanged', () => {
      this.updateCartDisplay();
    });
  }

  // Load cart from localStorage
  loadCartFromStorage() {
    try {
      const savedCart = localStorage.getItem('restaurant-cart');
      if (savedCart) {
        this.cart = JSON.parse(savedCart);
        this.calculateTotals();
      }
    } catch (error) {
      console.error('Error loading cart from storage:', error);
      this.cart = { items: [], subtotal: 0, total: 0, itemCount: 0 };
    }
  }

  // Save cart to localStorage
  saveCartToStorage() {
    try {
      localStorage.setItem('restaurant-cart', JSON.stringify(this.cart));
    } catch (error) {
      console.error('Error saving cart to storage:', error);
    }
  }

  // Add item to cart
  async addItem(itemId, quantity = 1) {
    try {
      // Get item details
      const item = await this.getItemDetails(itemId);
      if (!item || !item.available) {
        return false;
      }

      // Check if item already exists in cart
      const existingItemIndex = this.cart.items.findIndex(cartItem => cartItem.id === itemId);

      if (existingItemIndex > -1) {
        // Update quantity of existing item
        this.cart.items[existingItemIndex].quantity += quantity;
      } else {
        // Add new item to cart
        this.cart.items.push({
          id: item.id,
          name: item.name,
          price: item.price,
          image_url: item.image_url,
          quantity: quantity,
          category: item.category
        });
      }

      this.calculateTotals();
      this.updateCartDisplay();
      this.saveCartToStorage();

      // Send to backend if available
      this.syncWithBackend();

      return true;
    } catch (error) {
      console.error('Error adding item to cart:', error);
      return false;
    }
  }

  // Remove item from cart
  removeItem(itemId) {
    const itemIndex = this.cart.items.findIndex(item => item.id === itemId);
    if (itemIndex > -1) {
      this.cart.items.splice(itemIndex, 1);
      this.calculateTotals();
      this.updateCartDisplay();
      this.saveCartToStorage();
      this.syncWithBackend();
    }
  }

  // Update item quantity
  updateQuantity(itemId, newQuantity) {
    const item = this.cart.items.find(item => item.id === itemId);
    if (item) {
      if (newQuantity <= 0) {
        this.removeItem(itemId);
      } else {
        item.quantity = newQuantity;
        this.calculateTotals();
        this.updateCartDisplay();
        this.saveCartToStorage();
        this.syncWithBackend();
      }
    }
  }

  // Clear cart
  clearCart() {
    this.cart = { items: [], subtotal: 0, total: 0, itemCount: 0 };
    this.updateCartDisplay();
    this.saveCartToStorage();
    this.syncWithBackend();
  }

  // Calculate totals
  calculateTotals() {
    this.cart.subtotal = this.cart.items.reduce((total, item) => {
      return total + (item.price * item.quantity);
    }, 0);

    this.cart.itemCount = this.cart.items.reduce((count, item) => {
      return count + item.quantity;
    }, 0);

    const tax = this.cart.subtotal * this.taxRate;
    this.cart.total = this.cart.subtotal + tax + this.deliveryFee;
  }

  // Get item details
  async getItemDetails(itemId) {
    try {
      // First try to get from menu manager
      if (window.menuManager && window.menuManager.menuItems) {
        const item = window.menuManager.menuItems.find(item => item.id === itemId);
        if (item) return item;
      }

      // Fallback to API call
      const response = await fetch(`/api/menu/items/${itemId}`);
      const data = await response.json();
      
      if (data.success) {
        return data.item;
      } else {
        throw new Error(data.error || 'Item not found');
      }
    } catch (error) {
      console.error('Error getting item details:', error);
      return null;
    }
  }

  // Update cart display
  updateCartDisplay() {
    this.updateCartCount();
    this.updateCartSidebar();
    this.updateCheckoutButton();
  }

  // Update cart count badge
  updateCartCount() {
    const cartCount = document.getElementById('cart-count');
    if (cartCount) {
      cartCount.textContent = this.cart.itemCount;
      cartCount.style.display = this.cart.itemCount > 0 ? 'flex' : 'none';
    }
  }

  // Update cart sidebar content
  updateCartSidebar() {
    const cartContent = document.getElementById('cart-content');
    const cartEmpty = document.getElementById('cart-empty');
    const cartItems = document.getElementById('cart-items');
    const cartFooter = document.getElementById('cart-footer');

    if (!cartContent) return;

    if (this.cart.items.length === 0) {
      if (cartEmpty) cartEmpty.style.display = 'block';
      if (cartItems) cartItems.style.display = 'none';
      if (cartFooter) cartFooter.style.display = 'none';
    } else {
      if (cartEmpty) cartEmpty.style.display = 'none';
      if (cartItems) cartItems.style.display = 'block';
      if (cartFooter) cartFooter.style.display = 'block';

      // Render cart items
      if (cartItems) {
        cartItems.innerHTML = this.cart.items.map(item => this.renderCartItem(item)).join('');
        this.attachCartItemListeners();
      }

      // Update totals
      this.updateCartTotals();
    }
  }

  // Render single cart item
  renderCartItem(item) {
    const imageUrl = this.getImageUrl(item);
    const itemTotal = item.price * item.quantity;

    return `
      <div class="cart-item" data-id="${item.id}">
        <img src="${imageUrl}" 
             alt="${item.name}" 
             class="cart-item-image"
             onerror="this.src='/static/images/placeholder.jpg'">
        
        <div class="cart-item-info">
          <h5 class="cart-item-name">${item.name}</h5>
          <p class="cart-item-price">${this.formatPrice(itemTotal)}</p>
        </div>
        
        <div class="cart-item-controls">
          <div class="quantity-controls">
            <button class="quantity-btn" data-action="decrease" data-id="${item.id}">-</button>
            <span class="quantity-value">${item.quantity}</span>
            <button class="quantity-btn" data-action="increase" data-id="${item.id}">+</button>
          </div>
          
          <button class="remove-item-btn" data-id="${item.id}" aria-label="Remove ${item.name}">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
      </div>
    `;
  }

  // Attach event listeners to cart items
  attachCartItemListeners() {
    const cartItems = document.getElementById('cart-items');
    if (!cartItems) return;

    // Quantity buttons - scope to cart items only
    cartItems.querySelectorAll('.quantity-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        
        const action = btn.dataset.action;
        const itemId = btn.dataset.id;
        const item = this.cart.items.find(item => item.id === itemId);
        
        if (item) {
          const newQuantity = action === 'increase' 
            ? item.quantity + 1 
            : item.quantity - 1;
          this.updateQuantity(itemId, newQuantity);
        }
      });
    });

    // Remove buttons - scope to cart items only
    cartItems.querySelectorAll('.remove-item-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        
        const itemId = btn.dataset.id;
        this.removeItem(itemId);
      });
    });
  }

  // Update cart totals display
  updateCartTotals() {
    const cartSubtotal = document.getElementById('cart-subtotal');
    const cartTotal = document.getElementById('cart-total');

    if (cartSubtotal) {
      cartSubtotal.textContent = this.formatPrice(this.cart.subtotal);
    }

    if (cartTotal) {
      cartTotal.textContent = this.formatPrice(this.cart.total);
    }
  }

  // Update checkout button state
  updateCheckoutButton() {
    const checkoutBtn = document.getElementById('checkout-btn');
    if (checkoutBtn) {
      checkoutBtn.disabled = this.cart.items.length === 0;
    }
  }

  // Toggle cart sidebar
  toggle() {
    console.log('Cart toggle method called. Current state:', this.isOpen);
    if (this.isOpen) {
      this.close();
    } else {
      this.open();
    }
  }

  // Open cart sidebar
  open() {
    console.log('Opening cart sidebar...');
    const cartSidebar = document.getElementById('cart-sidebar');
    if (cartSidebar) {
      cartSidebar.classList.add('open');
      this.isOpen = true;
      console.log('Cart sidebar opened successfully');

      // Prevent body scroll on mobile
      if (window.innerWidth <= 768) {
        document.body.style.overflow = 'hidden';
      }
    } else {
      console.error('Cart sidebar element not found!');
    }
  }

  // Close cart sidebar
  close() {
    console.log('Closing cart sidebar...');
    const cartSidebar = document.getElementById('cart-sidebar');
    if (cartSidebar) {
      cartSidebar.classList.remove('open');
      this.isOpen = false;
      console.log('Cart sidebar closed successfully');

      // Restore body scroll
      document.body.style.overflow = '';
    }
  }

  // Setup checkout modal
  setupCheckoutModal() {
    const checkoutModalOverlay = document.getElementById('checkout-modal-overlay');
    const checkoutModalClose = document.getElementById('checkout-modal-close');

    if (checkoutModalClose) {
      checkoutModalClose.addEventListener('click', () => this.closeCheckoutModal());
    }

    if (checkoutModalOverlay) {
      checkoutModalOverlay.addEventListener('click', (e) => {
        if (e.target === checkoutModalOverlay) {
          this.closeCheckoutModal();
        }
      });
    }
  }

  // Initiate checkout process
  initiateCheckout() {
    if (this.cart.items.length === 0) return;

    this.openCheckoutModal();
  }

  // Open checkout modal
  openCheckoutModal() {
    const checkoutModalOverlay = document.getElementById('checkout-modal-overlay');
    const checkoutContent = document.getElementById('checkout-content');

    if (!checkoutModalOverlay || !checkoutContent) return;

    checkoutContent.innerHTML = this.renderCheckoutForm();
    checkoutModalOverlay.classList.add('active');

    // Setup form interactions
    this.setupCheckoutForm();

    // Prevent body scroll
    document.body.style.overflow = 'hidden';
  }

  // Close checkout modal
  closeCheckoutModal() {
    const checkoutModalOverlay = document.getElementById('checkout-modal-overlay');
    if (checkoutModalOverlay) {
      checkoutModalOverlay.classList.remove('active');
    }

    // Restore body scroll
    document.body.style.overflow = '';
  }

  // Render checkout form
  renderCheckoutForm() {
    return `
      <div class="checkout-summary">
        <h4>Order Summary</h4>
        <div class="checkout-items">
          ${this.cart.items.map(item => `
            <div class="checkout-item">
              <span class="checkout-item-name">${item.name} × ${item.quantity}</span>
              <span class="checkout-item-price">${this.formatPrice(item.price * item.quantity)}</span>
            </div>
          `).join('')}
        </div>
        
        <div class="checkout-totals">
          <div class="checkout-total-row">
            <span>Subtotal:</span>
            <span>${this.formatPrice(this.cart.subtotal)}</span>
          </div>
          <div class="checkout-total-row">
            <span>Tax:</span>
            <span>${this.formatPrice(this.cart.subtotal * this.taxRate)}</span>
          </div>
          <div class="checkout-total-row">
            <span>Delivery:</span>
            <span>Free</span>
          </div>
          <div class="checkout-total-row final">
            <span>Total:</span>
            <span>${this.formatPrice(this.cart.total)}</span>
          </div>
        </div>
      </div>

      <form class="checkout-form" id="checkout-form">
        <div class="form-section">
          <h5>Contact Information</h5>
          <div class="form-group">
            <input type="text" id="customer-name" name="name" placeholder="Full Name" required>
          </div>
          <div class="form-group">
            <input type="tel" id="customer-phone" name="phone" placeholder="Phone Number" required>
          </div>
          <div class="form-group">
            <input type="email" id="customer-email" name="email" placeholder="Email Address" required>
          </div>
        </div>

        <div class="form-section">
          <h5>Delivery Address</h5>
          <div class="form-group">
            <input type="text" id="address-street" name="street" placeholder="Street Address" required>
          </div>
          <div class="form-row">
            <div class="form-group">
              <input type="text" id="address-city" name="city" placeholder="City" required>
            </div>
            <div class="form-group">
              <input type="text" id="address-zip" name="zip" placeholder="ZIP Code" required>
            </div>
          </div>
          <div class="form-group">
            <textarea id="delivery-notes" name="notes" placeholder="Delivery Instructions (Optional)" rows="3"></textarea>
          </div>
        </div>

        <div class="form-section">
          <h5>Payment Method</h5>
          <div class="payment-methods">
            <label class="payment-option">
              <input type="radio" name="payment" value="cash" checked>
              <span class="payment-label">💵 Cash on Delivery</span>
            </label>
            <label class="payment-option">
              <input type="radio" name="payment" value="card">
              <span class="payment-label">💳 Credit Card</span>
            </label>
          </div>
        </div>

        <div class="checkout-actions">
          <button type="button" class="btn btn-outline" onclick="window.cartManager.closeCheckoutModal()">
            Cancel
          </button>
          <button type="submit" class="btn btn-primary">
            Place Order ${this.formatPrice(this.cart.total)}
          </button>
        </div>
      </form>
    `;
  }

  // Setup checkout form interactions
  setupCheckoutForm() {
    const checkoutForm = document.getElementById('checkout-form');
    if (!checkoutForm) return;

    checkoutForm.addEventListener('submit', (e) => {
      e.preventDefault();
      this.processOrder(new FormData(checkoutForm));
    });

    // Phone number formatting
    const phoneInput = document.getElementById('customer-phone');
    if (phoneInput) {
      phoneInput.addEventListener('input', (e) => {
        let value = e.target.value.replace(/\D/g, '');
        if (value.length >= 10) {
          value = value.replace(/(\d{3})(\d{3})(\d{4})/, '($1) $2-$3');
        }
        e.target.value = value;
      });
    }
  }

  // Process order
  async processOrder(formData) {
    try {
      const submitButton = document.querySelector('.checkout-form .btn-primary');
      if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = 'Processing...';
      }

      // Prepare order data
      const orderData = {
        items: this.cart.items,
        customer: {
          name: formData.get('name'),
          phone: formData.get('phone'),
          email: formData.get('email')
        },
        delivery: {
          street: formData.get('street'),
          city: formData.get('city'),
          zip: formData.get('zip'),
          notes: formData.get('notes')
        },
        payment: {
          method: formData.get('payment')
        },
        totals: {
          subtotal: this.cart.subtotal,
          tax: this.cart.subtotal * this.taxRate,
          delivery: this.deliveryFee,
          total: this.cart.total
        }
      };

      // Submit order to backend
      const response = await fetch('/api/orders', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(orderData)
      });

      const result = await response.json();

      if (result.success) {
        // Order successful
        this.handleOrderSuccess(result.order);
      } else {
        throw new Error(result.error || 'Order failed');
      }

    } catch (error) {
      console.error('Order processing error:', error);
      this.handleOrderError(error.message);
    }
  }

  // Handle successful order
  handleOrderSuccess(order) {
    // Clear cart
    this.clearCart();
    
    // Close modals
    this.closeCheckoutModal();
    this.close();

    // Show success message
    if (window.restaurantApp) {
      window.restaurantApp.showToast(
        `Order #${order.id} placed successfully! Estimated delivery: ${order.estimated_delivery}`,
        'success'
      );
    }

    // Optionally redirect to order tracking page
    // window.location.href = `/orders/${order.id}`;
  }

  // Handle order error
  handleOrderError(errorMessage) {
    // Re-enable submit button
    const submitButton = document.querySelector('.checkout-form .btn-primary');
    if (submitButton) {
      submitButton.disabled = false;
      submitButton.textContent = `Place Order ${this.formatPrice(this.cart.total)}`;
    }

    // Show error message
    if (window.restaurantApp) {
      window.restaurantApp.showToast(
        `Order failed: ${errorMessage}`,
        'error'
      );
    }
  }

  // Sync cart with backend
  async syncWithBackend() {
    try {
      // Only sync if user is identified (has previous orders or logged in)
      const sessionId = this.getSessionId();
      if (!sessionId) return;

      await fetch('/api/cart/sync', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          session_id: sessionId,
          cart: this.cart
        })
      });
    } catch (error) {
      console.error('Cart sync error:', error);
      // Sync failures are not critical, so we don't show errors to user
    }
  }

  // Get or create session ID
  getSessionId() {
    let sessionId = localStorage.getItem('restaurant-session-id');
    if (!sessionId) {
      sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
      localStorage.setItem('restaurant-session-id', sessionId);
    }
    return sessionId;
  }

  // Utility methods
  getImageUrl(item) {
    return item.image_url && item.image_url !== '/static/images/placeholder.svg' 
      ? item.image_url 
      : '/static/images/placeholder.jpg';
  }

  formatPrice(price) {
    // Get current language from restaurant app or default to 'az'
    const currentLanguage = window.restaurantApp ? window.restaurantApp.currentLanguage : 'az';
    
    const formatter = new Intl.NumberFormat(currentLanguage === 'az' ? 'az-AZ' : 'en-US', {
      style: 'currency',
      currency: currentLanguage === 'az' ? 'AZN' : 'USD',
      minimumFractionDigits: 2
    });
    return formatter.format(price);
  }

  // Get cart item count
  getItemCount() {
    return this.cart.itemCount;
  }

  // Get cart total
  getTotal() {
    return this.cart.total;
  }

  // Check if cart is empty
  isEmpty() {
    return this.cart.items.length === 0;
  }
}

// Initialize cart manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM loaded, initializing cart manager...');
  window.cartManager = new CartManager();
  window.cartManager.init();
});

export default CartManager;
