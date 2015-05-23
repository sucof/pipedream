# "pipedream" socket fuzzer
The pipedream proxy is a pure-python single-threaded proxy server, designed to
capture traffic and replay it with modifications, to identify vulnerabilities
in networked software.

In it's 'capture' mode, this captures a socket conversation as a .cnv file,
which can then be used in the 'replay' mode to simulate a client, as well as
a 'fuzz' mode to inject random faults. An 'order editor' is also included
which can be used to edit captured conversations before use.
