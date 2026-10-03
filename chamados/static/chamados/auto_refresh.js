let ultimoNumero = null;
let statusAnteriores = {};

async function verificarChamados() {
    try {
        const resposta = await fetch("/verificar-status-chamados/");

        if (!resposta.ok) {
            return;
        }

        const dados = await resposta.json();

        console.log("STATUS DOS CHAMADOS:", dados.chamados);

        /*
         * PRIMEIRA EXECUÇÃO
         *
         * Apenas registra o estado atual dos chamados.
         * Não altera a tela.
         */
        if (ultimoNumero === null) {
            dados.chamados.forEach(function (chamado) {
                statusAnteriores[chamado.numero] = chamado.status;
            });

            if (dados.chamados.length > 0) {
                ultimoNumero = Math.max(
                    ...dados.chamados.map(chamado => chamado.numero)
                );
            } else {
                ultimoNumero = 0;
            }

            return;
        }

        /*
         * NOVOS CHAMADOS
         */
        const novoNumero = dados.chamados.length > 0
            ? Math.max(...dados.chamados.map(chamado => chamado.numero))
            : 0;

        if (novoNumero > ultimoNumero) {
            window.location.reload();
            return;
        }

        /*
         * ALTERAÇÕES DE STATUS
         */
        dados.chamados.forEach(function (chamado) {

            const statusAnterior =
                statusAnteriores[chamado.numero];

            if (
                statusAnterior !== undefined &&
                statusAnterior !== chamado.status
            ) {
                atualizarStatusNaTabela(chamado);
            }

            statusAnteriores[chamado.numero] = chamado.status;
        });

        ultimoNumero = novoNumero;

    } catch (erro) {
        console.error(
            "Erro ao verificar chamados:",
            erro
        );
    }
}


function atualizarStatusNaTabela(chamado) {

    const linhas = document.querySelectorAll(
        "#changelist .results tbody tr"
    );

    linhas.forEach(function (linha) {

        const linkNumero =
            linha.querySelector(".field-numero a");

        if (!linkNumero) {
            return;
        }

        const textoNumero =
            linkNumero.textContent.trim();

        const numero =
            parseInt(textoNumero.replace("#", ""), 10);

        if (numero !== chamado.numero) {
            return;
        }

        const celulaStatus =
            linha.querySelector(".field-status_visual");

        if (!celulaStatus) {
            return;
        }

        const configuracoes = {
            "ABERTO": {
                texto: "Aberto",
                classe: "status-aberto"
            },
            "ATENDIMENTO": {
                texto: "Em atendimento",
                classe: "status-atendimento"
            },
            "FINALIZADO": {
                texto: "Finalizado",
                classe: "status-finalizado"
            }
        };

        const configuracao =
            configuracoes[chamado.status];

        if (!configuracao) {
            return;
        }

        celulaStatus.innerHTML =
            '<span class="admin-status ' +
            configuracao.classe +
            '">' +
            configuracao.texto +
            '</span>';
    });
}


setInterval(verificarChamados, 5000);

verificarChamados();