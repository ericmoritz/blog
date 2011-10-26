
Understanding PSQL's MVCC
#########################
:date: 2008-06-18 16:40:54
:tags: django, postgresql

=========================
Understanding PSQL's MVCC
=========================
PostgresSQL implements something called `MVCC`_.  Which alleviates the need for a Read-Lock in many cases.
However when `Glenn Franxman`_ and I were trying to figure out how this works we were having trouble understanding 
it completely.  

If you ask about `MVCC`_ in the #postgres irc channel on Freenode, they will direct you to the following three
links
  
  * http://en.wikipedia.org/wiki/Multiversion_concurrency_control
  * http://www.developer.com/net/vb/article.php/877181
  * http://www.postgresql.org/docs/current/static/mvcc.html

With SQL there are `four transaction isolation levels`_, unfortunately the Wikipedia `entry`_ only describes one, serializable. So relying on
the Wikipedia documentation to describe how Postgres' opperates is not completely accurate.  I think that internally Postgres may operate the
way that the Wikipedia entry describes, but uses a write-lock to emulate a "Read Commit" isolation level to prevent the transaction abort that
would normally occur by one transaction writing and comitting data .  
I don't know if that's true or not.

Another confusing bit about Postgres is that Postgres only implements two levels, "Read Committed" and "Serializable" even though 
you can set the other isolation levels.  In the documentation, the `four transaction isolation levels`_ refers to the SQL standard
and not Postgres' actually functionality.

So when you look at the `four transaction isolation levels`_, you'll notice that it says that a dirty
read is possible if you set the isolation level to "READ UNCOMMITTED", however because "READ UNCOMMITTED" is the 
same as "READ COMMITTED" internally in Postgres, you can never get a dirty read even if you set the isolation level 
to READ UNCOMMITTED.  That's ok because, as the documentation states, "the four isolation levels only define which phenomena must not 
happen, they do not define which phenomena must happen."

I'll run some examples of concurrent transaction to show you how the four levels act.


---------------
Read Committed
---------------

+----------------------------------------------+------------------------------------------------------+
| Transaction 1				       | Transaction 2 	       	       	       	       	      |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode ::                                     |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# BEGIN;         	       	       |   mvcc_test=# BEGIN;                                 |
|   BEGIN                                      |   BEGIN                                              |
|   mvcc_test=# SET TRANSACTION ISOLATION LEVEL|   mvcc_test=# SET TRANSACTION ISOLATION LEVEL        |
|   mvcc_test-# READ COMMITTED;                |   mvcc_test-# READ COMMITTED;                        |
|   SET                                        |   SET                                                |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode ::                                     |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# select * from mvcc_test;       |   mvcc_test=# select * from mvcc_test;               |
|    id | i                                    |    id | i                                            |
|   ----+---                                   |   ----+---                                           |
|     1 | 1                                    |     1 | 1                                            |
|   (1 row)                                    |   (1 row)                                            |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode ::                                     |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# update mvcc_test set i = i + 1;|   mvcc_test=# select * from mvcc_test;               |
|   UPDATE 1                                   |    id | i                                            |
|                                              |   ----+---                                           |
|                                              |     1 | 1                                            |
|                                              |   (1 row)                                            |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode ::                                     |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# select * from mvcc_test;       |   mvcc_test=# select * from mvcc_test;               |
|    id | i                                    |    id | i                                            |
|   ----+---                                   |   ----+---                                           |
|     1 | 2                                    |     1 | 1                                            |
|   (1 row)                                    |   (1 row)                                            |
+----------------------------------------------+------------------------------------------------------+
|                                              | .. sourcecode ::                                     |
|                                              |   sql                                                |
|                                              |                                                      |
|                                              |   mvcc_test=# update mvcc_test set i = i + 1; -- 7   |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode ::                                     |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# commit;                        |   UPDATE 1    	       	                              |
|   COMMIT                                     |   mvcc_test=# -- blocked until the other commited    |
+----------------------------------------------+------------------------------------------------------+
|                                              | .. sourcecode ::                                     |
|                                              |   sql                                                |
|                                              |                                                      |
|                                              |   mvcc_test=# commit;                                |
|                                              |   COMMIT                                             |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode ::                                     |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# select * from mvcc_test;       |   mvcc_test=# select * from mvcc_test;               |
|    id | i                                    |    id | i                                            |
|   ----+---                                   |   ----+---                                           |
|     1 | 3                                    |     1 | 3                                            |
|   (1 row)                                    |   (1 row)                                            |
+----------------------------------------------+------------------------------------------------------+

