// get elements from HTML document
const form = document.getElementById('input-text');
const send = document.getElementById('send');

// constanst
const errors = [];

send.addEventListener('click', function (event) {
    event.preventDefault();
    let text = document.forms["input-text"]["text"].value;
    callAPI(text);
})

async function callAPI(inputText) {
    try {
        const response = await fetch("https://mAIndmap-API.hf.space/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                text: inputText
            })
        });
    } catch (error) {
        errors.push("Errore nella richiesta: " + error)
        console.log(errors);
    }


    if (!response.ok) {
        errors.push("Errore nella richiesta: " + response.statusText)
        //throw new Error("Errore nella richiesta: " + response.statusText);
    }

    const result = await response.json();

    console.log("title", result.value);
    const title = result.value;
    console.log(title);
    const result_string = JSON.stringify(result);
    document.forms["input-text"]["title"].value = title;
    document.forms["input-text"]["result"].value = result_string;
    sessionStorage.setItem("result", result_string);
    console.log("Risultato:", result);

    console.log(errors);
    if (errors.length > 0) {
        errors.forEach((error) => {
            const error_card = document.createElement('div');
            error_card.classList.add('error_card');
            error_card.innerText = error;
            const error_container = document.getElementById('errors');
            error_container.appendChild(error_card);
        })
    } else {
        form.submit();
    }
}
