// Global Variables
let currentLang = '{{ lang }}' || 'en';
let currentPage = 'dashboard';

// Language Toggle
function toggleLang(lang) {
    currentLang = lang;
    document.querySelectorAll('[data-lang]').forEach(el => {
        el.textContent = translations[currentLang][el.dataset.lang] || el.dataset.lang;
    });
    // Reload page sections if needed
    loadDashboard();
    if (currentPage !== 'dashboard') showPage(currentPage);
}

// FAB Menu Toggle
document.getElementById('fab-btn').addEventListener('click', function() {
    const menu = document.getElementById('fab-menu');
    menu.classList.toggle('hidden');
});

// Close Modals
function closeModal(modalId) {
    document.getElementById(modalId + '-modal').classList.add('hidden');
}

// Open Modal
function openModal(type) {
    document.querySelectorAll('[id$="-modal"]').forEach(m => m.classList.add('hidden'));
    document.getElementById(type + '-modal').classList.remove('hidden');
}

// Load Dashboard on Start
document.addEventListener('DOMContentLoaded', loadDashboard);

// Dashboard Load
function loadDashboard() {
    loadWeatherSummary();
    loadMarketPrices();
    loadNews();
}

// Weather Summary (Open-Meteo via /weather/{state})
function loadWeatherSummary() {
    const state = 'punjab'; // Default; enhance with user input
    fetch(`/weather/${state}`)
        .then(resp => resp.json())
        .then(data => {
            const content = document.getElementById('weather-content');
            if (data.current_weather) {
                content.innerHTML = `
                    <p class="text-lg font-bold">${data.current_weather.temperature}°C</p>
                    <p>${data.current_weather.weathercode === 0 ? translations[currentLang]['sunny'] || 'Sunny' : translations[currentLang]['cloudy'] || 'Cloudy'}</p>
                    <p>${translations[currentLang]['wind'] || 'Wind'}: ${data.current_weather.windspeed} km/h</p>
                `;
            } else {
                content.innerHTML = `<p class="text-red-500">${translations[currentLang]['weather_error'] || 'Weather unavailable'}</p>`;
            }
        })
        .catch(() => {
            document.getElementById('weather-content').innerHTML = `<p class="text-red-500">${translations[currentLang]['weather_error'] || 'Weather unavailable'}</p>`;
        });
}

// Market Prices (Mock Data)
function loadMarketPrices() {
    const mockData = [
        {crop: 'Wheat', min: 2100, max: 2300, modal: 2200},
        {crop: 'Rice', min: 1700, max: 1900, modal: 1800},
        {crop: 'Maize', min: 1500, max: 1700, modal: 1600}
    ];
    const content = document.getElementById('market-content');
    content.innerHTML = mockData.map(item => `
        <li class="flex justify-between">
            <span>${translations[currentLang][item.crop.toLowerCase()] || item.crop}:</span>
            <span>₹${item.modal}/quintal</span>
        </li>
    `).join('');
}

// News (NewsAPI via /crop-news/{crop})
function loadNews() {
    const crop = 'wheat'; // Default; enhance with user input
    fetch(`/crop-news/${crop}`)
        .then(resp => resp.json())
        .then(data => {
            const content = document.getElementById('news-content');
            content.innerHTML = (data.articles || []).map(article => `
                <li class="p-2 bg-gray-50 rounded hover:bg-gray-100 transition truncate">
                    <strong>${article.title.substring(0, 50)}...</strong>
                    <p class="text-sm text-gray-600">${article.source.name}</p>
                </li>
            `).join('');
        })
        .catch(() => {
            document.getElementById('news-content').innerHTML = `<p class="text-red-500">${translations[currentLang]['news_error'] || 'News unavailable'}</p>`;
        });
}

// Micro Calculator Modal
function calculateAdvice() {
    const crop = document.getElementById('crop-type').value;
    const stage = document.getElementById('growth-stage').value;
    const state = document.getElementById('state').value;
    const lang = document.getElementById('lang').value;

    fetch('/micro-calculator/get_advice', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({crop_type: crop, growth_stage: stage, state: state, lang: lang})
    })
    .then(resp => resp.json())
    .then(data => {
        if (data.success) {
            const result = document.getElementById('calculator-result');
            result.innerHTML = `
                <div class="space-y-2">
                    <h4 class="font-bold">${translations[currentLang]['irrigation_title'] || 'Irrigation:'}</h4>
                    <p>${translations[currentLang]['et0_label'] || 'ET₀'}: ${data.advice.irrigation.et0} mm/day</p>
                    <p>${translations[currentLang]['etc_label'] || 'ETc'}: ${data.advice.irrigation.etc} mm/day</p>
                    <p>${translations[currentLang]['irrigation_need_label'] || 'Irrigation Need'}: ${data.advice.irrigation.irrigation_need} mm</p>
                    <h4 class="font-bold mt-4">${translations[currentLang]['fertilizer_title'] || 'Fertilizer:'}</h4>
                    <p>${translations[currentLang]['urea_label'] || 'Urea'}: ${data.advice.fertilizer.total_fertilizer.urea} kg/ha</p>
                    <p>${translations[currentLang]['dap_label'] || 'DAP'}: ${data.advice.fertilizer.total_fertilizer.dap} kg/ha</p>
                    <p>${translations[currentLang]['mop_label'] || 'MOP'}: ${data.advice.fertilizer.total_fertilizer.mop} kg/ha</p>
                </div>
            `;
        } else {
            document.getElementById('calculator-result').innerHTML = `<p class="text-red-500">${translations[currentLang]['error'] || 'Error'}: ${data.error}</p>`;
        }
    });
}

