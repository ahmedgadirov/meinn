// Restaurant App - Main Application Logic
// Handles initialization, loading, search, language switching, and core functionality

class RestaurantApp {
  constructor() {
    this.isLoading = false;
    this.currentLanguage = 'az';
    this.searchTimeout = null;
    this.loadingScreen = null;
    this.translations = {
      az: {
        loading: 'Menyunuz hazırlanır...',
        searchPlaceholder: 'Yemək axtarın...',
        noResults: 'Heç bir məhsul tapılmadı',
        addedToCart: 'Səbətə əlavə edildi',
        itemUnavailable: 'Məhsul müvəqqəti mövcud deyil',
        networkError: 'Şəbəkə xətası. Yenidən cəhd edin.',
        cartEmpty: 'Səbətiniz boşdur',
        orderPlaced: 'Sifariş uğurla yerləşdirildi!',
        heroTitle: 'Orijinalın dadını çəkin',
        heroSubtitle: 'Təzə inqrediyentlər, ənənəvi reseptlər, qapınıza çatdırılır',
        exploreMenu: 'Menyunu kəşf edin',
        browseCategories: 'Kateqoriyalara baxın',
        ourMenu: 'Bizim menyu',
        allItems: 'Bütün məhsullar',
        recommendedForYou: 'Sizin üçün tövsiyə edilir',
        yourOrder: 'Sifarişiniz',
        cartEmptyTitle: 'Səbətiniz boşdur',
        cartEmptyDesc: 'Başlamaq üçün ləzzətli məhsullar əlavə edin',
        subtotal: 'Ara cəm:',
        delivery: 'Çatdırılma:',
        total: 'Cəmi:',
        free: 'Pulsuz',
        proceedToCheckout: 'Ödənişə keçin',
        completeYourOrder: 'Sifarişinizi tamamlayın',
        menu: 'Menyu',
        favorites: 'Sevimlilər',
        orders: 'Sifarişlər',
        profile: 'Profil'
      },
      en: {
        loading: 'Preparing your menu...',
        searchPlaceholder: 'Search for food...',
        noResults: 'No items found',
        addedToCart: 'Added to cart',
        itemUnavailable: 'Item temporarily unavailable',
        networkError: 'Network error. Please try again.',
        cartEmpty: 'Your cart is empty',
        orderPlaced: 'Order placed successfully!',
        heroTitle: 'Taste the Authentic',
        heroSubtitle: 'Fresh ingredients, traditional recipes, delivered to your door',
        exploreMenu: 'Explore Menu',
        browseCategories: 'Browse Categories',
        ourMenu: 'Our Menu',
        allItems: 'All Items',
        recommendedForYou: 'Recommended for You',
        yourOrder: 'Your Order',
        cartEmptyTitle: 'Your cart is empty',
        cartEmptyDesc: 'Add some delicious items to get started',
        subtotal: 'Subtotal:',
        delivery: 'Delivery:',
        total: 'Total:',
        free: 'Free',
        proceedToCheckout: 'Proceed to Checkout',
        completeYourOrder: 'Complete Your Order',
        menu: 'Menu',
        favorites: 'Favorites',
        orders: 'Orders',
        profile: 'Profile'
      },
      ru: {
        loading: 'Подготовка меню...',
        searchPlaceholder: 'Поиск еды...',
        noResults: 'Ничего не найдено',
        addedToCart: 'Добавлено в корзину',
        itemUnavailable: 'Товар временно недоступен',
        networkError: 'Ошибка сети. Попробуйте снова.',
        cartEmpty: 'Ваша корзина пуста',
        orderPlaced: 'Заказ успешно размещен!',
        heroTitle: 'Почувствуйте подлинность',
        heroSubtitle: 'Свежие ингредиенты, традиционные рецепты с доставкой к вашей двери',
        exploreMenu: 'Изучить меню',
        browseCategories: 'Просмотр категорий',
        ourMenu: 'Наше меню',
        allItems: 'Все блюда',
        recommendedForYou: 'Рекомендуется для вас',
        yourOrder: 'Ваш заказ',
        cartEmptyTitle: 'Ваша корзина пуста',
        cartEmptyDesc: 'Добавьте вкусные блюда, чтобы начать',
        subtotal: 'Промежуточный итог:',
        delivery: 'Доставка:',
        total: 'Итого:',
        free: 'Бесплатно',
        proceedToCheckout: 'Перейти к оформлению',
        completeYourOrder: 'Завершите свой заказ',
        menu: 'Меню',
        favorites: 'Избранное',
        orders: 'Заказы',
        profile: 'Профиль'
      },
      tr: {
        loading: 'Menünüz hazırlanıyor...',
        searchPlaceholder: 'Yemek ara...',
        noResults: 'Hiçbir öğe bulunamadı',
        addedToCart: 'Sepete eklendi',
        itemUnavailable: 'Ürün geçici olarak mevcut değil',
        networkError: 'Ağ hatası. Lütfen tekrar deneyin.',
        cartEmpty: 'Sepetiniz boş',
        orderPlaced: 'Sipariş başarıyla verildi!',
        heroTitle: 'Otantik tadı keşfedin',
        heroSubtitle: 'Taze malzemeler, geleneksel tarifler, kapınıza kadar',
        exploreMenu: 'Menüyü keşfet',
        browseCategories: 'Kategorilere göz at',
        ourMenu: 'Menümüz',
        allItems: 'Tüm ürünler',
        recommendedForYou: 'Sizin için önerilen',
        yourOrder: 'Siparişiniz',
        cartEmptyTitle: 'Sepetiniz boş',
        cartEmptyDesc: 'Başlamak için lezzetli ürünler ekleyin',
        subtotal: 'Ara toplam:',
        delivery: 'Teslimat:',
        total: 'Toplam:',
        free: 'Ücretsiz',
        proceedToCheckout: 'Ödemeye geç',
        completeYourOrder: 'Siparişinizi tamamlayın',
        menu: 'Menü',
        favorites: 'Favoriler',
        orders: 'Siparişler',
        profile: 'Profil'
      },
      ar: {
        loading: 'جاري تحضير قائمتك...',
        searchPlaceholder: 'البحث عن الطعام...',
        noResults: 'لم يتم العثور على عناصر',
        addedToCart: 'تمت الإضافة إلى السلة',
        itemUnavailable: 'العنصر غير متوفر مؤقتًا',
        networkError: 'خطأ في الشبكة. يرجى المحاولة مرة أخرى.',
        cartEmpty: 'سلتك فارغة',
        orderPlaced: 'تم تقديم الطلب بنجاح!',
        heroTitle: 'اكتشف النكهة الأصيلة',
        heroSubtitle: 'مكونات طازجة، وصفات تقليدية، توصيل إلى بابك',
        exploreMenu: 'استكشف القائمة',
        browseCategories: 'تصفح الفئات',
        ourMenu: 'قائمتنا',
        allItems: 'جميع العناصر',
        recommendedForYou: 'موصى به لك',
        yourOrder: 'طلبك',
        cartEmptyTitle: 'سلتك فارغة',
        cartEmptyDesc: 'أضف بعض العناصر اللذيذة للبدء',
        subtotal: 'المجموع الفرعي:',
        delivery: 'التوصيل:',
        total: 'المجموع:',
        free: 'مجاني',
        proceedToCheckout: 'المتابعة للدفع',
        completeYourOrder: 'أكمل طلبك',
        menu: 'القائمة',
        favorites: 'المفضلة',
        orders: 'الطلبات',
        profile: 'الملف الشخصي'
      },
      hi: {
        loading: 'आपका मेनू तैयार कर रहे हैं...',
        searchPlaceholder: 'खाना खोजें...',
        noResults: 'कोई आइटम नहीं मिला',
        addedToCart: 'कार्ट में जोड़ा गया',
        itemUnavailable: 'आइटम अस्थायी रूप से अनुपलब्ध',
        networkError: 'नेटवर्क त्रुटि। कृपया फिर से कोशिश करें।',
        cartEmpty: 'आपका कार्ट खाली है',
        orderPlaced: 'ऑर्डर सफलतापूर्वक दिया गया!',
        heroTitle: 'प्रामाणिक स्वाद चखें',
        heroSubtitle: 'ताज़ी सामग्री, पारंपरिक व्यंजन, आपके दरवाज़े तक',
        exploreMenu: 'मेनू देखें',
        browseCategories: 'श्रेणियां ब्राउज़ करें',
        ourMenu: 'हमारा मेनू',
        allItems: 'सभी आइटम',
        recommendedForYou: 'आपके लिए सुझाया गया',
        yourOrder: 'आपका ऑर्डर',
        cartEmptyTitle: 'आपका कार्ट खाली है',
        cartEmptyDesc: 'शुरू करने के लिए कुछ स्वादिष्ट आइटम जोड़ें',
        subtotal: 'उप-योग:',
        delivery: 'डिलीवरी:',
        total: 'कुल:',
        free: 'मुफ़्त',
        proceedToCheckout: 'चेकआउट पर जाएं',
        completeYourOrder: 'अपना ऑर्डर पूरा करें',
        menu: 'मेनू',
        favorites: 'पसंदीदा',
        orders: 'ऑर्डर',
        profile: 'प्रोफ़ाइल'
      },
      fr: {
        loading: 'Préparation de votre menu...',
        searchPlaceholder: 'Rechercher de la nourriture...',
        noResults: 'Aucun élément trouvé',
        addedToCart: 'Ajouté au panier',
        itemUnavailable: 'Article temporairement indisponible',
        networkError: 'Erreur réseau. Veuillez réessayer.',
        cartEmpty: 'Votre panier est vide',
        orderPlaced: 'Commande passée avec succès!',
        heroTitle: 'Goûtez l\'authentique',
        heroSubtitle: 'Ingrédients frais, recettes traditionnelles, livrés à votre porte',
        exploreMenu: 'Explorer le menu',
        browseCategories: 'Parcourir les catégories',
        ourMenu: 'Notre menu',
        allItems: 'Tous les articles',
        recommendedForYou: 'Recommandé pour vous',
        yourOrder: 'Votre commande',
        cartEmptyTitle: 'Votre panier est vide',
        cartEmptyDesc: 'Ajoutez de délicieux articles pour commencer',
        subtotal: 'Sous-total:',
        delivery: 'Livraison:',
        total: 'Total:',
        free: 'Gratuit',
        proceedToCheckout: 'Procéder au paiement',
        completeYourOrder: 'Complétez votre commande',
        menu: 'Menu',
        favorites: 'Favoris',
        orders: 'Commandes',
        profile: 'Profil'
      },
      it: {
        loading: 'Preparazione del menu...',
        searchPlaceholder: 'Cerca cibo...',
        noResults: 'Nessun elemento trovato',
        addedToCart: 'Aggiunto al carrello',
        itemUnavailable: 'Articolo temporaneamente non disponibile',
        networkError: 'Errore di rete. Riprova.',
        cartEmpty: 'Il tuo carrello è vuoto',
        orderPlaced: 'Ordine effettuato con successo!',
        heroTitle: 'Assapora l\'autentico',
        heroSubtitle: 'Ingredienti freschi, ricette tradizionali, consegnati alla tua porta',
        exploreMenu: 'Esplora il menu',
        browseCategories: 'Sfoglia le categorie',
        ourMenu: 'Il nostro menu',
        allItems: 'Tutti gli articoli',
        recommendedForYou: 'Consigliato per te',
        yourOrder: 'Il tuo ordine',
        cartEmptyTitle: 'Il tuo carrello è vuoto',
        cartEmptyDesc: 'Aggiungi alcuni articoli deliziosi per iniziare',
        subtotal: 'Subtotale:',
        delivery: 'Consegna:',
        total: 'Totale:',
        free: 'Gratis',
        proceedToCheckout: 'Procedi al checkout',
        completeYourOrder: 'Completa il tuo ordine',
        menu: 'Menu',
        favorites: 'Preferiti',
        orders: 'Ordini',
        profile: 'Profilo'
      }
    };
  }

