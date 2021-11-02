---
# These are meta-variables defined with YAML syntax, change them as you wish.
# see https://pandoc.org/MANUAL.html#variables
title: TDT4225 Exercise 4
author:
  - Hauk Aleksander Olaussen
date: \today # This is a latex command, ignored for HTML output
lang: en-US
papersize: a4
geometry: margin=4cm
toc: false
toc-title: "List of Contents"
toc-depth: 2
numbersections: false
colorlinks: true
links-as-notes: true
# The document is following the break written using Markdown syntax
---

## 1. Kleppmann Chap 5

a) 
**When should you use multi-leader replication, and why should you use it in these cases? When is leader-based replication better to use?**

As Kleppmann says: "It rarely makes sense to use multi-leader replication within a single datacenter". 

Usecases for this approach then makes us turn our head toward operations distributed over multiple datacenters. This will make each datacenter have its own leader, which will be the one to recieve the writes, but it will share and recieve data from other leaders in other datacenters. This will improve performance as a client may connect to any of the leaders in any datacenter (probably the one closest geographically), and not just one designated leader in one datacenter somewhere in the world. It will also tolerate a whole datacenter failing due to some fault - be it network problems or outages. The database will still be operating while the faulty datacenter is catching up to the rest.

Still, multiple datacenters is not the only usecase for multi-leader replication. They are appropriate to use when needing an application to work without internet connection, and then "sync" up when reconnected. This makes each device act as a datacenter/leader updating itself when it gets updated data from another device. Kleppmann uses the calendar on our phones and other devices as an example for this. It may also be used in applications where collaborative editing is a thing. Multi-leader replication will allow these applications (users) to share their local replica with other users, and with some conflict handling, allowing them to write in the same document simultaneously.

When not having the operation distributed over multiple datacenters, using leader-based replication with just a single leader will propably be a better approach. One of the reasons for this is that we do not need to worry about conflicts when it comes to writing. All the followers will update themselves based on the leader, and nothing else - meaning that the leader has absolute control. This means, however, that should the leader fail, a user can not write to the database. This is dealt with by assigning one of the followers as the new leader, a process called *failover*. For smaller scale applcations, the single leader approach will probably be a better choice.

b) 
**Why should you use log shipping as a replication means instead of replicating the SQL statements?**

We would not want to just replicate the SQL statements given to the leader if it includes non-deterministic functions, as this would mean that we write data to the follower not neccessarily equal to the leaders. Here, log shipping would be a better approach. Another case is if the statements depend on data already existing in the database. This would mean that the SQL statements must be executed in the same order as they did on the leader to ensure that the data is the same. 

As we can see, just replication the SQL statements on the follower will not neccessarily give us the result we want, and we must then use another approach - namely different kinds of log shipping.

c) 
**How could a database management system support read your writes consistency when there are multiple replicas present of data?**


Read-after-write consistency (read-your-writes) essentially means that a user should always see the data they themselves have submitted. It ensures this by always reading data that the user has modified from the leader, which always has the most recent data. If most of the things in the application are able to be edited by the user, this approach will not do, as most of the data will have to be read from the leader. Another way of ensuring this is to save time of the last update, and after a set time (Kleppmann uses 1 minute in his example), all the reads will be made from the leader. One can also save the timestamp and make sure that the read is handled by a replica sufficiently up do date, or wait until the current one is.

There are other related problems to this - namely *monotonic reads* and *consistent prefix reads*, which considers the user always seing data it has already seen, and always viewing the data that makes causal sense, respectively.

## 2. Kleppmann Chap 6

a) 
**Why should we support sharding / partitioning?**

Being able to split the data into partitions resting on different computers ensures scalability for the application. This will help with distributing both disk usage, and query load across the nodes.

b) 
**What is the best way of supporting re-partitioning? And why is this the best way? (According to Kleppmann)**

Kleppmann discusses different ways of rebalancing the data into new partitions in the nodes. He first discusses "hash mod N", which for obvious reasons do not work well for operations where the amount of nodes changes. He speaks positively around a solution with a fixed number of partitions where each node is assigned multiple partitions, and when a new node is introduced, it steals some from the other nodes. The difficult part with doing it this way is getting the number of partitions for each node just right. If the partitions are large, rebalancing and recovery will become too expensive. Too small, and there will be too much overhead.

Because of these negative features, we turn to dynamic rebalancing. A new partition is introduces when a partition exceeds some set size. The data is split between the old and the new. This keeps the number of partitions adapting to the size of the data - which scales well with little overhead. One problem is that for when the dataset is small, it will be processed by a single node until it splits. This is negated with *pre-splitting* where an initial configured set of partitions is created for an empty database. Kleppmann also discusses partitioning based on the number of nodes, and not the data size. This will scale well when we introduce new nodes, and as the data volume increases (as we probably will need new nodes). When a new node is added to the cluster, it will randomly split some partitions and take over half the data for each. This may cause unfair splits, but when averaged over the number of partitions each node have, it will not end up as fair as one might think. Kleppmann speaks higly of this approach - dynamic partitioning proportional to the number of nodes.


c) 
**Explain when you should use local indexing, and when you should use global indexing?**

As *local indexing* makes writes more efficient as you can just write to the document you can just use the partition that contains that document. Reads however is another story, as you will need to query all partititons and combine the results to get the full picture. Needless to say - this is expensive.

*Global indexing* on the other will have the opposite effect. As the indexes themselves are partitioned, reading will be very efficient as we just query the partition containing the term we want. Writing is the slow part with doing it this way, as a write may affect multiple partitions - making it expensive.

Hence, one should use *local indexing* when you are expecting a lot of writes, and *global indexing* when expecting a lot of reads.

## 3. Kleppmann Chap 7

a) 
**We want to compare read committed with snapshot isolation. We assume the traditional way of implementing read committed, where write locks are held to the end of the transaction, while read locks are set and released when doing the read itself. Show how the following schedule is executed using these two approaches:** \newline
***r1(A); w2(A); w2(B); r1(B);c1;c2;***

See figures 1 and 2.

![Read committed](./images/read_committed.PNG)

![Snapshot isolation](./images/snapshot_isolation.PNG)


b) 
**Also show how this is executed using serializable with 2PL (two-phase locking).**

See figure 3.

![Two-phase locking (2PL)](./images/2pl.PNG)

c) 
**Explain by an example write skew, and show how SSI (serializable snapshot isolation) may solve this problem**

If a write is dependent on some data which have been altered within its commit, it will abort this transaction, as the consistency of the snapshot have been compromised. 

We can use the example Kleppmann uses. Both doctors Bob and Alice wants to check whether or not two or more doctors are on call. If this is true, they will put themselves off call. There must always be one doctor on call. They only change their own table. As both doctors check this concurrently - the condition of two or more will be true for both. As we are using SSI, a snapshot have been created at the start of the transactions. When alice commits, Bob is unaware that she has gone off, and goes off himself. However, the transaction manager sees that Alices value has changed from the snapshot, refusing Bob to commit his changes, and aborts the transaction. Bob still has to work. 

