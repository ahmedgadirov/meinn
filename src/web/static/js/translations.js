// Translation service for static content
// Handles dynamic translation of HTML elements based on selected language

class TranslationService {
  constructor() {
    this.currentLanguage = 'az';
    this.translations = {
      az: {
        // Page title and meta
        pageTitle: 'Pizza Inn - Ləzzətli Yemək Çatdırılması',
        restaurantTagline: 'Orijinal İtalyan Mətbəxi',
        
        // Hero section
        heroTitle: 'Orijinalın dadını çəkin',
        heroSubtitle: 'Təzə inqrediyentlər, ənənəvi reseptlər, qapınıza çatdırılır',
        exploreMenu: 'Menyunu kəşf edin',
        
        // Sections
        browseCategories: 'Kateqoriyalara baxın',
        ourMenu: 'Bizim menyu',
        allItems: 'Bütün məhsullar',
        recommendedForYou: 'Sizin üçün tövsiyə edilir',
        
        // Cart
        yourOrder: 'Sifarişiniz',
        cartEmpty: 'Səbətiniz boşdur',
        cartEmptyDesc: 'Başlamaq üçün ləzzətli məhsullar əlavə edin',
        subtotal: 'Ara cəm:',
        delivery: 'Çatdırılma:',
        total: 'Cəmi:',
        free: 'Pulsuz',
        proceedToCheckout: 'Ödənişə keçin',
        
        // Modal
        completeYourOrder: 'Sifarişinizi tamamlayın',
        close: 'Bağla',
        
        // Navigation
        menu: 'Menyu',
        favorites: 'Sevimlilər',
        orders: 'Sifarişlər',
        profile: 'Profil',
        
        // Loading and messages
        preparingMenu: 'Menyunuz hazırlanır...',
        loadingOptions: 'Ləzzətli variantlar yüklənir...',
        searchPlaceholder: 'Yemək axtarın...',
        searchMenu: 'Menyuda axtarış',
        closeSearch: 'Axtarışı bağla',
        viewCart: 'Səbətə bax',
        gridView: 'Şəbəkə görünüşü',
        listView: 'Siyahı görünüşü',
        
        // Menu badges and labels
        popular: 'Məşhur',
        new: 'Yeni',
        spicy: 'Acı',
        unavailable: 'Mövcud deyil',
        addToCart: 'Səbətə əlavə et',
        noItemsFound: 'Heç bir məhsul tapılmadı',
        tryDifferentCategory: 'Başqa kateqoriya və ya axtarış sözü sınayın',
        
        // Admin panel
        addNewMenuItem: 'Yeni menyu elementi əlavə et',
        editMenuItem: 'Menyu elementini redaktə et',
        addNewCategory: 'Yeni kateqoriya əlavə et',
        editCategory: 'Kateqoriyani redaktə et',
        multiLanguage: 'Çoxdilli',
        category: 'Kateqoriya',
        price: 'Qiymət',
        imageUrl: 'Şəkil URL-i',
        available: 'Mövcuddur',
        popularItem: 'Məşhur element',
        save: 'Saxla',
        update: 'Yenilə',
        cancel: 'Ləğv et',
        delete: 'Sil',
        edit: 'Redaktə et',
        confirmDelete: 'Bu elementi silmək istədiyinizə əminsiniz? Bu əməliyyat geri qaytarıla bilməz.',
        itemAddedSuccessfully: 'Element uğurla əlavə edildi!',
        itemUpdatedSuccessfully: 'Element uğurla yeniləndi!',
        itemDeletedSuccessfully: 'Element uğurla silindi!',
        categoryAddedSuccessfully: 'Kateqoriya uğurla əlavə edildi!',
        categoryUpdatedSuccessfully: 'Kateqoriya uğurla yeniləndi!',
        categoryDeletedSuccessfully: 'Kateqoriya uğurla silindi!',
        pleaseProvideEnglishName: 'Zəhmət olmasa ən azı ingilis dilində ad verin',
        pleaseFillRequiredFields: 'Zəhmət olmasa tələb olunan sahələri doldurun',
        errorSaving: 'Saxlama zamanı xəta',
        errorUpdating: 'Yeniləmə zamanı xəta',
        errorDeleting: 'Silmə zamanı xəta',
        errorLoading: 'Yükləmə zamanı xəta'
      },
      en: {
        // Page title and meta
        pageTitle: 'Pizza Inn - Delicious Food Delivered',
        restaurantTagline: 'Authentic Italian Cuisine',
        
        // Hero section
        heroTitle: 'Taste the Authentic',
        heroSubtitle: 'Fresh ingredients, traditional recipes, delivered to your door',
        exploreMenu: 'Explore Menu',
        
        // Sections
        browseCategories: 'Browse Categories',
        ourMenu: 'Our Menu',
        allItems: 'All Items',
        recommendedForYou: 'Recommended for You',
        
        // Cart
        yourOrder: 'Your Order',
        cartEmpty: 'Your cart is empty',
        cartEmptyDesc: 'Add some delicious items to get started',
        subtotal: 'Subtotal:',
        delivery: 'Delivery:',
        total: 'Total:',
        free: 'Free',
        proceedToCheckout: 'Proceed to Checkout',
        
        // Modal
        completeYourOrder: 'Complete Your Order',
        close: 'Close',
        
        // Navigation
        menu: 'Menu',
        favorites: 'Favorites',
        orders: 'Orders',
        profile: 'Profile',
        
        // Loading and messages
        preparingMenu: 'Preparing your menu...',
        loadingOptions: 'Loading delicious options...',
        searchPlaceholder: 'Search for food...',
        searchMenu: 'Search menu',
        closeSearch: 'Close search',
        viewCart: 'View cart',
        gridView: 'Grid view',
        listView: 'List view',
        
        // Menu badges and labels
        popular: 'Popular',
        new: 'New',
        spicy: 'Spicy',
        unavailable: 'Unavailable',
        addToCart: 'Add to Cart',
        noItemsFound: 'No items found',
        tryDifferentCategory: 'Try selecting a different category or search term',
        
        // Admin panel
        addNewMenuItem: 'Add New Menu Item',
        editMenuItem: 'Edit Menu Item',
        addNewCategory: 'Add New Category',
        editCategory: 'Edit Category',
        multiLanguage: 'Multi-language',
        category: 'Category',
        price: 'Price',
        imageUrl: 'Image URL',
        available: 'Available',
        popularItem: 'Popular Item',
        save: 'Save',
        update: 'Update',
        cancel: 'Cancel',
        delete: 'Delete',
        edit: 'Edit',
        confirmDelete: 'Are you sure you want to delete this item? This action cannot be undone.',
        itemAddedSuccessfully: 'Item added successfully!',
        itemUpdatedSuccessfully: 'Item updated successfully!',
        itemDeletedSuccessfully: 'Item deleted successfully!',
        categoryAddedSuccessfully: 'Category added successfully!',
        categoryUpdatedSuccessfully: 'Category updated successfully!',
        categoryDeletedSuccessfully: 'Category deleted successfully!',
        pleaseProvideEnglishName: 'Please provide at least an English name',
        pleaseFillRequiredFields: 'Please fill in all required fields',
        errorSaving: 'Error saving',
        errorUpdating: 'Error updating',
        errorDeleting: 'Error deleting',
        errorLoading: 'Error loading'
      },
      ru: {
        // Page title and meta
        pageTitle: 'Pizza Inn - Доставка вкусной еды',
        restaurantTagline: 'Подлинная итальянская кухня',
        
        // Hero section
        heroTitle: 'Почувствуйте подлинность',
        heroSubtitle: 'Свежие ингредиенты, традиционные рецепты с доставкой к вашей двери',
        exploreMenu: 'Изучить меню',
        
        // Sections
        browseCategories: 'Просмотр категорий',
        ourMenu: 'Наше меню',
        allItems: 'Все блюда',
        recommendedForYou: 'Рекомендуется для вас',
        
        // Cart
        yourOrder: 'Ваш заказ',
        cartEmpty: 'Ваша корзина пуста',
        cartEmptyDesc: 'Добавьте вкусные блюда, чтобы начать',
        subtotal: 'Промежуточный итог:',
        delivery: 'Доставка:',
        total: 'Итого:',
        free: 'Бесплатно',
        proceedToCheckout: 'Перейти к оформлению',
        
        // Modal
        completeYourOrder: 'Завершите свой заказ',
        close: 'Закрыть',
        
        // Navigation
        menu: 'Меню',
        favorites: 'Избранное',
        orders: 'Заказы',
        profile: 'Профиль',
        
        // Loading and messages
        preparingMenu: 'Подготовка меню...',
        loadingOptions: 'Загрузка вкусных вариантов...',
        searchPlaceholder: 'Поиск еды...',
        searchMenu: 'Поиск в меню',
        closeSearch: 'Закрыть поиск',
        viewCart: 'Посмотреть корзину',
        gridView: 'Вид сетки',
        listView: 'Вид списка',
        
        // Menu badges and labels
        popular: 'Популярное',
        new: 'Новое',
        spicy: 'Острое',
        unavailable: 'Недоступно',
        addToCart: 'Добавить в корзину',
        noItemsFound: 'Ничего не найдено',
        tryDifferentCategory: 'Попробуйте выбрать другую категорию или поисковый запрос',
        
        // Admin panel
        addNewMenuItem: 'Добавить новый элемент меню',
        editMenuItem: 'Редактировать элемент меню',
        addNewCategory: 'Добавить новую категорию',
        editCategory: 'Редактировать категорию',
        multiLanguage: 'Многоязычный',
        category: 'Категория',
        price: 'Цена',
        imageUrl: 'URL изображения',
        available: 'Доступно',
        popularItem: 'Популярный элемент',
        save: 'Сохранить',
        update: 'Обновить',
        cancel: 'Отменить',
        delete: 'Удалить',
        edit: 'Редактировать',
        confirmDelete: 'Вы уверены, что хотите удалить этот элемент? Это действие нельзя отменить.',
        itemAddedSuccessfully: 'Элемент успешно добавлен!',
        itemUpdatedSuccessfully: 'Элемент успешно обновлен!',
        itemDeletedSuccessfully: 'Элемент успешно удален!',
        categoryAddedSuccessfully: 'Категория успешно добавлена!',
        categoryUpdatedSuccessfully: 'Категория успешно обновлена!',
        categoryDeletedSuccessfully: 'Категория успешно удалена!',
        pleaseProvideEnglishName: 'Пожалуйста, укажите хотя бы английское название',
        pleaseFillRequiredFields: 'Пожалуйста, заполните все обязательные поля',
        errorSaving: 'Ошибка сохранения',
        errorUpdating: 'Ошибка обновления',
        errorDeleting: 'Ошибка удаления',
        errorLoading: 'Ошибка загрузки'
      },
      tr: {
        // Page title and meta
        pageTitle: 'Pizza Inn - Lezzetli Yemek Teslimatı',
        restaurantTagline: 'Otantik İtalyan Mutfağı',
        
        // Hero section
        heroTitle: 'Otantik tadı keşfedin',
        heroSubtitle: 'Taze malzemeler, geleneksel tarifler, kapınıza kadar',
        exploreMenu: 'Menüyü keşfet',
        
        // Sections
        browseCategories: 'Kategorilere göz at',
        ourMenu: 'Menümüz',
        allItems: 'Tüm ürünler',
        recommendedForYou: 'Sizin için önerilen',
        
        // Cart
        yourOrder: 'Siparişiniz',
        cartEmpty: 'Sepetiniz boş',
        cartEmptyDesc: 'Başlamak için lezzetli ürünler ekleyin',
        subtotal: 'Ara toplam:',
        delivery: 'Teslimat:',
        total: 'Toplam:',
        free: 'Ücretsiz',
        proceedToCheckout: 'Ödemeye geç',
        
        // Modal
        completeYourOrder: 'Siparişinizi tamamlayın',
        close: 'Kapat',
        
        // Navigation
        menu: 'Menü',
        favorites: 'Favoriler',
        orders: 'Siparişler',
        profile: 'Profil',
        
        // Loading and messages
        preparingMenu: 'Menünüz hazırlanıyor...',
        loadingOptions: 'Lezzetli seçenekler yükleniyor...',
        searchPlaceholder: 'Yemek ara...',
        searchMenu: 'Menüde ara',
        closeSearch: 'Aramayı kapat',
        viewCart: 'Sepeti görüntüle',
        gridView: 'Izgara görünümü',
        listView: 'Liste görünümü',
        
        // Menu badges and labels
        popular: 'Popüler',
        new: 'Yeni',
        spicy: 'Acılı',
        unavailable: 'Mevcut değil',
        addToCart: 'Sepete ekle',
        noItemsFound: 'Hiçbir öğe bulunamadı',
        tryDifferentCategory: 'Farklı bir kategori veya arama terimi deneyin'
      },
      ar: {
        // Page title and meta
        pageTitle: 'بيتزا إن - توصيل الطعام اللذيذ',
        restaurantTagline: 'المطبخ الإيطالي الأصيل',
        
        // Hero section
        heroTitle: 'اكتشف النكهة الأصيلة',
        heroSubtitle: 'مكونات طازجة، وصفات تقليدية، توصيل إلى بابك',
        exploreMenu: 'استكشف القائمة',
        
        // Sections
        browseCategories: 'تصفح الفئات',
        ourMenu: 'قائمتنا',
        allItems: 'جميع العناصر',
        recommendedForYou: 'موصى به لك',
        
        // Cart
        yourOrder: 'طلبك',
        cartEmpty: 'سلتك فارغة',
        cartEmptyDesc: 'أضف بعض العناصر اللذيذة للبدء',
        subtotal: 'المجموع الفرعي:',
        delivery: 'التوصيل:',
        total: 'المجموع:',
        free: 'مجاني',
        proceedToCheckout: 'المتابعة للدفع',
        
        // Modal
        completeYourOrder: 'أكمل طلبك',
        close: 'إغلاق',
        
        // Navigation
        menu: 'القائمة',
        favorites: 'المفضلة',
        orders: 'الطلبات',
        profile: 'الملف الشخصي',
        
        // Loading and messages
        preparingMenu: 'جاري تحضير قائمتك...',
        loadingOptions: 'جاري تحميل الخيارات اللذيذة...',
        searchPlaceholder: 'البحث عن الطعام...',
        searchMenu: 'البحث في القائمة',
        closeSearch: 'إغلاق البحث',
        viewCart: 'عرض السلة',
        gridView: 'عرض الشبكة',
        listView: 'عرض القائمة',
        
        // Menu badges and labels
        popular: 'شائع',
        new: 'جديد',
        spicy: 'حار',
        unavailable: 'غير متوفر',
        addToCart: 'أضف إلى السلة',
        noItemsFound: 'لم يتم العثور على عناصر',
        tryDifferentCategory: 'جرب تحديد فئة مختلفة أو مصطلح بحث'
      },
      hi: {
        // Page title and meta
        pageTitle: 'पिज़्ज़ा इन - स्वादिष्ट खाना डिलीवरी',
        restaurantTagline: 'प्रामाणिक इतालवी व्यंजन',
        
        // Hero section
        heroTitle: 'प्रामाणिक स्वाद चखें',
        heroSubtitle: 'ताज़ी सामग्री, पारंपरिक व्यंजन, आपके दरवाज़े तक',
        exploreMenu: 'मेनू देखें',
        
        // Sections
        browseCategories: 'श्रेणियां ब्राउज़ करें',
        ourMenu: 'हमारा मेनू',
        allItems: 'सभी आइटम',
        recommendedForYou: 'आपके लिए सुझाया गया',
        
        // Cart
        yourOrder: 'आपका ऑर्डर',
        cartEmpty: 'आपका कार्ट खाली है',
        cartEmptyDesc: 'शुरू करने के लिए कुछ स्वादिष्ट आइटम जोड़ें',
        subtotal: 'उप-योग:',
        delivery: 'डिलीवरी:',
        total: 'कुल:',
        free: 'मुफ़्त',
        proceedToCheckout: 'चेकआउट पर जाएं',
        
        // Modal
        completeYourOrder: 'अपना ऑर्डर पूरा करें',
        close: 'बंद करें',
        
        // Navigation
        menu: 'मेनू',
        favorites: 'पसंदीदा',
        orders: 'ऑर्डर',
        profile: 'प्रोफ़ाइल',
        
        // Loading and messages
        preparingMenu: 'आपका मेनू तैयार कर रहे हैं...',
        loadingOptions: 'स्वादिष्ट विकल्प लोड कर रहे हैं...',
        searchPlaceholder: 'खाना खोजें...',
        searchMenu: 'मेनू में खोजें',
        closeSearch: 'खोज बंद करें',
        viewCart: 'कार्ट देखें',
        gridView: 'ग्रिड दृश्य',
        listView: 'सूची दृश्य',
        
        // Menu badges and labels
        popular: 'लोकप्रिय',
        new: 'नया',
        spicy: 'मसालेदार',
        unavailable: 'उपलब्ध नहीं',
        addToCart: 'कार्ट में जोड़ें',
        noItemsFound: 'कोई आइटम नहीं मिला',
        tryDifferentCategory: 'एक अलग श्रेणी या खोज शब्द चुनने का प्रयास करें'
      },
      fr: {
        // Page title and meta
        pageTitle: 'Pizza Inn - Livraison de nourriture délicieuse',
        restaurantTagline: 'Cuisine italienne authentique',
        
        // Hero section
        heroTitle: 'Goûtez l\'authentique',
        heroSubtitle: 'Ingrédients frais, recettes traditionnelles, livrés à votre porte',
        exploreMenu: 'Explorer le menu',
        
        // Sections
        browseCategories: 'Parcourir les catégories',
        ourMenu: 'Notre menu',
        allItems: 'Tous les articles',
        recommendedForYou: 'Recommandé pour vous',
        
        // Cart
        yourOrder: 'Votre commande',
        cartEmpty: 'Votre panier est vide',
        cartEmptyDesc: 'Ajoutez de délicieux articles pour commencer',
        subtotal: 'Sous-total:',
        delivery: 'Livraison:',
        total: 'Total:',
        free: 'Gratuit',
        proceedToCheckout: 'Procéder au paiement',
        
        // Modal
        completeYourOrder: 'Complétez votre commande',
        close: 'Fermer',
        
        // Navigation
        menu: 'Menu',
        favorites: 'Favoris',
        orders: 'Commandes',
        profile: 'Profil',
        
        // Loading and messages
        preparingMenu: 'Préparation de votre menu...',
        loadingOptions: 'Chargement d\'options délicieuses...',
        searchPlaceholder: 'Rechercher de la nourriture...',
        searchMenu: 'Rechercher dans le menu',
        closeSearch: 'Fermer la recherche',
        viewCart: 'Voir le panier',
        gridView: 'Vue en grille',
        listView: 'Vue en liste',
        
        // Menu badges and labels
        popular: 'Populaire',
        new: 'Nouveau',
        spicy: 'Épicé',
        unavailable: 'Indisponible',
        addToCart: 'Ajouter au panier',
        noItemsFound: 'Aucun article trouvé',
        tryDifferentCategory: 'Essayez de sélectionner une catégorie ou un terme de recherche différent'
      },
      it: {
        // Page title and meta
        pageTitle: 'Pizza Inn - Consegna di cibo delizioso',
        restaurantTagline: 'Autentica cucina italiana',
        
        // Hero section
        heroTitle: 'Assapora l\'autentico',
        heroSubtitle: 'Ingredienti freschi, ricette tradizionali, consegnati alla tua porta',
        exploreMenu: 'Esplora il menu',
        
        // Sections
        browseCategories: 'Sfoglia le categorie',
        ourMenu: 'Il nostro menu',
        allItems: 'Tutti gli articoli',
        recommendedForYou: 'Consigliato per te',
        
        // Cart
        yourOrder: 'Il tuo ordine',
        cartEmpty: 'Il tuo carrello è vuoto',
        cartEmptyDesc: 'Aggiungi alcuni articoli deliziosi per iniziare',
        subtotal: 'Subtotale:',
        delivery: 'Consegna:',
        total: 'Totale:',
        free: 'Gratis',
        proceedToCheckout: 'Procedi al checkout',
        
        // Modal
        completeYourOrder: 'Completa il tuo ordine',
        close: 'Chiudi',
        
        // Navigation
        menu: 'Menu',
        favorites: 'Preferiti',
        orders: 'Ordini',
        profile: 'Profilo',
        
        // Loading and messages
        preparingMenu: 'Preparazione del menu...',
        loadingOptions: 'Caricamento opzioni deliziose...',
        searchPlaceholder: 'Cerca cibo...',
        searchMenu: 'Cerca nel menu',
        closeSearch: 'Chiudi ricerca',
        viewCart: 'Visualizza carrello',
        gridView: 'Vista a griglia',
        listView: 'Vista elenco',
        
        // Menu badges and labels
        popular: 'Popolare',
        new: 'Nuovo',
        spicy: 'Piccante',
        unavailable: 'Non disponibile',
        addToCart: 'Aggiungi al carrello',
        noItemsFound: 'Nessun articolo trovato',
        tryDifferentCategory: 'Prova a selezionare una categoria o un termine di ricerca diverso'
      }
    };
  }

