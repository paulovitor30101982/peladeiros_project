// Arquivo: static/js/admin_espaco.js

window.addEventListener("load", function() {
    (function($) {
        $(document).ready(function() {
            // Seleciona o campo dropdown 'Modelo de Cobrança'
            var modeloCobrancaField = $('#id_modelo_de_cobranca');
            
            // CORREÇÃO: Os IDs corretos que o Django gera são baseados no nome do modelo em minúsculo
            var precoHoraSection = $('#regrapreco_set-group');
            var precoPeriodoSection = $('#precoperiodo_set-group');

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

            // Executa a função uma vez no carregamento da página
            togglePriceSections();

            // Adiciona um "ouvinte" que executa a função sempre que o valor do dropdown mudar
            modeloCobrancaField.on('change', function() {
                togglePriceSections();
            });
        });
    })(django.jQuery);
});