document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       VERIFICAR SE EXISTE UM SEGUNDO RELOAD PENDENTE
    ===================================================== */

    const segundoReload =
        sessionStorage.getItem(
            "segundo_reload_chamado"
        );


    if (segundoReload === "1") {

        setTimeout(function () {

            sessionStorage.removeItem(
                "segundo_reload_chamado"
            );

            window.location.reload();

        }, 5000);

    }


    /* =====================================================
       VERIFICAR CHAMADOS
    ===================================================== */

    async function verificarStatus() {

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


            const dados =
                await resposta.json();


            const tabela =
                document.querySelector(
                    ".tabela-container table"
                );


            if (!tabela) {
                return;
            }


            const tbody =
                tabela.querySelector("tbody");


            if (!tbody) {
                return;
            }


            /* =================================================
               VERIFICAR CADA CHAMADO
            ================================================= */

            dados.chamados.forEach(function (chamado) {

                let linha =
                    document.querySelector(
                        `tr[data-chamado="${chamado.numero}"]`
                    );


                /* =================================================
                   NOVO CHAMADO
                ================================================= */

                if (
                    !linha &&
                    (
                        chamado.status === "ABERTO" ||
                        chamado.status === "ATENDIMENTO"
                    )
                ) {

                    console.log(
                        "Novo chamado detectado: #" +
                        chamado.numero
                    );


                    window.location.reload();

                    return;
                }


                /*
                 * Se o chamado não está na tabela,
                 * não há nada para atualizar.
                 */

                if (!linha) {
                    return;
                }


                const status =
                    linha.querySelector(".status");


                if (!status) {
                    return;
                }


                const statusAtual =
                    status.dataset.status;


                /* =================================================
                   CHAMADO FINALIZADO
                ================================================= */

                if (
                    chamado.status === "FINALIZADO" &&
                    statusAtual !== "FINALIZADO"
                ) {

                    console.log(
                        "Chamado finalizado: #" +
                        chamado.numero
                    );


                    /*
                     * Marca que após o primeiro reload
                     * deverá ocorrer o segundo reload.
                     */

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

                if (
                    statusAtual === chamado.status
                ) {

                    return;
                }


                /* =================================================
                   ATUALIZAR STATUS VISUAL
                ================================================= */

                status.className =
                    "status";


                if (
                    chamado.status === "ABERTO"
                ) {

                    status.classList.add(
                        "status-aberto"
                    );

                    status.textContent =
                        "Aberto";


                } else if (
                    chamado.status === "ATENDIMENTO"
                ) {

                    status.classList.add(
                        "status-atendimento"
                    );

                    status.textContent =
                        "Em atendimento";


                } else if (
                    chamado.status === "FINALIZADO"
                ) {

                    status.classList.add(
                        "status-finalizado"
                    );

                    status.textContent =
                        "Finalizado";


                } else {

                    status.classList.add(
                        "status-padrao"
                    );

                    status.textContent =
                        chamado.status;

                }


                status.dataset.status =
                    chamado.status;

            });


        } catch (erro) {

            console.error(
                "Erro ao verificar status dos chamados:",
                erro
            );

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