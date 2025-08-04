// Arquivo: static/js/admin_espaco.js

// Garante que o jQuery do admin do Django esteja disponível
if (typeof django !== 'undefined' && typeof django.jQuery !== 'undefined') {
    (function($) {
        $(document).ready(function() {
            // Seleciona o campo dropdown 'Modelo de Cobrança'
            var modeloCobrancaField = $('#id_modelo_de_cobranca');
            
            // CORREÇÃO: Encontra as seções pelo texto do título, o que é mais confiável que o ID.
            var precoHoraSection = $('h2:contains("Regras de Preço por Hora")').closest('.inline-group');
            var precoPeriodoSection = $('h2:contains("Regras de Preço por Período")').closest('.inline-group');

            // Função para mostrar/esconder as seções baseada na escolha
            function togglePriceSections() {
                var selectedValue = modeloCobrancaField.val();
                
                if (selectedValue === 'hora') {
                    precoHoraSection.show();
                    precoPeriodoSection.hide();
                } else if (selectedValue === 'periodo') {
                    precoHoraSection.hide();
                    precoPeriodoSection.show();
                } else {
                    // Esconde ambos se nada for selecionado
                    precoHoraSection.hide();
                    precoPeriodoSection.hide();
                }
            }

            // Roda a função assim que a página carrega
            togglePriceSections();

            // Adiciona um "ouvinte" que executa a função sempre que o valor do dropdown mudar
            modeloCobrancaField.on('change', togglePriceSections);
        });
    })(django.jQuery);
}