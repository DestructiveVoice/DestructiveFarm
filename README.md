Destructive Farm
================

<p align="center">
    Language: <b>English</b> | <a href="https://github.com/DestructiveVoice/DestructiveFarm/blob/master/docs/ru/index.md">Русский</a>
</p>

Exploit farm for attack-defense CTF competitions

<p align="center">
    <img src="https://github.com/borzunov/DestructiveFarm/blob/master/docs/images/farm_server_screenshot.png" width="700">
</p>

Read the [FAQ](docs/en/faq.md) if you want to know what are attack-defense CTFs, what features this farm has and why it has the architecture described below.

## Components

1. An **exploit** is a script that steals flags from some service of other teams. It is written by a participant during the competition and should accept a victim's host (an IP address or a domain) as the first command-line argument, attack them and print flags to stdout.

    [Example](client/spl_example_runme.py) | [More details](docs/en/exploit_format.md)

2. A **farm client** is a tool that periodically runs exploits to attack other teams and looks after their work. It is being run by a participant on their laptop after they've written an exploit.

    The client is a one-file script [start_sploit.py](client/start_sploit.py) from this repository.

    [More details](docs/en/farm_client.md)

3. A **farm server** is a tool that collects flags from farm clients, sends them to the checksystem, monitors the usage of quotas and shows the stats about the accepted and rejected flags. It is being configured and run by a team's admin in the beginning of the competition. After that, team members can use its web interface (see the screenshot above) to watch the exploits' results and stats.

    The server is a Flask web service from the [server](server) directory of this repository.

    [More details](docs/en/farm_client.md)

<p align="center">
    <img src="https://github.com/borzunov/DestructiveFarm/blob/master/docs/images/diagram.png" width="500"><br><br>
    <i>The arrows display the flow of the flags</i>
</p>

## Future plans

See [here](https://github.com/borzunov/DestructiveFarm/issues/1).

## Alternatives

- The [Bay's farm](https://github.com/alexbers/exploit_farm) is a simpler farm whose architecture and some implementation details were adopted in this project. It uses the same exploit format and also divided to a client (*start_sploit.py*) and a server (*start_posting.py*). However, it requires them to be run on the same computer (see the [FAQ](docs/en/faq.md) on why it's bad), and the server doesn't have a web interface.

- The [Andrew Gein's farm](https://github.com/andgein/ctf-exploit-farm) solves the issue of the large number of processes (in case of the large number of teams) using asynchronous networking (asyncio).

## Authors

Copyright &copy; 2017&ndash;2018 Aleksandr Borzunov ("Destructive Voice" team)

Inspired by the [Bay's farm](https://github.com/alexbers/exploit_farm).
