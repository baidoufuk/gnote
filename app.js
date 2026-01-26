// 配置：后端 API 地址
const API_BASE_URL = 'http://tofuali.top'; // 临时使用 HTTP，待 SSL 证书修复后改回 HTTPS

// 格式化日期时间
function formatDateTime(dateString) {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}`;
}

function formatDateTimeFull(dateString) {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    return `${year}年${month}月${day}日 ${hours}:${minutes}:${seconds}`;
}

// 创建单个帖子卡片
function createPostCard(post) {
    const postItem = document.createElement('div');
    postItem.className = 'relative mb-8';

    const modalId = `modal_${post.id}`;

    postItem.innerHTML = `
        <div class="timeline-dot"></div>
        <div class="bg-white rounded-xl p-5 sm:p-4 shadow-md hover:shadow-lg hover:translate-x-1 transition-all duration-300 cursor-pointer" data-modal-id="${modalId}">
            <div class="inline-block text-[#667eea] text-sm font-semibold mb-2">
                <svg class="inline-block w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                ${formatDateTime(post.created_at)}
            </div>
            <div class="text-gray-700 text-[15px] leading-relaxed line-clamp-3">${escapeHtml(post.content)}</div>
        </div>
    `;

    // 添加点击事件监听器
    const card = postItem.querySelector('[data-modal-id]');
    card.addEventListener('click', () => {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.showModal();
        }
    });

    return postItem;
}

// 创建模态框
function createModal(post) {
    const modal = document.createElement('dialog');
    modal.id = `modal_${post.id}`;
    modal.className = 'modal';

    const imageHtml = post.image_path ? `
        <div class="mt-5 rounded-lg overflow-hidden">
            <img src="${escapeHtml(API_BASE_URL)}/uploads/${escapeHtml(post.image_path)}" alt="内容配图" loading="lazy" class="w-full h-auto">
        </div>
    ` : '';

    modal.innerHTML = `
        <div class="modal-box max-w-2xl">
            <form method="dialog">
                <button class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">✕</button>
            </form>
            <h3 class="font-bold text-lg mb-4">
                <svg class="inline-block w-5 h-5 mr-1 text-[#667eea]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                ${formatDateTimeFull(post.created_at)}
            </h3>
            <div class="text-gray-700 text-base leading-relaxed whitespace-pre-wrap break-words">${escapeHtml(post.content)}</div>
            ${imageHtml}
        </div>
        <form method="dialog" class="modal-backdrop">
            <button>close</button>
        </form>
    `;

    return modal;
}

// HTML 转义，防止 XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 渲染帖子列表
function renderPosts(posts) {
    const container = document.getElementById('posts-container');
    container.innerHTML = '';

    // 清除旧的模态框
    const oldModals = document.querySelectorAll('dialog.modal');
    oldModals.forEach(modal => modal.remove());

    posts.forEach(post => {
        // 添加卡片
        const postCard = createPostCard(post);
        container.appendChild(postCard);

        // 添加模态框
        const modal = createModal(post);
        document.body.appendChild(modal);
    });

    // 显示内容容器
    container.classList.remove('hidden');
}

// 显示错误信息
function showError(message) {
    const errorDiv = document.getElementById('error');
    const errorMessage = document.getElementById('error-message');
    errorMessage.textContent = message;
    errorDiv.classList.remove('hidden');
}

// 隐藏错误信息
function hideError() {
    const errorDiv = document.getElementById('error');
    errorDiv.classList.add('hidden');
}

// 隐藏加载状态
function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

// 获取帖子数据
async function fetchPosts() {
    try {
        hideError(); // 隐藏之前的错误信息
        const response = await fetch(`${API_BASE_URL}/api/posts`);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();

        if (result.success && result.data) {
            renderPosts(result.data);
        } else {
            throw new Error('数据格式错误');
        }
    } catch (error) {
        console.error('获取数据失败:', error);
        showError(`无法连接到服务器，请检查后端 API 是否正常运行。错误信息: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', () => {
    fetchPosts();
});
