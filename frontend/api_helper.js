/**
 * GenesisAI API HELPER
 * Handles all backend communication
 */
const GenesisAPI = {
    async getModels() {
        try {
            const res = await fetch('/api/models');
            const data = await res.json();
            console.log("API HELPER: Models fetched ->", data); // Verification log
            return data;
        } catch (err) {
            console.error("API HELPER: Fetch failed", err);
            return { models: ["qwen2.5-coder"] }; // Resilient fallback[cite: 4]
        }
    },

    async postChat(message, model, mode="chat", history=[]) {
        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message, model, mode, history })
            });
            return await res.json();
        } catch (e) {
            return { source: "SYSTEM", reply: "Network Error: " + e.message };
        }
    },

    async saveSession(payload) {
        try {
            const res = await fetch('/api/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            return await res.json();
        } catch (e) {
            return { status: "error", message: e.message };
        }
    },

    async setSystemMode(mode) {
        return fetch('/api/mode', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode })
        });
    },

    async uploadDocument(file) {
        const formData = new FormData();
        formData.append('file', file);
        const res = await fetch('/api/upload', { method: 'POST', body: formData });
        return await res.json();
    }
};