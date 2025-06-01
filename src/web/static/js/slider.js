/**
 * Hero Slider Module
 * Handles auto-advancing image slider with manual controls
 */

class HeroSlider {
    constructor() {
        this.currentSlide = 0;
        this.totalSlides = 0;
        this.autoAdvanceInterval = null;
        this.autoAdvanceDelay = 5000; // 5 seconds
        this.isPlaying = true;
        
        this.init();
    }

    init() {
        this.slider = document.getElementById('hero-slider');
        this.track = document.getElementById('slider-track');
        this.prevBtn = document.getElementById('slider-prev');
        this.nextBtn = document.getElementById('slider-next');
        this.indicators = document.getElementById('slider-indicators');
        
        if (!this.slider || !this.track) {
            console.warn('Slider elements not found');
            return;
        }

        this.slides = this.track.querySelectorAll('.slide');
        this.totalSlides = this.slides.length;
        
        if (this.totalSlides === 0) {
            console.warn('No slides found');
            return;
        }
        
        // Set up CSS dimensions based on actual slide count
        this.initializeDimensions();
        
        this.bindEvents();
        this.updateSlidePosition();
        this.updateIndicators();
        this.startAutoAdvance();
        
        // Pause on hover
        this.slider.addEventListener('mouseenter', () => this.pauseAutoAdvance());
        this.slider.addEventListener('mouseleave', () => this.startAutoAdvance());
        
        // Touch support for mobile
        this.addTouchSupport();
        
        // Responsive resize handling
        this.addResizeSupport();
    }

    bindEvents() {
        if (this.prevBtn) {
            this.prevBtn.addEventListener('click', () => this.previousSlide());
        }
        
        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', () => this.nextSlide());
        }
        
        if (this.indicators) {
            this.indicators.addEventListener('click', (e) => {
                if (e.target.classList.contains('indicator')) {
                    const slideIndex = parseInt(e.target.dataset.slide);
                    this.goToSlide(slideIndex);
                }
            });
        }
    }

    updateSlidePosition() {
        if (!this.track) return;
        
        // Calculate the correct translation based on slide width
        // Each slide is 33.333% wide (100% / 3 slides)
        const slideWidth = 100 / this.totalSlides;
        const translateX = -(this.currentSlide * slideWidth);
        this.track.style.transform = `translateX(${translateX}%)`;
        
        // Update active states
        this.slides.forEach((slide, index) => {
            slide.classList.toggle('active', index === this.currentSlide);
        });
    }

    updateIndicators() {
        if (!this.indicators) return;
        
        const indicatorButtons = this.indicators.querySelectorAll('.indicator');
        indicatorButtons.forEach((btn, index) => {
            btn.classList.toggle('active', index === this.currentSlide);
        });
    }

    nextSlide() {
        this.currentSlide = (this.currentSlide + 1) % this.totalSlides;
        this.updateSlidePosition();
        this.updateIndicators();
        this.restartAutoAdvance();
    }

    previousSlide() {
        this.currentSlide = (this.currentSlide - 1 + this.totalSlides) % this.totalSlides;
        this.updateSlidePosition();
        this.updateIndicators();
        this.restartAutoAdvance();
    }

    goToSlide(index) {
        if (index >= 0 && index < this.totalSlides) {
            this.currentSlide = index;
            this.updateSlidePosition();
            this.updateIndicators();
            this.restartAutoAdvance();
        }
    }

    startAutoAdvance() {
        if (this.isPlaying && this.totalSlides > 1) {
            this.autoAdvanceInterval = setInterval(() => {
                this.nextSlide();
            }, this.autoAdvanceDelay);
        }
    }

    pauseAutoAdvance() {
        if (this.autoAdvanceInterval) {
            clearInterval(this.autoAdvanceInterval);
            this.autoAdvanceInterval = null;
        }
    }

    restartAutoAdvance() {
        this.pauseAutoAdvance();
        this.startAutoAdvance();
    }

    addTouchSupport() {
        let startX = 0;
        let endX = 0;
        let isDragging = false;

        this.slider.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            isDragging = true;
            this.pauseAutoAdvance();
        }, { passive: true });

        this.slider.addEventListener('touchmove', (e) => {
            if (!isDragging) return;
            endX = e.touches[0].clientX;
        }, { passive: true });

        this.slider.addEventListener('touchend', () => {
            if (!isDragging) return;
            isDragging = false;
            
            const deltaX = startX - endX;
            const minSwipeDistance = 50;

            if (Math.abs(deltaX) > minSwipeDistance) {
                if (deltaX > 0) {
                    this.nextSlide();
                } else {
                    this.previousSlide();
                }
            }
            
            this.startAutoAdvance();
        }, { passive: true });
    }

    initializeDimensions() {
        if (!this.track || !this.totalSlides) return;
        
        // Set track width based on actual number of slides
        const trackWidth = this.totalSlides * 100;
        this.track.style.width = `${trackWidth}%`;
        
        // Set each slide width
        const slideWidth = 100 / this.totalSlides;
        this.slides.forEach(slide => {
            slide.style.width = `${slideWidth}%`;
        });
    }

    addResizeSupport() {
        let resizeTimeout;
        
        const handleResize = () => {
            // Clear any pending resize handler
            clearTimeout(resizeTimeout);
            
            // Debounce resize events to prevent excessive calculations
            resizeTimeout = setTimeout(() => {
                // Recalculate dimensions on resize
                this.initializeDimensions();
                this.updateSlidePosition();
                
                // Ensure slider maintains state after resize
                this.restartAutoAdvance();
            }, 150);
        };
        
        window.addEventListener('resize', handleResize, { passive: true });
        window.addEventListener('orientationchange', handleResize, { passive: true });
    }

    // Public methods for external control
    play() {
        this.isPlaying = true;
        this.startAutoAdvance();
    }

    pause() {
        this.isPlaying = false;
        this.pauseAutoAdvance();
    }

    destroy() {
        this.pauseAutoAdvance();
        // Remove event listeners if needed
    }
}

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.heroSlider = new HeroSlider();
});

// Export for potential external use
export default HeroSlider;
