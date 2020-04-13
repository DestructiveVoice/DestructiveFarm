FAQ
===

1. **What are attack-defense CTFs?**

    An attack-defense CTF is an information security competition. Each team is given an identical image of an operating system running several *services* (such as a message board or a weather forecast service) that have vulnerabilities. The task is to find the vulnerabilities, then protect your own services, attack the services of other teams, and steal some secret information (*flags*).

    During the game, the jury hosts a *checksystem*. Every several minutes, it checks that team services work and adds new flags to them.

2. **Why do I need the exploit farm?**

    Since the flags are added periodically, it is not enough to hack a service manually once. Usually, teams write an [exploit](exploit_format.md) that steals flags from a specified victim and then run it for every adversarial team.

    The farm solves several related issues such as:

    - Allows to avoid duplicating flag sending code in each exploit
    - Periodically restarts exploits for every adversarial team (while not overloading a computer with a large number of processes)
    - Kills exploit processes when they freeze
    - Watches a checksystem quota for sending flags
    - Protects from [flag spam](farm_server.md#Flag-Spam-Protection)
    - Shows exploits' results and stats
    - Resends flags in case if the checksystem stops working for some time

3. **Why the farm is divided into a client and a server?**

    This corresponds to how responsibilities are divided between the team members.
    
    An admin configures a list of teams and a procedure of sending flags on the *farm server* (no need for every team member to do it), then watches it during the game.

    Exploit authors write and run the exploits on their laptops using the *farm client*. This allows to avoid reinstalling libraries an exploit depends on, to debug the exploit on their laptops, to watch the exploit and its output by themselves. If the exploit eats all the laptop resources, other team members' exploits will remain intact.

4. **What database does the farm use to store flags?**

    It uses SQLite. That's because it doesn't need to install and run additional software, stores the whole database in one file and provides a convenient API to work with it.

    The SQLite performance is enough even for the number of flags typical for large competitions (even the full scan queries run on the flag table without visible delays).

5. **Why the farm doesn't use asyncio?**

    One way to solve the issue of a large number of threads/processes (in case of a large number of teams) is to use asynchronous networking (e.g. asyncio library). Unfortunately, this imposes several restrictions:

    - All the exploits should be written in Python 3 and interact with the network only asynchronously.
    - Exploit authors should be familiar with asyncio. If a long blocking operation happens in an exploit, the farm client won't be able to attack other teams during this time.
    - There are no asyncio-compatible libraries for rare protocols that may be used in the services (e.g. variants of RPC).

    While we don't plan to support asynchronous networking, you can check out the [Andrew Gein's farm](https://github.com/andgein/ctf-exploit-farm) that uses asyncio. It can be used independently or as a farm client sending flags to the Destructive Farm server.
