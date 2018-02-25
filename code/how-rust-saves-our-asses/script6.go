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
