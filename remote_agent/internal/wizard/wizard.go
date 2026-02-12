package wizard

import (
	"bufio"
	"fmt"
	"os"
	"strings"

	"deco-agent/internal/config"

	"github.com/google/uuid"
)

func RunWizard() (*config.Config, error) {
	reader := bufio.NewReader(os.Stdin)

	fmt.Println("========================================")
	fmt.Println("   BIENVENIDO AL AGENTE DECO (SETUP)   ")
	fmt.Println("========================================")
	fmt.Println("No se encontró archivo de configuración.")
	fmt.Println("Por favor, ingrese los siguientes datos:")
	fmt.Println("")

	// 1. Client ID
	fmt.Print("Client ID (ej: cliente-01): ")
	clientID, _ := reader.ReadString('\n')
	clientID = strings.TrimSpace(clientID)
	if clientID == "" {
		return nil, fmt.Errorf("Client ID es obligatorio")
	}

	// 2. Agent Name
	hostname, _ := os.Hostname()
	fmt.Printf("Nombre del Agente [Default: %s]: ", hostname)
	agentName, _ := reader.ReadString('\n')
	agentName = strings.TrimSpace(agentName)
	if agentName == "" {
		agentName = hostname
	}

	// 3. API URL
	defaultURL := "http://localhost:18001"
	fmt.Printf("API URL [Default: %s]: ", defaultURL)
	apiURL, _ := reader.ReadString('\n')
	apiURL = strings.TrimSpace(apiURL)
	if apiURL == "" {
		apiURL = defaultURL
	}

	// 4. Auth Token
	fmt.Print("Auth Token (Token inicial): ")
	authToken, _ := reader.ReadString('\n')
	authToken = strings.TrimSpace(authToken)
	if authToken == "" {
		return nil, fmt.Errorf("Auth Token es obligatorio")
	}

	// Generate UUID
	agentUUID := uuid.New().String()

	cfg := &config.Config{
		ClientID:     clientID,
		AgentName:    agentName,
		AgentUUID:    agentUUID,
		APIURL:       apiURL,
		AuthToken:    authToken,
		LogLevel:     "info",
		PollInterval: 60,
	}

	// Save Config
	if err := config.SaveConfig(cfg, ""); err != nil {
		return nil, fmt.Errorf("error guardando configuración: %w", err)
	}

	fmt.Println("")
	fmt.Println("Configuración generada y guardada exitosamente.")
	fmt.Printf("UUID Generado: %s\n", agentUUID)
	fmt.Println("========================================")

	return cfg, nil
}
