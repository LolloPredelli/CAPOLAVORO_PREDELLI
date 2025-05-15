// Array con le posizioni e il contenuto degli span
const spans = [];

// Riferimento al contenitore
const container = document.getElementById('spanContainer');
const addButton = document.getElementById('add-button');
const spanTitle = document.getElementById('span-title');
const svgContainer = document.getElementById('svgContainer');
const button = document.querySelector('button');

button.addEventListener('click', function () {
    addSpan();
})

// Posiziona `spanTitle` e carica il JSON al caricamento della pagina
window.onload = () => {
    spanTitle.style.left = container.offsetWidth / 2 + "px";
    spanTitle.style.top = container.offsetHeight / 2 + "px";

    fetchAndShowJSON();
};

// Carica e mostra il JSON
async function fetchAndShowJSON() {
    try {
        const JSONFile = await openJSONFIle("../Backend/stable/output/result.json");
        showJSON(JSONFile);
    } catch (error) {
        console.error("Unable to fetch data:", error);
    }
}

// Funzione per aprire un file JSON
async function openJSONFIle(path) {
    const answer = await fetch(path);
    if (!answer.ok) {
        throw new Error(`HTTP error! Status: ${answer.status}`);
    }
    return await answer.json();
}

// Mostra i dati del JSON
function showJSON(file) {
    if (file.title) {
        spanTitle.innerHTML = `<h1>${file.title}</h1>`;
    } else {
        spanTitle.innerHTML = "<h1>No Title</h1>";
    }

    const centerX = container.offsetWidth / 2;
    const centerY = container.offsetHeight / 2;

    const angleStep = (2 * Math.PI) / file.branches.length;
    let angle = 0;

    for (let branch of file.branches) {
        const x = centerX + 300 * Math.cos(angle);
        const y = centerY + 300 * Math.sin(angle);
        renderNode(branch, centerX, centerY, x, y);
        angle += angleStep;
    }
}


function renderNode(node, parentX, parentY, x, y, label = null) {
    const span = document.createElement("span");
    span.className = "span-item";
    span.style.left = x + "px";
    span.style.top = y + "px";
    span.innerHTML = `<p>${node.value || "(vuoto)"}</p>`;
    container.appendChild(span);

    // Linea padre -> figlio
    drawLine(parentX, parentY, x, y);

    // Etichetta della connessione (es. "nsubj", "prep", ecc.)
    if (label) {
        const labelElement = document.createElement("div");
        labelElement.className = "line-label";
        labelElement.innerText = label;
        labelElement.style.left = (parentX + x) / 2 + "px";
        labelElement.style.top = (parentY + y) / 2 + "px";
        container.appendChild(labelElement);
    }

    // Calcolo posizione figli
    if (node.children && node.children.length > 0) {
        const childAngleStep = (Math.PI * 2) / node.children.length;
        let childAngle = 0;
        for (let child of node.children) {
            if (!child.value) continue; // ignora oggetti vuoti
            const childX = x + 200 * Math.cos(childAngle);
            const childY = y + 200 * Math.sin(childAngle);
            renderNode(child, x, y, childX, childY, child.dep);
            childAngle += childAngleStep;
        }
    }
}




// funzione per aggiunhgere uno span all'array spans
function addSpan(element) {
    const span = document.createElement('span');
    span.innerHTML = `<p>${element.value}</p>`;
    span.classList.add('span-item');
    container.appendChild(span);
    positionateSpan();
}

// calcola le posizioni degli span
function positionateSpan() {
    const spanItems = document.querySelectorAll('.span-item');
    svgContainer.innerHTML = ""; // Pulisce le linee esistenti

    let angleDifference = findAngle(spanItems.length);
    let spanAngle = 0;

    for (let i = 0; i < spanItems.length; i++) {
        // Centro della pagina
        const centerX = container.offsetWidth / 2;
        const centerY = container.offsetHeight / 2;

        // Calcolo delle posizioni
        let xFromCenter = findXCatet(spanAngle, 300);
        let yFromCenter = findYCatet(spanAngle, 300);

        // Posizionamento dello span
        spanItems[i].style.left = centerX + xFromCenter + "px";
        spanItems[i].style.top = centerY + yFromCenter + "px";

        // Coordinate dello span
        const spanX = centerX + xFromCenter;
        const spanY = centerY + yFromCenter;

        // Disegna una linea tra il titolo e lo span
        drawLine(centerX, centerY, spanX, spanY);

        // Aggiorna l'angolo
        spanAngle += angleDifference;
    }
}


function findAngle(nElements) {
    let degreeAngle = 360 / nElements;
    console.log(degreeAngle);
    let radianAngle = degree2radians(degreeAngle);
    return radianAngle
}

function degree2radians(degreeAngle) {
    return degreeAngle * Math.PI / 180;
}

function findXCatet(angle, ipotentus) {
    let catX = Math.round(ipotentus * Math.cos(angle));
    return catX;
}

function findYCatet(angle, ipotentus) {
    let catY = Math.round(ipotentus * Math.sin(angle));
    return catY;
}

// Funzione per disegnare una linea tra due punti
function drawLine(x1, y1, x2, y2) {
    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line.setAttribute("x1", x1);
    line.setAttribute("y1", y1);
    line.setAttribute("x2", x2);
    line.setAttribute("y2", y2);
    line.setAttribute("stroke", "black");
    line.setAttribute("stroke-width", "2");
    svgContainer.appendChild(line);
}