// Voice Chat (Integrate with /chat/voice_chat)
function openVoiceChat() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'audio/*';
    input.onchange = function(e) {
        const file = e.target.files[0];
        const formData = new FormData();
        formData.append('audio', file);

        fetch('/chat/voice_chat', {
            method: 'POST',
            body: formData
        })
        .then(resp => resp.json())
        .then(data => {
            if (data.voice_url) {
                const audio = new Audio(data.voice_url);
                audio.play();
                document.getElementById('chatbot-content').innerHTML += `<p><strong>${translations[currentLang]['you'] || 'You'}:</strong> ${data.transcript}</p><p><strong>${translations[currentLang]['crop_drop'] || 'Crop Drop'}:</strong> ${data.response_text}</p>`;
            } else {
                document.getElementById('chatbot-content').innerHTML += `<p class="text-red-500">${translations[currentLang]['voice_error'] || 'Voice response failed'}</p>`;
            }
        });
    };
    input.click();
}

// Image Analysis (Integrate with /image-analysis/analyze)
function analyzeImage() {
    const file = document.getElementById('image-file').files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('voice', 'true');
    formData.append('lang', currentLang);

    fetch('/image-analysis/analyze', {
        method: 'POST',
        body: formData
    })
    .then(resp => resp.json())
    .then(data => {
        document.getElementById('image-result').innerHTML = `
            <p><strong>${translations[currentLang]['predicted'] || 'Predicted'}:</strong> ${data.analysis_result.predicted_class}</p>
            <p><strong>${translations[currentLang]['cause'] || 'Cause'}:</strong> ${data.analysis_result.cause}</p>
            <p><strong>${translations[currentLang]['treatment'] || 'Treatment'}:</strong> ${data.analysis_result.cure}</p>
            ${data.voice_url ? `<audio controls src="${data.voice_url}"></audio>` : ''}
        `;
    });
}

// Text Chat (Integrate with /chat/general)
function sendTextChat() {
    const prompt = document.getElementById('chat-prompt').value;
    if (!prompt) return;

    fetch('/chat/general', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({prompt: prompt})
    })
    .then(resp => resp.json())
    .then(data => {
        document.getElementById('chatbot-content').innerHTML += `<p><strong>${translations[currentLang]['you'] || 'You'}:</strong> ${prompt}</p><p><strong>${translations[currentLang]['crop_drop'] || 'Crop Drop'}:</strong> ${data.response}</p>`;
        document.getElementById('chat-prompt').value = '';
    });
}

// Page Navigation (Toggle Full Pages)
function showPage(page) {
    currentPage = page;
    document.querySelectorAll('#full-pages > div').forEach(div => div.classList.add('hidden'));
    document.getElementById(page + '-page').classList.remove('hidden');
    if (page !== 'dashboard') {
        document.getElementById('full-pages').classList.remove('hidden');
    } else {
        document.getElementById('full-pages').classList.add('hidden');
    }
    if (page === 'weather') loadWeatherPage();
    if (page === 'market') loadMarketPage();
    if (page === 'news') loadNewsPage();
}

// Load Specific Pages
function loadWeatherPage() {
    const state = document.getElementById('state-select').value;
    fetch(`/weather/${state}`)
        .then(resp => resp.json())
        .then(data => {
            const forecast = document.getElementById('weather-forecast');
            forecast.innerHTML = data.hourly.time.slice(0, 24).map((time, i) => `
                <div class="text-center p-2 border rounded">
                    <p>${new Date(time).toLocaleTimeString()}</p>
                    <p>${data.hourly.temperature_2m[i]}°C</p>
                    <p>${data.hourly.precipitation[i]}mm</p>
                </div>
            `).join('');
        });
}

document.getElementById('state-select').addEventListener('change', loadWeatherPage);

function loadMarketPage() {
    const mockData = [
        {crop: 'Wheat', min: 2100, max: 2300, modal: 2200},
        {crop: 'Rice', min: 1700, max: 1900, modal: 1800},
        {crop: 'Maize', min: 1500, max: 1700, modal: 1600}
    ];
    const tbody = document.getElementById('market-table-body');
    tbody.innerHTML = mockData.map(item => `
        <tr>
            <td class="border p-2">${translations[currentLang][item.crop.toLowerCase()] || item.crop}</td>
            <td class="border p-2">₹${item.min}</td>
            <td class="border p-2">₹${item.max}</td>
            <td class="border p-2">₹${item.modal}</td>
        </tr>
    `).join('');
}

function loadNewsPage() {
    const crop = 'wheat'; // Default; enhance with user input
    fetch(`/crop-news/${crop}`)
        .then(resp => resp.json())
        .then(data => {
            const list = document.getElementById('news-list');
            list.innerHTML = (data.articles || []).map(article => `
                <div class="p-4 border rounded bg-gray-50">
                    <h4 class="font-bold">${article.title}</h4>
                    <p class="text-sm text-gray-600">${article.description}</p>
                    <a href="${article.url}" target="_blank" class="text-blue-500">${translations[currentLang]['read_more'] || 'Read more'}</a>
                </div>
            `).join('');
        });
}

// Navigation Buttons
document.querySelectorAll('.card-hover').forEach(card => {
    card.addEventListener('click', function() {
        const id = this.id.split('-')[0];
        if (id === 'weather') showPage('weather');
        if (id === 'market') showPage('market');
        if (id === 'news') showPage('news');
    });
});

// Intersection Observer for Scroll Animations
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate-fade-in-up');
        }
    });
}, { threshold: 0.1 });

document.querySelectorAll('.animate-fade-in-up').forEach(el => observer.observe(el));