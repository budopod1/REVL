setTimeout(() => {
    const css = `
input:focus {
    border: 3px solid blue !important;
}
    `;

    const styleElem = document.createElement("style");
    styleElem.appendChild(document.createTextNode(css));
    document.head.appendChild(styleElem);
}, 0);
