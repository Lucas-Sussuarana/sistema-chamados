let ultimoNumero = null;
let statusAnteriores = {};


/* =========================================================
   VERIFICAR SE PRECISA FAZER O SEGUNDO REFRESH
========================================================= */

const parametros =
    new URLSearchParams(window.location.search);

const segundoRefresh =
    parametros.get("segundo_refresh");


if (segundoRefresh === "1") {

    console.log(
        "Segundo refresh programado. Aguardando 5 segundos..."
    );


    setTimeout(function () {

        console.log(
            "Executando segundo refresh..."
        );


        /*
         * Remove o parâmetro antes do refresh
         * para não ficar repetindo infinitamente.
         */

        const url =
            new URL(window.location.href);

        url.searchParams.delete(
            "segundo_refresh"
        );


        window.location.href =
            url.toString();

    }, 5000);

}


/* =========================================================
   VERIFICAR CHAMADOS
========================================================= */

async function verificarChamados() {

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


        console.log(
            "STATUS DOS CHAMADOS:",
            dados.chamados
        );


        /* =================================================
           PRIMEIRA EXECUÇÃO
        ================================================= */

        if (ultimoNumero === null) {

            dados.chamados.forEach(
                function (chamado) {

                    statusAnteriores[
                        chamado.numero
                    ] = chamado.status;

                }
            );


            if (
                dados.chamados.length > 0
            ) {

                ultimoNumero =
                    Math.max(
                        ...dados.chamados.map(
                            chamado =>
                                chamado.numero
                        )
                    );

            } else {

                ultimoNumero = 0;

            }


            return;
        }


        /* =================================================
           VERIFICAR NOVO CHAMADO
        ================================================= */

        const novoNumero =
            dados.chamados.length > 0
                ? Math.max(
                    ...dados.chamados.map(
                        chamado =>
                            chamado.numero
                    )
                )
                : 0;


        if (
            novoNumero >
            ultimoNumero
        ) {

            console.log(
                "Novo chamado detectado. Atualizando..."
            );


            window.location.reload();

            return;

        }


        /* =================================================
           VERIFICAR ALTERAÇÃO DE STATUS
        ================================================= */

        for (
            const chamado of dados.chamados
        ) {

            const statusAnterior =
                statusAnteriores[
                    chamado.numero
                ];


            if (
                statusAnterior !== undefined &&
                statusAnterior !==
                    chamado.status
            ) {

                console.log(
                    "STATUS ALTERADO:",
                    "#" + chamado.numero,
                    statusAnterior,
                    "->",
                    chamado.status
                );


                /* =========================================
                   SE FOI FINALIZADO
                ========================================= */

                if (
                    chamado.status ===
                    "FINALIZADO"
                ) {

                    console.log(
                        "Chamado finalizado."
                    );

                    console.log(
                        "Primeiro refresh agora."
                    );


                    /*
                     * Adiciona um parâmetro na URL
                     * avisando a próxima página que
                     * deverá fazer o segundo refresh.
                     */

                    const url =
                        new URL(
                            window.location.href
                        );


                    url.searchParams.set(
                        "segundo_refresh",
                        "1"
                    );


                    /*
                     * PRIMEIRO REFRESH
                     */

                    window.location.href =
                        url.toString();


                    return;

                }


                /* =========================================
                   OUTRAS ALTERAÇÕES DE STATUS
                ========================================= */

                console.log(
                    "Status alterado. Atualizando..."
                );


                window.location.reload();

                return;

            }


            statusAnteriores[
                chamado.numero
            ] = chamado.status;

        }


        ultimoNumero =
            novoNumero;


    } catch (erro) {

        console.error(
            "Erro ao verificar chamados:",
            erro
        );

    }

}


/* =========================================================
   INICIAR
========================================================= */

verificarChamados();


setInterval(
    verificarChamados,
    5000
);