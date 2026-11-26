package main

import (
	"context"
	"log"
	"net/http"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/jackc/pgx/v5/pgxpool"
)

type app struct {
	config config
	db     *pgxpool.Pool
}

type config struct {
	addr string
	db   dbConfig
}

type dbConfig struct {
	dsn string
}

func (app *app) mount() http.Handler {
	router := chi.NewRouter()

	router.Use(middleware.RequestID)
	router.Use(middleware.Logger)
	router.Use(middleware.Recoverer)
	router.Use(middleware.Timeout(60 * time.Second))
	router.Get("/health", app.healthHandler)
	router.Get("/db-health", app.dbHealthHandler)
	return router
}

func (app *app) healthHandler(
	w http.ResponseWriter,
	r *http.Request,
) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Server up!"))
}

func (app *app) dbHealthHandler(
	w http.ResponseWriter,
	r *http.Request,
) {
	ctx, cancel := context.WithTimeout(
		r.Context(),
		3*time.Second,
	)
	defer cancel()

	if err := app.db.Ping(ctx); err != nil {
		log.Printf("Database health check failed: %v", err)

		http.Error(
			w,
			"Database unavailable",
			http.StatusServiceUnavailable,
		)
		return
	}

	w.WriteHeader(http.StatusOK)
	w.Write([]byte("PostgreSQL connection established!"))
}

func (app *app) run(handler http.Handler) error {
	server := &http.Server{
		Addr:         app.config.addr,
		Handler:      handler,
		WriteTimeout: time.Second * 30,
		ReadTimeout:  time.Second * 10,
		IdleTimeout:  time.Minute,
	}

	log.Printf("Server is up! Addr %s", app.config.addr)
	return server.ListenAndServe()
}
