nodesPromise.then(() => drawTimeline());

function drawTimeline() {

    dates = nodes.map(d => {
        const dateString = Date.parse(d.date);
        if (isNaN(dateString)) return null;
        const date = new Date(dateString);
        return date.getFullYear();
    });

    console.log(dates);

    const startYear = Math.min(...dates)-1;
    const endYear = Math.max(...dates)+1;
    console.log(startYear);
    console.log(endYear);
    const timeline = $('#timeline');
    const timelineWidth = timeline.width();
    const numYears = endYear - startYear + 1;
    const yearWidth = timelineWidth / numYears;
    let dragStart = null;
    let dragEnd = null;
    let selectionBox = null;


    if (numYears > 10) labelEvery = 5;
    else labelEvery = 1;

    let i = 0;
    for (let year = startYear; year <= endYear; year++) {
        const tickX = (year - startYear) * yearWidth;
        if (i % labelEvery == 0) {
            const $bigtick = $('<div>').addClass('bigtick').css('left', `${tickX}px`);
            timeline.append($bigtick);
            const $label = $('<div>').addClass('label').css('left', `${tickX - 5}px`).text(year);
            timeline.append($label);
        } else {
            const $tick = $('<div>').addClass('tick').css('left', `${tickX}px`);
            timeline.append($tick);
        }
        i++;
    }

    let isDragging = false;

    timeline.on('mousedown', function (e) {
        selectionBox = null;
        dragStart = e.clientX - timeline.offset().left;
        isDragging = true;

        $(".selection-box").remove();
        $('.date-circle').removeClass('highlighted');

    });

    timeline.on('mousemove', function (e) {
        if (!isDragging) return;
        dragEnd = e.clientX - timeline.offset().left;
        updateSelectionBox(dragStart, dragEnd);
    });


    timeline.on('mouseup', function (e) {
        dragEnd = e.clientX - timeline.offset().left;

        yearRange = getYearRange(dragStart, dragEnd);
        searchFilter({ field: "date", value: yearRange }, section = "timeline")

        isDragging = false;
        dragStart = null;
        dragEnd = null;
    });

    function getDatePosition(year) {
        return (year - startYear) * yearWidth;
    }

    let dateY = {}
    let circleElems = {}
    for (const date of dates) {
        const dateX = getDatePosition(date);
        if (date in dateY) {
            bottom = `${dateY[date]}px`;
            dateY[date] += 10;
        }
        else {
            bottom = '10px';
            dateY[date] = 10;
        }
        const $circle = $('<div>').addClass('date-circle').css({
            left: `${dateX - 5}px`,
            bottom: bottom
        });
        timeline.append($circle);
        if (dateX in circleElems)
            circleElems[dateX].push($circle);
        else
            circleElems[dateX] = [$circle]
    }

    function updateSelectionBox(start, end) {
        const left = Math.min(start, end);
        const right = Math.max(start, end);

        if (!selectionBox) {
            selectionBox = $('<div>').addClass('selection-box').appendTo(timeline);
        }
        selectionBox.css({
            left: `${left}px`,
            width: `${right - left}px`
        });

        $('.date-circle').removeClass('highlighted');
        for (const [x, circles] of Object.entries(circleElems)) {
            if (x >= left && x <= right) {
                for (const circle of circles)
                    circle.addClass('highlighted');
            }
        }

    }

    function getYearRange(start, end) {
        years = [];
        const left = Math.min(start, end);
        const right = Math.max(start, end);

        for (let year = startYear; year <= endYear; year++) {
            if (getDatePosition(year) >= left && getDatePosition(year) <= right) {
                years.push(year);
            }
        }
        return years;
    }
}