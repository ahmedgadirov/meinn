// Enhanced Menu Manager - Handles menu display, filtering, and interactions
// Integrates with backend API and provides smooth user experience

class MenuManager {
  constructor() {
    this.categories = [];
    this.menuItems = [];
    this.filteredItems = [];
    this.currentCategory = 'all';
    this.currentView = 'grid';
    this.isLoading = false;

    // Listen for language changes to update menu
    window.addEventListener('languageChanged', () => {
      this.fetchMenuItemsForCurrentLanguage();
    });
  }

  // Initialize menu manager
  init() {
    this.setupViewControls();
    this.setupFilterTabs();
    this.setupCategoryCards();
    this.setupItemModals();

    // Initial fetch of menu items for current language
    this.fetchMenuItemsForCurrentLanguage();
    
    console.log('Menu manager initialized');
  }

  // Set categories data
  setCategories(categories) {
    this.categories = categories;
  }

  // Fetch menu items for the current language and re-render
  async fetchMenuItemsForCurrentLanguage() {
    try {
      const currentLanguage = window.restaurantApp ? window.restaurantApp.currentLanguage : 'az';
      // Fetch categories and menu items for the new language
      const [categories, menuItems] = await Promise.all([
        fetch(`/api/menu/categories?language=${currentLanguage}`)
          .then(res => res.json())
          .then(data => data.success ? data.categories || [] : []),
        fetch(`/api/menu/items?language=${currentLanguage}`)
          .then(res => res.json())
          .then(data => data.success ? data.items || [] : [])
      ]);
      this.setCategories(categories);
      this.setMenuItems(menuItems);
      this.renderCategories();
      this.renderFilterTabs();
      this.renderMenuItems();
    } catch (error) {
      console.error('Error updating menu for new language:', error);
    }
  }

  // Set menu items data
  setMenuItems(items) {
    this.menuItems = items;
    this.filteredItems = [...items];
  }

  // Render categories grid
  renderCategories() {
    const categoriesGrid = document.getElementById('categories-grid');
    if (!categoriesGrid || !this.categories.length) return;

    // Add "All Items" category
    const allCategory = {
      id: 'all',
      name: 'All Items',
      description: 'Browse everything',
      count: this.menuItems.length
    };

    const categoriesToRender = [allCategory, ...this.categories];

    categoriesGrid.innerHTML = categoriesToRender.map(category => `
      <div class="category-card" data-category="${category.id}">
        <div class="category-icon">
          ${this.getCategoryIcon(category.id)}
        </div>
        <h4 class="category-name">${category.name}</h4>
        <p class="category-count">${this.getCategoryCount(category.id)} items</p>
      </div>
    `).join('');

    // Add click event listeners
    categoriesGrid.querySelectorAll('.category-card').forEach(card => {
      card.addEventListener('click', () => {
        const categoryId = card.dataset.category;
        this.filterByCategory(categoryId);
        this.scrollToMenu();
      });
    });
  }

  // Render filter tabs
  renderFilterTabs() {
    const filterTabs = document.getElementById('filter-tabs');
    if (!filterTabs) return;

    // Create tabs for categories
    const allTab = { id: 'all', name: 'All Items' };
    const tabsToRender = [allTab, ...this.categories];

    filterTabs.innerHTML = tabsToRender.map(category => `
      <button class="filter-tab ${category.id === this.currentCategory ? 'active' : ''}" 
              data-category="${category.id}">
        ${category.name}
      </button>
    `).join('');

    // Add click event listeners
    filterTabs.querySelectorAll('.filter-tab').forEach(tab => {
      tab.addEventListener('click', () => {
        const categoryId = tab.dataset.category;
        this.filterByCategory(categoryId);
      });
    });
  }

  // Render menu items
  renderMenuItems() {
    const menuGrid = document.getElementById('menu-grid');
    const menuLoading = document.getElementById('menu-loading');
    
    if (!menuGrid) return;

    // Show loading if no items yet
    if (!this.filteredItems.length && this.isLoading) {
      if (menuLoading) menuLoading.style.display = 'flex';
      menuGrid.innerHTML = this.renderSkeletonItems();
      return;
    }

    // Hide loading
    if (menuLoading) menuLoading.style.display = 'none';

    // Update grid class for view mode
    menuGrid.className = `menu-grid ${this.currentView === 'list' ? 'list-view' : ''}`;

    if (!this.filteredItems.length) {
      menuGrid.innerHTML = `
        <div class="menu-empty">
          <h4>No items found</h4>
          <p>Try selecting a different category or search term.</p>
        </div>
      `;
      return;
    }

    menuGrid.innerHTML = this.filteredItems.map(item => this.renderMenuItem(item)).join('');

    // Add event listeners
    this.attachMenuItemListeners();
  }

