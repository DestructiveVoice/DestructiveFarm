Farm Server
===========

<p align="center">
    <img src="https://github.com/borzunov/DestructiveFarm/blob/master/docs/images/farm_server_screenshot.png" width="700">
</p>

The **farm server** is a tool that collects flags from farm clients, sends them to the checksystem, monitors the usage of quotas and shows the stats about the accepted and rejected flags. It is being configured and run by a team's admin at the start of the competition. After that, team members can use a web interface (see the screenshot above) to watch the exploits' results and stats.

The server is a Flask web service from the [server](../../server) directory of this repository.

## Installation and Running

The server requires Python 3 and OS Linux or macOS. It depends on several Python libraries but does not require any additional software (e.g. MySQL or Redis) to be installed.

To install the server, run:

```bash
git clone https://github.com/borzunov/DestructiveFarm
cd DestructiveFarm/server
python3 -m pip install -r requirements.txt
```

Before every competition:

1. Remove the old flag database (the `flags.sqlite` file) if it exists.

2. Set appropriate settings in the [config.py](../../server/config.py) file (team list, flag format, flag submission protocol, checksystem quotas).

    Flag submission protocols for the [Hackerdom checksystem](https://github.com/HackerDom/checksystem) (RuCTFE, RuCTF), [Themis](https://github.com/themis-project/themis-finals) (VolgaCTF), and [ForcAD](https://github.com/pomo-mondreganto/ForcAD) are supported by default. You can add new protocols to the [protocols](../../server/protocols) directory (feel free to make pull requests with them!).

3. If other teams have access to your team's subnetwork during the competition, don't forget to change the web interface password (the `SERVER_PASSWORD` value in [config.py](../../server/config.py)). The other teams will see all your flags otherwise.

To start the server, run:

```bash
./start_server.sh
```

By default, you can use the password `1234` and any login to enter.

## Flag database

The server keeps all flags received from the clients in the `flags.sqlite` file. A flag is never added to the database twice. You can also add flags manually using the form in the web interface.

The web interface lets you list and filter flags by a number of parameters (see the screenshot above):

- Filename of the exploit that produced the flag
- Team the flag was stolen from
- Flag itself
- Time the flag was added to the database for the first time
- Status (see below)
- Result of the last attempt to send the flag to the checksystem (error message or checksystem verdict)

A flag can have one of the following *statuses*:

- **QUEUED** &mdash; the flag is in the queue for submitting to the checksystem.

    This means that either the server didn't send the flag yet, or it didn't get a clear response (e.g. the checksystem was down or reported that the quota was exceeded). In the latter case, the "Checksystem Response" field would be non-empty, and the flag will be resent soon.

- **ACCEPTED** &mdash; the checksystem has considered the flag correct.

- **REJECTED** &mdash; the checksystem has considered the flag incorrect.

- **SKIPPED** &mdash; the farm didn't get a clear response regarding the flag during its lifetime. It doesn't make sense to resent the flag anymore, so it was excluded from the submission queue.

    This means that either the server didn't have free quotas to send the flag, or the checksystem was returning an error or an unknown verdict every time the farm tried to submit the flag. In the latter case, the "Checksystem Response" field will be non-empty.

    To support a new checksystem verdict, update the submission protocol in the [protocols](../../server/protocols) directory.

Note that the web interface shows the total number of matching flags after filtering. For example, this lets you check whether the exploit was performing better during different periods of time.

## Architecture

The server contains a web application comprised of the web interface and an HTTP API for the farm clients.

A separate thread runs a flag submission loop. Every `SUBMIT_PERIOD` seconds the server loads new settings from the [config.py](../../server/config.py) file (if it was updated and runs without errors), then sends no more than `SUBMIT_FLAG_LIMIT` flags from the submission queue. The flags added earlier than `FLAG_LIFETIME` seconds ago are removed from the queue (and are assigned the *SKIPPED* status).

## Flag Spam Protection

**Flag spam** is a situation when a team puts a lot of fake flags (random strings matching the flag format) in their or someone else's service. Fake flags usually don't affect the quality of service but obstruct attacks (if getting a flag is a long process for an attacker or the checksystem has quotas for flag submission).

In the latter case, adversarial teams can't send all the flags from the service and send a random subset (a large part of it is fake flags). At the same time, the spammer can distinguish genuine flags and get more game points.

The flag spam is not explicitly prohibited in many competitions. Starting from 2017, competitions use different approaches to avoid its negative effects:

- On RuCTF, the flag submission quota was canceled
- On VolgaCTF, flags have a digital signature that the farm can check before sending a flag

To eliminate the negative effect in other cases, the farm server implements the following algorithm. Flags are divided into groups corresponding to *(exploit, team)* pairs. Then the farm sends flags uniformly chosen from all the groups. This way, even if one of the services (or all services of one team) contains many fake flags, they won't spend all your submission quota.
