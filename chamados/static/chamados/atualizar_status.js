
document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       CONFIGURAÇÃO DO FILTRO ATUAL
    ===================================================== */

    const parametrosURL = new URLSearchParams(
        window.location.search
    );

    const statusFiltro =
        parametrosURL.get("status") || "abertos";


    /* =====================================================
       SEGUNDO RELOAD APÓS FINALIZAÇÃO
    ===================================================== */

    if (
        sessionStorage.getItem("segundo_reload_chamado") === "1"
    ) {

        setTimeout(function () {

            sessionStorage.removeItem(
                "segundo_reload_chamado"
            );

            window.location.reload();

        }, 5000);

    }


    /* =====================================================
       CONTROLE DE CONSULTAS
    ===================================================== */

    let numerosConhecidos = null;
    let verificacaoEmAndamento = false;
    let reloadSolicitado = false;


    /* =====================================================
       VERIFICAR CHAMADOS NO SERVIDOR
    ===================================================== */

    async function verificarStatus() {

        if (
            verificacaoEmAndamento ||
            reloadSolicitado
        ) {
            return;
        }

        verificacaoEmAndamento = true;

        try {

            const resposta = await fetch(
                "/verificar-status-chamados/?t=" +
                Date.now(),
                {
                    cache: "no-store"
                }
            );

            if (!resposta.ok) {
                return;
            }

            const dados = await resposta.json();

            if (!Array.isArray(dados.chamados)) {
                return;
            }


            /* =================================================
               PRIMEIRA CONSULTA
               Registra os chamados existentes para que
               não sejam confundidos com chamados novos.
            ================================================= */

            if (numerosConhecidos === null) {

                numerosConhecidos = new Set(
                    dados.chamados.map(
                        chamado => String(chamado.numero)
                    )
                );

                return;
            }


            /* =================================================
               LOCALIZAR TABELA
            ================================================= */

            const tabela = document.querySelector(
                ".tabela-container table"
            );

            if (!tabela) {
                return;
            }

            const tbody = tabela.querySelector("tbody");

            if (!tbody) {
                return;
            }


            /* =================================================
               VERIFICAR CHAMADOS RECEBIDOS
            ================================================= */

            for (const chamado of dados.chamados) {

                const numero = String(chamado.numero);

                const linha = tbody.querySelector(
                    `tr[data-chamado="${numero}"]`
                );

                const numeroJaConhecido =
                    numerosConhecidos.has(numero);


                /* =================================================
                   NOVO CHAMADO REAL
                   Só considera números que não existiam
                   na primeira consulta desta página.
                ================================================= */

                if (!numeroJaConhecido) {

                    numerosConhecidos.add(numero);

                    const deveRecarregar =
                        statusFiltro === "finalizados"
                            ? chamado.status === "FINALIZADO"
                            : statusFiltro === "todos"
                                ? true
                                : (
                                    chamado.status === "ABERTO" ||
                                    chamado.status === "ATENDIMENTO" ||
                                    chamado.status === "FINALIZADO"
                                );

                    if (deveRecarregar) {

                        reloadSolicitado = true;

                        window.location.reload();

                        return;
                    }
                }


                /* =================================================
                   SE A LINHA NÃO ESTÁ NA TABELA,
                   NÃO TENTAR INSERIR OU RECARREGAR POR ISSO.
                   Ela pode estar em outra página ou fora do filtro.
                ================================================= */

                if (!linha) {
                    continue;
                }


                const elementoStatus =
                    linha.querySelector(".status");

                if (!elementoStatus) {
                    continue;
                }


                const statusAtual =
                    elementoStatus.dataset.status;


                /* =================================================
                   CHAMADO FOI FINALIZADO
                   Somente dispara o primeiro reload quando
                   a linha estava na tabela e mudou de status.
                ================================================= */

                if (
                    chamado.status === "FINALIZADO" &&
                    statusAtual !== "FINALIZADO"
                ) {

                    reloadSolicitado = true;

                    sessionStorage.setItem(
                        "segundo_reload_chamado",
                        "1"
                    );

                    window.location.reload();

                    return;
                }


                /* =================================================
                   STATUS NÃO MUDOU
                ================================================= */

                if (statusAtual === chamado.status) {
                    continue;
                }


                /* =================================================
                   ATUALIZAR STATUS VISUAL
                ================================================= */

                elementoStatus.className = "status";

                if (chamado.status === "ABERTO") {

                    elementoStatus.classList.add(
                        "status-aberto"
                    );

                    elementoStatus.textContent = "Aberto";

                } else if (
                    chamado.status === "ATENDIMENTO"
                ) {

                    elementoStatus.classList.add(
                        "status-atendimento"
                    );

                    elementoStatus.textContent =
                        "Em atendimento";

                } else if (
                    chamado.status === "FINALIZADO"
                ) {

                    elementoStatus.classList.add(
                        "status-finalizado"
                    );

                    elementoStatus.textContent =
                        "Finalizado";

                } else {

                    elementoStatus.classList.add(
                        "status-padrao"
                    );

                    elementoStatus.textContent =
                        chamado.status;
                }

                elementoStatus.dataset.status =
                    chamado.status;

            }

        } catch (erro) {

            console.error(
                "Erro ao verificar status dos chamados:",
                erro
            );

        } finally {

            verificacaoEmAndamento = false;

        }

    }


    /* =====================================================
       PRIMEIRA VERIFICAÇÃO
    ===================================================== */

    verificarStatus();


    /* =====================================================
       VERIFICAR AUTOMATICAMENTE A CADA 5 SEGUNDOS
    ===================================================== */

    setInterval(
        verificarStatus,
        5000
    );

});