  // Render single menu item
  renderMenuItem(item) {
    const imageUrl = this.getImageUrl(item);
    const price = this.formatPrice(item.price);
    const badges = this.getItemBadges(item);

    return `
      <div class="menu-item" data-id="${item.id}">
        <img src="${imageUrl}" 
             alt="${item.name}" 
             class="menu-item-image"
             loading="lazy"
             onerror="this.src='/static/images/placeholder.jpg'">
        
        <div class="menu-item-content">
          ${this.currentView === 'list' ? '<div class="menu-item-info">' : ''}
          
          <div class="menu-item-header">
            <h4 class="menu-item-name">${item.name}</h4>
            ${badges.length ? `<div class="menu-item-badges">${badges.join('')}</div>` : ''}
          </div>
          
          <p class="menu-item-description">${item.description || ''}</p>
          
          ${item.nutrition ? this.renderNutritionInfo(item.nutrition) : ''}
          
          ${this.currentView === 'list' ? '</div>' : ''}
          
          <div class="menu-item-footer">
            <span class="menu-item-price">${price}</span>
            <button class="add-to-cart-btn" 
                    data-id="${item.id}"
                    ${!item.available ? 'disabled' : ''}
                    aria-label="Add ${item.name} to cart">
              ${item.available ? '+' : '✗'}
            </button>
          </div>
        </div>
      </div>
    `;
  }

  // Render nutrition info
  renderNutritionInfo(nutrition) {
    if (!nutrition) return '';

    return `
      <div class="menu-item-meta">
        ${nutrition.calories ? `<span class="meta-item">🔥 ${nutrition.calories} cal</span>` : ''}
        ${nutrition.protein ? `<span class="meta-item">💪 ${nutrition.protein}g protein</span>` : ''}
        ${nutrition.carbs ? `<span class="meta-item">🌾 ${nutrition.carbs}g carbs</span>` : ''}
      </div>
    `;
  }

  // Get item badges
  getItemBadges(item) {
    const badges = [];
    
    if (item.popular) {
      badges.push('<span class="item-badge badge-popular">Popular</span>');
    }
    
    if (item.new) {
      badges.push('<span class="item-badge badge-new">New</span>');
    }
    
    if (item.spicy) {
      badges.push('<span class="item-badge badge-spicy">Spicy</span>');
    }
    
    return badges;
  }

  // Render skeleton loading items
  renderSkeletonItems() {
    return Array(6).fill().map(() => `
      <div class="skeleton-item">
        <div class="skeleton-image skeleton"></div>
        <div class="skeleton-content">
          <div class="skeleton-text long skeleton"></div>
          <div class="skeleton-text short skeleton"></div>
          <div class="skeleton-text long skeleton"></div>
        </div>
      </div>
    `).join('');
  }

