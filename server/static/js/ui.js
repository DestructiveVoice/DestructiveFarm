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
        var cells = [
            item.sploit,
            item.team !== null ? item.team : '',
            item.flag,
            dateToString(new Date(item.time * 1000)),
            item.status,
            item.checksystem_response !== null ? item.checksystem_response : ''
        ];

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
    $('.query-status').html(`
        <div class="progress">
            <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width: 75%"></div>
        </div>
    `).show();

    $.post('/ui/show_flags', $('#show-flags-form').serialize())
        .done((response) => {
            $('.search-results tbody').html(generateFlagTableRows(response.rows));

            $('.search-results .total-count').text(response.total_count);
            $('.search-results .pagination').html(generatePaginator(
                response.total_count, response.rows_per_page, getPageNumber()));
            $('.search-results .page-link').click((event) => {
                event.preventDefault();

                setPageNumber($(this).data("content"));
                showFlags();
            });

            $('.query-status').hide();
            $('.search-results').show();
        })
        .fail(() => {
            $('.query-status').html(`
                <div class="alert alert-danger" role="alert">
                    Failed to load flags from the farm server
                </div>`
            );
        })
        .always(() => {
            queryInProgress = false;
        });
}

function postFlagsManual() {
    if (queryInProgress)
        return;
    queryInProgress = true;

    $.post('/ui/post_flags_manual', $('#post-flags-manual-form').serialize())
        .done(function () {
            var sploitSelect = $('#sploit-select');
            if ($('#sploit-manual-option').empty())
                sploitSelect.append($('<option id="sploit-manual-option">Manual</option>'));
            sploitSelect.val('Manual');

            $('#team-select, #flag-input, #time-since-input, #time-until-input, ' +
                '#status-select, #checksystem-response-input').val('');

            queryInProgress = false;
            showFlags();
        })
        .fail(function () {
            $('.query-status').html("Failed to post flags to the farm server");
            queryInProgress = false;
        });
}

let GRAPH_CONFIG = {
    type: 'line',
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: false,
            }
        },
        scales: {
            x: {
                type: "time"
            },
            y: {
                type: "logarithmic"
            }
        }
    },
};
function updateGraph(chart) {
    let sse = new EventSource("/api/graphstream")

    sse.onmessage = (resp) => {
        let json = JSON.parse(resp.data);
        if (json.length == 0) return;

        json.forEach(sploit => {
            let index = chart.data.datasets.findIndex(el => el.label == sploit.sploit)
            if (index != -1) {
                chart.data.datasets[index].data.push({ x: Date.now(), y: sploit.n })
            } else {
                chart.data.datasets.push({
                    borderColor: 'hsla(' + (Math.random() * 360) + ', 100%, 50%, 1)',
                    fill: false,

                    label: sploit.sploit,
                    data: [{ x: Date.now(), y: sploit.n }],
                });
            }
        })

        chart.update()
    };
}


$(() => {
    showFlags();

    $('#show-flags-form').submit(function (event) {
        event.preventDefault();

        setPageNumber(1);
        showFlags();
    });
    $('#post-flags-manual-form').submit(function (event) {
        event.preventDefault();

        postFlagsManual();
    });

    var ctx = document.getElementById('flag-graph').getContext('2d');
    var chart = new Chart(ctx, GRAPH_CONFIG)

    updateGraph(chart)
});