-----------------
Read Uncommitted
-----------------

With *Read Uncommited* I observed the same behavior as *Read Commited*.  
This reflects the `transaction documentation`_::

   But internally, there are only two distinct isolation levels, which correspond to the levels Read Committed
   and Serializable. When you select the level Read Uncommitted you really get Read Committed, and when you select
   Repeatable Read you really get Serializable, so the actual isolation level might be stricter than what you select.
   

+----------------------------------------------+------------------------------------------------------+
| Transaction 1				       | Transaction 2 	       	       	       	       	      |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode ::                                     |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# BEGIN;         	       	       |   mvcc_test=# BEGIN;                                 |
|   BEGIN                                      |   BEGIN                                              |
|   mvcc_test=# SET TRANSACTION ISOLATION LEVEL|   mvcc_test=# SET TRANSACTION ISOLATION LEVEL        |
|   mvcc_test-# READ UNCOMMITTED;              |   mvcc_test-# READ UNCOMMITTED;                      |
|   SET                                        |   SET                                                |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode ::                                     |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# BEGIN; -- 1	       	       |   mvcc_test=# BEGIN; -- 2.                           |
|   BEGIN                                      |   BEGIN                                              |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode ::                                     |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# select * from mvcc_test;       |   mvcc_test=# select * from mvcc_test;               |
|    id | i                                    |    id | i                                            |
|   ----+---                                   |   ----+---                                           |
|     1 | 1                                    |    1 | 1                                             |
|   (1 row)                                    |   (1 row)                                            |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode ::                                     |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# update mvcc_test set i = i + 1;|   mvcc_test=# select * from mvcc_test;               |
|   UPDATE 1                                   |    id | i                                            |
|                                              |   ----+---                                           |
|                                              |     1 | 1                                            |
|                                              |   (1 row)                                            |
|                                              |                                                      |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode ::                                     |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# select * from mvcc_test;       |   mvcc_test=# select * from mvcc_test;               |
|    id | i                                    |    id | i                                            |
|   ----+---                                   |   ----+---                                           |
|     1 | 2                                    |     1 | 1                                            |
|   (1 row)                                    |   (1 row)                                            |
+----------------------------------------------+------------------------------------------------------+
|                                              | .. sourcecode ::                                     |
|                                              |   sql                                                |
|                                              |                                                      |
|                                              |   mvcc_test=# update mvcc_test set i = i + 1;        |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode ::                                     |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# commit;                        |   UPDATE 1    	       	                              |
|   COMMIT                                     |   mvcc_test=# -- blocked until the other commited    |
+----------------------------------------------+------------------------------------------------------+
|                                              | .. sourcecode ::                                     |
|                                              |   sql                                                |
|                                              |                                                      |
|                                              |   mvcc_test=# commit;                                |
|                                              |   COMMIT                                             |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode ::                                     |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# select * from mvcc_test;       |   mvcc_test=# select * from mvcc_test;               |
|    id | i                                    |    id | i                                            |
|   ----+---                                   |   ----+---                                           |
|     1 | 3                                    |     1 | 3                                            |
|   (1 row)                                    |   (1 row)                                            |
+----------------------------------------------+------------------------------------------------------+


-----------------
SERIALIZABLE
-----------------


