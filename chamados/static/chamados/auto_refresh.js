let ultimoNumero = null;
let statusAnteriores = {};

async function verificarChamados() {
    try {
        const resposta = await fetch("/verificar-status-chamados/");

        if (!resposta.ok) {
            return;
        }

        const dados = await resposta.json();

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

        let textoStatus = "";

        if (chamado.status === "ABERTO") {
            textoStatus = "Aberto";
        } else if (chamado.status === "ATENDIMENTO") {
            textoStatus = "Em atendimento";
        } else if (chamado.status === "FINALIZADO") {
            textoStatus = "Finalizado";
        }

        celulaStatus.innerHTML =
            '<span class="admin-status">' +
            textoStatus +
            '</span>';
    });
}


setInterval(verificarChamados, 5000);

verificarChamados();