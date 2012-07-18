Title: Websocket Demo Results V2
Date: 2012-07-18 18:01:00
Tags: erlang, websockets, c10k, node, nodejs
Status: draft

<style>
  tr {
    text-align: right;
  }
</style>


Roughly about a month ago I wondered if Erlang's promise of massive
concurrency was actually true.  

Rather than take everyone's word for it, inspired by Richard Jones'
[C1M
experiment](http://www.metabrew.com/article/a-million-user-comet-application-with-mochiweb-part-1)
I decided to whip together a benchmark of my own.  

This benchmark pit a [Cowboy](https://github.com/extend/cowboy)
implemented WebSocket echo server against five echo servers
implemented in other languages.  I picked platforms that I assumed
would pass a c10k benchmark.  These platforms included Java/Netty, Go,
Node.js and Python. These platforms came with an event-based framework
that promised claims of high concurrency.

I ran the benchmark of these servers on a m1.medium EC2 instance.  The
[outcome](https://github.com/ericmoritz/wsdemo/blob/results-v1/results.md)
was surprising.  All the servers but the Erlang/Cowboy implementation
had massive connection timeouts.  At 3am I sent out an off the cuff
tweet that was heard around the world.

I woke up that morning with cries of foul and anger that their
framework of choice was poorly represented or that my methodology was
faulty.  I sifted through the trolls, accepted pull requests and
refined my methodology with the [help of many
people](https://github.com/ericmoritz/wsdemo/blob/v2/AUTHORS)

In the past month I automated the benchmark so that I did not have to
stay up all night babysitting the starting and stopping of each of the
19 servers.

After many small scale benchmarks on AWS amidst data-center failures
(which seem to occur in the middle of a benchmark). I found that EC2
performed in a peculiar manor with a majority of the servers.  After I
noticed this I picked up a AMD Phenom 9600 Quad Core - 2300 mhz with
2GB of Memory off a Craigslist to compare the results.

## Methodology

Each server needed to accept a connection and echo back every message
that is sent to it.  The benchmark process created a connection as
fast as the server would allow and each client connection would send a
33 byte WebSocket message every second.

I used two individual machines, a client and a server.  On the server I ran
supervisord which I used to start and stop the servers. The client
machine would do for each server the following:

  1. Start the server
  2. Warm up the server by doing 10% of the test; 1000 clients for 30 seconds
  3. Do the full test of 10,000 clients for 5 minutes.
  4. Cool down the machine by waiting 15 seconds after stopping the server
  
For the EC2 benchmark I used two m1.large instances because they are
multi-core.

For the local benchmark I used the AMD Phenom 9600 machine as the
server and my Mac Mini running native Ubuntu 12.04.


## Results

Starting with the EC2 benchmark (times are in milliseconds), you will
notice the peculiar behavior that EC2 exhibited:

Handshake elapsed time over time and message latencies over time:

![EC2 handshake times](wsdemo-results/v2/m1.large-c10k-handshake-times.png)
![EC2 latency times](wsdemo-results/v2/m1.large-c10k-latency.png)

There is what looks like O(log N) growth in connection times and
linear growth in the message latency.

When compared to the local machine, the data takes what looks like a
much different shape.

![Local handshake times](wsdemo-results/v2/moritz-server-c10k-handshake-times.png)
![Local latency times](wsdemo-results/v2/moritz-server-c10k-latency.png)

If you look at the box plots of the EC2:

![EC2 handshake times box plot](wsdemo-results/v2/m1.large-c10k-handshake-times-box.png)
![EC2 latency times box plot](wsdemo-results/v2/m1.large-c10k-latency-box.png)

You will notice that while Erlang did the best, 5% of the messages
sent were >1.3 seconds which is likely unacceptable.

On my local hardware, all the servers did ridiculously better: 

![Local handshake times](wsdemo-results/v2/moritz-server-c10k-handshake-times-box.png)
![Local latency times](wsdemo-results/v2/moritz-server-c10k-latency-box.png)

So much better that the top 5 servers are nearly a tie when it comes
to time and consistency.

## My Conclusion

If you are deploying something on EC2 you will likely need to load
balance your service to reach c10k on any of these servers.  Even the
leader in the EC2 benchmark (Erlang) reach what is probably
unacceptable message latencies of > 1 second.

It just goes to show you that you must test your assumptions and do
some capacity planning.  Hacking together a quick node.js prototype to
throw on EC2 to show the boss how viable it is will likely end in pain
(and maybe your job).

## Charts, Stats and Raw data

Here are links to more detailed charts and stats along with the raw
CSV data.  Try to be kind to Dropbox and only download the raw data if
you really plan on using it.

[Detailed EC2 charts](wsdemo-results/v2/results-m1.large-c10k-v2.pdf)
[Detailed EC2 stats](wsdemo-results/v2/m1.large-c10k.html)
[EC2 CSV Tables 1.12 gigs compressed](https://www.dropbox.com/s/sfeiresei4zoed9/m1.large-c10k.tar.bz2)

[Detailed Local charts](wsdemo-results/v2/results-moritz-server-c10k-v2.pdf)
[Detailed Local stats](wsdemo-results/v2/moritz-server-c10k.html)
[Local CSV Tables 1.19 gigs compressed](https://www.dropbox.com/s/y6lf5x06kgp6a7k/moritz-server-c10k.tar.bz2)
