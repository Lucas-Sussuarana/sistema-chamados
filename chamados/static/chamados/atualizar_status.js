document.addEventListener("DOMContentLoaded", function () {

    async function verificarStatus() {

        try {

            const resposta = await fetch(
                "/verificar-status-chamados/"
            );

            if (!resposta.ok) {
                return;
            }

            const dados = await resposta.json();

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


            dados.chamados.forEach(function (chamado) {

                let linha = document.querySelector(
                    `tr[data-chamado="${chamado.numero}"]`
                );


                /*
                 * Se o chamado não está na tabela
                 * e está aberto ou em atendimento,
                 * adiciona automaticamente.
                 */
                if (
                    !linha &&
                    (
                        chamado.status === "ABERTO" ||
                        chamado.status === "ATENDIMENTO"
                    )
                ) {

                    const novaLinha = document.createElement("tr");

                    novaLinha.setAttribute(
                        "data-chamado",
                        chamado.numero
                    );

                    let classeStatus = "status-padrao";
                    let textoStatus = chamado.status;

                    if (chamado.status === "ABERTO") {

                        classeStatus = "status-aberto";
                        textoStatus = "Aberto";

                    } else if (
                        chamado.status === "ATENDIMENTO"
                    ) {

                        classeStatus = "status-atendimento";
                        textoStatus = "Em atendimento";

                    }

                    novaLinha.innerHTML = `
                        <td>
                            <a
                                href="/consultar/${chamado.numero}/"
                                class="numero-chamado"
                            >
                                #${chamado.numero}
                            </a>
                        </td>

                        <td>
                            ${chamado.solicitante || ""}
                        </td>

                        <td>
                            ${chamado.setor || ""}
                        </td>

                        <td>
                            ${chamado.local || ""}
                        </td>

                        <td>
                            ${chamado.data_abertura || ""}
                        </td>

                        <td>
                            <span
                                class="status ${classeStatus}"
                                data-status="${chamado.status}"
                            >
                                ${textoStatus}
                            </span>
                        </td>
                    `;

                    tbody.insertBefore(
                        novaLinha,
                        tbody.firstChild
                    );

                    return;
                }


                /*
                 * Se a linha não existe,
                 * não há mais nada para atualizar.
                 */
                if (!linha) {
                    return;
                }


                const status = linha.querySelector(".status");

                if (!status) {
                    return;
                }


                const statusAtual = status.dataset.status;


                /*
                 * Se o chamado foi finalizado,
                 * remove a linha da lista.
                 */
                if (
                    chamado.status === "FINALIZADO" &&
                    statusAtual !== "FINALIZADO"
                ) {

                    linha.remove();
                    return;

                }


                /*
                 * Se o status não mudou,
                 * não faz nada.
                 */
                if (statusAtual === chamado.status) {
                    return;
                }


                /*
                 * Atualiza visualmente o status.
                 */
                status.className = "status";


                if (chamado.status === "ABERTO") {

                    status.classList.add("status-aberto");
                    status.textContent = "Aberto";

                } else if (
                    chamado.status === "ATENDIMENTO"
                ) {

                    status.classList.add("status-atendimento");
                    status.textContent = "Em atendimento";

                } else if (
                    chamado.status === "FINALIZADO"
                ) {

                    status.classList.add("status-finalizado");
                    status.textContent = "Finalizado";

                } else {

                    status.classList.add("status-padrao");
                    status.textContent = chamado.status;

                }

                status.dataset.status = chamado.status;

            });


            /*
             * Reativa o clique nas novas linhas.
             */
            tbody.querySelectorAll("tr").forEach(function (linha) {

                const link = linha.querySelector(".numero-chamado");

                if (!link) {
                    return;
                }

                if (linha.dataset.cliqueConfigurado) {
                    return;
                }

                linha.dataset.cliqueConfigurado = "true";

                linha.style.cursor = "pointer";

                linha.addEventListener(
                    "click",
                    function (evento) {

                        if (
                            evento.target.closest("a") ||
                            evento.target.closest("button") ||
                            evento.target.closest("input") ||
                            evento.target.closest("select")
                        ) {
                            return;
                        }

                        window.location.href = link.href;

                    }
                );

            });

        } catch (erro) {

            console.error(
                "Erro ao verificar status dos chamados:",
                erro
            );

        }

    }


    setInterval(verificarStatus, 5000);

});