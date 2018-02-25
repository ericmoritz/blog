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