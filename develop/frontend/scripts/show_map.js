console.log("js")

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
    spanTitle.style.top = container.offsetHeight + "px";
};

document.addEventListener('DOMContentLoaded', function () {
    fetchAndShowJSON();
})


// Carica e mostra il JSON
async function fetchAndShowJSON() {
    try {
        const JSONString = document.getElementById('result').innerText;
        console.log(JSONString)
        const JSONFile = JSON.parse(JSONString)
        showJSON(JSONFile);
    } catch (error) {
        console.error("Unable to fetch data:", error);
    }
}

// Mostra i dati del JSON
function showJSON(file) {
    if (file.value) {
        spanTitle.innerHTML = `<h1>${file.value}</h1>`;
    } else {
        console.warn("No title found in JSON file");
        spanTitle.innerHTML = "<h1>No Title</h1>";
    }



    const angle_step = findAngle(file.children.length);
    const centerX = container.offsetWidth / 2;
    const centerY = container.offsetHeight;
    const initial_distance = 200

    let angle = angle_step
    for (i = 0; i < file.children.length; i++) {
        buildBranch(centerX, centerY, angle, initial_distance, file.children[i], angle);
        angle = angle + angle_step;
    }


}


function buildBranchDemo(parentX, parentY, angle, distance, element, parent_type) {
    if (!element || !element.value) return;

    let x = 0;
    let y = 0;

    if (parent_type == 'LINK' || element.type == 'LINK') {
        x = findXCatet(angle, (distance / 2));
        y = findYCatet(angle, (distance / 2));
    } else {
        x = findXCatet(angle, distance);
        y = findYCatet(angle, distance);
    }

    const spanX = parentX + x;
    const spanY = parentY + y;

    // 👉 BLOCCO PER EVITARE SOVRAPPOSIZIONE (collision detection)
    const newBox = {
        left: spanX,
        top: spanY,
        right: spanX + 150, // stima larghezza massima
        bottom: spanY + 50  // stima altezza massima
    };

    const elements = document.querySelectorAll('.span-item');
    let collision = false;
    elements.forEach(el => {
        const rect = el.getBoundingClientRect();
        const box = {
            left: rect.left + window.scrollX,
            top: rect.top + window.scrollY,
            right: rect.right + window.scrollX,
            bottom: rect.bottom + window.scrollY
        };

        if (
            newBox.left < box.right &&
            newBox.right > box.left &&
            newBox.top < box.bottom &&
            newBox.bottom > box.top
        ) {
            collision = true;
        }
    });

    if (collision) {
        buildBranch(parentX, parentY, angle, distance + 60, element, parent_type);
        return;
    }

    // 👉 CREA E POSIZIONA IL NODO
    const span = document.createElement('span');
    span.innerHTML = `<p>${element.value}</p>`;
    span.classList.add('span-item');
    span.classList.add(element.type);
    container.appendChild(span);

    span.style.left = spanX + "px";
    span.style.top = spanY + "px";

    // 👉 DISEGNA LA LINEA
    drawLine(parentX, parentY, spanX, spanY);

    // 👉 CONTINUA RICORSIONE
    if (Array.isArray(element.children)) {
        const count = element.children.length;

        if (count == 1) {
            buildBranch(spanX, spanY, angle, distance * 0.95, element.children[0])
        } else {
            const spread = degrees2radians(180);
            const baseAngle = angle - spread / 2;
            const angleStep = spread / count;

            element.children.forEach((child, index) => {
                const nextAngle = baseAngle + index * angleStep;
                buildBranch(spanX, spanY, nextAngle, distance * 0.95, child);
            });
        }
    }
}



function buildBranch(parentX, parentY, angle, distance, element, parent_type) {
    if (!element || !element.value) return;

    let x = 0
    let y = 0

    if (parent_type == 'LINK' || element.type == 'LINK') {
        x = findXCatet(angle, (distance / 2));
        y = findYCatet(angle, (distance / 2));
    } else {
        x = findXCatet(angle, distance);
        y = findYCatet(angle, distance);
    }

    // create element
    const span = document.createElement('span');
    span.innerHTML = `<p>${element.value}</p>`;
    span.classList.add('span-item');
    span.classList.add(element.type);
    container.appendChild(span);

    // positionate element
    const spanX = parentX + x;
    const spanY = parentY + y;
    span.style.left = spanX + "px";
    span.style.top = spanY + "px";

    // draw linking line
    drawLine(parentX, parentY, spanX, spanY);

    // if element has children
    if (Array.isArray(element.children)) {
        const count = element.children.length;

        // if element has only one child
        if (count == 1) {
            buildBranch(spanX, spanY, angle, distance * 0.95, element.children[0])
        } else { // else 

            // set angles
            const spread = degrees2radians(180); // angolo piano
            const baseAngle = angle - spread / 2; // angolo piano rispetto all'angolo del padre
            if (element.id == 586) {
                console.log(radians2degrees(spread, baseAngle))
            }
            const angleStep = ((baseAngle + spread) / (count + 1)) / 2

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
    let radianAngle = degrees2radians(degreeAngle);
    return radianAngle
}

function degrees2radians(degreesAngle) {
    return degreesAngle * Math.PI / 180;
}

function radians2degrees(radiansAngle) {
    return radiansAngle / Math.PI * 180;
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

