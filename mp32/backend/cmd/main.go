package main

import (
	"log"
	"os"
)

func main() {
	config := config{
		addr: ":8080",
		db: dbConfig{
			dsn: os.Getenv("DATABASE_URL"),
		},
	}

	db, err := newDB(config.db.dsn)
	if err != nil {
		log.Fatal("Database initialization failed: ", err)
	}
	defer db.Close()
	log.Println("PostgreSQL connection established")

	api := app{
		config: config,
		db:     db,
	}

	handler := api.mount()
	if err := api.run(handler); err != nil {
		log.Printf("Server has failed to start, err: %s", err)
		os.Exit(1)
	}
}
