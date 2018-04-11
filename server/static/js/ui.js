function padLeft(s, length) {
    s = s.toString();
    while (s.length < length)
        s = '0' + s;
    return s;
}

function dateToString(date) {
    return padLeft(date.getFullYear(), 4) + '-' + padLeft(date.getMonth() + 1, 2) + '-' +
        padLeft(date.getDate(), 2) + ' ' +
        padLeft(date.getHours(), 2) + ':' + padLeft(date.getMinutes(), 2) + ':' +
        padLeft(date.getSeconds(), 2);
}

function escapeHtml(text) {
    return $('<div>').text(text).html();
}

function generateFlagTableRows(rows) {
    var html = '';
    rows.forEach(function (item) {
        var cells = [item.sploit, item.team, item.flag,
            dateToString(new Date(item.time * 1000)), item.status, item.checksystem_response];

        html += '<tr>';
        cells.forEach(function (text) {
            html += '<td>' + escapeHtml(text) + '</td>';
        });
        html += '</tr>';
    });
    return html;
}

function generatePaginator(totalCount, rowsPerPage, pageNumber) {
    var totalPages = Math.ceil(totalCount / rowsPerPage);
    var firstShown = Math.max(1, pageNumber - 3);
    var lastShown = Math.min(totalPages, pageNumber + 3);

    var html = '';
    if (firstShown > 1)
        html += '<li class="page-item"><a class="page-link" href="#" data-content="1">«</a></li>';

    for (var i = firstShown; i <= lastShown; i++) {
        var extraClasses = (i === pageNumber ? "active" : "");
        html += '<li class="page-item ' + extraClasses + '">' +
            '<a class="page-link" href="#" data-content="' + i + '">' + i + '</a>' +
        '</li>';
    }

    if (lastShown < totalPages)
        html += '<li class="page-item">' +
            '<a class="page-link" href="#" data-content="' + totalPages + '">»</a>' +
        '</li>';
    return html;
}

function getPageNumber() {
    return parseInt($('#page-number').val());
}

function setPageNumber(number) {
    $('#page-number').val(number);
}

var queryInProgress = false;

function showFlags() {
    if (queryInProgress)
        return;
    queryInProgress = true;

    $('.search-results').hide();
    $('.query-status').html('Loading...').show();

    $.post('/ui/show_flags', $('#show-flags-form').serialize())
        .done(function (response) {
            $('.search-results tbody').html(generateFlagTableRows(response.rows));

            $('.search-results .total-count').text(response.total_count);
            $('.search-results .pagination').html(generatePaginator(
                response.total_count, response.rows_per_page, getPageNumber()));
            $('.search-results .page-link').click(function (event) {
                event.preventDefault();

                setPageNumber($(this).data("content"));
                showFlags();
            });

            $('.query-status').hide();
            $('.search-results').show();
        })
        .fail(function () {
            $('.query-status').html("Failed to load flags from the farm server");
        })
        .always(function () {
            queryInProgress = false;
        });
}

$(function () {
    showFlags();

    $('#show-flags-form').submit(function (event) {
        event.preventDefault();

        setPageNumber(1);
        showFlags();
    });
});
