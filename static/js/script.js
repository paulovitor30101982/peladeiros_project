// =========================================================================
// FUNÇÕES GLOBAIS
// (Funções de ajuda que serão usadas em todo o script)
// =========================================================================

const monthNames = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
];

/**
 * Gera os horários disponíveis para um container específico.
 * @param {HTMLElement} timeSlotsEl O elemento container dos horários.
 */
function generateTimeSlots(timeSlotsEl) {
    if (!timeSlotsEl) return;
    
    timeSlotsEl.innerHTML = '';
    const times = ['08:00', '09:00', '10:00', '11:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00'];
    
    times.forEach(time => {
        const slot = document.createElement('div');
        slot.className = 'time-slot';
        slot.setAttribute('aria-label', `Horário ${time}`);
        
        // Simula horários indisponíveis
        if (Math.random() > 0.7) {
            slot.classList.add('unavailable');
            slot.textContent = time;
        } else {
            slot.textContent = time;
            slot.addEventListener('click', () => {
                const currentCard = timeSlotsEl.closest('.item-card');
                currentCard.querySelectorAll('.time-slot.selected').forEach(el => el.classList.remove('selected'));
                slot.classList.add('selected');
            });
        }
        timeSlotsEl.appendChild(slot);
    });
}

/**
 * Renderiza o calendário para uma instância de card específica.
 * @param {HTMLElement} card O elemento .item-card que contém o calendário.
 */
function renderCalendar(card) {
    const calendarEl = card.querySelector('.calendar');
    const currentMonthEl = card.querySelector('.current-month');
    
    let currentMonth = parseInt(card.dataset.month);
    let currentYear = parseInt(card.dataset.year);

    calendarEl.innerHTML = '';
    currentMonthEl.textContent = `${monthNames[currentMonth]} ${currentYear}`;
    
    const dayNames = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];
    dayNames.forEach(day => {
        const dayEl = document.createElement('div');
        dayEl.className = 'day-name';
        dayEl.textContent = day;
        calendarEl.appendChild(dayEl);
    });
    
    const firstDay = new Date(currentYear, currentMonth, 1).getDay();
    const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
    
    for (let i = 0; i < firstDay; i++) {
        calendarEl.appendChild(document.createElement('div')).className = 'day empty';
    }
    
    for (let day = 1; day <= daysInMonth; day++) {
        const dayEl = document.createElement('div');
        dayEl.className = 'day';
        dayEl.textContent = day;
        dayEl.setAttribute('aria-label', `Dia ${day} de ${monthNames[currentMonth]}`);
        
        const today = new Date();
        today.setHours(0,0,0,0);
        const dayDate = new Date(currentYear, currentMonth, day);

        if (dayDate < today) {
            dayEl.classList.add('unavailable');
        } else {
            dayEl.addEventListener('click', () => {
                card.querySelectorAll('.day.selected').forEach(el => el.classList.remove('selected'));
                dayEl.classList.add('selected');
                generateTimeSlots(card.querySelector('.time-slots'));
            });
        }
        calendarEl.appendChild(dayEl);
    }
}

/**
 * Valida a seleção de data e horário para um item específico.
 * @param {HTMLElement} button O botão 'Adicionar ao Carrinho' que foi clicado.
 * @returns {object} Objeto com status de validação e detalhes da reserva.
 */
function validateReservation(button) {
    const card = button.closest('.item-card');
    const selectedDayEl = card.querySelector('.day.selected');
    const selectedTimeEl = card.querySelector('.time-slot.selected');
    
    if (!selectedDayEl || !selectedTimeEl) {
        alert('❌ Selecione uma data e horário válidos para este item antes de adicionar ao carrinho.');
        return { isValid: false };
    }
    
    const selectedDay = parseInt(selectedDayEl.textContent);
    const [monthName, yearStr] = card.querySelector('.current-month').textContent.split(' ');
    const selectedYear = parseInt(yearStr);
    const selectedTime = selectedTimeEl.textContent;
    
    const selectedMonth = monthNames.indexOf(monthName);
    const [hours, minutes] = selectedTime.split(':').map(Number);
    const selectedDate = new Date(selectedYear, selectedMonth, selectedDay, hours, minutes);
    const now = new Date();

    if (selectedDate < now) {
        alert('⏰ Não é possível reservar para datas/horários passados.');
        return { isValid: false };
    }
    
    return { 
        isValid: true,
        day: selectedDay,
        month: monthName,
        year: selectedYear,
        time: selectedTime
    };
}


// =========================================================================
// INICIALIZAÇÃO DO SCRIPT QUANDO O DOCUMENTO ESTIVER PRONTO
// =========================================================================