  // Initialize the application
  async init() {
    try {
      this.showLoadingScreen();
      await this.loadInitialData();
      this.setupEventListeners();
      this.setupSearch();
      this.setupLanguageSelector();
      this.setupBottomNavigation();
      this.hideLoadingScreen();
      
      console.log('Restaurant app initialized successfully');
    } catch (error) {
      console.error('Failed to initialize restaurant app:', error);
      this.showToast('Failed to load the application. Please refresh the page.', 'error');
      this.hideLoadingScreen();
    }
  }

  // Show loading screen
  showLoadingScreen() {
    this.loadingScreen = document.getElementById('loading-screen');
    if (this.loadingScreen) {
      this.loadingScreen.style.display = 'flex';
      const loadingText = this.loadingScreen.querySelector('p');
      if (loadingText) {
        loadingText.textContent = this.getTranslation('loading');
      }
    }
  }

  // Hide loading screen
  hideLoadingScreen() {
    if (this.loadingScreen) {
      setTimeout(() => {
        this.loadingScreen.style.display = 'none';
      }, 500);
    }
  }

  // Load initial data
  async loadInitialData() {
    try {
      // Load categories and initial menu items
      const [categories, menuItems] = await Promise.all([
        this.fetchCategories(),
        this.fetchMenuItems()
      ]);

      // Initialize menu and categories
      if (window.menuManager) {
        window.menuManager.setCategories(categories);
        window.menuManager.setMenuItems(menuItems);
        window.menuManager.renderCategories();
        window.menuManager.renderMenuItems();
      }

      // Load recommendations
      this.loadRecommendations();

    } catch (error) {
      console.error('Error loading initial data:', error);
      throw error;
    }
  }

