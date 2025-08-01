// Hamburger menu toggle
const hamburger = document.querySelector('.hamburger');
const navLinks = document.querySelector('.nav-links');

if (hamburger && navLinks) {
    hamburger.addEventListener('click', () => {
        navLinks.classList.toggle('active');
    });

    // Fechar menu ao clicar em um link
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', () => {
            navLinks.classList.remove('active');
        });
    });
}

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        if (this.getAttribute('href') === '#') return;
        
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            window.scrollTo({
                top: target.offsetTop - 80,
                behavior: 'smooth'
            });
            if (navLinks) navLinks.classList.remove('active');
        }
    });
});

// ViaCEP integration
const searchCepBtn = document.getElementById('search-cep');
if (searchCepBtn) {
    searchCepBtn.addEventListener('click', () => {
        const cep = document.getElementById('cep').value.replace(/\D/g, '');
        
        if (cep.length !== 8) {
            alert('CEP inválido!');
            return;
        }
        
        fetch(`https://viacep.com.br/ws/${cep}/json/`)
            .then(response => response.json())
            .then(data => {
                if (data.erro) {
                    alert('CEP não encontrado!');
                    return;
                }
                
                document.getElementById('street').value = data.logradouro;
                document.getElementById('neighborhood').value = data.bairro;
                document.getElementById('city').value = data.localidade;
                document.getElementById('state').value = data.uf;
                document.getElementById('number').focus();
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Erro ao buscar CEP!');
            });
    });
}

// =========================================================================
// INÍCIO - CÓDIGO PARA MÚLTIPLOS CALENDÁRIOS E CARRINHO
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
                // Remove seleção apenas dos horários dentro do mesmo card
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
    
    // Usa data attributes para armazenar o estado de cada calendário
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
        
        // Desabilitar dias passados
        const today = new Date();
        today.setHours(0,0,0,0);
        const dayDate = new Date(currentYear, currentMonth, day);

        if (dayDate < today) {
            dayEl.classList.add('unavailable');
        } else {
            dayEl.addEventListener('click', () => {
                // Remove seleção apenas dos dias dentro do mesmo card
                card.querySelectorAll('.day.selected').forEach(el => el.classList.remove('selected'));
                dayEl.classList.add('selected');
                generateTimeSlots(card.querySelector('.time-slots'));
            });
        }
        calendarEl.appendChild(dayEl);
    }
}

// Inicializa cada calendário na página
document.querySelectorAll('.item-card').forEach(card => {
    // Define o estado inicial (mês/ano) para cada card
    const today = new Date();
    card.dataset.month = today.getMonth();
    card.dataset.year = today.getFullYear();
    
    const prevMonthBtn = card.querySelector('.prev-month-btn');
    const nextMonthBtn = card.querySelector('.next-month-btn');

    if(prevMonthBtn && nextMonthBtn) {
        prevMonthBtn.addEventListener('click', () => {
            let month = parseInt(card.dataset.month);
            let year = parseInt(card.dataset.year);
            month--;
            if (month < 0) {
                month = 11;
                year--;
            }
            card.dataset.month = month;
            card.dataset.year = year;
            renderCalendar(card);
        });
    
        nextMonthBtn.addEventListener('click', () => {
            let month = parseInt(card.dataset.month);
            let year = parseInt(card.dataset.year);
            month++;
            if (month > 11) {
                month = 0;
                year++;
            }
            card.dataset.month = month;
            card.dataset.year = year;
            renderCalendar(card);
        });
        
        // Renderiza o estado inicial
        renderCalendar(card);
        generateTimeSlots(card.querySelector('.time-slots'));
    }
});


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


// Carrinho de Reservas (lógica adaptada)
const cartItemsEl = document.getElementById('cart-items');
const cartCountEl = document.getElementById('cart-count');
const cartTotalEl = document.getElementById('cart-total');
const emptyCartEl = document.querySelector('.empty-cart');

let cartItems = [];

document.querySelectorAll('.add-to-cart').forEach(button => {
    button.addEventListener('click', () => {
        const validation = validateReservation(button); // Passa o botão para a validação
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
            id: Date.now(), // ID único para facilitar a remoção
            item, 
            price,
            day: validation.day,
            month: validation.month,
            year: validation.year,
            time: validation.time
        });
        
        updateCart();
        button.classList.add('added');
        setTimeout(() => button.classList.remove('added'), 1000);
    });
});

