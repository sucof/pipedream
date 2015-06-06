# "pipedream" fuzzer
The pipedream proxy is a pure-python single-threaded proxy server, designed to
capture traffic and replay it with modifications, to identify vulnerabilities
in both networked and desktop software.

In it's 'capture' mode, this captures a socket conversation as a .cnv file,
which can then be used in the 'replay' mode to simulate a client, as well as
a 'fuzz' mode to inject random faults. A 'data editor' is also included
which can be used to edit captured conversations before use.

*Note: it is strongly recommended that a fuzz file be edited before trying to
emulate a server*

## basic use (no fuzzing)
The first step of using the fuzzer is to capture a socket conversation. This
is done with the "capture" mode, which sets up a socket proxy, as follows. The
example below captures traffic to the google web server, without 

    pipedream.py -m capture -i localhost:8082 -o www.google.com:80 -f google

Then, the saved format spec file can be used to emulate either the client or
the server, as follows:

    pipedream.py -m replay -o www.google.com:80 -f google-12345.cnv
    pipedream.py -m replayserver -o localhost:8081 -f google-12345.cnv

To introduce mutations, use the -c flag, to specify the percent chance that
a given node will mutate.

## basic use (editor)
This fuzzer also includes a editor, which can modify conversation files. This
can be accessed via:

    pipedream.py -m edit -f google-12345.cnv

## practical example (fuzzing a browser)
The first step is to capture a browser's request / response pair, as follows:

    python pipedream.py -m capture -i localhost:4040 -o www.blah.com:80 -f creche

For the purposes of this demo, a socket conversation has already been prepared,
simulating a conversation between a user's browser and reddit (sample.cn_). Make
a copy of this, and open it up in the editor:

    python pipedream.py -m edit -f herpaderp-10348.cnv

Use the "p" command to inspect the socket conversation: note that it includes two
requests, and both responses are split into two recv calls:

    [####] : p
    [ 0 -> len:0x0162 ]  [ 47 45 54 20 2f 63 64 6e  GET /cdn ]
    [ 1 <- len:0x0550 ]  [ 48 54 54 50 2f 31 2e 31  HTTP/1.1 ]
    [ 2 <- len:0x1018 ]  [ 95 1c 5c 5b 3b ff ad b5  ..\[;... ]
    [ 3 -> len:0x0179 ]  [ 47 45 54 20 2f 63 64 6e  GET /cdn ]
    [ 4 <- len:0x0550 ]  [ 48 54 54 50 2f 31 2e 31  HTTP/1.1 ]
    [ 5 <- len:0x2800 ]  [ c5 8d 22 22 62 44 44 44  ..""bDDD ]
    [ 6 <- len:0x12bb ]  [ cd 15 22 38 1f fe 3b 17  .."8..;. ]
    [####] : q

Note that this describes two HTTP requests, and the responses for both of these
have been split into two pieces (i.e. two recv calls). We can delete the last 3
and merge the first two responses, as follows:

    d 6
    d 5
    d 4
    d 3
    s 1
    swallow 2
    save
    p all

The end result should look like this:

    [####] : p
    [ 0 -> len:0x0162 ]  [ 47 45 54 20 2f 63 64 6e  GET /cdn ]
    [ 1 <- len:0x1568 ]  [ 48 54 54 50 2f 31 2e 31  HTTP/1.1 ]
    [####] :

Now, select the second node, and bind it to the GET keyword:

    s 1
    bind .*GET.*
    save

Now, emulate the server with the following:

    python pipedream.py -m replayserver -f herpaderp-10348.cnv -c 100 -i localhost:4040

This will open up a server on localhost:4040
