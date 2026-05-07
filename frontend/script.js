const GenesisApp = (() => {
    let state = {
        model: "qwen2.5-coder",
        mode: "chat",
        loading: false,
        history: [] 
    };

    async function init() {
        console.log("GenesisAI APP: Initializing...");
        bindEvents();
        
        if (typeof GenesisUI !== 'undefined') {
            GenesisUI.init();
        }

        await loadModels();
        await loadSystemModes();
    }

    function bindEvents() {
        document.getElementById('sendBtn')?.addEventListener('click', handleSend);
        document.getElementById('chatInput')?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
            }
        });
        document.getElementById('modeSelect')?.addEventListener('change', handleModeChange);
        document.getElementById('uploadBtn')?.addEventListener('click', handleUpload);
    }

    async function loadModels() {
        const modelSelect = document.getElementById('modelSelect');
        if (!modelSelect) return;

        const data = await GenesisAPI.getModels();
        
        if (data && data.models && data.models.length > 0) {
            modelSelect.innerHTML = '';
            data.models.forEach(m => {
                const opt = document.createElement('option');
                opt.value = m;
                opt.textContent = m.toUpperCase();
                if (m.includes('qwen')) {
                    opt.selected = true;
                    state.model = m;
                }
                modelSelect.appendChild(opt);
            });
            if (!state.model && data.models.length > 0) {
                state.model = data.models[0];
            }
        }
        
        modelSelect.addEventListener('change', (e) => {
            state.model = e.target.value;
            console.log("Model changed to:", state.model);
        });
    }

    async function loadSystemModes() {
        const modeSelect = document.getElementById('modeSelect');
        if (!modeSelect) return;
        
        try {
            const response = await fetch('/api/modes');
            const data = await response.json();

            if (data.modes) {
                modeSelect.innerHTML = ''; 
                data.modes.forEach(m => {
                    const opt = document.createElement('option');
                    opt.value = m.id;
                    opt.textContent = m.name;
                    modeSelect.appendChild(opt);
                });
                
                if(data.modes.length > 0) {
                    state.mode = data.modes[0].id;
                    GenesisUI.setModeUI(state.mode);
                }
            }
        } catch (e) {
            console.error("Failed to load modes", e);
        }
    }

    async function handleSend() {
        const input = document.getElementById('chatInput');
        const message = input.value.trim();
        if (!message || state.loading) return;

        state.loading = true;
        GenesisUI.setLoading(true);
        GenesisUI.appendMessage('USER', message, state.mode);
        input.value = '';
        input.style.height = 'auto'; // Reset height

        try {
            // Using dynamically fetched mode instead of hardcoded
            const res = await GenesisAPI.postChat(message, state.model, state.mode, state.history);
            
            state.history.push({ role: "user", content: message });
            state.history.push({ role: "assistant", agent: res.source, content: res.reply });

            GenesisUI.appendMessage(res.source, res.reply);
        } catch (err) {
            GenesisUI.appendMessage("SYSTEM", "Error: " + err.message);
        }

        state.loading = false;
        GenesisUI.setLoading(false);
    }

    async function saveConversation() {
        if (state.history.length === 0) return alert("No messages to save.");
        
        let textContent = "GenesisAI CHAT SESSION\n================\n\n";
        state.history.forEach(msg => {
            textContent += `${msg.role.toUpperCase()}: ${msg.content}\n\n`;
        });
        
        // Trigger browser download dialog
        const blob = new Blob([textContent], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `GenesisAI_Session_${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    async function commitToMemory() {
        if (state.history.length === 0) return alert("No messages to memorize.");
        const status = document.getElementById('ragStatus');
        
        status.innerText = "Summarizing for memory...";
        // Show immediate notification in the chat
        GenesisUI.appendMessage('SYSTEM', "*(⏳ Memory Agent is summarizing the conversation and saving it to ChromaDB...)*");
        GenesisUI.setLoading(true);
        
        try {
            const res = await fetch('/api/memory/commit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ history: state.history, model: state.model })
            });
            const data = await res.json();
            
            if(data.status === "error") throw new Error(data.reply);
            
            status.innerText = "Memory Committed!";
            GenesisUI.appendMessage('SYSTEM', `**🧠 Memory Agent Completed**\n${data.reply}`);
        } catch(e) {
            status.innerText = "Memory commit failed.";
            GenesisUI.appendMessage('SYSTEM', "Error committing to memory: " + e.message);
        }
        
        GenesisUI.setLoading(false);
    }

    async function wipeMemory() {
        if (confirm("⚠️ WARNING: Are you sure you want to permanently delete all RAG documents and long-term memory from the database? This cannot be undone.")) {
            const status = document.getElementById('ragStatus');
            status.innerText = "Wiping database...";
            GenesisUI.setLoading(true);
            
            try {
                const res = await fetch('/api/memory/wipe', { method: 'DELETE' });
                const data = await res.json();
                
                if(data.status === "error") throw new Error(data.reply);
                
                status.innerText = "Database Wiped!";
                GenesisUI.appendMessage('SYSTEM', `**🗑️ Database Wiped**\n${data.reply}`);
            } catch(e) {
                status.innerText = "Wipe failed.";
                GenesisUI.appendMessage('SYSTEM', "Error wiping memory: " + e.message);
            }
            
            GenesisUI.setLoading(false);
        }
    }

    function clearChat() {
        const chat = document.getElementById('chatDisplay');
        chat.innerHTML = `
            <div class="welcome-screen">
                <h1>Welcome to GenesisAI</h1>
                <p>Select a mode and start interacting.</p>
            </div>
        `;
        state.history = [];
    }

    async function handleModeChange(e) {
        state.mode = e.target.value;
        GenesisUI.setModeUI(state.mode);
        await GenesisAPI.setSystemMode(state.mode);
    }

    async function handleUpload() {
        const fileInput = document.getElementById('pdfUpload');
        const status = document.getElementById('ragStatus');
        if (!fileInput.files[0]) return alert("Select File First");
        
        status.innerText = "Indexing...";
        GenesisUI.setLoading(true);
        
        try {
            const res = await GenesisAPI.uploadDocument(fileInput.files[0]);
            status.innerText = res.reply;
            
            // Show a clear confirmation in the chat interface
            GenesisUI.appendMessage('SYSTEM', `**Document Loaded Successfully!**\n${res.reply}\n\n*Make sure to select **RAG MODE** from the System Mode dropdown before asking questions about this document.*`);
        } catch(err) {
            status.innerText = "Upload failed.";
            GenesisUI.appendMessage('SYSTEM', "Error uploading document: " + err.message);
        }
        
        GenesisUI.setLoading(false);
        fileInput.value = ''; // Reset file input
    }

    return { init, clearChat, saveConversation, commitToMemory, wipeMemory };
})();

window.addEventListener('DOMContentLoaded', GenesisApp.init);