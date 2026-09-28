document.addEventListener("DOMContentLoaded", function () {
    const tabela = document.querySelector("#changelist .results table");

    if (!tabela) {
        return;
    }

    tabela.querySelectorAll("tbody tr").forEach(function (linha) {
        const link = linha.querySelector(".field-numero a");

        if (!link) {
            return;
        }

        linha.style.cursor = "pointer";

        linha.addEventListener("click", function (evento) {
            // Não interfere em checkbox, botões ou outros controles
            if (
                evento.target.closest("input") ||
                evento.target.closest("button") ||
                evento.target.closest("select") ||
                evento.target.closest("a")
            ) {
                return;
            }

            window.location.href = link.href;
        });
    });
});