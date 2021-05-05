function generateFlagTableRows(rows) {
    let dateFormat = new Intl.DateTimeFormat('it-IT', { dateStyle: "short", timeStyle: "long" })
    let html = '';
    let STATUSES = {
        "QUEUED": "bi-clock-fill text-warning",
        "ACCEPTED": "bi-check-circle-fill text-success",
        "REJECTED": "bi-x-circle-fill text-danger",
        "SKIPPED": "bi-skip-forward-circle-fill text-info"
    };
    rows.forEach(item => {

        let cells = [
            item.sploit,
            item.team !== null ? item.team : '',
            `<code>${item.flag}</code>`,
            dateFormat.format(new Date(item.time * 1000)),
            item.sent_cycle,
            `<i class="bi ${STATUSES[item.status]}"></i>`,
            item.checksystem_response !== null ? item.checksystem_response : '',
        ];

        html += '<tr>';
        cells.forEach(text => {
            html += `<td>${text}</td>`;
        });
        html += '</tr>';
    });
    return html;
}

function generatePaginator(totalCount, rowsPerPage, pageNumber) {
    let totalPages = Math.ceil(totalCount / rowsPerPage);
    let firstShown = Math.max(1, pageNumber - 3);
    let lastShown = Math.min(totalPages, pageNumber + 3);

    let html = '';
    if (firstShown > 1)
        html += '<li class="page-item"><a class="page-link" href="#" data-content="1">«</a></li>';

    for (let i = firstShown; i <= lastShown; i++) {
        let extraClasses = (i === pageNumber ? "active" : "");
        html += `<li class="page-item ${extraClasses}">
                    <a class="page-link" href="#" data-content="${i}">${i}</a>
                </li>`;
    }

    if (lastShown < totalPages)
        html += `<li class="page-item">
                    <a class="page-link" href="#" data-content="${totalPages}">»</a>
                </li>`;
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
            <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width: 100%"></div>
        </div>
    `).show();

    $.get('/ui/show_flags?' + $('#show-flags-form').serialize())
        .done(response => {
            $('.search-results tbody').html(generateFlagTableRows(response.rows));

            $('.search-results .total-count').text(response.total_count);
            $('.search-results .pagination').html(
                generatePaginator(response.total_count, response.rows_per_page, getPageNumber())
            );
            $('.search-results .page-link').click((event) => {
                event.preventDefault();

                setPageNumber($(event.currentTarget).data("content"));
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
    $("#post-flags-manual-progress").show()

    $.post('/ui/post_flags_manual', $('#post-flags-manual-form').serialize())
        .done(() => {
            var sploitSelect = $('#sploit-select');
            if ($('#sploit-manual-option').empty())
                sploitSelect.append($('<option id="sploit-manual-option">Manual</option>'));
            sploitSelect.val('Manual');

            $('#team-select, #flag-input, #time-since-input, #time-until-input, ' +
                '#status-select, #checksystem-response-input').val('');

            queryInProgress = false;
            $("#post-flags-manual-progress").hide();
            showFlags();
        })
        .fail(() => {
            $('.query-status').html(`
            <div class="alert alert-danger" role="alert">
                Failed to post flags to the farm server
            </div>
            `);

            queryInProgress = false;
            $("#post-flags-manual-progress").hide();
        });
}

let GRAPH_CONFIG = {
    type: 'bar',
    data: {
        datasets: [{
            label: "Totale",
            type: "line",

            fill: true,
            borderColor: 'hsla(120, 50%, 50%, 0.6)',
            backgroundColor: 'hsla(120, 50%, 50%, 0.05)',
            tension: 0.6,
            cubicInterpolationMode: "monotone"

        }]
    },
    options: {
        maintainAspectRatio: false,
        //responsive: true,
        barThickness: "flex",
        plugins: {
            zoom: {
                zoom: {
                    enabled: true,
                    mode: 'x',
                },
                pan: {
                    enabled: true,
                    mode: "x"
                },
                limits: {
                    x: {
                        min: 0
                    },
                    y: {
                        min: 0
                    }
                }
            },
            legend: {
                position: 'top',
            },
            title: {
                display: false,
            },
            tooltip: {
                enabled: false
            },
        },
        scales: {
            x: {
                type: "linear",
                beginAtZero: true,
                ticks: {
                    stepSize: 1
                }

            },
            y: {
                type: "linear",
                beginAtZero: true,
                ticks: {
                    stepSize: 1
                },
                grace: '10%',
                //stacked: true,
            }
        }
    },
};

var SPLOITS = new Set();
function updateGraph(chart) {
    let sse = new EventSource("/api/graphstream")
    let l_values = []
    sse.onmessage = (resp) => {
        let elements = JSON.parse(resp.data);
        if (elements.length == 0) return;


        elements.forEach(elem => {
            let cycle = elem["cycle"];
            let total = 0;
            for (sploit of new Set([...Object.keys(elem["sploits"]), ...SPLOITS])) {

                let index = chart.data.datasets.findIndex(el => el.label == sploit);
                let n = elem["sploits"][sploit] || 0;
                total += n;
                if (index != -1) {
                    chart.data.datasets[index].data.push({ x: cycle, y: n });
                } else {
                    SPLOITS.add(sploit);
                    chart.data.datasets.push({
                        type: "bar",
                        borderColor: 'hsla(' + hashCode(sploit) % 360 + ', 70%, 50%, 1)',
                        backgroundColor: 'hsla(' + hashCode(sploit) % 360 + ', 70%, 50%, 0.5)',
                        borderWidth: 1,

                        label: sploit,
                        data: [{ x: cycle, y: n }],
                    });
                }
            }
            // if (total == 0) return;

            l_values.push(total)
            let DIM = 3;
            if (l_values.length > DIM - 1) {
                l_values.shift()

                chart.data.datasets[0].data.push({ x: cycle, y: l_values.reduce((a, b) => a + b) / DIM });
            }
        })

        chart.update()
    };
}

function hashCode(str) { // java String#hashCode
    var hash = 5831;
    for (var i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    return hash;
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


    // Update table every x seconds
    var REF_INTERVAL = 30; // Seconds
    var i = 0;
    setInterval(() => {
        if (i < REF_INTERVAL) {
            i++;
            let prog = i / REF_INTERVAL * 100;
            $("#refresh-progress").attr('aria-valuenow', prog).css('width', prog + '%');
            $("#refresh-progress").html(`Refresh in ${REF_INTERVAL - i}`);
        } else {
            i = 0;
            $("#refresh-progress").attr('aria-valuenow', 0).css('width', '0%');
            showFlags();
        }
    }, 1000)
});