  // Attach event listeners to menu items
  attachMenuItemListeners() {
    const menuItems = document.querySelectorAll('.menu-item');
    const addToCartBtns = document.querySelectorAll('.add-to-cart-btn');

    // Menu item clicks (open modal)
    menuItems.forEach(item => {
      item.addEventListener('click', (e) => {
        // Don't open modal if clicking add to cart button
        if (e.target.classList.contains('add-to-cart-btn')) return;
        
        const itemId = item.dataset.id;
        this.openItemModal(itemId);
      });
    });

    // Add to cart button clicks
    addToCartBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const itemId = btn.dataset.id;
        this.addToCart(itemId, btn);
      });
    });
  }

  // Filter by category
  async filterByCategory(categoryId) {
    if (this.currentCategory === categoryId) return;

    this.currentCategory = categoryId;
    this.isLoading = true;

    // Update active tab
    document.querySelectorAll('.filter-tab').forEach(tab => {
      tab.classList.toggle('active', tab.dataset.category === categoryId);
    });

    try {
      // Fetch items for specific category if not "all"
      if (categoryId === 'all') {
        this.filteredItems = [...this.menuItems];
      } else {
        const items = await this.fetchItemsByCategory(categoryId);
        this.filteredItems = items;
      }

      this.renderMenuItems();
    } catch (error) {
      console.error('Error filtering by category:', error);
      this.showError('Failed to load category items');
    } finally {
      this.isLoading = false;
    }
  }

  // Fetch items by category
  async fetchItemsByCategory(categoryId) {
    try {
      // Get current language
      const currentLanguage = window.restaurantApp ? window.restaurantApp.currentLanguage : 'en';
      const response = await fetch(`/api/menu/items?category=${categoryId}&language=${currentLanguage}`);
      const data = await response.json();
      
      if (data.success) {
        return data.items || [];
      } else {
        throw new Error(data.error || 'Failed to fetch items');
      }
    } catch (error) {
      console.error('Error fetching category items:', error);
      // Return filtered items from current menu as fallback
      return this.menuItems.filter(item => 
        item.category_id?.toLowerCase() === categoryId.toLowerCase()
      );
    }
  }

  // Setup view controls
  setupViewControls() {
    const gridViewBtn = document.getElementById('grid-view');
    const listViewBtn = document.getElementById('list-view');

    if (gridViewBtn) {
      gridViewBtn.addEventListener('click', () => this.switchView('grid'));
    }

    if (listViewBtn) {
      listViewBtn.addEventListener('click', () => this.switchView('list'));
    }
  }

  // Switch view mode
  switchView(viewMode) {
    if (this.currentView === viewMode) return;

    this.currentView = viewMode;

    // Update active button
    document.querySelectorAll('.view-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.view === viewMode);
    });

    // Re-render items with new view
    this.renderMenuItems();

    // Save preference
    localStorage.setItem('menu-view-preference', viewMode);
  }

  // Setup filter tabs
  setupFilterTabs() {
    // Render initial tabs
    this.renderFilterTabs();
  }

  // Setup category cards
  setupCategoryCards() {
    // Category cards are rendered in renderCategories()
  }

  // Setup item modals
  setupItemModals() {
    const modalOverlay = document.getElementById('item-modal-overlay');
    const modalClose = document.getElementById('item-modal-close');

    if (modalClose) {
      modalClose.addEventListener('click', () => this.closeItemModal());
    }

    if (modalOverlay) {
      modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) {
          this.closeItemModal();
        }
      });
    }
  }

  // Open item modal
  openItemModal(itemId) {
    const item = this.menuItems.find(item => item.id === itemId);
    if (!item) return;

    const modalOverlay = document.getElementById('item-modal-overlay');
    const modalContent = document.getElementById('item-modal-content');

    if (!modalOverlay || !modalContent) return;

    modalContent.innerHTML = this.renderItemModal(item);
    modalOverlay.classList.add('active');

    // Setup modal interactions
    this.setupModalInteractions(item);

    // Prevent body scroll
    document.body.style.overflow = 'hidden';
  }

  // Close item modal
  closeItemModal() {
    const modalOverlay = document.getElementById('item-modal-overlay');
    if (modalOverlay) {
      modalOverlay.classList.remove('active');
    }

    // Restore body scroll
    document.body.style.overflow = '';
  }

  // Render item modal content
  renderItemModal(item) {
    const imageUrl = this.getImageUrl(item);
    const price = this.formatPrice(item.price);
    const badges = this.getItemBadges(item);

    return `
      <div class="item-modal-image">
        <img src="${imageUrl}" alt="${item.name}" onerror="this.src='/static/images/placeholder.jpg'">
      </div>
      
      <div class="item-modal-info">
        <div class="item-modal-header">
          <h3 class="item-modal-name">${item.name}</h3>
          ${badges.length ? `<div class="item-modal-badges">${badges.join('')}</div>` : ''}
        </div>
        
        <p class="item-modal-description">${item.description || 'No description available.'}</p>
        
        ${item.allergens ? this.renderAllergens(item.allergens) : ''}
        ${item.nutrition ? this.renderDetailedNutrition(item.nutrition) : ''}
        
        <div class="item-modal-footer">
          <div class="item-modal-price">
            <span class="price-label">Price:</span>
            <span class="price-value">${price}</span>
          </div>
          
          <div class="item-modal-actions">
            <div class="quantity-selector">
              <button class="quantity-btn" data-action="decrease">-</button>
              <span class="quantity-value" id="modal-quantity">1</span>
              <button class="quantity-btn" data-action="increase">+</button>
            </div>
            
            <button class="modal-add-to-cart-btn btn-primary" 
                    data-id="${item.id}"
                    ${!item.available ? 'disabled' : ''}>
              ${item.available ? 'Add to Cart' : 'Unavailable'}
            </button>
          </div>
        </div>
      </div>
    `;
  }

  // Render allergens info
  renderAllergens(allergens) {
    if (!allergens || !allergens.length) return '';

    return `
      <div class="item-allergens">
        <h5>Allergens:</h5>
        <div class="allergen-tags">
          ${allergens.map(allergen => `<span class="allergen-tag">${allergen}</span>`).join('')}
        </div>
      </div>
    `;
  }

  // Render detailed nutrition info
  renderDetailedNutrition(nutrition) {
    if (!nutrition) return '';

    return `
      <div class="item-nutrition">
        <h5>Nutrition Information:</h5>
        <div class="nutrition-grid">
          ${nutrition.calories ? `<div class="nutrition-item">
            <span class="nutrition-label">Calories</span>
            <span class="nutrition-value">${nutrition.calories}</span>
          </div>` : ''}
          ${nutrition.protein ? `<div class="nutrition-item">
            <span class="nutrition-label">Protein</span>
            <span class="nutrition-value">${nutrition.protein}g</span>
          </div>` : ''}
          ${nutrition.carbs ? `<div class="nutrition-item">
            <span class="nutrition-label">Carbs</span>
            <span class="nutrition-value">${nutrition.carbs}g</span>
          </div>` : ''}
          ${nutrition.fat ? `<div class="nutrition-item">
            <span class="nutrition-label">Fat</span>
            <span class="nutrition-value">${nutrition.fat}g</span>
          </div>` : ''}
        </div>
      </div>
    `;
  }

  // Setup modal interactions
  setupModalInteractions(item) {
    const quantityBtns = document.querySelectorAll('.quantity-btn');
    const quantityValue = document.getElementById('modal-quantity');
    const addToCartBtn = document.querySelector('.modal-add-to-cart-btn');

    let quantity = 1;

    // Quantity controls
    quantityBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const action = btn.dataset.action;
        
        if (action === 'increase') {
          quantity++;
        } else if (action === 'decrease' && quantity > 1) {
          quantity--;
        }
        
        if (quantityValue) {
          quantityValue.textContent = quantity;
        }
      });
    });

    // Add to cart from modal
    if (addToCartBtn) {
      addToCartBtn.addEventListener('click', () => {
        this.addToCart(item.id, addToCartBtn, quantity);
      });
    }
  }

  // Add item to cart
  async addToCart(itemId, buttonElement, quantity = 1) {
    const item = this.menuItems.find(item => item.id === itemId);
    if (!item || !item.available) return false;

    try {
      // Add visual feedback
      if (buttonElement) {
        buttonElement.classList.add('added');
        setTimeout(() => {
          buttonElement.classList.remove('added');
        }, 1000);
      }

      // Add to cart via cart manager
      if (window.cartManager) {
        const success = await window.cartManager.addItem(itemId, quantity);
        
        if (success) {
          // Close modal if open
          this.closeItemModal();
          return true;
        }
      }

      return false;
    } catch (error) {
      console.error('Error adding to cart:', error);
      return false;
    }
  }

  // Render recommendations
  renderRecommendations(recommendations) {
    const recommendationsGrid = document.getElementById('recommendations-grid');
    if (!recommendationsGrid || !recommendations.length) return;

    recommendationsGrid.innerHTML = recommendations.map(item => `
      <div class="recommendation-item" data-id="${item.id}">
        <img src="${this.getImageUrl(item)}" 
             alt="${item.name}" 
             class="recommendation-image"
             loading="lazy"
             onerror="this.src='/static/images/placeholder.jpg'">
        <div class="recommendation-content">
          <h5 class="recommendation-name">${item.name}</h5>
          <p class="recommendation-price">${this.formatPrice(item.price)}</p>
          <button class="recommendation-add-btn" data-id="${item.id}">+</button>
        </div>
      </div>
    `).join('');

    // Add event listeners
    recommendationsGrid.querySelectorAll('.recommendation-item').forEach(item => {
      item.addEventListener('click', (e) => {
        if (!e.target.classList.contains('recommendation-add-btn')) {
          const itemId = item.dataset.id;
          this.openItemModal(itemId);
        }
      });
    });

    recommendationsGrid.querySelectorAll('.recommendation-add-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const itemId = btn.dataset.id;
        this.addToCart(itemId, btn);
      });
    });
  }

  // Utility methods
  getCategoryIcon(categoryId) {
    const icons = {
      all: '🍽️',
      pizza: '🍕',
      pasta: '🍝',
      salads: '🥗',
      drinks: '🥤',
      desserts: '🍰',
      burgers: '🍔',
      sandwiches: '🥪',
      soups: '🍲'
    };
    
    return icons[categoryId] || '🍽️';
  }

  getCategoryCount(categoryId) {
    if (categoryId === 'all') return this.menuItems.length;
    
    return this.menuItems.filter(item => 
      item.category_id?.toLowerCase() === categoryId.toLowerCase()
    ).length;
  }

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

  scrollToMenu() {
    const menuSection = document.getElementById('menu-section');
    if (menuSection) {
      menuSection.scrollIntoView({ behavior: 'smooth' });
    }
  }

  showError(message) {
    if (window.restaurantApp) {
      window.restaurantApp.showToast(message, 'error');
    }
  }
}

// Initialize menu manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.menuManager = new MenuManager();
  window.menuManager.init();
});

export default MenuManager;
