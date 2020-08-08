Destructive Farm
================

<p align="center">
    Language: <b>English</b> | <a href="https://github.com/DestructiveVoice/DestructiveFarm/blob/master/docs/ru/index.md">Русский</a>
</p>

Exploit farm for attack-defense CTF competitions

<p align="center">
    <img src="https://github.com/borzunov/DestructiveFarm/blob/master/docs/images/farm_server_screenshot.png" width="700">
</p>

Read the [FAQ](docs/en/faq.md) if you want to know what attack-defense CTFs are, why you need this exploit farm for them, and why it has the architecture described below.

## Components

1. An **exploit** is a script that steals flags from some service of other teams. It is written by a participant during the competition and should accept the victim's host (IP address or domain) as the first command-line argument, attack them and print flags to stdout.

    [Example](client/spl_example.py) | [More details](docs/en/exploit_format.md)

2. A **farm client** is a tool that periodically runs exploits to attack other teams and looks after their work. It is being run by a participant on their laptop after they've written an exploit.

    The client is a one-file script [start_sploit.py](client/start_sploit.py) from this repository.

    [More details](docs/en/farm_client.md)

3. A **farm server** is a tool that collects flags from farm clients, sends them to the checksystem, monitors the usage of quotas and shows the stats about the accepted and rejected flags. It is being configured and run by a team's admin at the start of the competition. After that, team members can use a web interface (see the screenshot above) to watch the exploits' results and stats.

    The server is a Flask web service from the [server](server) directory of this repository.

    [More details](docs/en/farm_server.md)

<p align="center">
    <img src="https://github.com/borzunov/DestructiveFarm/blob/master/docs/images/diagram_en.png" width="500"><br><br>
    <i>The arrows display the flow of the flags</i>
</p>

## Future Plans

See the list [here](https://github.com/borzunov/DestructiveFarm/issues/1).

## Authors

Copyright &copy; 2017&ndash;2018 [Aleksandr Borzunov](https://github.com/borzunov)

Inspired by the [Bay's farm](https://github.com/alexbers/exploit_farm).
