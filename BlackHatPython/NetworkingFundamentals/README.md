## Python Networking in a Paragraph

Programmers have a number of third-party tools to create networked servers and clients in Python,
but the core module for all of those tools is socket. This module exposes all of the necessary pieces
to quickly write TCP and UDP clients and servers, use raw sockets, and so forth. For the purposes of
breaking in or maintaining access to target machines, this module is all you really need. Let’s start by
creating some simple clients and servers, the two most common quick network scripts you’ll write.