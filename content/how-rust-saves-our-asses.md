Title: How Rust Saves Our Asses
Date: 2017-02-24
Tags: rust, python, go, golang
Status: draft


**TODO** intro

Let me start with a bit of `JSON` data:

```json
{
  "@context": {
    "@vocab": "http://schema.org/"
  },
  "people": [
    {
      "name": "Eric",
      "@type": "Person",
      "address": {
        "@type": "Address",
        "addressLocality": "Rockville",
        "addressRegion": "Maryland"
      },
      "worksFor": {
        "@type": "Address",
        "name": "Gannett",
        "address": {
          "@type": "Address",
          "addressLocality": "Mclean",
          "addressRegion": "Virginia"
        }
      }
    },
    {
      "name": "Jane Doe",
      "@type": "Person",
      "address": null
    }
  ]
}
```

So we have a collection of people.  Lets write a bit of Python that uses this data:

```python
import sys
import json
data = json.load(sys.stdin)
for person in data["people"]:
    print """
   	 {name} lives in {city}, {state}.
    They work for {workName} in {workCity}, {workState}
    """.format(
    	name=person["name"],
    	city=person["address"]["city"],
    	state=person["address"]["state"],
        workName=person["worksFor"]["name"],
    	workCity=person["worksFor"]["address"]["addressLocality"],
    	workState=person["worksFor"]["address"]["addressRegion"],
    )
```

What happens when we use this code?

```
$ cat data.json | python script1.py 
Eric works for Gannett in Mclean, Virginia
Traceback (most recent call last):
  File "script1.py", line 7, in <module>
    workName=person["worksFor"]["name"],
KeyError: 'worksFor'
```

Oh, We have no idea who Jane Doe works for, so our code crashes. Let us fix this.

```python
import sys
import json
data = json.load(sys.stdin)
for person in data["people"]:
    address = person.get("address", {})
    works_for = person.get("worksFor", {})
    works_for_address = works_for.get("address", {})

    print """
{name} lives in {city}, {state}.
They work for {workName} in {workCity}, {workState}.
    """.format(
    	name=person.get("name", ""),
        city=address.get("addressLocality", "???"),
        state=address.get("addressRegion", "???"),
    	workName=works_for.get("name", "???"),
        workCity=works_for_address.get("addressLocality", "???"),
    	workState=works_for_address.get("addressRegion", "???")
    )
```

Ok, we've fixed the `KeyError`. What happen now?

```
$ cat data.json | python script2.py

Eric lives in Rockville, Maryland.
They work for Gannett in Mclean, Virginia.

Traceback (most recent call last):
  File "script2.py", line 14, in <module>
    city=address.get("addressLocality", "???"),
AttributeError: 'NoneType' object has no attribute 'get'
```

Oh no, that address value is `null`, we have to compensate for that.

```python
import sys
import json
data = json.load(sys.stdin)
for person in data["people"]:
    address = person.get("address")
    if address is None:
        address = {}
    works_for = person.get("worksFor", {})
    works_for_address = works_for.get("address", {})

    print """
{name} lives in {city}, {state}.
They work for {workName} in {workCity}, {workState}.
    """.format(
    	name=person.get("name", ""),
        city=address.get("addressLocality", "???"),
        state=address.get("addressRegion", "???"),
    	workName=works_for.get("name", "???"),
        workCity=works_for_address.get("addressLocality", "???"),
    	workState=works_for_address.get("addressRegion", "???")
    )
```

```
$ cat data.json | python script3.py

Eric lives in Rockville, Maryland.
They work for Gannett in Mclean, Virginia.


Jane Doe lives in ???, ???.
They work for ??? in ???, ???.
```

So we've now covered the case that `address` can be `null`.  Actually, any value in `JSON` could be `null`.  Shit. We have to do that for every field we pull out of `JSON` or we're hosed.

We have to code really defensively because at any point keys might be missing or a value might be `null`. 

The natural way to access a `dict` in Python is with use the `x[key]` syntax but we can never trust that a key exists. Additionally, We can never trust that if the key exists, that it is not `null`.

In production, this leads to many crashes and `500` errors because programmers like to program for the happy case and often forget about the sad cases. So we write a lot of unit tests and rely on code reviews and cry into our pillows at night because we never know where the next error will be.

Can a static type system help us here? Many Python programmers have started using Golang for the static typing. The hope that static typing can save their asses. So, can Go save our asses?

