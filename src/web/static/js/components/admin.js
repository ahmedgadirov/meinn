/**
 * Admin Panel JavaScript - Menu Management System
 * Handles all admin panel functionality including navigation, CRUD operations, and modal management
 */

class AdminPanel {
    constructor() {
        this.currentSection = 'dashboard';
        this.menuItems = [];
        this.categories = [];
        this.supportedLanguages = [
            { code: 'az', name: 'Azerbaijani' },
            { code: 'en', name: 'English' },
            { code: 'ru', name: 'Russian' },
            { code: 'tr', name: 'Turkish' },
            { code: 'ar', name: 'Arabic' },
            { code: 'hi', name: 'Hindi' },
            { code: 'fr', name: 'French' },
            { code: 'it', name: 'Italian' }
        ];
        this.init();
    }

    init() {
        console.log('Admin Panel initializing...');
        this.bindEvents();
        this.loadInitialData();
    }

    bindEvents() {
        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => this.handleNavigation(e));
        });

        // Menu Management Buttons
        const addMenuItemBtn = document.getElementById('add-menu-item');
        if (addMenuItemBtn) {
            addMenuItemBtn.addEventListener('click', () => this.showAddMenuItemModal());
        }

        const manageCategoriesBtn = document.getElementById('manage-categories');
        if (manageCategoriesBtn) {
            manageCategoriesBtn.addEventListener('click', () => this.showCategoriesModal());
        }

        // Category Management
        const addCategoryBtn = document.getElementById('add-category-btn');
        if (addCategoryBtn) {
            addCategoryBtn.addEventListener('click', () => this.showAddCategoryForm());
        }

        const saveCategoryBtn = document.getElementById('save-category');
        if (saveCategoryBtn) {
            saveCategoryBtn.addEventListener('click', () => this.saveCategory());
        }

        const updateCategoryBtn = document.getElementById('update-category');
        if (updateCategoryBtn) {
            updateCategoryBtn.addEventListener('click', () => this.updateCategory());
        }

        const cancelAddCategoryBtn = document.getElementById('cancel-add-category');
        if (cancelAddCategoryBtn) {
            cancelAddCategoryBtn.addEventListener('click', () => this.hideAddCategoryForm());
        }

        const cancelEditCategoryBtn = document.getElementById('cancel-edit-category');
        if (cancelEditCategoryBtn) {
            cancelEditCategoryBtn.addEventListener('click', () => this.hideEditCategoryForm());
        }

        // Modal close events
        document.querySelectorAll('.modal-close').forEach(closeBtn => {
            closeBtn.addEventListener('click', (e) => this.closeModal(e));
        });

        document.querySelectorAll('.modal-overlay').forEach(overlay => {
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    this.closeModal(e);
                }
            });
        });

        // Category filter
        const categoryFilter = document.getElementById('category-filter');
        if (categoryFilter) {
            categoryFilter.addEventListener('change', () => this.filterMenuItems());
        }
    }

    async loadInitialData() {
        try {
            await this.loadCategories();
            await this.loadMenuItems();
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showNotification('Error loading data. Please refresh the page.', 'error');
        }
    }

    handleNavigation(e) {
        e.preventDefault();
        const section = e.currentTarget.dataset.section;
        if (section) {
            this.switchSection(section);
        }
    }

    switchSection(section) {
        // Remove active class from all nav items and sections
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelectorAll('.dashboard-section, .menu-section, .orders-section, .analytics-section, .settings-section').forEach(sec => {
            sec.classList.remove('active');
        });

        // Add active class to current nav item and section
        const navItem = document.querySelector(`[data-section="${section}"]`);
        const sectionElement = document.getElementById(`${section}-section`);
        
        if (navItem) {
            navItem.classList.add('active');
        }
        
        if (sectionElement) {
            sectionElement.classList.add('active');
        }

        this.currentSection = section;

        // Load section-specific data
        if (section === 'menu') {
            this.loadMenuItems();
        }
        if (section === 'analytics') {
            this.loadAnalyticsSummary();
        }
    }

    async loadAnalyticsSummary() {
        try {
            const response = await fetch('/api/analytics/summary');
            const data = await response.json();
            if (data.success) {
                this.renderAnalyticsSummary(data);
            } else {
                this.renderAnalyticsSummary({ top_viewed: [], top_added_to_cart: [], top_ordered: [] });
                this.showNotification('Failed to load analytics', 'error');
            }
        } catch (error) {
            this.renderAnalyticsSummary({ top_viewed: [], top_added_to_cart: [], top_ordered: [] });
            this.showNotification('Error loading analytics', 'error');
        }
    }

    renderAnalyticsSummary(data) {
        const analyticsSection = document.getElementById('analytics-section');
        if (!analyticsSection) return;

        // Helper to get item name and category by ID
        const getItemInfo = (itemId) => {
            const item = this.menuItems.find(i => i.id === itemId);
            if (item) {
                return {
                    name: this.escapeHtml(item.name),
                    category: this.escapeHtml(item.category || item.category_id || '')
                };
            }
            return { name: '(Unknown)', category: '' };
        };

        analyticsSection.innerHTML = `
            <h2>Analytics Summary</h2>
            <div class="analytics-tables">
                <div class="analytics-table">
                    <h3>Top Viewed Items</h3>
                    <table>
                        <thead><tr><th>Item ID</th><th>Name</th><th>Category</th><th>Views</th></tr></thead>
                        <tbody>
                            ${data.top_viewed && data.top_viewed.length > 0 ? data.top_viewed.map(item => {
                                const info = getItemInfo(item.item_id);
                                return `<tr><td>${item.item_id}</td><td>${info.name}</td><td>${info.category}</td><td>${item.views}</td></tr>`;
                            }).join('') : '<tr><td colspan="4">No data</td></tr>'}
                        </tbody>
                    </table>
                </div>
                <div class="analytics-table">
                    <h3>Top Added to Cart</h3>
                    <table>
                        <thead><tr><th>Item ID</th><th>Name</th><th>Category</th><th>Adds</th></tr></thead>
                        <tbody>
                            ${data.top_added_to_cart && data.top_added_to_cart.length > 0 ? data.top_added_to_cart.map(item => {
                                const info = getItemInfo(item.item_id);
                                return `<tr><td>${item.item_id}</td><td>${info.name}</td><td>${info.category}</td><td>${item.adds}</td></tr>`;
                            }).join('') : '<tr><td colspan="4">No data</td></tr>'}
                        </tbody>
                    </table>
                </div>
                <div class="analytics-table">
                    <h3>Top Ordered Items</h3>
                    <table>
                        <thead><tr><th>Item ID</th><th>Name</th><th>Category</th><th>Orders</th></tr></thead>
                        <tbody>
                            ${data.top_ordered && data.top_ordered.length > 0 ? data.top_ordered.map(item => {
                                const info = getItemInfo(item.item_id);
                                return `<tr><td>${item.item_id}</td><td>${info.name}</td><td>${info.category}</td><td>${item.orders}</td></tr>`;
                            }).join('') : '<tr><td colspan="4">No data</td></tr>'}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }

    async loadCategories() {
        try {
            const response = await fetch('/api/menu/categories');
            const data = await response.json();
            
            if (data.success) {
                this.categories = data.categories;
                this.updateCategoryFilter();
                this.updateCategoriesTable();
            } else {
                console.error('Failed to load categories:', data.error);
                this.showNotification('Failed to load categories', 'error');
            }
        } catch (error) {
            console.error('Error loading categories:', error);
            this.showNotification('Error loading categories', 'error');
        }
    }

    async loadMenuItems() {
        try {
            const categoryFilter = document.getElementById('category-filter');
            const selectedCategory = categoryFilter ? categoryFilter.value : '';
            
            const url = selectedCategory ? 
                `/api/menu/items?category=${selectedCategory}` : 
                '/api/menu/items';
                
            const response = await fetch(url);
            const data = await response.json();
            
            if (data.success) {
                this.menuItems = data.items;
                this.updateMenuItemsTable();
            } else {
                console.error('Failed to load menu items:', data.error);
                this.showNotification('Failed to load menu items', 'error');
            }
        } catch (error) {
            console.error('Error loading menu items:', error);
            this.showNotification('Error loading menu items', 'error');
        }
    }

    updateCategoryFilter() {
        const categoryFilter = document.getElementById('category-filter');
        if (!categoryFilter) return;

        // Clear existing options except "All Categories"
        const allOption = categoryFilter.querySelector('option[value=""]');
        categoryFilter.innerHTML = '';
        if (allOption) {
            categoryFilter.appendChild(allOption);
        } else {
            const newAllOption = document.createElement('option');
            newAllOption.value = '';
            newAllOption.textContent = 'All Categories';
            categoryFilter.appendChild(newAllOption);
        }

        // Add category options
        this.categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category.id;
            option.textContent = category.name;
            categoryFilter.appendChild(option);
        });
    }

    updateMenuItemsTable() {
        const tableBody = document.querySelector('.menu-section .data-table tbody');
        if (!tableBody) return;

        if (this.menuItems.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center;">No menu items found</td></tr>';
            return;
        }

        tableBody.innerHTML = this.menuItems.map(item => `
            <tr>
                <td>${item.id}</td>
                <td>${this.escapeHtml(item.name)}</td>
                <td>${this.escapeHtml(item.category || item.category_id)}</td>
                <td>₼${item.price.toFixed(2)}</td>
                <td>
                    <span class="status-badge ${item.available ? 'status-ready' : 'status-cancelled'}">
                        ${item.available ? 'Available' : 'Unavailable'}
                    </span>
                </td>
                <td>
                    <span class="status-badge ${item.popular ? 'status-ready' : 'status-pending'}">
                        ${item.popular ? 'Popular' : 'Regular'}
                    </span>
                </td>
                <td>
                    <div class="table-row-actions">
                        <button class="row-action edit" onclick="adminPanel.editMenuItem('${item.id}')" title="Edit">
                            ✏️
                        </button>
                        <button class="row-action delete" onclick="adminPanel.deleteMenuItem('${item.id}')" title="Delete">
                            🗑️
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    updateCategoriesTable() {
        const tableBody = document.querySelector('#categories-table tbody');
        if (!tableBody) return;

        if (this.categories.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="4" style="text-align: center;">No categories found</td></tr>';
            return;
        }

        tableBody.innerHTML = this.categories.map(category => `
            <tr>
                <td>${category.id}</td>
                <td>${this.escapeHtml(category.name)}</td>
                <td>${this.escapeHtml(category.description || '')}</td>
                <td>
                    <div class="table-row-actions">
                        <button class="row-action edit" onclick="adminPanel.editCategory('${category.id}')" title="Edit">
                            ✏️
                        </button>
                        <button class="row-action delete" onclick="adminPanel.deleteCategory('${category.id}')" title="Delete">
                            🗑️
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    filterMenuItems() {
        this.loadMenuItems();
    }

    showCategoriesModal() {
        const modal = document.getElementById('categories-modal');
        if (modal) {
            modal.classList.add('active');
            this.loadCategories();
        }
    }

    showAddCategoryForm() {
        document.getElementById('add-category-form').style.display = 'block';
        document.getElementById('edit-category-form').style.display = 'none';
        
        // Clear form
        document.getElementById('category-id').value = '';
        document.getElementById('category-image').value = '';
        
        // Setup multilingual fields for categories
        this.setupCategoryMultilingualFields('add');
        
        // Clear all language fields
        this.supportedLanguages.forEach(lang => {
            const nameField = document.getElementById(`add-category-name-${lang.code}`);
            const descField = document.getElementById(`add-category-description-${lang.code}`);
            if (nameField) nameField.value = '';
            if (descField) descField.value = '';
        });
    }

    hideAddCategoryForm() {
        document.getElementById('add-category-form').style.display = 'none';
    }

    hideEditCategoryForm() {
        document.getElementById('edit-category-form').style.display = 'none';
    }

    async saveCategory() {
        // Collect multi-language data
        const nameTranslations = this.collectLanguageValues('add-category-name');
        const descriptionTranslations = this.collectLanguageValues('add-category-description');

        // Validate that at least English name is provided
        if (!nameTranslations.en || !nameTranslations.en.trim()) {
            this.showNotification('Please provide at least an English name', 'error');
            return;
        }

        const categoryData = {
            id: document.getElementById('category-id').value.trim(),
            image_url: document.getElementById('category-image').value.trim(),
            translations: {}
        };

        // Add translations for each language
        this.supportedLanguages.forEach(lang => {
            categoryData.translations[lang.code] = {
                name: nameTranslations[lang.code] || nameTranslations.en || '',
                description: descriptionTranslations[lang.code] || descriptionTranslations.en || ''
            };
        });

        if (!categoryData.id) {
            this.showNotification('Please fill in the category ID', 'error');
            return;
        }

        try {
            const response = await fetch('/api/menu/admin/categories', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(categoryData)
            });

            const data = await response.json();
            
            if (data.success) {
                this.showNotification('Category added successfully!', 'success');
                this.hideAddCategoryForm();
                await this.loadCategories();
            } else {
                this.showNotification(data.error || 'Failed to add category', 'error');
            }
        } catch (error) {
            console.error('Error saving category:', error);
            this.showNotification('Error saving category', 'error');
        }
    }

    editCategory(categoryId) {
        const category = this.categories.find(c => c.id === categoryId);
        if (!category) {
            this.showNotification('Category not found', 'error');
            return;
        }

        document.getElementById('add-category-form').style.display = 'none';
        document.getElementById('edit-category-form').style.display = 'block';

        document.getElementById('edit-category-id').value = category.id;
        document.getElementById('edit-category-image').value = category.image_url || '';

        // Setup multilingual fields for editing
        this.setupCategoryMultilingualFields('edit');

        // Populate fields with existing translation data
        const nameValues = {};
        const descriptionValues = {};
        
        if (category.translations) {
            this.supportedLanguages.forEach(lang => {
                nameValues[lang.code] = category.translations[lang.code]?.name || '';
                descriptionValues[lang.code] = category.translations[lang.code]?.description || '';
            });
        } else {
            // Fallback for categories without translations
            nameValues.en = category.name || '';
            descriptionValues.en = category.description || '';
        }

        // Fill in the multilingual fields
        this.supportedLanguages.forEach(lang => {
            const nameField = document.getElementById(`edit-category-name-${lang.code}`);
            const descField = document.getElementById(`edit-category-description-${lang.code}`);
            if (nameField) nameField.value = nameValues[lang.code] || '';
            if (descField) descField.value = descriptionValues[lang.code] || '';
        });
    }

    async updateCategory() {
        const categoryId = document.getElementById('edit-category-id').value;
        
        // Collect multi-language data
        const nameTranslations = this.collectLanguageValues('edit-category-name');
        const descriptionTranslations = this.collectLanguageValues('edit-category-description');

        // Validate that at least English name is provided
        if (!nameTranslations.en || !nameTranslations.en.trim()) {
            this.showNotification('Please provide at least an English name', 'error');
            return;
        }

        const categoryData = {
            image_url: document.getElementById('edit-category-image').value.trim(),
            translations: {}
        };

        // Add translations for each language
        this.supportedLanguages.forEach(lang => {
            categoryData.translations[lang.code] = {
                name: nameTranslations[lang.code] || nameTranslations.en || '',
                description: descriptionTranslations[lang.code] || descriptionTranslations.en || ''
            };
        });

        try {
            const response = await fetch(`/api/menu/admin/categories/${categoryId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(categoryData)
            });

            const data = await response.json();
            
            if (data.success) {
                this.showNotification('Category updated successfully!', 'success');
                this.hideEditCategoryForm();
                await this.loadCategories();
            } else {
                this.showNotification(data.error || 'Failed to update category', 'error');
            }
        } catch (error) {
            console.error('Error updating category:', error);
            this.showNotification('Error updating category', 'error');
        }
    }

    async deleteCategory(categoryId) {
        if (!confirm('Are you sure you want to delete this category? This action cannot be undone.')) {
            return;
        }

        try {
            const response = await fetch(`/api/menu/admin/categories/${categoryId}`, {
                method: 'DELETE'
            });

            const data = await response.json();
            
            if (data.success) {
                this.showNotification('Category deleted successfully!', 'success');
                await this.loadCategories();
            } else {
                this.showNotification(data.error || 'Failed to delete category', 'error');
            }
        } catch (error) {
            console.error('Error deleting category:', error);
            this.showNotification('Error deleting category', 'error');
        }
    }

    showAddMenuItemModal() {
        const modal = this.createMenuItemModal();
        document.body.appendChild(modal);
        modal.classList.add('active');
    }

    createMenuItemModal(item = null) {
        const isEdit = item !== null;
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        
        // Prepare multi-language values for editing
        const nameValues = {};
        const descriptionValues = {};
        if (item && item.translations) {
            this.supportedLanguages.forEach(lang => {
                nameValues[lang.code] = item.translations[lang.code]?.name || '';
                descriptionValues[lang.code] = item.translations[lang.code]?.description || '';
            });
        }

        modal.innerHTML = `
            <div class="modal-container" style="max-width: 800px; max-height: 90vh; overflow-y: auto;">
                <div class="modal-header">
                    <h3 class="modal-title">${isEdit ? 'Edit Menu Item' : 'Add New Menu Item'}</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    <form id="menu-item-form">
                        <div class="form-grid">
                            <div class="form-group">
                                <label class="form-label" for="item-category">Category *</label>
                                <select id="item-category" class="form-control" required>
                                    <option value="">Select a category</option>
                                    ${this.categories.map(cat => 
                                        `<option value="${cat.id}" ${item && item.category_id === cat.id ? 'selected' : ''}>${cat.name}</option>`
                                    ).join('')}
                                </select>
                            </div>
                            <div class="form-group">
                                <label class="form-label" for="item-price">Price *</label>
                                <input type="number" id="item-price" class="form-control" step="0.01" min="0" value="${item ? item.price : ''}" required>
                            </div>
                            <div class="form-group">
                                <label class="form-label" for="item-image">Image URL</label>
                                <input type="url" id="item-image" class="form-control" value="${item ? (item.image_url || '') : ''}" placeholder="https://example.com/image.jpg">
                            </div>
                        </div>
                        
                        <!-- Multi-language Name Fields -->
                        <div class="form-group">
                            <label class="form-label">Name (Multi-language) *</label>
                            ${this.createLanguageTabs()}
                            <div class="language-fields">
                                ${this.createMultiLanguageFields('item-name', 'input', nameValues, true)}
                            </div>
                        </div>
                        
                        <!-- Multi-language Description Fields -->
                        <div class="form-group">
                            <label class="form-label">Description (Multi-language)</label>
                            <div class="language-fields">
                                ${this.createMultiLanguageFields('item-description', 'textarea', descriptionValues, false)}
                            </div>
                        </div>

                        <div class="form-grid">
                            <div class="form-group">
                                <label>
                                    <input type="checkbox" id="item-available" ${item ? (item.available ? 'checked' : '') : 'checked'}>
                                    Available
                                </label>
                            </div>
                            <div class="form-group">
                                <label>
                                    <input type="checkbox" id="item-popular" ${item && item.popular ? 'checked' : ''}>
                                    Popular Item
                                </label>
                            </div>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="adminPanel.${isEdit ? `updateMenuItem('${item.id}')` : 'saveMenuItem()'}">${isEdit ? 'Update' : 'Save'} Item</button>
                </div>
            </div>
        `;

        // Add close event
        modal.querySelector('.modal-close').addEventListener('click', () => modal.remove());
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.remove();
        });

        // Add CSS styles for language tabs
        if (!document.head.querySelector('#language-tabs-styles')) {
            const style = document.createElement('style');
            style.id = 'language-tabs-styles';
            style.textContent = `
                .language-tabs {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 8px;
                    margin-bottom: 15px;
                    border-bottom: 1px solid #e0e0e0;
                    padding-bottom: 10px;
                }
                .language-tab {
                    background: #f8f9fa;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 6px 12px;
                    cursor: pointer;
                    font-size: 12px;
                    color: #666;
                    transition: all 0.2s ease;
                }
                .language-tab:hover {
                    background: #e9ecef;
                    color: #333;
                }
                .language-tab.active {
                    background: #007bff;
                    color: white;
                    border-color: #007bff;
                }
                .language-field {
                    margin-bottom: 0;
                }
                .language-fields {
                    margin-bottom: 15px;
                }
            `;
            document.head.appendChild(style);
        }

        return modal;
    }

    async saveMenuItem() {
        // Collect multi-language data
        const nameTranslations = this.collectLanguageValues('item-name');
        const descriptionTranslations = this.collectLanguageValues('item-description');

        // Validate that at least English name is provided
        if (!nameTranslations.en || !nameTranslations.en.trim()) {
            this.showNotification('Please provide at least an English name', 'error');
            return;
        }

        const itemData = {
            category: document.getElementById('item-category').value,
            price: parseFloat(document.getElementById('item-price').value),
            image_url: document.getElementById('item-image').value.trim(),
            available: document.getElementById('item-available').checked,
            popular: document.getElementById('item-popular').checked,
            translations: {}
        };

        // Add translations for each language
        this.supportedLanguages.forEach(lang => {
            itemData.translations[lang.code] = {
                name: nameTranslations[lang.code] || nameTranslations.en || '',
                description: descriptionTranslations[lang.code] || descriptionTranslations.en || ''
            };
        });

        if (!itemData.category || !itemData.price) {
            this.showNotification('Please fill in all required fields', 'error');
            return;
        }

        try {
            const response = await fetch('/api/menu/admin/items', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(itemData)
            });

            const data = await response.json();
            
            if (data.success) {
                this.showNotification('Menu item added successfully!', 'success');
                document.querySelector('.modal-overlay').remove();
                await this.loadMenuItems();
            } else {
                this.showNotification(data.error || 'Failed to add menu item', 'error');
            }
        } catch (error) {
            console.error('Error saving menu item:', error);
            this.showNotification('Error saving menu item', 'error');
        }
    }

    editMenuItem(itemId) {
        const item = this.menuItems.find(i => i.id === itemId);
        if (!item) {
            this.showNotification('Menu item not found', 'error');
            return;
        }

        const modal = this.createMenuItemModal(item);
        document.body.appendChild(modal);
        modal.classList.add('active');
    }

    async updateMenuItem(itemId) {
        // Collect multi-language data
        const nameTranslations = this.collectLanguageValues('item-name');
        const descriptionTranslations = this.collectLanguageValues('item-description');

        // Validate that at least English name is provided
        if (!nameTranslations.en || !nameTranslations.en.trim()) {
            this.showNotification('Please provide at least an English name', 'error');
            return;
        }

        const itemData = {
            category: document.getElementById('item-category').value,
            price: parseFloat(document.getElementById('item-price').value),
            image_url: document.getElementById('item-image').value.trim(),
            available: document.getElementById('item-available').checked,
            popular: document.getElementById('item-popular').checked,
            translations: {}
        };

        // Add translations for each language
        this.supportedLanguages.forEach(lang => {
            itemData.translations[lang.code] = {
                name: nameTranslations[lang.code] || nameTranslations.en || '',
                description: descriptionTranslations[lang.code] || descriptionTranslations.en || ''
            };
        });

        if (!itemData.category || !itemData.price) {
            this.showNotification('Please fill in all required fields', 'error');
            return;
        }

        try {
            const response = await fetch(`/api/menu/admin/items/${itemId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(itemData)
            });

            const data = await response.json();
            
            if (data.success) {
                this.showNotification('Menu item updated successfully!', 'success');
                document.querySelector('.modal-overlay').remove();
                await this.loadMenuItems();
            } else {
                this.showNotification(data.error || 'Failed to update menu item', 'error');
            }
        } catch (error) {
            console.error('Error updating menu item:', error);
            this.showNotification('Error updating menu item', 'error');
        }
    }

    async deleteMenuItem(itemId) {
        if (!confirm('Are you sure you want to delete this menu item? This action cannot be undone.')) {
            return;
        }

        try {
            const response = await fetch(`/api/menu/admin/items/${itemId}`, {
                method: 'DELETE'
            });

            const data = await response.json();
            
            if (data.success) {
                this.showNotification('Menu item deleted successfully!', 'success');
                await this.loadMenuItems();
            } else {
                this.showNotification(data.error || 'Failed to delete menu item', 'error');
            }
        } catch (error) {
            console.error('Error deleting menu item:', error);
            this.showNotification('Error deleting menu item', 'error');
        }
    }

    closeModal(e) {
        const modal = e.target.closest('.modal-overlay');
        if (modal) {
            modal.classList.remove('active');
            // Remove dynamically created modals
            if (modal.id !== 'categories-modal') {
                setTimeout(() => modal.remove(), 300);
            }
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#17a2b8'};
            color: white;
            padding: 12px 20px;
            border-radius: 4px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            z-index: 10000;
            max-width: 300px;
            font-size: 14px;
            animation: slideIn 0.3s ease;
        `;
        notification.textContent = message;

        // Add CSS animation
        if (!document.head.querySelector('#notification-styles')) {
            const style = document.createElement('style');
            style.id = 'notification-styles';
            style.textContent = `
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes slideOut {
                    from { transform: translateX(0); opacity: 1; }
                    to { transform: translateX(100%); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }

        document.body.appendChild(notification);

        // Auto remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Helper method to create multi-language form tabs
    createLanguageTabs(activeLanguage = 'en') {
        return `
            <div class="language-tabs">
                ${this.supportedLanguages.map(lang => `
                    <button type="button" class="language-tab ${lang.code === activeLanguage ? 'active' : ''}" 
                            data-language="${lang.code}" onclick="adminPanel.switchLanguageTab('${lang.code}')">
                        ${lang.name}
                    </button>
                `).join('')}
            </div>
        `;
    }

    // Helper method to create multi-language input fields
    createMultiLanguageFields(fieldName, fieldType = 'input', currentValues = {}, required = false) {
        return this.supportedLanguages.map(lang => `
            <div class="language-field" data-language="${lang.code}" style="display: ${lang.code === 'en' ? 'block' : 'none'};">
                <label class="form-label" for="${fieldName}-${lang.code}">
                    ${fieldType === 'input' ? 'Name' : 'Description'} (${lang.name}) ${required && lang.code === 'en' ? '*' : ''}
                </label>
                ${fieldType === 'input' ? 
                    `<input type="text" id="${fieldName}-${lang.code}" class="form-control" 
                            value="${this.escapeHtml(currentValues[lang.code] || '')}" ${required && lang.code === 'en' ? 'required' : ''}>` :
                    `<textarea id="${fieldName}-${lang.code}" class="form-control" rows="3">${this.escapeHtml(currentValues[lang.code] || '')}</textarea>`
                }
            </div>
        `).join('');
    }

    // Switch between language tabs
    switchLanguageTab(languageCode) {
        // Update tab states
        document.querySelectorAll('.language-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-language="${languageCode}"]`).classList.add('active');

        // Show/hide language fields
        document.querySelectorAll('.language-field').forEach(field => {
            field.style.display = field.dataset.language === languageCode ? 'block' : 'none';
        });
    }

    // Collect multi-language field values
    collectLanguageValues(fieldPrefix) {
        const values = {};
        this.supportedLanguages.forEach(lang => {
            const field = document.getElementById(`${fieldPrefix}-${lang.code}`);
            if (field) {
                values[lang.code] = field.value.trim();
            }
        });
        return values;
    }

    // Setup multilingual fields for categories
    setupCategoryMultilingualFields(formType) {
        const nameTabsContainer = document.getElementById(`${formType}-category-name-tabs`);
        const nameFieldsContainer = document.getElementById(`${formType}-category-name-fields`);
        const descFieldsContainer = document.getElementById(`${formType}-category-description-fields`);

        if (nameTabsContainer) {
            nameTabsContainer.innerHTML = this.createLanguageTabs();
        }

        if (nameFieldsContainer) {
            nameFieldsContainer.innerHTML = this.createMultiLanguageFields(`${formType}-category-name`, 'input', {}, true);
        }

        if (descFieldsContainer) {
            descFieldsContainer.innerHTML = this.createMultiLanguageFields(`${formType}-category-description`, 'textarea', {}, false);
        }

        // Add click handlers for language tabs
        document.querySelectorAll('.language-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                this.switchLanguageTab(tab.dataset.language);
            });
        });
    }
}

// Initialize admin panel when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.adminPanel = new AdminPanel();
});

// Make admin panel globally available
window.AdminPanel = AdminPanel;
