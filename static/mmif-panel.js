$(document).ready(function() {
    $('#mmifPanel').data('panel-state', 'closed');
    var panelContent = $('#mmifPanel').find(".panel-content");
    panelContent.slideToggle();
  });

$(".panel-header").click(function(){
    var panel = $(this).parent();
    var panelContent = panel.find(".panel-content");
    var panelId = panel.data("panel-id");
    var panelState = panel.data("panel-state");
    
    panelContent.slideToggle("slow");
    $(this).toggleClass("active");
    $(this).find(".fa-regular").toggleClass("rotated")
    
    if (panelState === "closed") {
        panel.data("panel-state", "open");
        // code to handle opening the panel
    } else {
        panel.data("panel-state", "closed");
        // code to handle closing the panel
    }
});

// $(".panel-header").html(function() {
//     if (clickedNode == null) return "No MMIF file selected!"
//     else return clickedNode
// })

function updatePanel(id) {
    const mmifContent = getMMIFFromID(id)
    const dropdownCaret = '<i class="fa-regular fa-square-caret-down fa-xl"></i>'
    $(".panel-header").html(function(){
        return `<p>${mmifContent['label']}</p>${dropdownCaret}`
    })
    $(".panel-content").html(function(){
        return `<p>SUMMARY:</p><p>${mmifContent['summary']}</p><a href="/">Visualize file</a>`
    })
}

window.onload = function() {
    $("#statsPanel").resizable();
  };

function getMMIFFromID(id) {
    for (elem of nodes) {
        if (elem["id"] === id) {
            return elem
        }
    }
}