document.addEventListener('DOMContentLoaded', () => {

    // ---------------------------------------------------------------------
    // CÓDIGO DE MÁSCARAS DE FORMULÁRIO
    // ---------------------------------------------------------------------
    const masks = {
        cpf: value => value.replace(/\D/g, '').replace(/(\d{3})(\d)/, '$1.$2').replace(/(\d{3})(\d)/, '$1.$2').replace(/(\d{3})(\d{1,2})/, '$1-$2').slice(0, 14),
        telefone: value => {
            let v = value.replace(/\D/g, '').slice(0, 11);
            return v.length >= 11 ? v.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3') : v.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
        },
        data: value => value.replace(/\D/g, '').replace(/(\d{2})(\d)/, '$1/$2').replace(/(\d{2})(\d)/, '$1/$2').slice(0, 10),
        cep: value => value.replace(/\D/g, '').replace(/(\d{5})(\d)/, '$1-$2').slice(0, 9)
    };
    const applyMask = (inputId, maskFunction) => {
        const input = document.getElementById(inputId);
        if (input) input.addEventListener('input', (e) => { e.target.value = maskFunction(e.target.value); });
    };
    applyMask('id_cpf', masks.cpf);
    applyMask('id_telefone', masks.telefone);
    applyMask('id_data_nascimento', masks.data);
    applyMask('id_cep', masks.cep);
    
    const closePopupButton = document.querySelector('.btn-close-popup');
    if (closePopupButton) {
        closePopupButton.addEventListener('click', () => {
            const popupOverlay = document.querySelector('.message-popup-overlay');
            if (popupOverlay) {
                popupOverlay.classList.remove('active');
            }
        });
    }
    
    // ---------------------------------------------------------------------
    // LÓGICA DO MENU HAMBURGUER
    // ---------------------------------------------------------------------
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');
    if (hamburger && navLinks) {
        hamburger.addEventListener('click', () => { navLinks.classList.toggle('active'); });
        document.querySelectorAll('.nav-links a').forEach(link => {
            link.addEventListener('click', () => { navLinks.classList.remove('active'); });
        });
    }

    // ---------------------------------------------------------------------
    // SCROLL SUAVE PARA ÂNCORAS
    // ---------------------------------------------------------------------
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            if (this.getAttribute('href') === '#') return;
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                window.scrollTo({ top: target.offsetTop - 80, behavior: 'smooth' });
                if (navLinks) navLinks.classList.remove('active');
            }
        });
    });

    // ---------------------------------------------------------------------
    // INTEGRAÇÃO COM VIACEP (SEÇÃO CORRIGIDA)
    // ---------------------------------------------------------------------
    const searchCepBtn = document.getElementById('search-cep');
    if (searchCepBtn) {
        searchCepBtn.addEventListener('click', async () => {
            const cepInput = document.getElementById('id_cep');
            const cep = cepInput.value.replace(/\D/g, '');
            if (cep.length !== 8) {
                alert('CEP inválido! O CEP deve conter 8 números.');
                return;
            }
            
            searchCepBtn.disabled = true;
            searchCepBtn.textContent = 'Buscando...';

            try {
                const response = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
                if (!response.ok) {
                    throw new Error('Erro de rede ao buscar o CEP.');
                }
                
                const data = await response.json();
                
                if (data.erro) {
                    alert('CEP não encontrado!');
                } else {
                    document.getElementById('id_logradouro').value = data.logradouro;
                    document.getElementById('id_bairro').value = data.bairro;
                    document.getElementById('id_cidade').value = data.localidade;
                    document.getElementById('id_estado').value = data.uf;
                    document.getElementById('id_numero').focus();
                }
            } catch (error) {
                console.error('Falha na busca do CEP:', error);
                // O alerta só será mostrado em caso de falha real (rede ou CEP não encontrado)
                if (!document.getElementById('id_logradouro').value) {
                     alert('Ocorreu um erro ao buscar o CEP. Tente novamente.');
                }
            } finally {
                // Este bloco sempre será executado
                searchCepBtn.disabled = false;
                searchCepBtn.textContent = 'Buscar';
            }
        });
    }

    // ---------------------------------------------------------------------
    // PREENCHIMENTO AUTOMÁTICO DO USERNAME COM O EMAIL
    // ---------------------------------------------------------------------
    const emailInput = document.getElementById('id_email');
    const usernameInput = document.getElementById('id_username');
    if (emailInput && usernameInput) {
        emailInput.addEventListener('input', () => {
            usernameInput.value = emailInput.value;
        });
    }

    // ---------------------------------------------------------------------
    // INICIALIZAÇÃO DOS CALENDÁRIOS
    // ---------------------------------------------------------------------
    document.querySelectorAll('.item-card').forEach(card => {
        const today = new Date();
        card.dataset.month = today.getMonth();
        card.dataset.year = today.getFullYear();
        
        const prevMonthBtn = card.querySelector('.prev-month-btn');
        const nextMonthBtn = card.querySelector('.next-month-btn');
        if (prevMonthBtn && nextMonthBtn) {
            prevMonthBtn.addEventListener('click', () => {
                let month = parseInt(card.dataset.month);
                let year = parseInt(card.dataset.year);
                month--;
                if (month < 0) { month = 11; year--; }
                card.dataset.month = month;
                card.dataset.year = year;
                renderCalendar(card);
            });
            nextMonthBtn.addEventListener('click', () => {
                let month = parseInt(card.dataset.month);
                let year = parseInt(card.dataset.year);
                month++;
                if (month > 11) { month = 0; year++; }
                card.dataset.month = month;
                card.dataset.year = year;
                renderCalendar(card);
            });
            renderCalendar(card);
            generateTimeSlots(card.querySelector('.time-slots'));
        }
    });
    
    // ---------------------------------------------------------------------
    // LÓGICA DO CARRINHO DE COMPRAS
    // ---------------------------------------------------------------------
    let cartItems = [];
    const cartItemsEl = document.getElementById('cart-items');
    const cartCountEl = document.getElementById('cart-count');
    const cartTotalEl = document.getElementById('cart-total');
    const emptyCartEl = document.querySelector('.empty-cart');
    
    function updateCart() {
        if (!cartItemsEl || !cartCountEl || !cartTotalEl || !emptyCartEl) return;
        cartItemsEl.innerHTML = '';
        cartCountEl.textContent = `${cartItems.length} ${cartItems.length === 1 ? 'item' : 'itens'}`;
        let cartTotal = 0;
        if (cartItems.length > 0) {
            emptyCartEl.style.display = 'none';
            cartItems.forEach(cartItem => {
                cartTotal += cartItem.price;
                const itemEl = document.createElement('div');
                itemEl.className = 'cart-item';
                itemEl.innerHTML = `
                    <div class="cart-item-details">
                        <h3>${cartItem.item}</h3>
                        <p>Data: ${cartItem.day} de ${cartItem.month}, ${cartItem.year} às ${cartItem.time}</p>
                    </div>
                    <div class="d-flex align-items-center">
                        <div class="cart-item-price">R$ ${cartItem.price.toFixed(2)}</div>
                        <button class="remove-from-cart" data-id="${cartItem.id}" title="Remover item">&times;</button>
                    </div>
                `;
                cartItemsEl.appendChild(itemEl);
            });
        } else {
            cartItemsEl.innerHTML = '';
            cartItemsEl.appendChild(emptyCartEl);
            emptyCartEl.style.display = 'block';
        }
        cartTotalEl.textContent = `R$ ${cartTotal.toFixed(2)}`;
    }

    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', () => {
            const validation = validateReservation(button);
            if (!validation.isValid) return;
            const item = button.getAttribute('data-item');
            const price = parseFloat(button.getAttribute('data-price'));
            const isDuplicate = cartItems.some(cartItem => 
                cartItem.item === item && 
                cartItem.day === validation.day &&
                cartItem.month === validation.month &&
                cartItem.year === validation.year &&
                cartItem.time === validation.time
            );
            if (isDuplicate) {
                alert(`⚠️ Você já adicionou "${item}" para esta data e horário!`);
                return;
            }
            cartItems.push({ 
                id: Date.now(), item, price,
                day: validation.day, month: validation.month,
                year: validation.year, time: validation.time
            });
            updateCart();
            button.classList.add('added');
            setTimeout(() => button.classList.remove('added'), 1000);
        });
    });

    // ---------------------------------------------------------------------
    // VALIDAÇÃO E SUBMISSÃO DE FORMULÁRIOS
    // ---------------------------------------------------------------------
    const registrationForm = document.getElementById('registration-form');
    const passwordInput = document.getElementById('id_password1');
    const requirements = {
        length: { el: document.getElementById('req-length'), valid: false },
        lower: { el: document.getElementById('req-lower'), valid: false },
        upper: { el: document.getElementById('req-upper'), valid: false },
        number: { el: document.getElementById('req-number'), valid: false },
        special: { el: document.getElementById('req-special'), valid: false }
    };

    if (passwordInput) {
        passwordInput.addEventListener('input', () => {
            const value = passwordInput.value;
            // Atualiza o status de cada requisito
            requirements.length.valid = value.length >= 8;
            requirements.lower.valid = /[a-z]/.test(value);
            requirements.upper.valid = /[A-Z]/.test(value);
            requirements.number.valid = /\d/.test(value);
            requirements.special.valid = /[\W_]/.test(value);

            // Atualiza a classe 'valid' no HTML para dar o feedback visual
            for (const key in requirements) {
                const req = requirements[key];
                if (req.el) {
                    req.el.classList.toggle('valid', req.valid);
                }
            }
        });
    }

    if (registrationForm) {
        registrationForm.addEventListener('submit', (e) => {
            const errorMessages = [];
            
            const requiredFields = registrationForm.querySelectorAll('[required]');
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    const label = document.querySelector(`label[for="${field.id}"]`);
                    // Garante que o campo de username escondido não gere um alerta visível
                    if (field.id !== 'id_username') {
                        errorMessages.push(`O campo "${label ? label.textContent : field.name}" é obrigatório.`);
                    }
                }
            });

            const isPasswordValid = Object.values(requirements).every(req => req.valid);
            if (!isPasswordValid) {
                errorMessages.push('A sua senha não atende a todos os critérios de segurança.');
            }

            const confirmPasswordInput = document.getElementById('id_password2');
            if (passwordInput && confirmPasswordInput && passwordInput.value !== confirmPasswordInput.value) {
                errorMessages.push('As senhas não coincidem.');
            }

            if (errorMessages.length > 0) {
                e.preventDefault();
                const uniqueMessages = [...new Set(errorMessages)];
                alert('Por favor, corrija os seguintes erros:\n\n- ' + uniqueMessages.join('\n- '));
            }
        });
    }

    // ---------------------------------------------------------------------
    // LÓGICA DOS MODAIS, CARROSSEL E OUTROS FORMULÁRIOS
    // ---------------------------------------------------------------------
    const checkoutBtn = document.querySelector('.checkout-btn');
    const paymentModal = document.getElementById('payment-modal');
    const confirmPaymentBtn = document.getElementById('confirm-payment-btn');
    const modalTotalValue = document.getElementById('modal-total-value');
    const loginBtnNav = document.getElementById('login-btn-nav');
    const loginModal = document.getElementById('login-modal');

    if (checkoutBtn && paymentModal) {
        checkoutBtn.addEventListener('click', () => {
            if (cartItems.length === 0) {
                alert('Adicione itens ao carrinho antes de finalizar!');
                return;
            }
            const total = cartItems.reduce((sum, item) => sum + item.price, 0);
            if(modalTotalValue) modalTotalValue.textContent = `R$ ${total.toFixed(2)}`;
            paymentModal.classList.add('active');
        });
    }

    if (confirmPaymentBtn) {
        confirmPaymentBtn.addEventListener('click', () => {
            paymentModal.classList.remove('active');
            alert('Pagamento simulado com sucesso! Reserva confirmada.');
            cartItems = [];
            updateCart();
        });
    }

    if (loginBtnNav && loginModal) {
        loginBtnNav.addEventListener('click', (e) => {
            e.preventDefault();
            loginModal.classList.add('active');
        });
    }

    document.querySelectorAll('.close-modal').forEach(button => {
        button.addEventListener('click', () => {
            button.closest('.modal')?.classList.remove('active');
        });
    });

    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            alert('Login realizado com sucesso!');
            loginModal.classList.remove('active');
        });
    }
    
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', (e) => {
            e.preventDefault();
            alert('Mensagem enviada com sucesso! Entraremos em contato em breve.');
            contactForm.reset();
        });
    }
    
    document.querySelectorAll('.carousel-container').forEach((carousel, index) => {
        const carouselId = index + 1;
        const prevBtn = carousel.querySelector('.prev-btn');
        const nextBtn = carousel.querySelector('.next-btn');
        const dotsContainer = document.querySelector(`.carousel-dots[data-carousel="${carouselId}"]`);
        const dots = dotsContainer ? dotsContainer.querySelectorAll('.dot') : [];
        const slides = carousel.querySelectorAll('.carousel-slide');

        if(slides.length > 0) {
            let slideIndex = 0;
            function updateCarousel() {
                slides.forEach((slide, i) => slide.classList.toggle('active', i === slideIndex));
                dots.forEach((dot, i) => dot.classList.toggle('active', i === slideIndex));
            }
            if (prevBtn && nextBtn) {
                prevBtn.addEventListener('click', () => {
                    slideIndex = (slideIndex - 1 + slides.length) % slides.length;
                    updateCarousel();
                });
                nextBtn.addEventListener('click', () => {
                    slideIndex = (slideIndex + 1) % slides.length;
                    updateCarousel();
                });
            }
            dots.forEach((dot, i) => {
                dot.addEventListener('click', () => {
                    slideIndex = i;
                    updateCarousel();
                });
            });
            updateCarousel();
        }
    });
});