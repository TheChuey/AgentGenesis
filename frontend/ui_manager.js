const GenesisUI = {
    init() {
        const chatInput = document.getElementById('chatInput');
        
        // Auto-resize textarea
        chatInput?.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
            if(this.value === '') {
                this.style.height = 'auto';
            }
        });

        // Mobile menu toggle
        const menuBtn = document.getElementById('mobileMenuBtn');
        const sidebar = document.getElementById('sidePanel');
        menuBtn?.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 768 && 
                !sidebar.contains(e.target) && 
                e.target !== menuBtn) {
                sidebar.classList.remove('open');
            }
        });
    },

    setModeUI(mode) {
        document.body.classList.remove('rag-theme', 'researcher-theme', 'recall-theme');
        if (mode === 'rag') document.body.classList.add('rag-theme');
        if (mode === 'researcher') document.body.classList.add('researcher-theme');
        if (mode === 'recall') document.body.classList.add('recall-theme');
        
        const header = document.getElementById('modeHeader');
        if(header) {
            header.innerText = "MODE: " + mode.replace("_", " ").toUpperCase();
        }
    },

    appendMessage(source, text, mode=null) {
        const chat = document.getElementById('chatDisplay');
        const welcome = chat.querySelector('.welcome-screen');
        if (welcome) welcome.remove();

        const isUser = source === 'USER';
        
        const wrapper = document.createElement('div');
        wrapper.className = `msg-wrapper ${isUser ? 'user' : 'assistant'}`;
        if (source === 'RAG') wrapper.classList.add('rag-msg');
        
        if (isUser && mode) {
            wrapper.setAttribute('data-mode', mode);
        }

        wrapper.innerHTML = `
            <div class="msg-header">
                ${isUser ? 'You' : source}
            </div>
            <div class="msg-bubble">
                ${this.formatText(text)}
            </div>
        `;

        chat.appendChild(wrapper);
        chat.scrollTop = chat.scrollHeight;
    },

    setLoading(isLoading) {
        const btn = document.getElementById('sendBtn');
        const input = document.getElementById('chatInput');
        if (btn) btn.disabled = isLoading;
        if (input) input.disabled = isLoading;
        
        if (isLoading) {
            btn.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="spinner"><line x1="12" y1="2" x2="12" y2="6"></line><line x1="12" y1="18" x2="12" y2="22"></line><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line><line x1="2" y1="12" x2="6" y2="12"></line><line x1="18" y1="12" x2="22" y2="12"></line><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line></svg>`;
        } else {
            btn.innerHTML = `<svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>`;
        }
    },

    formatText(text) {
        if (!text) return "";
        let formatted = this.escapeHtml(text);
        
        formatted = formatted.replace(/```(\w*)\n([\s\S]*?)```/g, (match, lang, code) => {
            return `
            <div class="code-box">
                <div class="code-header">
                    <span>${lang || 'code'}</span>
                    <button onclick="navigator.clipboard.writeText(this.parentElement.nextElementSibling.innerText)" style="background:none;border:none;color:var(--accent);cursor:pointer;font-size:0.8rem">Copy</button>
                </div>
                <div class="code-content">${code}</div>
            </div>`;
        });
        
        formatted = formatted.replace(/`([^`]+)`/g, '<code style="background:rgba(255,255,255,0.1);padding:2px 4px;border-radius:4px;font-family:monospace">$1</code>');
        formatted = formatted.replace(/\n/g, '<br>');
        return formatted;
    },

    escapeHtml(str) {
        return str.replace(/[&<>"']/g, tag => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        }[tag]));
    }
};

const style = document.createElement('style');
style.textContent = `
@keyframes spin { 100% { transform: rotate(360deg); } }
.spinner { animation: spin 1s linear infinite; }
`;
document.head.appendChild(style);