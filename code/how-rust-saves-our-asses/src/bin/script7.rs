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
        let unknown = String::from("???");
        
        let address = person.address;
        let city = address.as_ref()
            .map(|x| x.addressLocality.clone())
            .unwrap_or_else(|| unknown.clone());

        let state = address.as_ref()
            .map(|x| x.addressRegion.clone())
            .unwrap_or_else(|| unknown.clone());

        let works_for = person.worksFor;
        let works_for_name = works_for.as_ref()
            .map(|x| x.name.clone())
            .unwrap_or_else(|| unknown.clone());
            
        let (works_for_city, works_for_state) = works_for.as_ref()
            .and_then(|x| x.address.as_ref())
            .map(|x| (x.addressLocality.clone(), x.addressRegion.clone()))
            .unwrap_or_else(|| (unknown.clone(), unknown.clone()));

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