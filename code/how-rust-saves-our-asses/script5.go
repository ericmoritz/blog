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
They work for %s in %s, %s.
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
