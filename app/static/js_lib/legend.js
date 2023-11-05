function getLegend() {
    return document.querySelector('#legend');
}

function populateLegend(legendHtml) {
    const legend = getLegend();
    legend.innerHTML = legendHtml;
}