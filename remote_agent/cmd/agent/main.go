package main

import (
	"bufio"
	"context"
	"flag"
	"fmt"
	"log"
	"os"
	"os/signal"
	"runtime"
	"syscall"

	"deco-agent/internal/api"
	"deco-agent/internal/config"
	"deco-agent/internal/scheduler"
	"deco-agent/internal/wizard"
	"deco-agent/pkg/models"

	"github.com/google/uuid"
)

func main() {
	// Pause on exit helper
	defer func() {
		fmt.Println("\nPresione Enter para salir...")
		bufio.NewReader(os.Stdin).ReadString('\n')
	}()

	configPath := flag.String("config", "", "Path to config file")
	flag.Parse()

	// 1. Load Config
	cfg, err := config.LoadConfig(*configPath)
	if err != nil {
		// Si falla la carga, intentamos lanzar el Wizard
		fmt.Printf("No se pudo cargar configuración: %v\n", err)
		fmt.Println("Iniciando asistente de configuración...")

		cfg, err = wizard.RunWizard()
		if err != nil {
			log.Printf("Error en el asistente: %v", err)
			return
		}
	}

	log.Printf("Starting Deco Agent: %s (%s)", cfg.AgentName, cfg.AgentUUID)

	// 2. Init Client
	client := api.NewClient(cfg)

	// 3. Register if needed
	if cfg.AgentToken == "" {
		log.Println("Agent token missing. Attempting registration...")
		if cfg.AgentUUID == "" {
			cfg.AgentUUID = uuid.New().String()
		}

		hostname, _ := os.Hostname()
		req := models.RegisterRequest{
			ClientID:  cfg.ClientID,
			AgentUUID: cfg.AgentUUID,
			AgentName: cfg.AgentName,
			Hostname:  hostname,
			OS:        runtime.GOOS,
			AuthToken: cfg.AuthToken,
			// LocalIPs: TODO
		}

		resp, err := client.Register(req)
		if err != nil {
			log.Fatalf("Registration failed: %v", err)
		}

		log.Printf("Registration successful. Token received.")
		cfg.AgentToken = resp.AgentToken
		cfg.PollInterval = resp.PollIntervalSec

		if err := config.SaveConfig(cfg, *configPath); err != nil {
			log.Fatalf("Failed to save config: %v", err)
		}

		// Re-init client with new token
		client = api.NewClient(cfg)
	}

	// 4. Start Scheduler
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	sched := scheduler.NewScheduler(cfg, client)

	// Handle OS signals
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		<-sigChan
		log.Println("Shutdown signal received")
		cancel()
	}()

	sched.Start(ctx)
	log.Println("Agent stopped")
}