function updateCart() {
    if (!cartItemsEl || !cartCountEl || !cartTotalEl || !emptyCartEl) return;

    cartItemsEl.innerHTML = ''; // Limpa o carrinho para redesenhar
    cartCountEl.textContent = `${cartItems.length} ${cartItems.length === 1 ? 'item' : 'itens'}`;

    let cartTotal = 0;
    if (cartItems.length > 0) {
        emptyCartEl.style.display = 'none';
        cartItems.forEach(cartItem => {
            cartTotal += cartItem.price;

            const itemEl = document.createElement('div');
            itemEl.className = 'cart-item';
            // Adicionado o botão de remover com o data-id
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
        cartItemsEl.innerHTML = ''; // Garante que está limpo
        cartItemsEl.appendChild(emptyCartEl);
        emptyCartEl.style.display = 'block';
    }

    cartTotalEl.textContent = `R$ ${cartTotal.toFixed(2)}`;
}

// =========================================================================
// FIM - CÓDIGO ATUALIZADO
// =========================================================================

// Checkout functionality (com simulação de pagamento em modal)
const checkoutBtn = document.querySelector('.checkout-btn');
const paymentModal = document.getElementById('payment-modal');
const confirmPaymentBtn = document.getElementById('confirm-payment-btn');
const modalTotalValue = document.getElementById('modal-total-value');

if (checkoutBtn && paymentModal) {
    checkoutBtn.addEventListener('click', () => {
        if (cartItems.length === 0) {
            alert('Adicione itens ao carrinho antes de finalizar!');
            return;
        }

        // Calcula o total e atualiza o valor no modal
        const total = cartItems.reduce((sum, item) => sum + item.price, 0);
        modalTotalValue.textContent = `R$ ${total.toFixed(2)}`;

        // Abre o modal de confirmação
        paymentModal.classList.add('active');
    });
}

// Lógica para o botão de confirmação final dentro do modal
if (confirmPaymentBtn) {
    confirmPaymentBtn.addEventListener('click', () => {
        // Fecha o modal
        paymentModal.classList.remove('active');

        // Mostra mensagem de sucesso
        alert('Pagamento simulado com sucesso! Reserva confirmada.');

        // Limpa o carrinho
        cartItems = [];

        // Atualiza a interface do carrinho
        updateCart();
    });
}

// Adiciona funcionalidade aos botões de fechar modal
document.querySelectorAll('.close-modal').forEach(button => {
    button.addEventListener('click', () => {
        // Encontra o modal pai do botão e o fecha
        const modalToClose = button.closest('.modal');
        if (modalToClose) {
            modalToClose.classList.remove('active');
        }
    });
});

// Mercado Pago integration
function initMercadoPago() {
    const mpContainer = document.getElementById('mercado-pago-container');
    if (mpContainer) {
        mpContainer.innerHTML = `
            <div class="payment-success">
                <div style="text-align: center; margin-bottom: 20px;">
                    <i class="fas fa-check-circle" style="font-size: 3rem; color: var(--success);"></i>
                </div>
                <h3 style="text-align: center; margin-bottom: 15px;">Pagamento Simulado</h3>
                <p style="text-align: center;">Esta é uma simulação do processo de pagamento com Mercado Pago.</p>
                <p style="text-align: center;">Em uma implementação real, o checkout do Mercado Pago seria carregado aqui.</p>
                <button class="btn" style="width: 100%; margin-top: 20px;" id="close-payment">Fechar</button>
            </div>
        `;
        
        document.getElementById('close-payment').addEventListener('click', () => {
            document.getElementById('payment-modal').classList.remove('active');
            
            // Simula a confirmação após fechar o pagamento
            alert('Reserva confirmada com sucesso!');
            cartItems = [];
            updateCart();
        });
    }
}

// Login modal functionality
const loginBtnNav = document.getElementById('login-btn-nav');
const loginModal = document.getElementById('login-modal');
const closeModalBtns = document.querySelectorAll('.close-modal');

if (loginBtnNav && loginModal) {
    loginBtnNav.addEventListener('click', (e) => {
        e.preventDefault();
        loginModal.classList.add('active');
    });
}

closeModalBtns.forEach(button => {
    button.addEventListener('click', () => {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.remove('active');
        });
    });
});

// Password validation
const passwordInput = document.getElementById('password');
if (passwordInput) {
    passwordInput.addEventListener('input', () => {
        const value = passwordInput.value;
        const requirements = {
            length: value.length >= 8,
            upper: /[A-Z]/.test(value),
            lower: /[a-z]/.test(value),
            number: /\d/.test(value),
            special: /[\W_]/.test(value)
        };
        
        Object.keys(requirements).forEach(key => {
            const element = document.getElementById(`req-${key}`);
            if (element) {
                if (requirements[key]) {
                    element.classList.add('valid');
                } else {
                    element.classList.remove('valid');
                }
            }
        });
    });
}

// Form submissions
const loginForm = document.getElementById('login-form');
if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;

        if (!email.includes('@') || password.length < 6) {
            alert('Por favor, insira um e-mail válido e senha com pelo menos 6 caracteres');
            return;
        }
        
        alert('Login realizado com sucesso!');
        loginModal.classList.remove('active');
    });
}

const registrationForm = document.getElementById('registration-form');
if (registrationForm) {
    registrationForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm-password').value;
        
        if (password !== confirmPassword) {
            alert('As senhas não coincidem!');
            return;
        }
        
        alert('Conta criada com sucesso! Agora você pode fazer login.');
        window.location.href = 'index.html';
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

// =============================================
// CARROSSEL DUPLO - Implementação Atualizada
// =============================================
document.addEventListener('DOMContentLoaded', () => {
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
                slides.forEach((slide, i) => {
                    slide.classList.toggle('active', i === slideIndex);
                });
                
                dots.forEach((dot, i) => {
                    dot.classList.toggle('active', i === slideIndex);
                });
            }
    
            // Controles de navegação
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
    
            // Controle por dots (bolinhas)
            dots.forEach((dot, i) => {
                dot.addEventListener('click', () => {
                    slideIndex = i;
                    updateCarousel();
                });
            });
    
            // Inicializa
            updateCarousel();
        }
    });
});