+----------------------------------------------+------------------------------------------------------+
| Transaction 1				       | Transaction 2 	       	       	       	       	      |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode::                                      |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# BEGIN;         	       	       |   mvcc_test=# BEGIN;                                 |
|   BEGIN                                      |   BEGIN                                              |
|   mvcc_test=# SET TRANSACTION ISOLATION LEVEL|   mvcc_test=# SET TRANSACTION ISOLATION LEVEL        |
|   mvcc_test-# SERIALIZABLE;                  |   mvcc_test-# SERIALIZABLE;                          |
|   SET                                        |   SET                                                |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode::                                      |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# select * from mvcc_test;       |   mvcc_test=# select * from mvcc_test;               |
|    id | i                                    |    id | i                                            |
|   ----+---                                   |   ----+---                                           |
|     1 | 1                                    |     1 | 1                                            |
|   (1 row)                                    |   (1 row)                                            |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode::                                      |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# update mvcc_test set i = i + 1;|   mvcc_test=# select * from mvcc_test;               |
|   UPDATE 1                                   |    id | i                                            |
|                                              |   ----+---                                           |
|                                              |     1 | 1                                            |
|                                              |   (1 row)                                            |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode::                                      |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# select * from mvcc_test;       |   mvcc_test=# select * from mvcc_test;               |
|    id | i                                    |    id | i                                            |
|   ----+---                                   |   ----+---                                           |
|     1 | 2                                    |     1 | 1                                            |
|   (1 row)                                    |   (1 row)                                            |
+----------------------------------------------+------------------------------------------------------+
|                                              | .. sourcecode::                                      |
|                                              |   sql                                                |
|                                              |                                                      |
|                                              |   mvcc_test=# update mvcc_test set i = i + 1;        |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode::                                      |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# commit;                        |   ERROR:  could not serialize access due to          |
|   COMMIT                                     |   concurrent update                                  |
+----------------------------------------------+------------------------------------------------------+
|                                              | .. sourcecode::                                      |
|                                              |   sql                                                |
|                                              |                                                      |
|                                              |   mvcc_test=# select * from mvcc_test;               |
|                                              |   ERROR:  current transaction is aborted, commands   |
|                                              |   ignored until end of transaction block             |
+----------------------------------------------+------------------------------------------------------+
|                                              | .. sourcecode::                                      |
|                                              |   sql                                                |
|                                              |                                                      |
|                                              |   mvcc_test=# commit;                                |
|                                              |   ROLLBACK                                           |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode::                                      |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# select * from mvcc_test;       |   mvcc_test=# select * from mvcc_test;               |
|    id | i                                    |    id | i                                            |
|   ----+---                                   |   ----+---                                           |
|     1 | 2                                    |     1 | 2                                            |
|   (1 row)                                    |   (1 row)                                            |
+----------------------------------------------+------------------------------------------------------+


-----------------
Repeatable Read
-----------------

Refering to the same paragraph in the `transaction documentation`_::

   But internally, there are only two distinct isolation levels, which correspond to the levels Read Committed
   and Serializable. When you select the level Read Uncommitted you really get Read Committed, and when you select
   Repeatable Read you really get Serializable, so the actual isolation level might be stricter than what you select.
   <http://www.postgresql.org/docs/current/static/transaction-iso.html>

*Repeatable Read* is the same as Serializable.

