document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const emptyState = document.getElementById('empty-state');
    const newChatBtn = document.getElementById('new-chat-btn');
    const clearHistoryBtn = document.getElementById('clear-history-btn');
    const sessionListEl = document.getElementById('session-list');

    let currentSessionId = null;
    let currentUser = null;

    // Configure marked.js when the CDN dependency is available. Bot output is
    // still treated as plain text unless DOMPurify is also available.
    if (window.marked && typeof window.marked.setOptions === 'function') {
        window.marked.setOptions({
            breaks: true,
            gfm: true
        });
    }

    function renderBotContent(element, content) {
        const safeFallback = typeof content === 'string' ? content : String(content ?? '');
        const canRenderMarkdown = window.marked
            && typeof window.marked.parse === 'function'
            && window.DOMPurify
            && typeof window.DOMPurify.sanitize === 'function';

        if (canRenderMarkdown) {
            try {
                const renderedHtml = window.marked.parse(safeFallback);
                element.innerHTML = window.DOMPurify.sanitize(renderedHtml);
                return;
            } catch (error) {
                console.error('Unable to render sanitized Markdown:', error);
            }
        }

        element.textContent = safeFallback;
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function appendMessage(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        if (role === 'bot') {
            renderBotContent(contentDiv, content);
        } else {
            contentDiv.textContent = content;
        }

        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }

    function showTypingIndicator() {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot';
        messageDiv.id = 'typing-indicator';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = `
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;

        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }

    function removeTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    // --- MULTI-SESSION LOGIC ---
    async function fetchSessions() {
        if (!currentUser) return;
        try {
            const res = await fetch('/sessions');
            if (res.ok) {
                const data = await res.json();
                renderSessionList(data.sessions);
            }
        } catch (e) {
            console.error("Lỗi lấy danh sách session", e);
        }
    }

    function renderSessionList(sessions) {
        if (!sessionListEl) return;
        sessionListEl.innerHTML = '';
        sessions.forEach(session => {
            const li = document.createElement('li');
            li.className = 'session-item';
            if (session.id === currentSessionId) {
                li.classList.add('active');
            }

            const titleSpan = document.createElement('span');
            titleSpan.className = 'session-title';
            titleSpan.textContent = session.title || 'Đoạn chat mới';
            li.appendChild(titleSpan);

            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'session-actions';

            // Edit button
            const editBtn = document.createElement('button');
            editBtn.className = 'action-btn edit';
            editBtn.innerHTML = `<svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>`;
            editBtn.onclick = (e) => {
                e.stopPropagation();
                const newTitle = prompt("Nhập tên mới:", session.title || '');
                if (newTitle && newTitle.trim() !== "") {
                    renameSession(session.id, newTitle.trim());
                }
            };

            // Delete button
            const delBtn = document.createElement('button');
            delBtn.className = 'action-btn delete';
            delBtn.innerHTML = `<svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>`;
            delBtn.onclick = (e) => {
                e.stopPropagation();
                if (confirm("Bạn có chắc muốn xóa cuộc trò chuyện này?")) {
                    deleteSession(session.id);
                }
            };

            actionsDiv.appendChild(editBtn);
            actionsDiv.appendChild(delBtn);
            li.appendChild(actionsDiv);

            li.onclick = () => loadSession(session.id);
            sessionListEl.appendChild(li);
        });
    }

    async function renameSession(id, newTitle) {
        try {
            const res = await fetch(`/sessions/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title: newTitle })
            });
            if (res.ok) fetchSessions();
        } catch (e) {
            console.error("Lỗi đổi tên", e);
        }
    }

    async function deleteSession(id) {
        try {
            const res = await fetch(`/sessions/${id}`, {
                method: 'DELETE'
            });
            if (res.ok) {
                if (id === currentSessionId) {
                    currentSessionId = null;
                    chatMessages.querySelectorAll('.message').forEach(m => m.remove());
                    if (emptyState) emptyState.style.display = 'flex';
                }
                fetchSessions();
            }
        } catch (e) {
            console.error("Lỗi xóa", e);
        }
    }

    async function loadSession(id) {
        currentSessionId = id;
        chatMessages.querySelectorAll('.message').forEach(m => m.remove());
        if (emptyState) emptyState.style.display = 'none';

        fetchSessions(); // update active state

        try {
            const res = await fetch(`/sessions/${id}/messages`);
            if (res.ok) {
                const data = await res.json();
                data.messages.forEach(msg => {
                    appendMessage(msg.role === 'human' ? 'user' : 'bot', msg.content);
                });
                scrollToBottom();
            }
        } catch (e) {
            console.error("Lỗi tải tin nhắn", e);
        }
    }

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const query = userInput.value.trim();
        if (!query) return;

        // Hide empty state on first message
        if (emptyState && emptyState.style.display !== 'none') {
            emptyState.style.display = 'none';
        }

        // 1. Show user message
        appendMessage('user', query);
        userInput.value = '';

        // 2. Show typing indicator
        showTypingIndicator();

        try {
            // 3. Call API with session_id if exists
            const bodyData = { query: query };
            if (currentSessionId) bodyData.session_id = currentSessionId;

            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(bodyData)
            });

            const data = await response.json();

            // 4. Remove typing indicator and show response
            removeTypingIndicator();

            if (response.ok) {
                appendMessage('bot', data.answer);
                if (!currentSessionId && data.session_id) {
                    currentSessionId = data.session_id;
                }
                fetchSessions(); // refresh list to show new/updated session
            } else {
                appendMessage('bot', "Xin lỗi, đã có lỗi xảy ra: " + (data.detail || "Lỗi máy chủ"));
            }
        } catch (error) {
            console.error('Error:', error);
            removeTypingIndicator();
            appendMessage('bot', "Xin lỗi, không thể kết nối tới máy chủ. Vui lòng thử lại sau.");
        }
    });

    // New Chat Button functionality
    newChatBtn.addEventListener('click', () => {
        currentSessionId = null;
        const messages = chatMessages.querySelectorAll('.message');
        messages.forEach(msg => msg.remove());

        if (emptyState) {
            emptyState.style.display = 'flex';
        }
        fetchSessions(); // update active class
    });

    // Clear History Button functionality (legacy)
    if (clearHistoryBtn) {
        clearHistoryBtn.addEventListener('click', async () => {
            if (!confirm("Chức năng này không còn dùng nữa vì bạn có thể xóa từng session. Bạn có muốn tải lại trang?")) return;
            window.location.reload();
        });
    }

    // --- AUTHENTICATION & MODAL LOGIC ---
    const authModal = document.getElementById('auth-modal');
    const closeAuthModalBtn = document.getElementById('close-auth-modal');
    const loginBtn = document.getElementById('login-btn');
    const loginText = document.getElementById('login-text');
    const uploadPdfNav = document.getElementById('upload-pdf-nav');

    const tabLogin = document.getElementById('tab-login');
    const tabRegister = document.getElementById('tab-register');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');

    function isAdminUser(user) {
        return Boolean(
            user
            && typeof user.role === 'string'
            && user.role.trim().toLowerCase() === 'admin'
        );
    }

    function setAdminUploadVisibility(user) {
        if (uploadPdfNav) {
            uploadPdfNav.hidden = !isAdminUser(user);
        }
    }

    // Check Auth Status on Load
    async function checkAuth() {
        setAdminUploadVisibility(null);
        try {
            const res = await fetch('/auth/me');
            if (res.ok) {
                currentUser = await res.json();
                loginText.textContent = `Logout (${currentUser.username})`;
                setAdminUploadVisibility(currentUser);
                fetchSessions(); // load sessions after auth
            } else {
                currentUser = null;
                loginText.textContent = 'Log in';
            }
        } catch (e) {
            currentUser = null;
            loginText.textContent = 'Log in';
        }
    }
    checkAuth();

    // Modal behavior
    loginBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        if (currentUser) {
            // Logout
            try {
                await fetch('/auth/logout', { method: 'POST' });
                window.location.reload(); // Reload to clear state
            } catch (error) {
                console.error("Logout failed", error);
            }
        } else {
            // Open Modal
            authModal.classList.add('active');
        }
    });

    closeAuthModalBtn.addEventListener('click', () => {
        authModal.classList.remove('active');
    });

    // Tab Switching
    tabLogin.addEventListener('click', () => {
        tabLogin.classList.add('active');
        tabRegister.classList.remove('active');
        loginForm.classList.add('active');
        registerForm.classList.remove('active');
    });

    tabRegister.addEventListener('click', () => {
        tabRegister.classList.add('active');
        tabLogin.classList.remove('active');
        registerForm.classList.add('active');
        loginForm.classList.remove('active');
    });

    // Login Form Submit
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;
        const errorDiv = document.getElementById('login-error');
        errorDiv.textContent = '';

        try {
            const res = await fetch('/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await res.json();

            if (res.ok) {
                authModal.classList.remove('active');
                window.location.reload(); // Reload to apply auth state
            } else {
                errorDiv.textContent = data.detail || 'Login failed';
            }
        } catch (err) {
            errorDiv.textContent = 'Network error';
        }
    });

    // Register Form Submit
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('register-username').value;
        const password = document.getElementById('register-password').value;
        const errorDiv = document.getElementById('register-error');
        errorDiv.textContent = '';

        try {
            const res = await fetch('/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await res.json();

            if (res.ok) {
                alert('Đăng ký thành công! Vui lòng đăng nhập.');
                tabLogin.click();
                document.getElementById('login-username').value = username;
            } else {
                errorDiv.textContent = data.detail || 'Registration failed';
            }
        } catch (err) {
            errorDiv.textContent = 'Network error';
        }
    });

    // Admin PDF upload modal
    const uploadPdfBtn = document.getElementById('upload-pdf-btn');
    const uploadText = document.getElementById('upload-text');
    const uploadModal = document.getElementById('upload-modal');
    const uploadForm = document.getElementById('upload-form');
    const closeUploadModalBtn = document.getElementById('close-upload-modal');
    const cancelUploadBtn = document.getElementById('cancel-upload');
    const submitUploadBtn = document.getElementById('submit-upload');
    const submitUploadText = document.getElementById('submit-upload-text');
    const pdfUploadInput = document.getElementById('pdf-upload');
    const documentClassSelect = document.getElementById('document-class');
    const academicYearGroup = document.getElementById('academic-year-group');
    const academicYearInput = document.getElementById('academic-year');
    const uploadError = document.getElementById('upload-error');
    const maxPdfSizeBytes = 5 * 1024 * 1024;
    const allowedPdfMimeTypes = new Set(['application/pdf', 'application/x-pdf']);
    const allowedDocumentClasses = new Set([
        'tuition_actual_rate',
        'tuition_exemption_basis',
        'tuition_exemption_policy',
        'scholarship',
        'student_loan',
        'social_support',
        'other'
    ]);
    const classesRequiringAcademicYear = new Set([
        'tuition_actual_rate',
        'tuition_exemption_basis'
    ]);
    let uploadInProgress = false;

    if (
        uploadPdfBtn && uploadModal && uploadForm && closeUploadModalBtn
        && cancelUploadBtn && submitUploadBtn && pdfUploadInput
        && documentClassSelect && academicYearGroup && academicYearInput && uploadError
    ) {
        function requiresAcademicYear(documentClass = documentClassSelect.value) {
            return classesRequiringAcademicYear.has(documentClass);
        }

        function clearUploadError() {
            uploadError.textContent = '';
            pdfUploadInput.removeAttribute('aria-invalid');
            documentClassSelect.removeAttribute('aria-invalid');
            academicYearInput.removeAttribute('aria-invalid');
        }

        function showUploadError(message, field) {
            uploadError.textContent = message;
            if (field) {
                field.setAttribute('aria-invalid', 'true');
                field.focus();
            }
        }

        function updateAcademicYearField() {
            const isRequired = requiresAcademicYear();
            academicYearGroup.hidden = !isRequired;
            academicYearInput.required = isRequired;
            academicYearInput.disabled = !isRequired || uploadInProgress;
            academicYearInput.setAttribute('aria-required', String(isRequired));
            academicYearInput.setCustomValidity('');

            if (!isRequired) {
                academicYearInput.value = '';
                academicYearInput.removeAttribute('aria-invalid');
            }
        }

        function resetUploadForm() {
            uploadForm.reset();
            clearUploadError();
            updateAcademicYearField();
        }

        function setUploadLoading(isLoading) {
            uploadInProgress = isLoading;
            uploadForm.setAttribute('aria-busy', String(isLoading));
            pdfUploadInput.disabled = isLoading;
            documentClassSelect.disabled = isLoading;
            submitUploadBtn.disabled = isLoading;
            cancelUploadBtn.disabled = isLoading;
            closeUploadModalBtn.disabled = isLoading;
            uploadPdfBtn.setAttribute('aria-disabled', String(isLoading));

            if (submitUploadText) {
                submitUploadText.textContent = isLoading ? 'Đang xử lý...' : 'Tải lên';
            }
            if (uploadText) {
                uploadText.textContent = isLoading ? 'Đang xử lý...' : 'Upload PDF';
            }

            updateAcademicYearField();
        }

        function openUploadModal() {
            if (!isAdminUser(currentUser) || uploadInProgress) {
                if (!isAdminUser(currentUser)) {
                    alert('Chỉ tài khoản quản trị mới có thể tải tài liệu lên.');
                }
                return;
            }

            resetUploadForm();
            uploadModal.classList.add('active');
            uploadModal.setAttribute('aria-hidden', 'false');
            window.setTimeout(() => pdfUploadInput.focus(), 0);
        }

        function closeUploadModal(options = {}) {
            const { force = false, reset = true } = options;
            if (uploadInProgress && !force) {
                return;
            }

            uploadModal.classList.remove('active');
            uploadModal.setAttribute('aria-hidden', 'true');
            if (reset) {
                resetUploadForm();
            }
            uploadPdfBtn.focus();
        }

        function validateUploadForm() {
            const file = pdfUploadInput.files && pdfUploadInput.files[0];
            if (!file) {
                return { message: 'Vui lòng chọn một tệp PDF.', field: pdfUploadInput };
            }

            const hasPdfExtension = typeof file.name === 'string' && file.name.toLowerCase().endsWith('.pdf');
            const mimeType = typeof file.type === 'string' ? file.type.toLowerCase() : '';
            if (!hasPdfExtension || !allowedPdfMimeTypes.has(mimeType)) {
                return { message: 'Tệp phải có đuôi .pdf và MIME type hợp lệ.', field: pdfUploadInput };
            }

            if (file.size <= 0) {
                return { message: 'Tệp PDF không được để trống.', field: pdfUploadInput };
            }

            if (file.size > maxPdfSizeBytes) {
                return { message: 'Tệp PDF không được vượt quá 5 MiB.', field: pdfUploadInput };
            }

            const documentClass = documentClassSelect.value;
            if (!allowedDocumentClasses.has(documentClass)) {
                return { message: 'Vui lòng chọn loại tài liệu hợp lệ.', field: documentClassSelect };
            }

            let academicYear = '';
            if (requiresAcademicYear(documentClass)) {
                academicYear = academicYearInput.value.trim();
                const match = /^(\d{4})-(\d{4})$/.exec(academicYear);
                if (!match || Number(match[2]) !== Number(match[1]) + 1) {
                    return {
                        message: 'Năm học phải có dạng YYYY-YYYY và gồm hai năm liên tiếp, ví dụ 2025-2026.',
                        field: academicYearInput
                    };
                }
            }

            return { file, documentClass, academicYear };
        }

        async function readUploadResponse(response) {
            const responseText = await response.text();
            if (!responseText) {
                return {};
            }

            try {
                return JSON.parse(responseText);
            } catch (error) {
                console.error('Unable to parse upload response:', error);
                return {};
            }
        }

        function getUploadErrorMessage(result, fallback) {
            const detail = result && result.detail;
            if (typeof detail === 'string' && detail.trim()) {
                return detail;
            }
            if (Array.isArray(detail)) {
                const messages = detail
                    .map(item => (item && typeof item.msg === 'string' ? item.msg : ''))
                    .filter(Boolean);
                if (messages.length) {
                    return messages.join(' ');
                }
            }
            return fallback;
        }

        uploadPdfBtn.addEventListener('click', (event) => {
            event.preventDefault();
            openUploadModal();
        });

        closeUploadModalBtn.addEventListener('click', () => closeUploadModal());
        cancelUploadBtn.addEventListener('click', () => closeUploadModal());

        uploadModal.addEventListener('click', (event) => {
            if (event.target === uploadModal) {
                closeUploadModal();
            }
        });

        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape' && uploadModal.classList.contains('active')) {
                closeUploadModal();
            }
        });

        documentClassSelect.addEventListener('change', () => {
            clearUploadError();
            updateAcademicYearField();
        });
        pdfUploadInput.addEventListener('change', clearUploadError);
        academicYearInput.addEventListener('input', clearUploadError);

        uploadForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            if (uploadInProgress) {
                return;
            }

            clearUploadError();
            if (!isAdminUser(currentUser)) {
                showUploadError('Phiên đăng nhập quản trị không còn hợp lệ. Vui lòng đăng nhập lại.');
                setAdminUploadVisibility(null);
                return;
            }

            const validation = validateUploadForm();
            if (validation.message) {
                showUploadError(validation.message, validation.field);
                return;
            }

            const formData = new FormData();
            formData.append('file', validation.file);
            formData.append('document_class', validation.documentClass);
            if (validation.academicYear) {
                formData.append('academic_year', validation.academicYear);
            }

            let uploadSucceeded = false;
            let successMessage = 'Tài liệu đã được tải lên.';
            setUploadLoading(true);

            try {
                const response = await fetch('/document/upload', {
                    method: 'POST',
                    credentials: 'same-origin',
                    body: formData
                });
                const result = await readUploadResponse(response);

                if (response.ok) {
                    uploadSucceeded = true;
                    if (typeof result.message === 'string' && result.message.trim()) {
                        successMessage = result.message;
                    }
                } else {
                    if (response.status === 401 || response.status === 403) {
                        await checkAuth();
                    }
                    showUploadError(getUploadErrorMessage(result, 'Không thể xử lý tệp PDF.'));
                }
            } catch (error) {
                console.error('Upload error:', error);
                showUploadError('Không thể kết nối tới máy chủ. Vui lòng thử lại.');
            } finally {
                setUploadLoading(false);
            }

            if (uploadSucceeded) {
                closeUploadModal();
                alert(`Thành công: ${successMessage}`);
            }
        });

        updateAcademicYearField();
    }

});
