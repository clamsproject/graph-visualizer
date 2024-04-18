var chosenMMIF = null;
cardIsOpen = false;

$(document).ready(function() {
    $('.card-content').data('panel-state', 'closed');
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


function updatePanel(id) {
    const mmifContent = getMMIFFromID(id)
    entities = mmifContent['entities']
    entityTags = []
    entities.forEach(entity => {entityTags.push(`<span class="tag is-primary">${entity}</span>`)})
    entityTags = entityTags.join(" ")
    if (!cardIsOpen) {
        toggleCardOpen()
    }
    $(".card-header-title").html(function(){
        return `${mmifContent['label']}`
    })
    $(".content").html(function(){
        return `<p>SUMMARY:</p><p>${mmifContent['summary']}</p>${entityTags}`
    })
}

window.onload = function() {
    $("#statsPanel").resizable();
  };

function getMMIFFromID(id) {
    for (elem of nodes) {
        if (elem["id"] === id) {
            chosenMMIF = elem;
            return elem
        }
    }
}

// Get the card elements
const card = document.querySelector('.card');
const cardHeader = card.querySelector('.card-header');
const cardContent = card.querySelector('.card-content');
const cardFooter = card.querySelector('.card-footer');
const icon = cardHeader.querySelector('.fa-angle-down');

// Add a click event listener to the card header
cardHeader.addEventListener('click', toggleCardOpen);

function toggleCardOpen() {
  // Toggle the visibility of the card content and footer
  if (chosenMMIF == null) return;
  cardContent.classList.toggle('is-hidden');
  cardFooter.classList.toggle('is-hidden');

  // Toggle the icon in the card header
  icon.classList.toggle('fa-angle-down');
  icon.classList.toggle('fa-angle-up');

  cardIsOpen = !cardIsOpen;
}