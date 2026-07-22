document.addEventListener('DOMContentLoaded', () => {
    // API Base URL - determine relative or absolute based on location
    const API_BASE = window.location.origin.includes('http') 
        ? `${window.location.origin}/api` 
        : 'http://localhost:8000/api';

    // Elements
    const healthBadge = document.getElementById('healthBadge');
    const contactForm = document.getElementById('contactForm');
    const submitBtn = document.getElementById('submitBtn');
    const submitSpinner = document.getElementById('submitSpinner');
    const formAlert = document.getElementById('formAlert');

    // Inputs
    const nameInput = document.getElementById('nameInput');
    const phoneInput = document.getElementById('phoneInput');
    const emailInput = document.getElementById('emailInput');
    const commentInput = document.getElementById('commentInput');
    const charCounter = document.getElementById('charCounter');

    // Field errors
    const nameError = document.getElementById('nameError');
    const phoneError = document.getElementById('phoneError');
    const emailError = document.getElementById('emailError');
    const commentError = document.getElementById('commentError');

    // Result container
    const resultPlaceholder = document.getElementById('resultPlaceholder');
    const resultContent = document.getElementById('resultContent');
    const requestId = document.getElementById('requestId');
    const responseStatusTitle = document.getElementById('responseStatusTitle');
    const responseMessage = document.getElementById('responseMessage');
    const aiStatusTag = document.getElementById('aiStatusTag');
    const sentimentPill = document.getElementById('sentimentPill');
    const sentimentValue = document.getElementById('sentimentValue');
    const categoryTag = document.getElementById('categoryTag');
    const aiSuggestedReply = document.getElementById('aiSuggestedReply');

    // Metrics elements
    const refreshMetricsBtn = document.getElementById('refreshMetricsBtn');
    const metricTotal = document.getElementById('metricTotal');
    const metricAiSuccess = document.getElementById('metricAiSuccess');
    const metricAiFallback = document.getElementById('metricAiFallback');
    const countPositive = document.getElementById('countPositive');
    const countNeutral = document.getElementById('countNeutral');
    const countNegative = document.getElementById('countNegative');
    const barPositive = document.getElementById('barPositive');
    const barNeutral = document.getElementById('barNeutral');
    const barNegative = document.getElementById('barNegative');

    // Character counter for comment
    commentInput.addEventListener('input', () => {
        charCounter.textContent = commentInput.value.length;
    });

    // 1. Health Check
    async function checkHealth() {
        try {
            const res = await fetch(`${API_BASE}/health`);
            if (res.ok) {
                healthBadge.querySelector('.status-dot').className = 'status-dot online';
                healthBadge.querySelector('.status-text').textContent = 'API Доступен';
            } else {
                throw new Error('API Error');
            }
        } catch (err) {
            healthBadge.querySelector('.status-dot').className = 'status-dot offline';
            healthBadge.querySelector('.status-text').textContent = 'API Офлайн';
        }
    }

    // 2. Metrics Fetcher
    async function fetchMetrics() {
        try {
            const res = await fetch(`${API_BASE}/metrics`);
            if (!res.ok) return;
            const data = await res.json();

            metricTotal.textContent = data.total_contacts || 0;
            metricAiSuccess.textContent = data.ai_success_count || 0;
            metricAiFallback.textContent = data.ai_fallback_count || 0;

            const dist = data.sentiment_distribution || {};
            const pos = dist.positive || 0;
            const neu = dist.neutral || 0;
            const neg = dist.negative || 0;
            const total = pos + neu + neg || 1; // avoid divide by zero

            countPositive.textContent = pos;
            countNeutral.textContent = neu;
            countNegative.textContent = neg;

            barPositive.style.width = `${Math.round((pos / total) * 100)}%`;
            barNeutral.style.width = `${Math.round((neu / total) * 100)}%`;
            barNegative.style.width = `${Math.round((neg / total) * 100)}%`;
        } catch (err) {
            console.error('Failed to load metrics:', err);
        }
    }

    refreshMetricsBtn.addEventListener('click', fetchMetrics);

    // 3. Client Validation
    function clearErrors() {
        [nameError, phoneError, emailError, commentError].forEach(el => el.textContent = '');
        [nameInput, phoneInput, emailInput, commentInput].forEach(el => el.classList.remove('is-invalid'));
        formAlert.classList.add('hidden');
    }

    function validateForm() {
        clearErrors();
        let isValid = true;

        const nameVal = nameInput.value.trim();
        if (nameVal.length < 2) {
            nameError.textContent = 'Имя должно содержать минимум 2 символа.';
            nameInput.classList.add('is-invalid');
            isValid = false;
        } else if (/\d/.test(nameVal)) {
            nameError.textContent = 'Имя не должно содержать цифры.';
            nameInput.classList.add('is-invalid');
            isValid = false;
        }

        const phoneVal = phoneInput.value.trim();
        const digitCount = (phoneVal.match(/\d/g) || []).length;
        if (phoneVal.length < 10 || digitCount < 10) {
            phoneError.textContent = 'Номер должен содержать минимум 10 цифр.';
            phoneInput.classList.add('is-invalid');
            isValid = false;
        }

        const emailVal = emailInput.value.trim();
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailVal)) {
            emailError.textContent = 'Введите корректный email адрес.';
            emailInput.classList.add('is-invalid');
            isValid = false;
        }

        const commentVal = commentInput.value.trim();
        if (commentVal.length < 10) {
            commentError.textContent = 'Сообщение должно содержать не менее 10 символов.';
            commentInput.classList.add('is-invalid');
            isValid = false;
        }

        return isValid;
    }

    // 4. Submit Handler
    contactForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!validateForm()) return;

        // UI Loading state
        submitBtn.disabled = true;
        submitSpinner.classList.remove('hidden');
        submitBtn.querySelector('.btn-text').textContent = 'Анализ...';

        const payload = {
            name: nameInput.value.trim(),
            phone: phoneInput.value.trim(),
            email: emailInput.value.trim(),
            comment: commentInput.value.trim()
        };

        try {
            const res = await fetch(`${API_BASE}/contact`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await res.json();

            if (!res.ok) {
                if (res.status === 422) {
                    formAlert.className = 'alert alert-danger';
                    formAlert.textContent = data.message || 'Ошибка валидации данных на сервере.';
                    formAlert.classList.remove('hidden');
                } else if (res.status === 429) {
                    formAlert.className = 'alert alert-danger';
                    formAlert.textContent = 'Превышен лимит запросов. Пожалуйста, подождите минуту.';
                    formAlert.classList.remove('hidden');
                } else {
                    throw new Error(data.message || 'Произошла ошибка при отправке');
                }
                return;
            }

            // Render Results
            renderResults(data);
            fetchMetrics(); // Refresh metrics automatically

        } catch (err) {
            formAlert.className = 'alert alert-danger';
            formAlert.textContent = err.message || 'Не удалось связаться с сервером.';
            formAlert.classList.remove('hidden');
        } finally {
            submitBtn.disabled = false;
            submitSpinner.classList.add('hidden');
            submitBtn.querySelector('.btn-text').textContent = 'Отправить заявку';
        }
    });

    // 5. Render Result Card
    function renderResults(data) {
        resultPlaceholder.classList.add('hidden');
        resultContent.classList.remove('hidden');

        requestId.textContent = data.id || 'N/A';
        responseStatusTitle.textContent = data.status === 'accepted' ? 'Заявка принята' : data.status;
        responseMessage.textContent = data.message || 'Ваш запрос обработан.';

        const ai = data.ai_analysis;
        if (ai) {
            if (ai.is_available) {
                aiStatusTag.textContent = 'OpenAI';
                aiStatusTag.style.background = 'rgba(16, 185, 129, 0.2)';
                aiStatusTag.style.color = '#34D399';
            } else {
                aiStatusTag.textContent = 'Fallback / Off';
                aiStatusTag.style.background = 'rgba(245, 158, 11, 0.2)';
                aiStatusTag.style.color = '#FBBF24';
            }

            // Sentiment Mapping
            const sentiment = (ai.sentiment || 'neutral').toLowerCase();
            sentimentPill.className = `sentiment-pill ${sentiment}`;
            
            const sentimentLabels = {
                positive: 'Позитивная',
                neutral: 'Нейтральная',
                negative: 'Негативная',
                unknown: 'Неопределено'
            };
            sentimentValue.textContent = sentimentLabels[sentiment] || sentiment;

            // Category Translation
            const categoryLabels = {
                pricing: 'Цены / Стоимость',
                cooperation: 'Сотрудничество',
                technical_question: 'Технический вопрос',
                complaint: 'Жалоба',
                other: 'Прочее'
            };
            categoryTag.textContent = categoryLabels[ai.category] || ai.category || 'Общее';

            // Reply
            aiSuggestedReply.textContent = ai.suggested_reply || 'Автоматический ответ недоступен.';
        }
    }

    // Init
    checkHealth();
    fetchMetrics();
    setInterval(checkHealth, 30000); // Check API health every 30s
});
