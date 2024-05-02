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

}

function removeSearchSection(section) {
    delete queries[section];
    updateGraphSearch();
}