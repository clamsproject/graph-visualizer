let queries = {};
function searchFilter(query, section) {
    queries[section] = query;
    updateGraphSearch();
}

function updateGraphSearch() {
    let matches = {};
    for (mmifNode of nodes) {
        matches = 0;
        for (const [k, v] of Object.entries(queries)) {    
            if (v.value.length == 0) {
                matches++;
            }
            else if (v.field == "all") {
                if (Object.values(mmifNode).some(value => typeof value == "string" &&
                    value.toLowerCase().includes(v.value.toLowerCase()))) {
                        matches++;
                    }

            }

            else if (v.field == "entity") {
                if (mmifNode.entities.includes(hoveredEntity)) {
                    matches++;
                }
            }

            else if (v.field == "date") {
                nodeYear = new Date(mmifNode.date).getFullYear();
                if (v.value.includes(nodeYear)) {
                    matches++;
                }
            }

            else if (mmifNode[v.field].some(app => v.value.includes(app))) {
                matches++;
            }
        }

        if (matches == Object.keys(queries).length) {
            mmifNode.hidden = false;
        } else {
            mmifNode.hidden = true;
        }
    }
    
    tick();
    if (!frozen) updateGraph();
    renderCloud();

    $("#searchTags").empty();
    for (const [k, v] of Object.entries(queries)) {

        let textContent = v.value;
        if (k == "timeline") {
            minYear = Math.min(...v.value)
            maxYear = Math.max(...v.value)

            if (minYear == Infinity || maxYear == -Infinity) continue;

            textContent = `${minYear} - ${maxYear}`;
        }
        if (k == "searchbar" && v.value.length == 0) continue;

        spanTag = document.createElement('div');
        spanTag.textContent = textContent;
        const closeIcon = document.createElement('i');
        closeIcon.classList.add('fas', 'fa-times');
        spanTag.appendChild(closeIcon);
        spanTag.classList.add('tag', 'is-primary', 'searchTag');
        $("#searchTags").append(spanTag);

        closeIcon.onclick = function() {
            removeSearchSection(k);
        }
        
    }

}

function removeSearchSection(section) {
    delete queries[section];
    updateGraphSearch();
}