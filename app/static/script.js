let message = document.getElementById("message")
message.addEventListern("input", () => {
    let count = (message.value).legnth;
    document.getElementById("charcount").
    textContent = 'Total characters: ${count}';
});