// Array con le posizioni e il contenuto degli span
const spans = [];

// Riferimento al contenitore
const container = document.getElementById('spanContainer');
const addButton = document.getElementById('add-button');
const spanTitle = document.getElementById('span-title');
const svgContainer = document.getElementById('svgContainer');

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
        console.warn("No title found in JSON file");
        spanTitle.innerHTML = "<h1>No Title</h1>";
    }



    const angle_step = findAngle(file.branches.length);
    const centerX = container.offsetWidth / 2;
    const centerY = container.offsetHeight / 2;
    const initial_distance = 200

    let angle = angle_step
    for (i = 0; i < file.branches.length; i++) {
        buildBranch(centerX, centerY, angle, initial_distance, file.branches[i], angle);
        angle = angle + angle_step;
    }


}

function buildBranch(parentX, parentY, angle, distance, element, source_angle = null) {
    if (!element || !element.value) return;

    const x = findXCatet(angle, distance);
    const y = findYCatet(angle, distance);

    let span = null
    span = document.createElement('span');
    span.innerHTML = `<p>${element.value}</p>`;
    span.classList.add('span-item');
    if (element.type == 'LINK') {
        span.classList.add('link');
        container.appendChild(span);
        const spanX = parentX + (x / 2);
        const spanY = parentY + (y / 2);
        span.style.left = spanX + "px";
        span.style.top = spanY + "px";

        if (Array.isArray(element.children)) {
            element.children.forEach((child, index) => {
                buildBranch(parentX, parentY, angle, distance, child);
            });
        }

    } else {
        span.classList.add('block');
        container.appendChild(span);
        const spanX = parentX + x;
        const spanY = parentY + y;
        span.style.left = spanX + "px";
        span.style.top = spanY + "px";
        drawLine(parentX, parentY, spanX, spanY);

        if (Array.isArray(element.children)) {
            const count = element.children.length;
            const spread = Math.PI / 2; // angolo piano
            const baseAngle = angle - spread / 2; // angolo piano rispetto all'elemento padre
            const angleStep = ((baseAngle + spread) / (count + 1))

            element.children.forEach((child, index) => {
                const nextAngle = baseAngle + index * angleStep;
                buildBranch(spanX, spanY, nextAngle, distance * 0.95, child);
            });
        }
    }
}

function fix_contacts() {
    const spans = document.querySelectorAll('span');

    spans.forEach((current_span) => {
        spans.forEach((span) => {
            while (current_span.style.left <= (span.style.right + 5) && current_span.style.left >= span.style.left) {
                current_span.style.left++;
            }

            while (current_span.style.bottom <= (span.style.top + 5) && current_span.style.bottm >= span.style.bottom) {
                current_span.style.bottom++;
            }
        })
    })
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

