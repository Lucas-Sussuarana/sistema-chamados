document.addEventListener("DOMContentLoaded", function () {
    const tabela = document.querySelector(".tabela-container table");

    if (!tabela) {
        return;
    }

    tabela.querySelectorAll("tbody tr").forEach(function (linha) {
        const link = linha.querySelector(".numero-chamado");

        if (!link) {
            return;
        }

        linha.style.cursor = "pointer";

        linha.addEventListener("click", function (evento) {
            if (
                evento.target.closest("a") ||
                evento.target.closest("button") ||
                evento.target.closest("input") ||
                evento.target.closest("select")
            ) {
                return;
            }

            window.location.href = link.href;
        });
    });
});