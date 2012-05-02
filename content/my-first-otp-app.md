Title: My First Erlang/OTP App, a post-mortem
Date: 2012-05-02
Tags: erlang, otp, twitter, delicious
Status: draft

I have been toying with [Erlang](http://erlang.org) ever since I
interviewed at Mochi Media in late 2010.  Anyone with at least passing
knowledge of [Erlang](http://erlang.org) knows that Mochi Media is big
user of and contributor to Erlang
([mochiweb](https://github.com/mochi/mochiweb)). Over the past year, I
also played with [Riak](http://wiki.basho.com/Riak.html) quite a
bit. Basho, as well, is a huge user of and contributor to Erlang.

As I played with [Riak](http://wiki.basho.com/Riak.html), I tried my
best to avoid Erlang; I tried to stay within the familiar world of
Python while interacting with Riak.  When I needed a solution to
storing a sorted set into Riak, I wrote it in
[Python](https://github.com/ericmoritz/crdt).

After reading the [paper on
CRDTs](http://hal.archives-ouvertes.fr/docs/00/55/55/88/PDF/techreport.pdf),
I realized I had a gap in my knowledge of computer science.  Just to
decipher the paper, I had to teach myself [Discrete
Mathematics](http://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-042j-mathematics-for-computer-science-fall-2010/index.htm)
(thanks MIT!).

This desire to fill that gap lead me to [The Little
Schemer](http://amzn.to/z2FOF7), and functional programming.  After
learning how to solve problems using FP, my resistance to Clojure
lessened and I had a quick stint playing with it.  While Clojure
solves problems ([1](http://clojure.org/concurrent_programming),
[2](http://www.java.com/)) I don't have, I had trouble finding a
reason to replace Python with it for problems I do have.

I recently found myself on the job market and a few exciting positions
([1](http://www.opscode.com/careers/),
[2](http://bashojobs.theresumator.com/)) out there had Erlang in their
bullet points.  I had no way near the experience in Erlang to apply
for those positions but they egged me on to finally learn Erlang.

I grabbed a copy of [Programming Erlang: Software for a Concurrent
World](http://amzn.to/IXiMjP) and set out to finally learn this
thing.  In this post, I hope to share some tips that may help you
learn this unfamiliar language.

## Syntax

The syntax is the first thing that you hear people complain about when
introduced to Erlang. As an Python whitespace apologist, this is
familiar ground.

Don't fret. Just with Python whitespace, the strange Erlang syntax and
punctuation becomes familiar and second nature.

Erlang's
[syntax](http://www.erlang.org/course/sequential_programming.html) is
fairly small. It is not as small as LISP, but it is quite small.  This
is both a blessing and a curse.

There are only two special forms: if and case and a short list of simple
data types: atoms, numbers, tuples and lists.  Pattern Matching and
list comprehensions fill in the rest of the gaps that functions and
special forms do not.

### Punctuation

There are periods, semi-colons and commas in places that you are not
used to.  Don't worry.  The rules are simple:

 1. Statements are separated with commas.
 2. Code branches end with semicolons.
 3. Sentences end in periods.

First commas and periods:

    ::erlang
    A = 1,
    B = 2,
    C = 3.

Semicolons end code branches.  Wherever there would be a diamond in
your flow chart, those statements end in a semi-colon.

Pseudo-code:

    ::python
    X = foo()

    if X == 1:
         return "a"
    elif X == 2:
         return "b"
    else:
         return "c"

Erlang:

    ::erlang
    case foo() of
        1 -> "a";
        2 -> "b";
        _ -> "c"
    end.

Each branch of that case statement ends with a semi-colon (except the
last one).  Let's ignore that `_` for now; we'll discuss that with
pattern matching.

Let's write an entire "sentence" now:

    ::erlang
    search_internet(Query) ->
        Url = "https://search.example.com/?q=" ++ Query,

        case httpc:request(Url) of
           {ok, {{_Version, 200, _ReasonPhrase}, _Headers, Body}} ->
               {ok, Body};
           {ok, {{_, Status, ReasonPhrase}, _, Body}} ->
               {error, {Status, ReasonPhrase}, Body};
           {error, Reason} ->
               {error, Reason, ""}
        end.

This function fetches data from are imaginary search engine and
returns either {ok, Body} or {error, Reason, Body}.

In the case that your are completely new to Erlang, atoms start with a
lower-case letter and variables start with a capital letter.

## Pattern Matching

I will try to keep pattern matching quick because much better people
have done [a better
job](http://learnyousomeerlang.com/syntax-in-functions#pattern-matching)
than I will in explaining it.

The key to understanding pattern matching is to understand what an
unbound variable is.  An unbound variable is a vacuum.  Erlang abhors
a vacuum.  Erlang will fill in these vacuums whenever a pattern match
is done.

In the following expression:

    ::erlang
    % I lined things up for you
    {ok, {{   _Version, Status,  ReasonPhrase }, _Headers,            Body }} = 
    {ok, {{ "HTTP/1.1",    200,          "OK" },       [], "Hello, World!" }}.

All the capitalized keywords are unbound variables.  They are vacuums.
When = is evaluated, it overlays the right hand side over the left
hand side and fills in those holes. `Status == 200`,
`ReasonPhrase == "OK"`, and `Body == "Hello, World!"`.

You will notice that some of those variable names start with an `_`.
Any variable that is an underscore or starts with an underscore is a
just a placeholder, their value is never stored.  It just allows the
pattern to be matched.

Patterns also trickle down.  With our complex case statement in the
search_internet/1 function:


    ::erlang
        case httpc:request(Url) of
           {ok, {{_Version, 200, _ReasonPhrase}, _Headers, Body}} ->
               {ok, Body};
           {ok, {{_, Status, ReasonPhrase}, _, Body}} ->
               {error, {Status, ReasonPhrase}, Body};
           {error, Reason} ->
               {error, Reason, ""}
        end.

If the Status is 200, the first pattern matches, if the request
seceded but the HTTP status was not 200, the second pattern
matches. Finally, if the HTTP request failed, the last pattern
matches.  

## erl-twitterlinks

After that basic introduction to reading Erlang, let me introduce you
to my first Erlang application,
[erl-twitterlinks](https://github.com/ericmoritz/erl-twitterlinks/).

It is an itch I've been meaning to scratch ever since Trunk.ly was
bought by AVOS.  Trunk.ly watched your Twitter timeline and recorded
the links you posted.  `twitterlinks` watches my Twitter firehose and
posts any links it sees to my delicious account.

I fantasized about writing this using
[Storm](https://github.com/nathanmarz/storm) but Storm would be
overkill for this project.  I felt like I had a decent grasp of
Erlang/OTP to write it in Erlang, so that is what I did.

## OTP

OTP is a platform/framework written in Erlang that provides a number
of abstractions for building applications in Erlang.  An OTP app is
made up of one or more OTP apps.  Complex apps such as `Riak` are made
up of dozens of apps.  My little app is simpler.  It only depends on
[one external app](https://github.com/benahlan/struct) and some stdlib
apps which the http client relies on.

The key to reading any Erlang application is to first find its
`.app` file.  This file describes the Erlang application.


### Walk-through

I am using
[rebar](https://github.com/basho/rebar/wiki/Getting-started) to build
the project, so its `.app` file is generated by an `.app.src`
file. Starting with my
[twitterlinks.app.src](https://github.com/ericmoritz/erl-twitterlinks/blob/master/src/twitterlinks_app.erl)
file, you will see a line that says:

    ::erlang
    {mod, { twitterlinks_app, []}},

This tells OTP that this app exists in the [twitterlinks_app]() and is
started with the args of [].  The other junk just describes the app
and tells OTP which apps need to be started before `twitterlinks`.

The next concept in OTP the application uses is a
[supervisor](). Supervisors monitor your processes and restart them if
they die.

The [twitterlinks_sup]() supervisor gathers my credentials and starts
the middleman's supervisor.

In my application, the middleman process sits between the
[twitterlinks_stream_listener]() process and the
[twitterlinks_delicious_service]() process. As tweets are sent to the
middleman, the middleman tells the delicious service to post the
links it finds in the tweets.


The [twitterlinks_middleman_sup]() watches carefully over the three
services and if any of them die, the supervisor will restart the
middleman. Actually it only watches over the
[twitterlinks_middleman]() process which is linked to the other two
services.  This linkage causes the three linked process to die if any
of them die.  This may be too brutal and I could probably do something
that allows the delicious and stream servers to die independently but
that's for version 1.1.

If I ever wanted to build this out to a service for people to use, I
could create a intermediate service between the app and the middlemen
the was responsible for starting them and keeping a watchful eye over
them.  I "watchman" if you will.

The final OTP concept that the application uses is gen_server.  This
abstraction defines a server that communicates via messages.

Message are sent using the gen_server:call(Pid, Message) or
gen_server:cast(Pid, Message).  call/2 is a synchronous call and cast/2 as
fire and forget.

The modules that implement a gen_server have a number of callbacks but
we'll concentrate on
[handle_call](https://github.com/ericmoritz/erl-twitterlinks/blob/master/src/twitterlinks_delicious_service.erl#L41)
for my delicious gen_server.

There is only one command for the delicious service,

    ::erlang
    add_url(ServerPid, Url, Description, TagList) ->
        gen_server:call(ServerPid, {add_url, {Url, Description, TagList}}).

The add_url/4 function is part of the client API, gen_server:call
sends the {add_url, {Url, Description, TagList}} message to the
running server identified by ServerPid.

Meanwhile, the server is waiting for incoming messages, when the
message comes in, the gen_server code calls
twitterlinks_delicious_service:handle_call/3:

    ::erlang
    handle_call({add_url, {Url, Description, TagList}}, _From, State) ->
        Request = build_add_request(Url, Description, TagList,
                                    State#state.username,
        State#state.password),
        Result = httpc:request(post, Request, [],[]),
        {reply, Result, State}.
    
The incoming message is pattern matched to the function signature and
executes the code within.


## Conclusion

In the past, the biggest roadblock to reading apps written in Erlang
was understanding where to start.  I hope my app and little
walk-through helps you know the path to take with other OTP
applications.

*PS:* I got an offer at Mochi Media but could not move to SF.  One of
the saddest days of my life.

*DISCLAIMER*: Amazon links include an affiliate code, if that disturbs
 you, don't click.
