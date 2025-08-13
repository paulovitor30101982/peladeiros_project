// =========================================================================
// FUNÇÕES GLOBAIS
// =========================================================================

const monthNames = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
];

// =========================================================================
// INICIALIZAÇÃO DO SCRIPT QUANDO O DOCUMENTO ESTIVER PRONTO
// =========================================================================

document.addEventListener('DOMContentLoaded', () => {

    // ---------------------------------------------------------------------
    // CÓDIGO DE MÁSCARAS DE FORMULÁRIO (ATUALIZADO)
    // ---------------------------------------------------------------------
    const masks = {
        cpf: value => value.replace(/\D/g, '').replace(/(\d{3})(\d)/, '$1.$2').replace(/(\d{3})(\d)/, '$1.$2').replace(/(\d{3})(\d{1,2})/, '$1-$2').slice(0, 14),
        telefone: value => {
            let v = value.replace(/\D/g, '').slice(0, 11);
            return v.length >= 11 ? v.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3') : v.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
        },
        data: value => value.replace(/\D/g, '').replace(/(\d{2})(\d)/, '$1/$2').replace(/(\d{2})(\d)/, '$1/$2').slice(0, 10),
        cep: value => value.replace(/\D/g, '').replace(/(\d{5})(\d)/, '$1-$2').slice(0, 9),
        // NOVAS MÁSCARAS PARA O CARTÃO DE CRÉDITO
        creditCard: value => value.replace(/\D/g, '').replace(/(\d{4})(?=\d)/g, '$1 ').slice(0, 19),
        expiryDate: value => value.replace(/\D/g, '').replace(/(\d{2})(\d)/, '$1/$2').slice(0, 5),
        cvv: value => value.replace(/\D/g, '').slice(0, 4)
    };
    const applyMask = (inputId, maskFunction) => {
        const input = document.getElementById(inputId);
        if (input) input.addEventListener('input', (e) => { e.target.value = maskFunction(e.target.value); });
    };
    // Máscaras antigas
    applyMask('id_cpf', masks.cpf);
    applyMask('id_telefone', masks.telefone);
    applyMask('id_data_nascimento', masks.data);
    applyMask('id_cep', masks.cep);
    // Novas máscaras para o modal de pagamento
    applyMask('cc-number', masks.creditCard);
    applyMask('cc-expiry', masks.expiryDate);
    applyMask('cc-cvv', masks.cvv);
    
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
    // INTEGRAÇÃO COM VIACEP
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
                if (!document.getElementById('id_logradouro').value) {
                     alert('Ocorreu um erro ao buscar o CEP. Tente novamente.');
                }
            } finally {
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
    // LÓGICA DE RESERVAS, CALENDÁRIO E PREÇO DINÂMICO
    // ---------------------------------------------------------------------
    
    // Variável do carrinho movida para o escopo da Lógica do Carrinho
    let cartItems = [];

    function updatePriceDisplay(card) {
        const selectedTimeEl = card.querySelector('.time-slot.selected, .period-slot.selected');
        const selectedPriceValue = card.querySelector('.selected-price-value');
        const addToCartBtn = card.querySelector('.add-to-cart');

        if (!selectedTimeEl) {
            selectedPriceValue.textContent = '--';
            addToCartBtn.dataset.price = '0';
            return;
        }

        const price = selectedTimeEl.dataset.price;
        if (price && price !== 'null') {
            selectedPriceValue.textContent = `R$ ${parseFloat(price).toFixed(2)}`;
            addToCartBtn.dataset.price = price;
        } else {
            selectedPriceValue.textContent = 'Indisponível';
            addToCartBtn.dataset.price = '0';
        }
    }

    function generateSlots(card) {
        const timeSlotsEl = card.querySelector('.time-slots');
        const selectedDayEl = card.querySelector('.day.selected');
        const modeloCobranca = card.dataset.modelo;

        timeSlotsEl.innerHTML = '';
        updatePriceDisplay(card);

        if (!selectedDayEl) {
            timeSlotsEl.innerHTML = '<p class="info-text" style="font-size: 0.9em; text-align: center;">Selecione um dia para ver as opções.</p>';
            return;
        }

        const espacoId = card.dataset.espacoId;
        const espacoIndisponibilidades = (typeof indisponibilidades !== 'undefined' && indisponibilidades[espacoId]?.datas_especificas) ? indisponibilidades[espacoId].datas_especificas : [];
        
        const day = parseInt(selectedDayEl.textContent);
        const [monthName, yearStr] = card.querySelector('.current-month').textContent.split(' ');
        const month = monthNames.indexOf(monthName);
        const selectedDate = new Date(yearStr, month, day);
        const diaDaSemana = (selectedDate.getDay() + 6) % 7;
        const now = new Date();

        const renderSlot = (slotInfo) => {
            const { text, time, price, isPeriod } = slotInfo;
            const slotDate = new Date(selectedDate);
            const [hour, minute] = time.split(':');
            slotDate.setHours(hour, minute, 0, 0);

            let isUnavailable = slotDate < now;

            const isInCart = cartItems.some(item => 
                String(item.espacoId) === String(espacoId) &&
                item.year === selectedDate.getFullYear() &&
                item.month === monthNames[selectedDate.getMonth()] &&
                item.day === selectedDate.getDate() &&
                (isPeriod ? item.time === text : item.time === time)
            );
            if (isInCart) isUnavailable = true;
            
            if (!isUnavailable) {
                for (const indisponivel of espacoIndisponibilidades) {
                    const inicio = new Date(indisponivel.inicio);
                    const fim = new Date(indisponivel.fim);
                    if (slotDate >= inicio && slotDate < fim) {
                        isUnavailable = true;
                        break;
                    }
                }
            }
            
            const slot = document.createElement('div');
            slot.className = isPeriod ? 'period-slot' : 'time-slot';
            slot.textContent = text;
            slot.dataset.price = price;

            if (isUnavailable) {
                slot.classList.add('unavailable');
            } else {
                slot.addEventListener('click', () => {
                    card.querySelectorAll('.time-slot.selected, .period-slot.selected').forEach(el => el.classList.remove('selected'));
                    slot.classList.add('selected');
                    updatePriceDisplay(card);
                });
            }
            timeSlotsEl.appendChild(slot);
        };

        if (modeloCobranca === 'hora') {
            const espacoRegras = (typeof regrasPrecoHora !== 'undefined' && regrasPrecoHora[espacoId]) ? regrasPrecoHora[espacoId] : [];
            let possibleTimes = new Set();
            const regrasDoDia = espacoRegras.filter(regra => [diaDaSemana, 7, 8, 9, 10, 11].includes(regra.dia_semana));
            
            regrasDoDia.forEach(regra => {
                let [startHour] = regra.hora_inicio.split(':').map(Number);
                let [endHour] = regra.hora_fim.split(':').map(Number);
                if (endHour === 0) endHour = 24;

                for (let h = startHour; h < endHour; h++) {
                    possibleTimes.add(`${h.toString().padStart(2, '0')}:00`);
                }
            });

            const sortedTimes = Array.from(possibleTimes).sort();
            if (sortedTimes.length === 0) {
                timeSlotsEl.innerHTML = '<p class="info-text" style="font-size: 0.9em; text-align: center;">Não há horários para este dia.</p>'; return;
            }

            sortedTimes.forEach(time => {
                let precoEncontrado = null;
                 for (const regra of regrasDoDia) {
                    if (time + ':00' >= regra.hora_inicio && time + ':00' < regra.hora_fim) {
                         precoEncontrado = parseFloat(regra.preco);
                         break;
                    }
                 }
                renderSlot({ text: time, time: time, price: precoEncontrado, isPeriod: false });
            });

        } else if (modeloCobranca === 'periodo') {
            const espacoRegras = (typeof regrasPrecoPeriodo !== 'undefined' && regrasPrecoPeriodo[espacoId]) ? regrasPrecoPeriodo[espacoId] : [];
            const regrasDoDia = espacoRegras.filter(regra => [diaDaSemana, 7, 8].includes(regra.dia_semana));

            if (regrasDoDia.length === 0) {
                timeSlotsEl.innerHTML = '<p class="info-text" style="font-size: 0.9em; text-align: center;">Não há períodos para este dia.</p>'; return;
            }
            
            regrasDoDia.forEach(regra => {
                const periodoInfo = periodos[regra.periodo_id];
                const slotText = `${periodoInfo.nome} (${periodoInfo.inicio.slice(0,5)} - ${periodoInfo.fim.slice(0,5)})`;
                renderSlot({ text: slotText, time: periodoInfo.inicio.slice(0,5), price: regra.preco, isPeriod: true });
            });
        }
    }
    
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
            
            const today = new Date();
            today.setHours(0,0,0,0);
            const dayDate = new Date(currentYear, currentMonth, day);

            if (dayDate < today) {
                dayEl.classList.add('unavailable');
            } else {
                dayEl.addEventListener('click', () => {
                    card.querySelectorAll('.day.selected').forEach(el => el.classList.remove('selected'));
                    dayEl.classList.add('selected');
                    generateSlots(card);
                });
            }
            calendarEl.appendChild(dayEl);
        }
    }

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
                generateSlots(card);
            });
            nextMonthBtn.addEventListener('click', () => {
                let month = parseInt(card.dataset.month);
                let year = parseInt(card.dataset.year);
                month++;
                if (month > 11) { month = 0; year++; }
                card.dataset.month = month;
                card.dataset.year = year;
                renderCalendar(card);
                generateSlots(card);
            });
            renderCalendar(card);
            generateSlots(card);
        }
    });
    
    // ---------------------------------------------------------------------
    // LÓGICA DO CARRINHO, FINALIZAÇÃO E MODAL DE PAGAMENTO (SEÇÃO ATUALIZADA)
    // ---------------------------------------------------------------------
    const cartItemsEl = document.getElementById('cart-items');
    const cartCountEl = document.getElementById('cart-count');
    const cartTotalEl = document.getElementById('cart-total');
    const emptyCartEl = document.querySelector('.empty-cart');
    const checkoutBtn = document.querySelector('.checkout-btn');
    
    // Elementos do Modal de Pagamento
    const paymentModalOverlay = document.getElementById('payment-modal-overlay');
    const closePaymentModalBtn = document.querySelector('.close-payment-modal');
    const modalTotalValue = document.getElementById('modal-total-value');
    const paymentTabs = document.querySelectorAll('.payment-tab');
    const paymentContents = document.querySelectorAll('.payment-tab-content');
    const confirmPaymentBtn = document.getElementById('confirm-payment-btn');
    const copyPixCodeBtn = document.getElementById('copy-pix-code-btn');
    
    function updateCart() {
        if (!cartItemsEl || !cartCountEl || !cartTotalEl || !emptyCartEl) return;
        cartItemsEl.innerHTML = '';
        cartCountEl.textContent = `${cartItems.length} ${cartItems.length === 1 ? 'item' : 'itens'}`;
        let cartTotal = 0;
        if (cartItems.length > 0) {
            if (emptyCartEl) emptyCartEl.style.display = 'none';
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
            if (emptyCartEl) {
                cartItemsEl.innerHTML = '';
                cartItemsEl.appendChild(emptyCartEl);
                emptyCartEl.style.display = 'block';
            }
        }
        const totalFormatted = `R$ ${cartTotal.toFixed(2)}`;
        cartTotalEl.textContent = totalFormatted;
        if(modalTotalValue) modalTotalValue.textContent = totalFormatted; // Atualiza o total no modal também
    }

    if (cartItemsEl) {
        cartItemsEl.addEventListener('click', (e) => {
            if (e.target && e.target.classList.contains('remove-from-cart')) {
                const itemId = parseInt(e.target.dataset.id);
                cartItems = cartItems.filter(item => item.id !== itemId);
                updateCart();
                document.querySelectorAll('.item-card').forEach(card => {
                    if (card.querySelector('.day.selected')) {
                        generateSlots(card);
                    }
                });
            }
        });
    }

    function validateReservation(card) {
        const selectedDayEl = card.querySelector('.day.selected');
        const selectedTimeEl = card.querySelector('.time-slot.selected, .period-slot.selected');
        if (!selectedDayEl || !selectedTimeEl) {
            alert('❌ Selecione uma data e horário válidos para este item antes de adicionar ao carrinho.');
            return { isValid: false };
        }
        const selectedDay = parseInt(selectedDayEl.textContent);
        const [monthName, yearStr] = card.querySelector('.current-month').textContent.split(' ');
        const selectedYear = parseInt(yearStr);
        const selectedTime = selectedTimeEl.textContent;
        const selectedMonth = monthNames.indexOf(monthName);
        return { 
            isValid: true, day: selectedDay, month: monthName,
            year: selectedYear, time: selectedTime
        };
    }

    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', () => {
            const card = button.closest('.item-card');
            const validation = validateReservation(card);
            if (!validation.isValid) return;

            const price = parseFloat(button.dataset.price);
            if (price <= 0) {
                alert('Por favor, selecione um horário com preço válido.');
                return;
            }

            const item = button.dataset.item;
            const espacoId = card.dataset.espacoId;
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
                id: Date.now(), 
                espacoId: espacoId,
                item, price,
                day: validation.day, month: validation.month,
                year: validation.year, time: validation.time
            });
            updateCart();
            generateSlots(card);
        });
    });

    // Listener para o botão 'Finalizar Reserva' (agora abre o modal)
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', () => {
            if (typeof isUserAuthenticated === 'undefined' || !isUserAuthenticated) {
                alert('Você precisa estar logado para finalizar uma reserva. Redirecionando para a página de login...');
                window.location.href = '/entrar/';
                return;
            }

            if (cartItems.length === 0) {
                alert('Seu carrinho está vazio. Adicione itens antes de finalizar.');
                return;
            }
            
            // Abre o modal de pagamento
            if (paymentModalOverlay) {
                paymentModalOverlay.classList.add('active');
            }
        });
    }

    // Funções do Modal de Pagamento
    function closePaymentModal() {
        if (paymentModalOverlay) {
            paymentModalOverlay.classList.remove('active');
        }
    }

    if (closePaymentModalBtn) {
        closePaymentModalBtn.addEventListener('click', closePaymentModal);
    }
    if (paymentModalOverlay) {
        paymentModalOverlay.addEventListener('click', (e) => {
            if (e.target === paymentModalOverlay) {
                closePaymentModal();
            }
        });
    }

    // Lógica das abas do modal
    if (paymentTabs.length > 0) {
        paymentTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                paymentTabs.forEach(t => t.classList.remove('active'));
                paymentContents.forEach(c => c.classList.remove('active'));

                tab.classList.add('active');
                document.getElementById(`${tab.dataset.tab}-content`).classList.add('active');
            });
        });
    }

    // Lógica para copiar o código PIX
    if (copyPixCodeBtn) {
        copyPixCodeBtn.addEventListener('click', () => {
            const pixCodeInput = document.querySelector('.pix-code-container input');
            navigator.clipboard.writeText(pixCodeInput.value).then(() => {
                alert('Código PIX copiado para a área de transferência!');
            }).catch(err => {
                console.error('Falha ao copiar:', err);
                alert('Falha ao copiar o código.');
            });
        });
    }

    // Listener do botão 'Confirmar Pagamento' (executa a simulação e a finalização)
    if (confirmPaymentBtn) {
        confirmPaymentBtn.addEventListener('click', () => {
            const originalBtnText = confirmPaymentBtn.textContent;
            confirmPaymentBtn.disabled = true;
            confirmPaymentBtn.textContent = 'Processando...';

            // Simulação de 2 segundos de processamento
            setTimeout(async () => {
                try {
                    // Após a simulação, executa a requisição real ao backend
                    const response = await fetch('/finalizar-reserva/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ cart_items: cartItems })
                    });

                    const result = await response.json();

                    if (response.ok) {
                        closePaymentModal();
                        alert(result.message);
                        cartItems = [];
                        updateCart();
                        window.location.reload(); // Recarrega a página para atualizar tudo
                    } else {
                        alert(`Erro ao finalizar a reserva: ${result.message}`);
                    }

                } catch (error) {
                    console.error('Erro na requisição:', error);
                    alert('Ocorreu um erro de comunicação com o servidor. Tente novamente.');
                } finally {
                    confirmPaymentBtn.disabled = false;
                    confirmPaymentBtn.textContent = originalBtnText;
                }
            }, 2000); // 2 segundos de atraso
        });
    }
    
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
            requirements.length.valid = value.length >= 8;
            requirements.lower.valid = /[a-z]/.test(value);
            requirements.upper.valid = /[A-Z]/.test(value);
            requirements.number.valid = /\d/.test(value);
            requirements.special.valid = /[\W_]/.test(value);
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
    // LÓGICA DAS ABAS NA PÁGINA "MINHAS RESERVAS"
    // ---------------------------------------------------------------------
    const tabLinks = document.querySelectorAll('.tab-link');
    const tabContents = document.querySelectorAll('.tab-content');

    if (tabLinks.length > 0) {
        tabLinks.forEach(link => {
            link.addEventListener('click', () => {
                const tabId = link.dataset.tab;

                tabLinks.forEach(l => l.classList.remove('active'));
                tabContents.forEach(c => c.classList.remove('active'));

                link.classList.add('active');
                document.getElementById(tabId).classList.add('active');
            });
        });
    }

    // ---------------------------------------------------------------------
    // LÓGICA DO BOTÃO DE CANCELAR RESERVA
    // ---------------------------------------------------------------------
    document.body.addEventListener('click', function(event) {
        if (event.target.classList.contains('cancel-reserva-btn')) {
            const reservaId = event.target.dataset.reservaId;
            
            const isConfirmed = confirm('Tem a certeza de que deseja cancelar esta reserva? Esta ação não pode ser desfeita.');

            if (isConfirmed) {
                const csrftokenInput = document.querySelector('[name=csrfmiddlewaretoken]');
                if (!csrftokenInput) {
                    alert('Erro de segurança: Token CSRF não encontrado. Recarregue a página.');
                    return;
                }
                const csrftoken = csrftokenInput.value;

                fetch(`/cancelar-reserva/${reservaId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        alert(data.message);
                        window.location.reload();
                    } else {
                        alert(`Erro: ${data.message}`);
                    }
                })
                .catch(error => {
                    console.error('Erro ao cancelar reserva:', error);
                    alert('Ocorreu um erro de comunicação ao tentar cancelar a reserva.');
                });
            }
        }
    });


    // ---------------------------------------------------------------------
    // LÓGICA DE MODAIS GENÉRICOS, CARROSSEL E OUTROS FORMULÁRIOS
    // ---------------------------------------------------------------------
    const loginBtnNav = document.getElementById('login-btn-nav');
    const loginModal = document.getElementById('login-modal');

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

}); // Fim do 'DOMContentLoaded'