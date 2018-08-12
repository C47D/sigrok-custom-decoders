# Setup

Set SIGROKDECODE_DIR environment variable to point to wherever
you have this repo, e.g. in Windows:

%SIGROKDECODE_DIR% = %USERPROFILE%\Documents\sigrok-custom-decoders

# Some tips learned from the sigrok channel on Freenode (so i don't forget them):

Let's say you have a capture on PV of the protocol you want to write a stack
decoder for, e.g. i got one named nextion_page_cmd.sr, while on the same dir
i can do:

```
$ sigrok-cli -i nextion_page_cmd.sr -P uart:tx=TX:rx=RX,nextion -A nextion=instruction
```

As the nextion stack decoder sits on top of the uart protocol decoder i need
to set the options for the uart first, ```-P uart:tx=TX:rx=RX``` this means i
have a uart protocol decoder with the options `tx` and `rx` set up, `tx` value
is the name of the channel that have the tx data, this is TX on the .sr file,
same applies for the `rx` option.

Then the nextion stack decoder "get" the data output from the uart decoder and
works with it, this is using the ```,nextion``` at the end of the command above.

```-A nextion=instruction``` this just means that i only want to see the
annotations `instruction` from the `nextion` decoder.
