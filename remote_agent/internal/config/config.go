package config

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
)

type Config struct {
	ClientID     string `json:"client_id"`
	AgentName    string `json:"agent_name"`
	AgentUUID    string `json:"agent_uuid"`
	APIURL       string `json:"api_url"`
	AuthToken    string `json:"auth_token"`
	AgentToken   string `json:"agent_token"`
	LogLevel     string `json:"log_level"`
	PollInterval int    `json:"poll_interval_sec"`
}

func GetConfigPath() string {
	// En Windows: C:\ProgramData\DecoAgent\config.json
	// En Linux (dev): ./config.json o /etc/deco-agent/config.json
	// Simplificado para MVP:
	return "config.json"
}

func LoadConfig(path string) (*Config, error) {
	if path == "" {
		path = GetConfigPath()
	}
	if _, err := os.Stat(path); os.IsNotExist(err) {
		return nil, fmt.Errorf("config file not found at %s", path)
	}

	file, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	cfg := &Config{}
	decoder := json.NewDecoder(file)
	if err := decoder.Decode(cfg); err != nil {
		return nil, err
	}
	return cfg, nil
}

func SaveConfig(cfg *Config, path string) error {
	if path == "" {
		path = GetConfigPath()
	}

	// Ensure directory exists
	dir := filepath.Dir(path)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return fmt.Errorf("failed to create config dir: %w", err)
	}

	data, err := json.MarshalIndent(cfg, "", "  ")
	if err != nil {
		return fmt.Errorf("failed to marshal config: %w", err)
	}

	if err := os.WriteFile(path, data, 0644); err != nil {
		return fmt.Errorf("failed to write config file: %w", err)
	}

	return nil
}