```go
package main

import (
	"encoding/json"
	"fmt"
	"os"
)

type Data struct {
	People []Person
}
type Person struct {
	Name     string
	Address  Address
	WorksFor Organization
}
type Organization struct {
	Name    string
	Address Address
}

type Address struct {
	AddressLocality string
	AddressRegion   string
}

func main() {
	var data = Data{}
	if err := json.NewDecoder(os.Stdin).Decode(&data); err != nil {
		panic(err)
	}
	for _, person := range data.People {
		fmt.Printf(`
%s lives in %s %s.
They work %s for %s, %s.
			`,
			person.Name,
			person.Address.AddressLocality,
			person.Address.AddressRegion,
			person.WorksFor.Name,
			person.WorksFor.Address.AddressLocality,
			person.WorksFor.Address.AddressRegion,
		)
	}
}
```

```
$ cat data.json | go run script4.go

Eric lives in Rockville Maryland.
They work Gannett for Mclean, Virginia.

Jane Doe lives in  .
They work  for , .
```

Excellent, our code looks natural.  It doesn't crash when things are missing.  Golang's default values saves us from `null` and missing values. 

That output looks gross, Let us mimic the Python version and use `"???"`. The way to do that in Go is pointers.

```go
package main

import (
	"encoding/json"
	"fmt"
	"os"
)

type Data struct {
	People []Person
}
type Person struct {
	Name     string
	Address  *Address
	WorksFor *Organization
}
type Organization struct {
	Name    string
	Address *Address
}

type Address struct {
	AddressLocality string
	AddressRegion   string
}

func main() {
	var data = Data{}
	if err := json.NewDecoder(os.Stdin).Decode(&data); err != nil {
		panic(err)
	}
	for _, person := range data.People {
		fmt.Printf(`
%s lives in %s %s.
They work %s for %s, %s.
			`,
			person.Name,
			person.Address.AddressLocality,
			person.Address.AddressRegion,
			person.WorksFor.Name,
			person.WorksFor.Address.AddressLocality,
			person.WorksFor.Address.AddressRegion,
		)
	}
}
```

The problem is that with pointers, they can be `nil`, what happens when we try to use a pointer that is `nil`?

```
$ cat data.json | go run script5.go

Eric lives in Rockville Maryland.
They work Gannett for Mclean, Virginia.
                        panic: runtime error: invalid memory address or nil pointer dereference
[signal SIGSEGV: segmentation violation code=0x1 addr=0x0 pc=0x10b750a]

goroutine 1 [running]:
main.main()
        /Users/emoritz/Data/Projects/blog/code/how-rust-saves-our-asses/script5.go:38 +0x16a
exit status 2
```

