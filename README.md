# "pipedream" socket fuzzer
The pipedream proxy is a pure-python single-threaded proxy server, designed to
capture traffic and replay it with modifications, to identify vulnerabilities
in both networked and desktop software.

In it's 'capture' mode, this captures a socket conversation as a .cnv file,
which can then be used in the 'replay' mode to simulate a client, as well as
a 'fuzz' mode to inject random faults. An 'order editor' is also included
which can be used to edit captured conversations before use.

# basic use (no fuzzing)
The first step of using the fuzzer is to capture a socket conversation. This
is done with the "capture" mode, which sets up a socket proxy, as follows. The
example below captures traffic to the google web server, without 

pipedream.py -m capture -i localhost:8082 -o www.google.com:80 -f google

Then, the saved format spec file can be used to emulate either the client or
the server, as follows:

pipedream.py -m replay -o www.google.com:80 -f google-12345.cnv
pipedream.py -m replayserver -o localhost:8081 -f google-12345.cnv

# basic use (editor)
This software also includes a editor, which can modify conversation files. This
can be accessed via:

pipedream.py -m edit -f google-12345.cnv

# basic use (fuzzing)
Pipedream.py has limited capabilites for fuzzing data generation. Note that it
does not attempt to control process execution.