package main

import (
	"log"
	"os"
)

func main() {
	config := config{
		addr: ":8080",
		db: dbConfig{},
	}
	api := app{
		config: config,
	}

	handler := api.mount()
	if err := api.run(handler); err != nil {
		log.Printf("Server has failed to start, err: %s", err)
		os.Exit(1)
	}
}
