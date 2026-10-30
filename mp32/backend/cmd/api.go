package main

import (
	"log"
	"net/http"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
)

type app struct {
	config	config
}

type config struct {
	addr 	string
	db		dbConfig
}

type dbConfig struct {
	dsn	string
}

func (app *app) mount() http.Handler {
    router := chi.NewRouter()

	router.Use(middleware.RequestID)
	router.Use(middleware.Recoverer)
	router.Use(middleware.Timeout(60 * time.Second))
    router.Get("/health", func(w http.ResponseWriter, r *http.Request) {
        w.Write([]byte("Server up!"))
    })
	return router
}

func (app *app) run(handler http.Handler) error {
	server := &http.Server{
		Addr: app.config.addr,
		Handler: handler,
		WriteTimeout: time.Second * 30,
		ReadTimeout: time.Second * 10,
		IdleTimeout: time.Minute,
	}

	log.Printf("Server is up! Addr %s", app.config.addr)
	return server.ListenAndServe()
}