+----------------------------------------------+------------------------------------------------------+
| Transaction 1				       | Transaction 2 	       	       	       	       	      |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode::                                      |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# BEGIN;         	       	       |   mvcc_test=# BEGIN;                                 |
|   BEGIN                                      |   BEGIN                                              |
|   mvcc_test=# SET TRANSACTION ISOLATION LEVEL|   mvcc_test=# SET TRANSACTION ISOLATION LEVEL        |
|   mvcc_test-# REPEATABLE READ;               |   mvcc_test-# REPEATABLE READ;                       |
|   SET                                        |   SET                                                |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode::                                      |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# select * from mvcc_test;       |   mvcc_test=# select * from mvcc_test;               |
|    id | i                                    |    id | i                                            |
|   ----+---                                   |   ----+---                                           |
|     1 | 1                                    |     1 | 1                                            |
|   (1 row)                                    |   (1 row)                                            |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode::                                      |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# update mvcc_test set i = i + 1;|   mvcc_test=# select * from mvcc_test;               |
|   UPDATE 1                                   |    id | i                                            |
|                                              |   ----+---                                           |
|                                              |     1 | 1                                            |
|                                              |   (1 row)                                            |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode::                                      |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# select * from mvcc_test;       |   mvcc_test=# select * from mvcc_test;               |
|    id | i                                    |    id | i                                            |
|   ----+---                                   |   ----+---                                           |
|     1 | 2                                    |     1 | 1                                            |
|   (1 row)                                    |   (1 row)                                            |
+----------------------------------------------+------------------------------------------------------+
|                                              | .. sourcecode::                                      |
|                                              |   sql                                                |
|                                              |                                                      |
|                                              |   mvcc_test=# update mvcc_test set i = i + 1;        |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode::                                      |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# commit;                        |   ERROR:  could not serialize access due to          |
|   COMMIT                                     |   concurrent update                                  |
+----------------------------------------------+------------------------------------------------------+
|                                              | .. sourcecode::                                      |
|                                              |   sql                                                |
|                                              |                                                      |
|                                              |   mvcc_test=# select * from mvcc_test;               |
|                                              |   ERROR:  current transaction is aborted, commands   |
|                                              |   ignored until end of transaction block             |
+----------------------------------------------+------------------------------------------------------+
|                                              | .. sourcecode::                                      |
|                                              |   sql                                                |
|                                              |                                                      |
|                                              |   mvcc_test=# commit;                                |
|                                              |   ROLLBACK                                           |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode::                                      |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# select * from mvcc_test;       |   mvcc_test=# select * from mvcc_test;               |
|    id | i                                    |    id | i                                            |
|   ----+---                                   |   ----+---                                           |
|     1 | 2                                    |     1 | 2                                            |
|   (1 row)                                    |   (1 row)                                            |
+----------------------------------------------+------------------------------------------------------+

============================================
What is possible in Isolation Levels
============================================

So, in the `four transaction isolation levels`_ table, it describes what is possible in the different
isolation levels.  Since I've demostrated that there are only two isolation levels in Postgresql.  I'll
demostrate the two read phenomena that could happen in both Serializable and Read Committed.

Let me explain what those two phenomena are. Here is a good explanation of `read phenomena`_.  I'm
just simply repeating what is stated at that link

