Title: Websocket Demo Results V2
Date: 2012-07-18 18:01:00
Tags: erlang, websockets, c10k, node, nodejs
Status: draft

<style>
  tr {
    text-align: right;
  }
</style>

## History

Roughly about a month ago I wondered if Erlang's promise of massive
concurrency was actually true.  

Rather than take everyone's word for it, inspired by Richard Jones'
[C1M
experiment](http://www.metabrew.com/article/a-million-user-comet-application-with-mochiweb-part-1)
I decided to whip together a benchmark of my own.  

This benchmark pit a [Cowboy](https://github.com/extend/cowboy)
implemented WebSocket echo server against five echo servers
implemented in other languages.  The platforms I chose were known
for their ability to do c10k such as Netty, Node.js and gevent.

I ran the benchmark of these servers on a pair of m1.medium EC2
instance.  The
[outcome](https://github.com/ericmoritz/wsdemo/blob/results-v1/results.md)
was surprising.  All the servers but the Erlang/Cowboy implementation
had massive connection timeouts.  At 3am I sent out an off the cuff
tweet that was heard around the world.

I woke up that morning with cries of foul and anger that their
framework of choice was poorly represented or that my methodology was
faulty.  

## The Upgrade

After that initial benchmark, I spent the past month refining the
process. I sifted through the trolls, accepted pull requests and
refined my methodology with the [help of many
people](https://github.com/ericmoritz/wsdemo/blob/v2/AUTHORS)
 
I [automated the
test](https://github.com/ericmoritz/wsdemo/blob/master/README.md) to
make it easier to benchmark the 19 servers that composed the test.

After many small scale benchmarks on AWS amidst data-center failures,
I found that even a multi-core EC2 instance performed in a similarly
with a majority of the servers.  I decided that I needed actual
hardware so I picked up a AMD Phenom 9600 Quad Core - 2300 mhz with
2GB of Memory off a Craigslist to compare the results.

## Methodology

Before I get into the data, I'll briefly explain the testing methodology.

Each server needed to accept a connection and echo back every message
that is sent to it.  The benchmark process created a connection as
fast as the server would allow and each client connection would send a
33 byte WebSocket message every second (33 bytes is how large a binary
encoded ref() value is).  Connection initiation, WebSocket
Handshakes, Message send, Message receive and any error was recorded
in a leveldb event log on the client with a timestamp.

I used two individual machines, a client and a server.  On the server
I ran supervisord which I used to start and stop the servers using its
XML-RPC interface. 

For each server, the client would do the following:

  1. Start the server
  2. Warm up the server by doing 10% of the test; 1000 clients for 30 seconds
  3. Do the full test of 10,000 clients for 5 minutes.
  4. Cool down the machine by waiting 15 seconds after stopping the server
  
For the EC2 benchmark I used two m1.large instances because they are
multi-core.

For the local benchmark I used a Quad-core AMD Phenom 9600 machine as
the server and my Mac Mini with a 2.0 GHz Core 2 Duo running Ubuntu
12.04 on the metal (dual-booted).

## Results

### EC2:

<table>
  <tr>
     <th>Implementation</th>
     <th>Handshake Time (mean)</th>
     <th>Handshake Time (σ)</th>
     <th>Handshake Time (median)</th>
     <th>Handshake Time (95%)</th>
     <th>Handshake Time (99%)</th>
     <th>Handshake Time (99.9%)</th>
     <th>Latency (mean)</th>
     <th>Latency (σ)</th>
     <th>Latency (median)</th>
     <th>Latency (95%)</th>
     <th>Latency (99%)</th>
     <th>Latency (99.9%)</th>
     <th>Connection Timeouts</th>
  </tr>
  <tr>
     <td>erlang-cowboy</td>
     <td>46.435</td>
     <td>101.107</td>
     <td>18.974</td>
     <td>147.261</td>
     <td>352.168</td>
     <td>1063.972</td>
     <td>294.412</td>
     <td>596.273</td>
     <td>64.735</td>
     <td>1273.218</td>
     <td>3120.932</td>
     <td>4288.831</td>
     <td>0</td>
  </tr><tr>
     <td>go-gonet</td>
     <td>56.979</td>
     <td>140.531</td>
     <td>15.68</td>
     <td>185.868</td>
     <td>1003.776</td>
     <td>1236.265</td>
     <td>1044.942</td>
     <td>1137.411</td>
     <td>1055.743</td>
     <td>3283.068</td>
     <td>4368.498</td>
     <td>5537.2</td>
     <td>0</td>
  </tr><tr>
     <td>pypy-tornado-N</td>
     <td>64.072</td>
     <td>118.957</td>
     <td>21.854</td>
     <td>246.67</td>
     <td>423.039</td>
     <td>1103.369</td>
     <td>1327.666</td>
     <td>1823.508</td>
     <td>1028.256</td>
     <td>4354.553</td>
     <td>8401.357</td>
     <td>16029.463</td>
     <td>0</td>
  </tr><tr>
     <td>node-ws-cluster</td>
     <td>249.623</td>
     <td>508.366</td>
     <td>50.147</td>
     <td>1249.241</td>
     <td>2211.754</td>
     <td>3985.56</td>
     <td>30833.332</td>
     <td>32986.663</td>
     <td>14660.698</td>
     <td>100549.366</td>
     <td>114553.006</td>
     <td>121371.939</td>
     <td>0</td>
  </tr><tr>
     <td>scala-play</td>
     <td>908.584</td>
     <td>1393.172</td>
     <td>141.461</td>
     <td>3733.631</td>
     <td>5936.176</td>
     <td>8190.456</td>
     <td>366.273</td>
     <td>609.687</td>
     <td>79.203</td>
     <td>1330.0</td>
     <td>3117.377</td>
     <td>3476.734</td>
     <td>0</td>
  </tr><tr>
     <td>python-twisted-1</td>
     <td>2076.194</td>
     <td>2100.532</td>
     <td>1166.352</td>
     <td>5596.974</td>
     <td>6058.901</td>
     <td>6316.446</td>
     <td>93796.664</td>
     <td>61363.174</td>
     <td>94101.715</td>
     <td>185265.599</td>
     <td>197313.297</td>
     <td>199846.245</td>
     <td>0</td>
  </tr><tr>
     <td>java-webbit</td>
     <td>52.947</td>
     <td>123.325</td>
     <td>16.228</td>
     <td>161.269</td>
     <td>1003.017</td>
     <td>1060.396</td>
     <td>210.729</td>
     <td>453.46</td>
     <td>56.76</td>
     <td>1103.055</td>
     <td>1357.181</td>
     <td>6149.677</td>
     <td>1</td>
  </tr><tr>
     <td>python-twisted-N</td>
     <td>755.72</td>
     <td>1136.685</td>
     <td>187.814</td>
     <td>3434.43</td>
     <td>4442.401</td>
     <td>4889.723</td>
     <td>54210.334</td>
     <td>38623.448</td>
     <td>50500.447</td>
     <td>117697.486</td>
     <td>131026.009</td>
     <td>140935.195</td>
     <td>1</td>
  </tr><tr>
     <td>pypy-twisted-1</td>
     <td>149.641</td>
     <td>352.28</td>
     <td>21.637</td>
     <td>1102.857</td>
     <td>1355.267</td>
     <td>1479.419</td>
     <td>1084.287</td>
     <td>1558.89</td>
     <td>274.745</td>
     <td>4321.805</td>
     <td>6739.464</td>
     <td>9197.006</td>
     <td>9</td>
  </tr><tr>
     <td>python-gevent-websocket-N</td>
     <td>481.563</td>
     <td>829.23</td>
     <td>95.228</td>
     <td>2439.405</td>
     <td>3439.794</td>
     <td>4204.543</td>
     <td>22003.975</td>
     <td>13912.214</td>
     <td>21685.753</td>
     <td>44442.627</td>
     <td>52024.362</td>
     <td>64726.842</td>
     <td>10</td>
  </tr><tr>
     <td>pypy-twisted-N</td>
     <td>193.31</td>
     <td>1033.237</td>
     <td>36.382</td>
     <td>783.271</td>
     <td>1132.858</td>
     <td>16287.595</td>
     <td>2338.537</td>
     <td>2966.061</td>
     <td>1244.591</td>
     <td>7651.461</td>
     <td>13346.289</td>
     <td>22984.759</td>
     <td>11</td>
  </tr><tr>
     <td>python-tornado-N</td>
     <td>607.127</td>
     <td>786.601</td>
     <td>246.747</td>
     <td>2164.769</td>
     <td>3179.422</td>
     <td>4381.209</td>
     <td>56953.943</td>
     <td>37114.033</td>
     <td>56394.833</td>
     <td>118502.284</td>
     <td>130582.121</td>
     <td>134621.715</td>
     <td>15</td>
  </tr><tr>
     <td>clojure-aleph</td>
     <td>267.895</td>
     <td>514.649</td>
     <td>37.883</td>
     <td>1382.268</td>
     <td>2158.25</td>
     <td>4674.043</td>
     <td>1865.476</td>
     <td>1265.293</td>
     <td>2028.303</td>
     <td>4141.692</td>
     <td>5156.172</td>
     <td>7294.652</td>
     <td>320</td>
  </tr><tr>
     <td>haskell-snap</td>
     <td>427.79</td>
     <td>962.598</td>
     <td>44.693</td>
     <td>2051.212</td>
     <td>5218.067</td>
     <td>7650.281</td>
     <td>60924.311</td>
     <td>39791.393</td>
     <td>62482.556</td>
     <td>124664.402</td>
     <td>131380.959</td>
     <td>134375.903</td>
     <td>494</td>
  </tr><tr>
     <td>pypy-tornado-1</td>
     <td>518.101</td>
     <td>829.457</td>
     <td>66.107</td>
     <td>2624.818</td>
     <td>2890.471</td>
     <td>3940.884</td>
     <td>6477.86</td>
     <td>5016.109</td>
     <td>5672.344</td>
     <td>15301.014</td>
     <td>23690.165</td>
     <td>29351.708</td>
     <td>543</td>
  </tr><tr>
     <td>python-tornado-1</td>
     <td>2214.414</td>
     <td>2177.561</td>
     <td>1543.396</td>
     <td>6886.381</td>
     <td>8047.27</td>
     <td>24362.644</td>
     <td>88912.451</td>
     <td>51015.442</td>
     <td>89075.187</td>
     <td>166195.222</td>
     <td>173810.909</td>
     <td>177687.522</td>
     <td>829</td>
  </tr><tr>
     <td>node-ws</td>
     <td>1795.977</td>
     <td>1716.92</td>
     <td>1068.45</td>
     <td>5041.783</td>
     <td>6172.564</td>
     <td>8210.864</td>
     <td>113848.38</td>
     <td>70812.913</td>
     <td>127665.168</td>
     <td>209871.774</td>
     <td>224936.342</td>
     <td>233250.464</td>
     <td>1425</td>
  </tr><tr>
     <td>python-gevent-websocket-1</td>
     <td>3755.372</td>
     <td>4884.994</td>
     <td>817.072</td>
     <td>11084.85</td>
     <td>20798.476</td>
     <td>26905.43</td>
     <td>33670.264</td>
     <td>23107.803</td>
     <td>30398.543</td>
     <td>74106.901</td>
     <td>81290.792</td>
     <td>89833.786</td>
     <td>2830</td>
  </tr><tr>
     <td>perl-ev</td>
     <td>2229.378</td>
     <td>4027.54</td>
     <td>639.591</td>
     <td>10472.944</td>
     <td>20696.707</td>
     <td>29750.725</td>
     <td>1191.099</td>
     <td>2025.464</td>
     <td>408.571</td>
     <td>5899.183</td>
     <td>9190.275</td>
     <td>17235.574</td>
     <td>4371</td>
  </tr>
</table>

### Local

<table>
  <tr>
     <th>Implementation</th>
     <th>Handshake Time (mean)</th>
     <th>Handshake Time (σ)</th>
     <th>Handshake Time (median)</th>
     <th>Handshake Time (95%)</th>
     <th>Handshake Time (99%)</th>
     <th>Handshake Time (99.9%)</th>
     <th>Latency (mean)</th>
     <th>Latency (σ)</th>
     <th>Latency (median)</th>
     <th>Latency (95%)</th>
     <th>Latency (99%)</th>
     <th>Latency (99.9%)</th>
     <th>Connection Timeouts</th>
  </tr>
  <tr>
     <td>node-ws-cluster</td>
     <td>13.213</td>
     <td>9.284</td>
     <td>12.626</td>
     <td>29.475</td>
     <td>37.785</td>
     <td>49.817</td>
     <td>10.281</td>
     <td>6.076</td>
     <td>9.055</td>
     <td>21.966</td>
     <td>31.651</td>
     <td>38.85</td>
     <td>0</td>
  </tr><tr>
     <td>pypy-tornado-N</td>
     <td>13.323</td>
     <td>9.099</td>
     <td>12.701</td>
     <td>27.625</td>
     <td>35.48</td>
     <td>54.795</td>
     <td>10.283</td>
     <td>6.025</td>
     <td>9.048</td>
     <td>21.828</td>
     <td>32.21</td>
     <td>44.626</td>
     <td>0</td>
  </tr><tr>
     <td>python-tornado-N</td>
     <td>13.564</td>
     <td>9.352</td>
     <td>12.68</td>
     <td>30.095</td>
     <td>39.922</td>
     <td>56.357</td>
     <td>13.91</td>
     <td>8.865</td>
     <td>11.853</td>
     <td>29.213</td>
     <td>45.431</td>
     <td>89.296</td>
     <td>0</td>
  </tr><tr>
     <td>python-gevent-websocket-N</td>
     <td>13.657</td>
     <td>9.702</td>
     <td>12.775</td>
     <td>29.703</td>
     <td>36.899</td>
     <td>76.452</td>
     <td>10.931</td>
     <td>6.3</td>
     <td>9.836</td>
     <td>21.572</td>
     <td>32.288</td>
     <td>53.608</td>
     <td>0</td>
  </tr><tr>
     <td>erlang-cowboy</td>
     <td>13.874</td>
     <td>8.697</td>
     <td>13.64</td>
     <td>28.067</td>
     <td>35.509</td>
     <td>51.35</td>
     <td>11.183</td>
     <td>7.911</td>
     <td>9.332</td>
     <td>24.767</td>
     <td>40.981</td>
     <td>67.124</td>
     <td>0</td>
  </tr><tr>
     <td>python-twisted-N</td>
     <td>14.129</td>
     <td>9.586</td>
     <td>13.24</td>
     <td>30.999</td>
     <td>40.043</td>
     <td>55.277</td>
     <td>17.946</td>
     <td>13.381</td>
     <td>14.658</td>
     <td>43.116</td>
     <td>68.38</td>
     <td>110.879</td>
     <td>0</td>
  </tr><tr>
     <td>go-gonet</td>
     <td>14.278</td>
     <td>14.903</td>
     <td>12.595</td>
     <td>28.756</td>
     <td>59.599</td>
     <td>169.155</td>
     <td>13.824</td>
     <td>43.38</td>
     <td>9.274</td>
     <td>22.799</td>
     <td>40.163</td>
     <td>710.677</td>
     <td>0</td>
  </tr><tr>
     <td>pypy-twisted-N</td>
     <td>15.672</td>
     <td>17.321</td>
     <td>13.027</td>
     <td>33.088</td>
     <td>75.013</td>
     <td>193.445</td>
     <td>12.449</td>
     <td>7.772</td>
     <td>10.935</td>
     <td>25.944</td>
     <td>41.256</td>
     <td>72.259</td>
     <td>0</td>
  </tr><tr>
     <td>java-webbit</td>
     <td>17.547</td>
     <td>55.258</td>
     <td>13.121</td>
     <td>30.681</td>
     <td>52.433</td>
     <td>1004.434</td>
     <td>11.422</td>
     <td>7.918</td>
     <td>9.717</td>
     <td>28.734</td>
     <td>43.628</td>
     <td>55.844</td>
     <td>0</td>
  </tr><tr>
     <td>pypy-twisted-1</td>
     <td>27.441</td>
     <td>80.393</td>
     <td>13.516</td>
     <td>41.03</td>
     <td>564.404</td>
     <td>756.465</td>
     <td>13.872</td>
     <td>13.44</td>
     <td>11.223</td>
     <td>26.465</td>
     <td>87.42</td>
     <td>149.827</td>
     <td>0</td>
  </tr><tr>
     <td>pypy-tornado-1</td>
     <td>29.905</td>
     <td>84.353</td>
     <td>14.086</td>
     <td>57.936</td>
     <td>501.039</td>
     <td>772.808</td>
     <td>43.032</td>
     <td>66.326</td>
     <td>19.413</td>
     <td>226.929</td>
     <td>308.387</td>
     <td>351.444</td>
     <td>0</td>
  </tr><tr>
     <td>scala-play</td>
     <td>37.897</td>
     <td>129.066</td>
     <td>13.425</td>
     <td>67.791</td>
     <td>1011.026</td>
     <td>1025.334</td>
     <td>50.354</td>
     <td>109.526</td>
     <td>11.429</td>
     <td>332.623</td>
     <td>535.78</td>
     <td>642.44</td>
     <td>0</td>
  </tr><tr>
     <td>node-ws</td>
     <td>390.509</td>
     <td>503.25</td>
     <td>100.412</td>
     <td>1421.621</td>
     <td>1784.192</td>
     <td>1994.033</td>
     <td>13681.632</td>
     <td>4458.928</td>
     <td>15166.09</td>
     <td>18194.522</td>
     <td>19270.177</td>
     <td>20861.466</td>
     <td>0</td>
  </tr><tr>
     <td>python-twisted-1</td>
     <td>583.673</td>
     <td>987.51</td>
     <td>32.343</td>
     <td>3018.707</td>
     <td>3397.069</td>
     <td>3697.019</td>
     <td>28912.227</td>
     <td>13276.581</td>
     <td>29386.427</td>
     <td>48560.488</td>
     <td>50650.745</td>
     <td>52461.485</td>
     <td>0</td>
  </tr><tr>
     <td>clojure-aleph</td>
     <td>126.745</td>
     <td>299.223</td>
     <td>15.478</td>
     <td>1005.36</td>
     <td>1015.957</td>
     <td>1428.287</td>
     <td>1121.035</td>
     <td>486.259</td>
     <td>1013.214</td>
     <td>2020.782</td>
     <td>3020.174</td>
     <td>3037.376</td>
     <td>187</td>
  </tr><tr>
     <td>python-tornado-1</td>
     <td>1639.882</td>
     <td>1451.978</td>
     <td>1200.693</td>
     <td>4856.938</td>
     <td>6088.798</td>
     <td>6448.096</td>
     <td>65803.397</td>
     <td>39733.592</td>
     <td>66941.409</td>
     <td>128679.909</td>
     <td>135929.904</td>
     <td>137092.752</td>
     <td>265</td>
  </tr><tr>
     <td>haskell-snap</td>
     <td>176.855</td>
     <td>383.722</td>
     <td>20.219</td>
     <td>1010.429</td>
     <td>1742.526</td>
     <td>2042.309</td>
     <td>24428.761</td>
     <td>14931.595</td>
     <td>24404.437</td>
     <td>47912.411</td>
     <td>50257.414</td>
     <td>50702.091</td>
     <td>275</td>
  </tr><tr>
     <td>python-gevent-websocket-1</td>
     <td>1218.935</td>
     <td>1822.901</td>
     <td>239.617</td>
     <td>5067.439</td>
     <td>6033.99</td>
     <td>6535.422</td>
     <td>11203.601</td>
     <td>6301.863</td>
     <td>11600.681</td>
     <td>20927.817</td>
     <td>23976.174</td>
     <td>25890.765</td>
     <td>538</td>
  </tr><tr>
     <td>perl-ev</td>
     <td>1555.812</td>
     <td>3017.7</td>
     <td>479.488</td>
     <td>6982.455</td>
     <td>16591.74</td>
     <td>27522.464</td>
     <td>35.84</td>
     <td>17.569</td>
     <td>34.168</td>
     <td>66.911</td>
     <td>82.117</td>
     <td>91.16</td>
     <td>3955</td>
  </tr>
</table>

*rows are sorted by connection timeout, handshake time and stddev, 
   and message letency and stddev*


Starting with the EC2 benchmark (times are in milliseconds), you will
notice the peculiar behavior that EC2 exhibited:

Handshake elapsed time vs time and message latencies vs time:

![EC2 handshake times](wsdemo-results/v2/m1.large-c10k-handshake-times.png)
![EC2 latency times](wsdemo-results/v2/m1.large-c10k-latency.png)

There is what looks like O(log N) growth in connection times and
linear growth in the message latency.

When compared to the non-virtualized, local setup, the data takes a
much different shape.

![Local handshake times](wsdemo-results/v2/moritz-server-c10k-handshake-times.png)
![Local latency times](wsdemo-results/v2/moritz-server-c10k-latency.png)

If you look at the box plots of the EC2:

![EC2 handshake times box plot](wsdemo-results/v2/m1.large-c10k-handshake-times-box.png)
![EC2 latency times box plot](wsdemo-results/v2/m1.large-c10k-latency-box.png)

You will notice that while Erlang did the best, but 5% of the messages
sent were >1.3 seconds which is likely unacceptable.  It is a
bitter-sweet victory for Erlang on EC2.

On my local hardware, all the servers did ridiculously better: 

![Local handshake times](wsdemo-results/v2/moritz-server-c10k-handshake-times-box.png)
![Local latency times](wsdemo-results/v2/moritz-server-c10k-latency-box.png)

So much better that the top 5 servers are nearly a tie when it comes
to time and consistency.

## My Conclusion

This test shows the baseline overhead of the servers at ten thousand
concurrent client connections.  On physical hardware, save a few
outliers, the frameworks did comparably well. 

Testing these on EC2 on the other hand, the story is much different.
All of the servers had wide deviations from the median. You will need
to load balance your service in order to reach c10k on a m1.large EC2
instance. A single node using any platform will have trouble reaching
c10k on a m1.large instance. Even the leader in the EC2 benchmark
(Erlang) reached unacceptable message latencies of > 1 second.  I am
sure that there exists a instance type in EC2 that able to hit c10k on
a single node but they will cost more than I am willing to spend on
this test.

The moral of this story is that you must test your assumptions and do
some capacity planning.  If you're tempted to stick that node.js
prototype up on EC2 without load testing to show your boss that
node.js scales; you are likely to have egg on your face and be out of
a job.

## Code, Charts, Stats and Raw data

Here are links to more detailed charts and stats along with the raw
CSV data.  Try to be kind to Dropbox and only download the raw data if
you really plan on using it.

* [Detailed EC2 charts](wsdemo-results/v2/results-m1.large-c10k-v2.pdf)
* [EC2 CSV Tables 1.12 gigs compressed](https://www.dropbox.com/s/sfeiresei4zoed9/m1.large-c10k.tar.bz2)

* [Detailed Local charts](wsdemo-results/v2/results-moritz-server-c10k-v2.pdf)
* [Local CSV Tables 1.19 gigs compressed](https://www.dropbox.com/s/y6lf5x06kgp6a7k/moritz-server-c10k.tar.bz2)
* [wsdemo code](https://github.com/ericmoritz/wsdemo/tree/v2)

## Plea for support

I used Amazon affiliate fees earned through my [Books Every
Self-Taught Computer Scientist Should Read
post](http://eric.themoritzfamily.com/books-every-self-taught-computer-scientist-should-read.html)
to fund this project.  The server I bought off craigslist and the cost
of the numerous EC2 instances spun up for this test were all made
possible through those funds.  If you are in the market for any of
these books, I would appreciate the kick-back.  You get a book, I get
some money and it only cuts into Amazon's bottom-line (which is a
really large line).

I only recommend books that I have actually read and enjoyed. I hope
to put the money to good use. (I think a [Raspberry PI powered FAWN
cluster](http://www.cs.cmu.edu/~fawnproj/) written in Erlang is next
but no promises)

 * [Programming Erlang: Software for a Concurrent World](http://www.amazon.com/gp/product/193435600X/ref=as_li_ss_tl?ie=UTF8&camp=1789&creative=390957&creativeASIN=193435600X&linkCode=as2&tag=erimor-20)
 * [Erlang and OTP in Action](http://www.amazon.com/gp/product/1933988789/ref=as_li_ss_tl?ie=UTF8&camp=1789&creative=390957&creativeASIN=1933988789&linkCode=as2&tag=erimor-20)