  // Fetch categories from API
  async fetchCategories() {
    try {
      const response = await fetch(`/api/menu/categories?language=${this.currentLanguage}`);
      const data = await response.json();
      
      if (data.success) {
        return data.categories || [];
      } else {
        console.warn('Failed to fetch categories:', data.error);
        return this.getFallbackCategories();
      }
    } catch (error) {
      console.error('Error fetching categories:', error);
      return this.getFallbackCategories();
    }
  }

  // Fetch menu items from API
  async fetchMenuItems(category = null) {
    try {
      let url = `/api/menu/items?language=${this.currentLanguage}`;
      if (category) {
        url += `&category=${category}`;
      }
      const response = await fetch(url);
      const data = await response.json();
      
      if (data.success) {
        return data.items || [];
      } else {
        console.warn('Failed to fetch menu items:', data.error);
        return this.getFallbackMenuItems();
      }
    } catch (error) {
      console.error('Error fetching menu items:', error);
      return this.getFallbackMenuItems();
    }
  }

  // Get fallback categories if API fails
  getFallbackCategories() {
    return [
      { id: 'pizza', name: '🍕 Pizza', description: 'Delicious Italian pizzas' },
      { id: 'pasta', name: '🍝 Pasta', description: 'Fresh pasta dishes' },
      { id: 'salads', name: '🥗 Salads', description: 'Healthy and fresh salads' },
      { id: 'drinks', name: '🥤 Drinks', description: 'Refreshing beverages' },
      { id: 'desserts', name: '🍰 Desserts', description: 'Sweet treats' }
    ];
  }