Nonrepeatable Read
  S1 reads data which is later changed and commited by S2. If S1 reads the same data again (after S2's commit) 
  and finds it to have changed or to be deleted (according to S2's changes), this is called a non-repeatable 
  read. It is called non-repeatable because the same select statement doesn't return the same data 
  (within the same transaction). 

Phantom read
  S1 reads data (select) with a specific where condition. After this read, S2 inserts some data that meets 
  the S1's where condition and commits the inserted data. When S1 issues a select statement with the same 
  where condition, it finds new records. It is called phantom read because the new records seem to be of 
  phantom origin. A phantom read is thus a special case of a non-repeatable read. 

--------------------------------------------
Read Committed / Nonrepeatable Read Attempt
--------------------------------------------

The SQL Standard says that with a Read Committed Isolation level, a "Nonrepeatable Read" is possible.
Here is my attempt in proving that assertion.

+----------------------------------------------+------------------------------------------------------+
| Transaction 1				       | Transaction 2 	       	       	       	       	      |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode::                                      |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# BEGIN;         	       	       |   mvcc_test=# BEGIN;                                 |
|   BEGIN                                      |   BEGIN                                              |
|   mvcc_test=# SET TRANSACTION ISOLATION LEVEL|   mvcc_test=# SET TRANSACTION ISOLATION LEVEL        |
|   mvcc_test-# READ COMMITTED;                |   mvcc_test-# READ COMMITTED;                        |
|   SET                                        |   SET                                                |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode::                                      |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# select * from mvcc_test;       |   mvcc_test=# select * from mvcc_test;               |
|    id | i                                    |    id | i                                            |
|   ----+---                                   |   ----+---                                           |
|     1 | 1                                    |     1 | 1                                            |
|   (1 row)                                    |   (1 row)                                            |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode::                                      |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# update mvcc_test set i = i + 1;|   --                                                 |
|   UPDATE 1                                   |                                                      |
|                                              |                                                      |
|                                              |                                                      |
|                                              |                                                      |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode::                                      |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# select * from mvcc_test;       |   mvcc_test=# select * from mvcc_test;               |
|    id | i                                    |    id | i                                            |
|   ----+---                                   |   ----+---                                           |
|     1 | 2                                    |     1 | 1                                            |
|   (1 row)                                    |   (1 row)                                            |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode::                                      |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# commit;                        |   --                                                 |
|   COMMIT                                     |                                                      |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode::                                      |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# select * from mvcc_test;       |   mvcc_test=# select * from mvcc_test;               |
|    id | i                                    |    id | i                                            |
|   ----+---                                   |   ----+---                                           |
|     1 | 2                                    |     1 | 2                                            |
|   (1 row)                                    |   (1 row)                                            |
|                                              |                                                      |
|                                              | This is a Nonrepeatable Read. Because the data has   |
|                                              | change while inside a transaction.                   |
+----------------------------------------------+------------------------------------------------------+


--------------------------------------------
Read Committed / Phantom Read Attempt
--------------------------------------------
The SQL Standard says that with a Read Committed Isolation level, a "Phantom Read" is possible.
Here is my attempt in proving that assertion.

+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode::                                      |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# BEGIN;         	       	       |   mvcc_test=# BEGIN;                                 |
|   BEGIN                                      |   BEGIN                                              |
|   mvcc_test=# SET TRANSACTION ISOLATION LEVEL|   mvcc_test=# SET TRANSACTION ISOLATION LEVEL        |
|   mvcc_test-# READ COMMITTED;                |   mvcc_test-# READ COMMITTED;                        |
|   SET                                        |   SET                                                |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode::                                      |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# select * from mvcc_test        |   mvcc_test=# select * from mvcc_test                |
|     where id = 2;                            |      where id = 2;                                   |
|    id | i                                    |     id | i                                           |
|   ----+---                                   |    ----+---                                          |
|   (0 rows)                                   |    (0 rows)                                          |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode::                                      |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|  mvcc_test=# insert into mvcc_test (id, i)   |   mvcc_test=# select * from mvcc_test                |
|   values (2, 1);                             |      where id = 2;                                   |
|  INSERT 0 1                                  |     id | i                                           |
|                                              |    ----+---                                          |
|                                              |    (0 rows)                                          |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode::                                      |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# commit;                        |   mvcc_test=# select * from mvcc_test where id = 2;  |
|   COMMIT                                     |    id | i                                            |
|                                              |   ----+---                                           |
|                                              |     2 | 1                                            |
|                                              |   (1 row)                                            |
|                                              |                                                      |
|                                              | This is a phantom read because the row poofed into   |
|                                              | existance inside the transaction when it didn't      |
|                                              | exist before.                                        |
+----------------------------------------------+------------------------------------------------------+

--------------------------------------------
Serializable / Nonrepeatable Read Attempt
--------------------------------------------

The SQL Standard says that with a Serializable Isolation level, a "Nonrepeatable Read" is **not possible**.
Here is my attempt in proving that assertion.

+----------------------------------------------+------------------------------------------------------+
| Transaction 1				       | Transaction 2 	       	       	       	       	      |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode::                                      |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# BEGIN;         	       	       |   mvcc_test=# BEGIN;                                 |
|   BEGIN                                      |   BEGIN                                              |
|   mvcc_test=# SET TRANSACTION ISOLATION LEVEL|   mvcc_test=# SET TRANSACTION ISOLATION LEVEL        |
|   mvcc_test-# SERIALIZABLE;                  |   mvcc_test-# SERIALIZABLE;                          |
|   SET                                        |   SET                                                |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode::                                      |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# select * from mvcc_test;       |   mvcc_test=# select * from mvcc_test;               |
|    id | i                                    |    id | i                                            |
|   ----+---                                   |   ----+---                                           |
|     1 | 1                                    |     1 | 1                                            |
|   (1 row)                                    |   (1 row)                                            |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode::                                      |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# update mvcc_test set i = i + 1;|   --                                                 |
|   UPDATE 1                                   |                                                      |
|                                              |                                                      |
|                                              |                                                      |
|                                              |                                                      |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode::                                      |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# select * from mvcc_test;       |   mvcc_test=# select * from mvcc_test;               |
|    id | i                                    |    id | i                                            |
|   ----+---                                   |   ----+---                                           |
|     1 | 2                                    |     1 | 1                                            |
|   (1 row)                                    |   (1 row)                                            |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode::                                      |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# commit;                        |   --                                                 |
|   COMMIT                                     |                                                      |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode::                                      |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# select * from mvcc_test;       |   mvcc_test=# select * from mvcc_test;               |
|    id | i                                    |    id | i                                            |
|   ----+---                                   |   ----+---                                           |
|     1 | 2                                    |     1 | 1                                            |
|   (1 row)                                    |   (1 row)                                            |
|                                              |                                                      |
|                                              | This is not a Nonrepeatable Read. Because the data   |
|                                              | did not change while inside a transaction.           |
+----------------------------------------------+------------------------------------------------------+


--------------------------------------------
Read Committed / Phantom Read Attempt
--------------------------------------------
The SQL Standard says that with a Read Committed Isolation level, a "Phantom Read" is possible.
Here is my attempt in proving that assertion.

+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode::                                      |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# BEGIN;         	       	       |   mvcc_test=# BEGIN;                                 |
|   BEGIN                                      |   BEGIN                                              |
|   mvcc_test=# SET TRANSACTION ISOLATION LEVEL|   mvcc_test=# SET TRANSACTION ISOLATION LEVEL        |
|   mvcc_test-# READ COMMITTED;                |   mvcc_test-# READ COMMITTED;                        |
|   SET                                        |   SET                                                |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode::                                      |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# select * from mvcc_test        |   mvcc_test=# select * from mvcc_test                |
|     where id = 2;                            |      where id = 2;                                   |
|    id | i                                    |     id | i                                           |
|   ----+---                                   |    ----+---                                          |
|   (0 rows)                                   |    (0 rows)                                          |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode::                                      |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|  mvcc_test=# insert into mvcc_test (id, i)   |   mvcc_test=# select * from mvcc_test                |
|   values (2, 1);                             |      where id = 2;                                   |
|  INSERT 0 1                                  |     id | i                                           |
|                                              |    ----+---                                          |
|                                              |    (0 rows)                                          |
+----------------------------------------------+------------------------------------------------------+
| .. sourcecode::                              | .. sourcecode::                                      |
|    sql                                       |   sql                                                |
|                                              |                                                      |
|   mvcc_test=# commit;                        |   mvcc_test=# select * from mvcc_test where id = 2;  |
|   COMMIT                                     |    id | i                                            |
|                                              |   ----+---                                           |
|                                              |   (0 row)                                            |
|                                              |                                                      |
|                                              |                                                      |
|                                              | This is a phantom read because the new row did not   |
|                                              | appear inside the transaction after it was commit in |
|                                              | the first transaction.                               |
+----------------------------------------------+------------------------------------------------------+


.. raw:: html

  <p style="text-align: center;">
    <object width="425" height="344" type="application/x-shockwave-flash" data="http://www.youtube.com/v/LVsFuScCUMg&amp;hl=en">
     <param name="movie" value="http://www.youtube.com/v/LVsFuScCUMg&amp;hl=en" />

    <embed src="http://www.youtube.com/v/LVsFuScCUMg&amp;hl=en"  type="application/x-shockwave-flash" width="425" height="344" /></object>
  </p>

.. _Transaction Documentation: http://www.postgresql.org/docs/current/static/transaction-iso.html
.. _MVCC: http://en.wikipedia.org/wiki/Multiversion_concurrency_control
.. _Glenn Franxman: http://www.hackermojo.com
.. _four transaction isolation levels: http://www.postgresql.org/docs/current/static/transaction-iso.html#MVCC-ISOLEVEL-TABLE
.. _entry: http://en.wikipedia.org/wiki/Multiversion_concurrency_control
.. _read phenomena: http://www.adp-gmbh.ch/ora/misc/isolation_level.html