Well shit. How can a language that says that it ["makes it easy to build simple, reliable, and efficient software"](https://golang.org/).  Repeat the [billion dollar mistake](https://www.infoq.com/presentations/Null-References-The-Billion-Dollar-Mistake-Tony-Hoare) of `nil`-pointers. `nil`-pointers are notorious for making unreliable software.  

Java programmers the world over lose so much sleep because of the dreaded `java.lang.NullPointerException`.  Ever have an Android app crash? Look in the logs and you'll see `java.lang.NullPointerException` sprinkled all over the place.

Let us fix the go version.

```go
package main

import (
	"encoding/json"
	"fmt"
	"os"
)

type Data struct {
	People []Person
}
type Person struct {
	Name     string
	Address  *Address
	WorksFor *Organization
}
type Organization struct {
	Name    string
	Address *Address
}

type Address struct {
	AddressLocality string
	AddressRegion   string
}

func main() {
	var data = Data{}
	if err := json.NewDecoder(os.Stdin).Decode(&data); err != nil {
		panic(err)
	}
	for _, person := range data.People {
		city := "???"
		state := "???"
		works_for_name := "???"
		works_for_city := "???"
		works_for_state := "???"

		if person.Address != nil {
			city = person.Address.AddressLocality
			state = person.Address.AddressRegion
		}
		if person.WorksFor != nil {
			works_for_name = person.WorksFor.Name
			if person.WorksFor.Address != nil {
				works_for_city = person.WorksFor.Address.AddressLocality
				works_for_state = person.WorksFor.Address.AddressRegion
			}
		}

		fmt.Printf(`
%s lives in %s %s.
They work for %s in %s, %s.
`,
			person.Name,
			city,
			state,
			works_for_name,
			works_for_city,
			works_for_state,
		)
	}
}

```

Go fails to save our asses. Once again, a language lets us down.  So how does Rust save our asses? Rust does not have `null`.

Because no value can be `null`, we never have to worry about trying to access data that does not exist.  So, what do we do for `address` or `worksFor` which sometimes does not exist if we don't have `null`? Enter the `Option` type.

The `Option` type uses the type system to enforce an optional value. Here's a Rust version of the Go code that crashes:

```rust
#[macro_use]
extern crate serde_derive;
extern crate serde;
extern crate serde_json;

use std::io;

#[derive(Deserialize, Default, Debug)]
struct Data {
    pub people: Vec<Person>
}

#[derive(Deserialize, Default, Debug)]
struct Person {
    pub name: String,
    pub address: Option<Address>,
    pub worksFor: Option<Organization>
}

#[derive(Deserialize, Default, Debug)]
struct Organization {
    pub name: String,
    pub address: Option<Address>
}

#[derive(Deserialize, Default, Debug)]
struct Address {
    pub addressLocality: String,
    pub addressRegion: String
}

fn main() {
    let data: Data = serde_json::from_reader(io::stdin())
        .expect("Invalid JSON");

    for person in data.people.iter() {
        println!("
{} lives in {}, {}.
They work for {} in {} {}.
", 
    person.name,
    person.address.addressLocality,
    person.address.addressRegion,
    person.worksFor.name,
    person.worksFor.address.addressLocality,
    person.worksFor.address.addressRegion
)
    }
}
```

So, all values that can be `null` or missing are represented by an `Option<>` type.  We've tried to use those fields, which in Python and Go resulted in a runtime crash. What happens when we try to compile our Rust verson?

```
$ cat data.json | cargo run --bin script6
   Compiling scripts v0.1.0 (file:///Users/emoritz/Data/Projects/blog/code/how-rust-saves-our-asses)
error[E0609]: no field `addressLocality` on type `std::option::Option<Address>`
  --> src/bin/script6.rs:42:20
   |
42 |     person.address.addressLocality,
   |                    ^^^^^^^^^^^^^^^
 
error: Could not compile `scripts`.

To learn more, run the command again with --verbose.
GCI-EMORITZ2-M:how-rust-saves-our-asses emoritz$
```

The Rust compiler, won't let us accidentally use an unknown value. Do you see how it says that `person.address` is a `Option<Address>`.  That means we have an `Address` struct inside an `Option`.  We have to get it out of there to use it.

So when a value is of type `Option<Address>`, it can be one of two things, `Some(address)` or `None`.  In order to use the `Address` we have to unwrap it.

```rust
#[macro_use]
extern crate serde_derive;
extern crate serde;
extern crate serde_json;

use std::io;

#[derive(Deserialize, Default, Debug)]
struct Data {
    pub people: Vec<Person>
}

#[derive(Deserialize, Default, Debug)]
struct Person {
    pub name: String,
    pub address: Option<Address>,
    pub worksFor: Option<Organization>
}

#[derive(Deserialize, Default, Debug)]
struct Organization {
    pub name: String,
    pub address: Option<Address>
}

#[derive(Deserialize, Default, Debug)]
struct Address {
    pub addressLocality: String,
    pub addressRegion: String
}

fn main() {
    let data: Data = serde_json::from_reader(io::stdin())
        .expect("Invalid JSON");

    for person in data.people.into_iter() {
        let mut city = String::from("???");
        let mut state = String::from("???");
        let mut works_for_name = String::from("???");
        let mut works_for_city = String::from("???");
        let mut works_for_state = String::from("???");

        if let Some(address) = person.address {
            city = address.addressLocality;
            state = address.addressRegion;
        }
        if let Some(works_for) = person.worksFor {
            works_for_name = works_for.name;
            if let Some(address) = works_for.address {
                works_for_city = address.addressLocality;
                works_for_state = address.addressRegion;
            }
        }
        println!("
{} lives in {}, {}.
They work for {} in {} {}.
            ", 
            person.name,
            city,
            state,
            works_for_name,
            works_for_city,
            works_for_state
        );
    }
}
```

```
$ cat data.json | cargo run --bin script6

Eric lives in Rockville, Maryland.
They work for Gannett in Mclean Virginia.


Jane Doe lives in ???, ???.
They work for ??? in ??? ???.

```


This works just like the Python and Go versions we wrote.  The difference is the Rust version will not compile if we try to use the unknown values. So it is impossible to use an unknown value at runtime and crash your program.

When we wrote the following line:

```rust
if let Some(address) = person.address {
	city = address.addressLocality;
	state = address.addressRegion;
}
```

The `if` statement only runs if `person.address` is `Some()`, if it is `None`, the `if` statement moves on. We have to turn the `person.address` which is an `Option<Address>` into an `Address` so we can use it. One way to do that is by pattern matching using the `if let` syntax.