  // Initialize the translation service
  init() {
    // Listen for language change events
    window.addEventListener('languageChanged', (event) => {
      this.currentLanguage = event.detail.language;
      this.updatePageTranslations();
    });

    // Set initial language from restaurant app or localStorage
    const savedLanguage = localStorage.getItem('restaurant-language') || 'az';
    this.currentLanguage = savedLanguage;
    this.updatePageTranslations();
  }

  // Get translation for a key
  getTranslation(key) {
    return this.translations[this.currentLanguage]?.[key] || 
           this.translations['en']?.[key] || 
           key;
  }

  // Update all page translations
  updatePageTranslations() {
    // Update page title
    document.title = this.getTranslation('pageTitle');

    // Update elements with data-translate attributes
    const translatableElements = document.querySelectorAll('[data-translate]');
    translatableElements.forEach(element => {
      const key = element.getAttribute('data-translate');
      const translation = this.getTranslation(key);
      
      if (element.tagName === 'INPUT' && element.type === 'text') {
        element.placeholder = translation;
      } else if (element.hasAttribute('aria-label')) {
        element.setAttribute('aria-label', translation);
      } else {
        element.textContent = translation;
      }
    });

    // Update specific elements by ID/class
    this.updateSpecificElements();
  }

  // Update specific elements that need special handling
  updateSpecificElements() {
    // Restaurant tagline
    const tagline = document.querySelector('.restaurant-tagline');
    if (tagline) {
      tagline.textContent = this.getTranslation('restaurantTagline');
    }

    // Hero section
    const heroTitle = document.querySelector('.hero-title');
    if (heroTitle) {
      heroTitle.textContent = this.getTranslation('heroTitle');
    }

    const heroSubtitle = document.querySelector('.hero-subtitle');
    if (heroSubtitle) {
      heroSubtitle.textContent = this.getTranslation('heroSubtitle');
    }

    const heroCta = document.querySelector('.hero-cta');
    if (heroCta) {
      const text = heroCta.childNodes[0];
      if (text) {
        text.textContent = this.getTranslation('exploreMenu') + ' ';
      }
    }

    // Section titles
    const browseCategoriesTitle = document.querySelector('.categories-section .section-title');
    if (browseCategoriesTitle) {
      browseCategoriesTitle.textContent = this.getTranslation('browseCategories');
    }

    const ourMenuTitle = document.querySelector('.menu-section .section-title');
    if (ourMenuTitle) {
      ourMenuTitle.textContent = this.getTranslation('ourMenu');
    }

    const recommendedTitle = document.querySelector('.recommendations-section .section-title');
    if (recommendedTitle) {
      recommendedTitle.textContent = this.getTranslation('recommendedForYou');
    }

    // Cart section
    const cartTitle = document.querySelector('.cart-title');
    if (cartTitle) {
      cartTitle.textContent = this.getTranslation('yourOrder');
    }

    const cartEmptyTitle = document.querySelector('.cart-empty h4');
    if (cartEmptyTitle) {
      cartEmptyTitle.textContent = this.getTranslation('cartEmpty');
    }

    const cartEmptyDesc = document.querySelector('.cart-empty p');
    if (cartEmptyDesc) {
      cartEmptyDesc.textContent = this.getTranslation('cartEmptyDesc');
    }

    // Cart summary
    const subtotalLabel = document.querySelector('.subtotal span:first-child');
    if (subtotalLabel) {
      subtotalLabel.textContent = this.getTranslation('subtotal');
    }

    const deliveryLabel = document.querySelector('.delivery-fee span:first-child');
    if (deliveryLabel) {
      deliveryLabel.textContent = this.getTranslation('delivery');
    }

    const deliveryValue = document.querySelector('.delivery-fee span:last-child');
    if (deliveryValue) {
      deliveryValue.textContent = this.getTranslation('free');
    }

    const totalLabel = document.querySelector('.total span:first-child');
    if (totalLabel) {
      totalLabel.textContent = this.getTranslation('total');
    }

    // Checkout button
    const checkoutBtn = document.querySelector('.checkout-btn');
    if (checkoutBtn) {
      const text = checkoutBtn.childNodes[0];
      if (text) {
        text.textContent = this.getTranslation('proceedToCheckout') + ' ';
      }
    }

    // Bottom navigation
    const navItems = document.querySelectorAll('.nav-item span');
    const navKeys = ['menu', 'favorites', 'orders', 'profile'];
    navItems.forEach((item, index) => {
      if (navKeys[index]) {
        item.textContent = this.getTranslation(navKeys[index]);
      }
    });

    // Filter tabs
    const allItemsTab = document.querySelector('.filter-tab[data-category="all"]');
    if (allItemsTab) {
      allItemsTab.textContent = this.getTranslation('allItems');
    }

    // Loading text
    const preparingText = document.querySelector('#loading-screen p');
    if (preparingText) {
      preparingText.textContent = this.getTranslation('preparingMenu');
    }

    const loadingText = document.querySelector('#menu-loading p');
    if (loadingText) {
      loadingText.textContent = this.getTranslation('loadingOptions');
    }

    // Search placeholder
    const searchInput = document.querySelector('#search-input');
    if (searchInput) {
      searchInput.placeholder = this.getTranslation('searchPlaceholder');
    }

    // Aria labels for accessibility
    const searchBtn = document.querySelector('#search-btn');
    if (searchBtn) {
      searchBtn.setAttribute('aria-label', this.getTranslation('searchMenu'));
    }

    const searchClose = document.querySelector('#search-close');
    if (searchClose) {
      searchClose.setAttribute('aria-label', this.getTranslation('closeSearch'));
    }

    const cartToggle = document.querySelector('#cart-toggle');
    if (cartToggle) {
      cartToggle.setAttribute('aria-label', this.getTranslation('viewCart'));
    }

    const gridView = document.querySelector('#grid-view');
    if (gridView) {
      gridView.setAttribute('aria-label', this.getTranslation('gridView'));
    }

    const listView = document.querySelector('#list-view');
    if (listView) {
      listView.setAttribute('aria-label', this.getTranslation('listView'));
    }

    // Update checkout modal title
    const checkoutModalTitle = document.querySelector('.checkout-modal .modal-header h3');
    if (checkoutModalTitle) {
      checkoutModalTitle.textContent = this.getTranslation('completeYourOrder');
    }

    // Close buttons
    const closeButtons = document.querySelectorAll('.modal-close');
    closeButtons.forEach(btn => {
      btn.setAttribute('aria-label', this.getTranslation('close'));
    });

    // Menu empty state
    const menuEmptyTitle = document.querySelector('.menu-empty h4');
    if (menuEmptyTitle) {
      menuEmptyTitle.textContent = this.getTranslation('noItemsFound');
    }

    const menuEmptyDesc = document.querySelector('.menu-empty p');
    if (menuEmptyDesc) {
      menuEmptyDesc.textContent = this.getTranslation('tryDifferentCategory');
    }
  }

  // Set language programmatically
  setLanguage(language) {
    if (this.translations[language]) {
      this.currentLanguage = language;
      this.updatePageTranslations();
    }
  }
}

// Initialize translation service when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.translationService = new TranslationService();
  window.translationService.init();
});

export default TranslationService;
