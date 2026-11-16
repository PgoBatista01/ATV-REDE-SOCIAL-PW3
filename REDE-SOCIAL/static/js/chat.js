
document.addEventListener("DOMContentLoaded", () => {

    const socket = io();

    const formulario = document.getElementById("chat-formulario");
    const campoMensagem = document.getElementById("mensagem");
    const areaMensagens = document.getElementById("chat-mensagens");

    if (!formulario || !campoMensagem || !areaMensagens) {
        return;
    }

    // Entrar no chat
    socket.on("connect", () => {
        socket.emit("join");
    });

    // Enviar mensagem
    formulario.addEventListener("submit", (evento) => {
        evento.preventDefault();

        const mensagem = campoMensagem.value.trim();

        if (!mensagem) {
            return;
        }

        if (mensagem.length > 500) {
            alert("A mensagem deve ter no máximo 500 caracteres.");
            return;
        }

        socket.emit("msg", {
            mensagem: mensagem
        });

        campoMensagem.value = "";
        campoMensagem.focus();
    });

    // Receber mensagens
    socket.on("showmsg", (dados) => {

        const mensagem = document.createElement("div");
        mensagem.classList.add("chat-mensagem");

        if (dados.tipo === "entrada" || dados.tipo === "saida") {
            mensagem.classList.add("chat-sistema");
            mensagem.textContent = dados.mensagem;
        } else {

            const nome = document.createElement("strong");
            nome.textContent = dados.nickname + ": ";

            const texto = document.createElement("span");
            texto.textContent = dados.mensagem;

            const horario = document.createElement("small");
            horario.textContent = dados.horario || "";

            mensagem.appendChild(nome);
            mensagem.appendChild(texto);
            mensagem.appendChild(horario);
        }

        areaMensagens.appendChild(mensagem);

        // Manter a mensagem mais recente visível
        areaMensagens.scrollTop = areaMensagens.scrollHeight;
    });

});
