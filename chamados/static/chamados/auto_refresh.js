let ultimoNumero = null;

async function verificarNovoChamado() {
    try {
        const resposta = await fetch("/verificar-novo-chamado/");

        if (!resposta.ok) {
            return;
        }

        const dados = await resposta.json();

        if (ultimoNumero === null) {
            ultimoNumero = dados.ultimo_numero;
            return;
        }

        if (dados.ultimo_numero > ultimoNumero) {
            window.location.reload();
        }

    } catch (erro) {
        console.error("Erro ao verificar novos chamados:", erro);
    }
}

setInterval(verificarNovoChamado, 5000);