Farm Client
===========

<p align="center">
    <img src="https://github.com/borzunov/DestructiveFarm/blob/master/docs/images/farm_client_screenshot.png" width="600">
</p>

The **farm client** is a tool that periodically runs exploits to attack other teams and looks after their work. It is being run by a participant on their laptop after they've written an exploit.

The client is a one-file script [start_sploit.py](../../client/start_sploit.py) from this repository.

## Installation and Running

The client requires Python 3 and OS Linux, macOS, or Windows. It does not require any libraries to be installed.

To install the client on Linux or macOS, run:

```bash
wget bit.ly/start_sploit_v4 -O start_sploit.py && chmod +x start_sploit.py
```

The simplest way to run an exploit is:

```bash
./start_sploit.py sploit.py -u http://10.0.0.1:5000
```

Here, `sploit.py` is the exploit file, `http://10.0.0.1:5000` is the [farm server](farm_server.md) address.

You can watch the exploits' results and stats using the farm client output or the server web interface, which is available at the address from `-u` option.

## Details of the Algorithm

The farm client work is divided into periods (so-called *attacks*). During each attack, the client requests the up-to-date configuration (a team list, a flag format) from the farm server (if it's available), then attacks all the teams from the list using the exploit. One attack can't last more than the number of seconds specified in the `--attack-period` option (default: 120 seconds). Obviously, this period must not be greater than the *flag lifetime* (the period following adding a flag to a service when the checksystem considers it correct).

The number of concurrent exploit processes is limited by the `--pool-size` option (default: 50 processes). This limit saves from the exhaustion of the RAM (followed by freezing of the laptop) in case of competitions with a large number of teams (e.g. RuCTFE with more than 400 teams) or heavy exploits.

According to the parameters above, the *time limit* for one exploit process is calculated as `attack_period / ceil(len(teams) / pool_size)` (it is printed before each attack). After this time the farm client kills the process.

When the exploit is running, the client looks after its output and, when a substring matching the flag format appears, adds it to a queue. A flag is never added to the queue twice. The queue contents are being sent to the server every 5 seconds.

Before running the exploit, the client checks a part of the requirements for the [exploit format](exploit_format.md).

Occasionally you don't need a separate exploit process for each of the other teams. In this case, you can use the `--not-per-team` option, so each attack will be comprised of a single run of the exploit without the command-line arguments.

## What if the calculated time limit is not enough?

1. Increase the `--attack-period`. For example, the flag lifetime on RuCTF is usually 5 minutes, so `--attack-period` can be doubled.

    In this case, a small part of the flags may be lost (if a victim's service is not available for a short period matching the running of the exploit, some flags will die before the next attack).

2. Increase the `--pool-size` if you consider your laptop powerful enough to run a larger number of exploit processes.

    Be aware of the exhaustion of the RAM and freezing of the laptop.

3. Use the `--distribute=K/N` option. It deterministically divides the team list by *N* parts, then runs the client only on the *K*th part of the list. This way, you can distribute exploit processes among *N* laptops.

## Debugging of Exploits

Several first attacks (see the `--verbose-attacks` option) the farm client will show stdout and stderr of each exploit process, as well as the list of extracted flags. This way, you can see the errors arising from the exploit run.

At the end of each attack, the client shows a percentage of exploit processes exceeded the time limit (considering all attacks).

## Farm Server Autodiscover

To save your team members from specifying `-u URL` each time, you can change the [default domain](../../client/start_sploit.py#L82) of the server to a domain you control, and ask the team members to use the updated script.

When a competition starts, a team's admin can change the A record for the domain, so it will point to the IP address of the farm server in the local network. Note that the corresponding A records must have a small TTL (the changes will be applied with a delay otherwise).

<p align="center">
    <img src="https://github.com/borzunov/DestructiveFarm/blob/master/docs/images/changing_dns_record.png" width="500"><br>
    <i>Changing the A record on DigitalOcean</i>
</p>

## Additional Features

- The exploits are run with the environment variable `PYTHONUNBUFFERED=1`, so Python code will do `flush(stdout)` automatically after each newline. This saves from the loss of flags (see paragraph 4 in the [exploit format](exploit_format.md)).