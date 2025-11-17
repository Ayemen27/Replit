
/**
 * Dynamic Content Loader for Replit Website
 * يحمل البيانات من Flask APIs ويعرضها في الصفحات الثابتة
 */

const ReplitDynamic = {
    
    baseURL: window.location.origin,
    
    // تحميل المشاريع المميزة
    async loadFeaturedProjects(containerSelector) {
        try {
            const response = await fetch(`${this.baseURL}/api/projects?featured=true&per_page=6`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success && data.projects && data.projects.length > 0) {
                this.renderProjects(containerSelector, data.projects);
            }
        } catch (error) {
            console.error('Error loading featured projects:', error);
        }
    },
    
    // تحميل جميع المشاريع
    async loadAllProjects(containerSelector, page = 1, category = null) {
        try {
            let url = `${this.baseURL}/api/projects?page=${page}&per_page=12`;
            if (category) {
                url += `&category=${category}`;
            }
            
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success && data.projects && data.projects.length > 0) {
                this.renderProjects(containerSelector, data.projects);
                this.renderPagination(data);
            }
        } catch (error) {
            console.error('Error loading projects:', error);
        }
    },
    
    // تحميل الفئات
    async loadCategories(containerSelector) {
        try {
            const response = await fetch(`${this.baseURL}/api/categories`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success && data.categories && data.categories.length > 0) {
                this.renderCategories(containerSelector, data.categories);
            }
        } catch (error) {
            console.error('Error loading categories:', error);
        }
    },
    
    // تحميل مشروع معين
    async loadProject(slug) {
        try {
            const response = await fetch(`${this.baseURL}/api/projects/${slug}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.project) {
                return data.project;
            }
        } catch (error) {
            console.error('Error loading project:', error);
        }
        return null;
    },
    
    // عرض المشاريع
    renderProjects(containerSelector, projects) {
        const container = document.querySelector(containerSelector);
        if (!container) return;
        
        container.innerHTML = projects.map(project => `
            <div class="project-card" style="border: 1px solid #e5e7eb; border-radius: 0.75rem; overflow: hidden; transition: transform 0.2s;">
                ${project.image_url 
                    ? `<img src="${project.image_url}" alt="${project.title}" style="width: 100%; height: 200px; object-fit: cover;">`
                    : `<div style="width: 100%; height: 200px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);"></div>`
                }
                <div style="padding: 1.5rem;">
                    <h3 style="font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem;">
                        ${project.title}
                    </h3>
                    <p style="color: #6b7280; margin-bottom: 1rem;">
                        ${project.description.substring(0, 100)}${project.description.length > 100 ? '...' : ''}
                    </p>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #9ca3af; font-size: 0.875rem;">
                            By ${project.author ? project.author.username : 'Anonymous'}
                        </span>
                        <a href="/project/${project.slug}" style="color: #fd5402; text-decoration: none; font-weight: 500;">
                            View →
                        </a>
                    </div>
                </div>
            </div>
        `).join('');
    },
    
    // عرض الفئات
    renderCategories(containerSelector, categories) {
        const container = document.querySelector(containerSelector);
        if (!container) return;
        
        container.innerHTML = categories.map(category => `
            <a href="/gallery/${category.slug}" style="padding: 2rem; background: white; border-radius: 0.75rem; text-decoration: none; color: inherit; border: 1px solid #e5e7eb; transition: all 0.2s; display: block;">
                <div style="font-size: 2rem; margin-bottom: 0.75rem;">
                    ${category.icon || '📁'}
                </div>
                <h3 style="font-size: 1.125rem; font-weight: 600; margin-bottom: 0.5rem;">
                    ${category.name}
                </h3>
                <p style="color: #6b7280; font-size: 0.875rem;">
                    ${category.description || 'Explore projects'}
                </p>
            </a>
        `).join('');
    },
    
    // عرض الترقيم
    renderPagination(data) {
        const container = document.querySelector('[data-pagination]');
        if (!container) return;
        
        let html = '';
        
        if (data.page > 1) {
            html += `<a href="?page=${data.page - 1}" style="padding: 0.75rem 1.5rem; margin: 0 0.5rem; background: #f3f4f6; border-radius: 0.5rem; text-decoration: none; color: inherit;">← Previous</a>`;
        }
        
        html += `<span style="margin: 0 1rem;">Page ${data.page} of ${data.pages}</span>`;
        
        if (data.page < data.pages) {
            html += `<a href="?page=${data.page + 1}" style="padding: 0.75rem 1.5rem; margin: 0 0.5rem; background: #f3f4f6; border-radius: 0.5rem; text-decoration: none; color: inherit;">Next →</a>`;
        }
        
        container.innerHTML = html;
    },
    
    // تهيئة الصفحة بناءً على نوعها
    init() {
        const path = window.location.pathname;
        
        // الصفحة الرئيسية
        if (path === '/' || path === '/index.html') {
            this.loadFeaturedProjects('[data-featured-projects]');
            this.loadCategories('[data-categories]');
        }
        
        // صفحة Gallery
        if (path === '/gallery' || path === '/gallery.html' || path.startsWith('/gallery/')) {
            const urlParams = new URLSearchParams(window.location.search);
            const page = urlParams.get('page') || 1;
            this.loadAllProjects('[data-all-projects]', page);
            this.loadCategories('[data-categories]');
        }
        
        // أي صفحة تحتوي على علامات البيانات
        if (document.querySelector('[data-featured-projects]')) {
            this.loadFeaturedProjects('[data-featured-projects]');
        }
        if (document.querySelector('[data-all-projects]')) {
            const urlParams = new URLSearchParams(window.location.search);
            const page = urlParams.get('page') || 1;
            this.loadAllProjects('[data-all-projects]', page);
        }
        if (document.querySelector('[data-categories]')) {
            this.loadCategories('[data-categories]');
        }
    }
};

// تهيئة عند تحميل الصفحة
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => ReplitDynamic.init());
} else {
    ReplitDynamic.init();
}

// جعل الكائن متاحاً عالمياً
window.ReplitDynamic = ReplitDynamic;