  // Get fallback menu items if API fails
  getFallbackMenuItems() {
    return [
      {
        id: 'pizza-margherita',
        name: 'Margherita Pizza',
        description: 'Classic pizza with tomato sauce, mozzarella, and fresh basil',
        category: 'Pizza',
        price: 12.99,
        image_url: '/static/images/placeholder.jpg',
        available: true,
        popular: true,
        allergens: ['dairy', 'gluten'],
        nutrition: { calories: 850, protein: 35, carbs: 100, fat: 25 }
      },
      {
        id: 'pasta-carbonara',
        name: 'Spaghetti Carbonara',
        description: 'Creamy pasta with eggs, pancetta, and parmesan cheese',
        category: 'Pasta',
        price: 13.99,
        image_url: '/static/images/placeholder.jpg',
        available: true,
        popular: false,
        allergens: ['dairy', 'gluten', 'eggs'],
        nutrition: { calories: 650, protein: 28, carbs: 75, fat: 32 }
      }
    ];
  }

  // Setup event listeners
  setupEventListeners() {
    // Search button
    const searchBtn = document.getElementById('search-btn');
    const searchClose = document.getElementById('search-close');
    const searchBar = document.getElementById('search-bar');

    if (searchBtn && searchBar) {
      searchBtn.addEventListener('click', () => this.toggleSearch());
    }

    if (searchClose && searchBar) {
      searchClose.addEventListener('click', () => this.closeSearch());
    }

    // Cart toggle is handled by cart-modern.js to avoid conflicts

    // Modal close handlers
    document.addEventListener('click', (e) => {
      if (e.target.classList.contains('modal-overlay')) {
        this.closeAllModals();
      }
    });

    // Close modals with escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        this.closeAllModals();
      }
    });

    // Prevent zoom on double tap for iOS
    let lastTouchEnd = 0;
    document.addEventListener('touchend', (e) => {
      const now = new Date().getTime();
      if (now - lastTouchEnd <= 300) {
        e.preventDefault();
      }
      lastTouchEnd = now;
    }, false);
  }

  // Setup search functionality
  setupSearch() {
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');

    if (!searchInput) return;

    // Update placeholder text
    searchInput.placeholder = this.getTranslation('searchPlaceholder');

    searchInput.addEventListener('input', (e) => {
      const query = e.target.value.trim();
      
      // Clear previous timeout
      if (this.searchTimeout) {
        clearTimeout(this.searchTimeout);
      }

      // Debounce search
      this.searchTimeout = setTimeout(() => {
        this.performSearch(query);
      }, 300);
    });

    searchInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        const query = e.target.value.trim();
        this.performSearch(query);
      }
    });
  }

  // Perform search
  async performSearch(query) {
    const searchResults = document.getElementById('search-results');
    if (!searchResults) return;

    if (!query) {
      searchResults.innerHTML = '';
      return;
    }

    try {
      const response = await fetch(`/api/menu/items?search=${encodeURIComponent(query)}`);
      const data = await response.json();

      if (data.success && data.items.length > 0) {
        this.renderSearchResults(data.items);
      } else {
        searchResults.innerHTML = `
          <div class="search-no-results">
            <p>${this.getTranslation('noResults')}</p>
          </div>
        `;
      }
    } catch (error) {
      console.error('Search error:', error);
      searchResults.innerHTML = `
        <div class="search-error">
          <p>${this.getTranslation('networkError')}</p>
        </div>
      `;
    }
  }

  // Render search results
  renderSearchResults(items) {
    const searchResults = document.getElementById('search-results');
    if (!searchResults) return;

    searchResults.innerHTML = items.map(item => `
      <div class="search-result-item" data-id="${item.id}">
        <img src="${this.getImageUrl(item)}" alt="${item.name}" class="search-result-image">
        <div class="search-result-info">
          <h4 class="search-result-name">${item.name}</h4>
          <p class="search-result-price">${this.formatPrice(item.price)}</p>
        </div>
        <button class="search-result-add" data-id="${item.id}">+</button>
      </div>
    `).join('');

    // Add event listeners to search results
    searchResults.querySelectorAll('.search-result-item').forEach(item => {
      item.addEventListener('click', (e) => {
        if (!e.target.classList.contains('search-result-add')) {
          const itemId = item.dataset.id;
          this.openItemModal(itemId);
        }
      });
    });

    searchResults.querySelectorAll('.search-result-add').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const itemId = btn.dataset.id;
        this.addToCart(itemId);
      });
    });
  }

  // Toggle search bar
  toggleSearch() {
    const searchBar = document.getElementById('search-bar');
    if (searchBar) {
      const isActive = searchBar.classList.contains('active');
      if (isActive) {
        this.closeSearch();
      } else {
        searchBar.classList.add('active');
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
          searchInput.focus();
        }
      }
    }
  }

  // Close search bar
  closeSearch() {
    const searchBar = document.getElementById('search-bar');
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');

    if (searchBar) {
      searchBar.classList.remove('active');
    }
    
    if (searchInput) {
      searchInput.value = '';
    }
    
    if (searchResults) {
      searchResults.innerHTML = '';
    }
  }

  // Setup language selector
  setupLanguageSelector() {
    const languageSelect = document.getElementById('language-select');
    if (!languageSelect) return;

    // Set initial language
    const savedLanguage = localStorage.getItem('restaurant-language') || 'az';
    this.currentLanguage = savedLanguage;
    languageSelect.value = savedLanguage;

    languageSelect.addEventListener('change', (e) => {
      this.switchLanguage(e.target.value);
    });
  }

  // Switch language
  switchLanguage(language) {
    this.currentLanguage = language;
    localStorage.setItem('restaurant-language', language);
    
    // Update document language
    document.documentElement.lang = language;
    
    // Update search placeholder
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
      searchInput.placeholder = this.getTranslation('searchPlaceholder');
    }

    // Update any dynamic text
    this.updateUIText();
    
    // Reload categories and menu items for new language
    this.loadInitialData();

    // Notify other components
    window.dispatchEvent(new CustomEvent('languageChanged', { detail: { language } }));
  }

  // Update UI text based on current language
  updateUIText() {
    // Update any static text elements that need translation
    const elementsToUpdate = {
      '[data-translate="loading"]': 'loading',
      '[data-translate="search-placeholder"]': 'searchPlaceholder',
      '[data-translate="no-results"]': 'noResults'
    };

    Object.entries(elementsToUpdate).forEach(([selector, key]) => {
      const elements = document.querySelectorAll(selector);
      elements.forEach(el => {
        if (el.tagName === 'INPUT') {
          el.placeholder = this.getTranslation(key);
        } else {
          el.textContent = this.getTranslation(key);
        }
      });
    });
  }

  // Setup bottom navigation
  setupBottomNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        const section = item.dataset.section;
        this.handleBottomNavClick(section, item);
      });
    });
  }

  // Handle bottom navigation clicks
  handleBottomNavClick(section, navItem) {
    // Remove active class from all nav items
    document.querySelectorAll('.nav-item').forEach(item => {
      item.classList.remove('active');
    });
    
    // Add active class to clicked item
    navItem.classList.add('active');

    switch (section) {
      case 'menu':
        this.scrollToSection('menu-section');
        break;
      case 'favorites':
        this.showToast('Favorites feature coming soon!');
        break;
      case 'orders':
        this.showToast('Order history coming soon!');
        break;
      case 'profile':
        this.showToast('Profile feature coming soon!');
        break;
    }
  }

  // Scroll to section
  scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
      section.scrollIntoView({ behavior: 'smooth' });
    }
  }

  // Load recommendations
  async loadRecommendations() {
    try {
      const response = await fetch('/api/menu/recommendations');
      const data = await response.json();
      
      if (data.success && window.menuManager) {
        window.menuManager.renderRecommendations(data.recommendations);
      }
    } catch (error) {
      console.error('Error loading recommendations:', error);
    }
  }

  // Add item to cart
  async addToCart(itemId) {
    if (window.cartManager) {
      const success = await window.cartManager.addItem(itemId);
      if (success) {
        this.showToast(this.getTranslation('addedToCart'), 'success');
        // Log add to cart action for analytics
        this.logUserAction('add_to_cart', itemId);
      } else {
        this.showToast(this.getTranslation('itemUnavailable'), 'error');
      }
    }
  }

  // Utility: Get or generate persistent user_id
  getUserId() {
    let userId = localStorage.getItem('restaurant-user-id');
    if (!userId) {
      userId = 'user-' + Math.random().toString(36).substr(2, 12) + '-' + Date.now();
      localStorage.setItem('restaurant-user-id', userId);
    }
    return userId;
  }

  // Utility: Log user action to backend analytics
  async logUserAction(actionType, itemId) {
    const userId = this.getUserId();
    try {
      await fetch('/api/analytics/user_action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          action_type: actionType,
          item_id: itemId,
          timestamp: Math.floor(Date.now() / 1000)
        })
      });
    } catch (error) {
      // Silently fail, do not interrupt user experience
      // Optionally, could log to console for debugging
      // console.error('Failed to log user action:', error);
    }
  }

  // Open item modal
  openItemModal(itemId) {
    if (window.menuManager) {
      window.menuManager.openItemModal(itemId);
    }
    // Log item view for analytics
    this.logUserAction('view', itemId);
  }

  // Close all modals
  closeAllModals() {
    const modals = document.querySelectorAll('.modal-overlay');
    modals.forEach(modal => {
      modal.classList.remove('active');
    });
    
    // Close search if open
    this.closeSearch();
  }

  // Utility: Get translation
  getTranslation(key) {
    return this.translations[this.currentLanguage]?.[key] || this.translations['en'][key] || key;
  }

  // Utility: Format price
  formatPrice(price) {
    const formatter = new Intl.NumberFormat(this.currentLanguage === 'az' ? 'az-AZ' : 'en-US', {
      style: 'currency',
      currency: this.currentLanguage === 'az' ? 'AZN' : 'USD',
      minimumFractionDigits: 2
    });
    return formatter.format(price);
  }

  // Utility: Get image URL with fallback
  getImageUrl(item) {
    return item.image_url && item.image_url !== '/static/images/placeholder.svg' 
      ? item.image_url 
      : '/static/images/placeholder.jpg';
  }

  // Show toast notification
  showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
      <div class="toast-content">
        <span class="toast-message">${message}</span>
        <button class="toast-close" onclick="this.parentElement.parentElement.remove()">×</button>
      </div>
    `;

    toastContainer.appendChild(toast);

    // Auto remove after 3 seconds
    setTimeout(() => {
      if (toast.parentElement) {
        toast.remove();
      }
    }, 3000);
  }

  // Handle network errors gracefully
  handleNetworkError(error) {
    console.error('Network error:', error);
    this.showToast(this.getTranslation('networkError'), 'error');
  }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', async () => {
  try {
    window.restaurantApp = new RestaurantApp();
    await window.restaurantApp.init();
  } catch (error) {
    console.error('Failed to initialize restaurant app:', error);
  }
});

// Global error handler
window.addEventListener('error', (event) => {
  console.error('Global error:', event.error);
  if (window.restaurantApp) {
    window.restaurantApp.showToast('An unexpected error occurred', 'error');
  }
});

// Global unhandled promise rejection handler
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
  if (window.restaurantApp) {
    window.restaurantApp.handleNetworkError(event.reason);
  }
});

export default RestaurantApp;
