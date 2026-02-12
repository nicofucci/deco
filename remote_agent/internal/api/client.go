package api

import (
	"bytes"
	"deco-agent/internal/config"
	"deco-agent/pkg/models"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

type Client struct {
	BaseURL    string
	AgentToken string
	HTTP       *http.Client
}

func NewClient(cfg *config.Config) *Client {
	return &Client{
		BaseURL:    cfg.APIURL,
		AgentToken: cfg.AgentToken,
		HTTP:       &http.Client{Timeout: 30 * time.Second},
	}
}

func (c *Client) Register(req models.RegisterRequest) (*models.RegisterResponse, error) {
	body, _ := json.Marshal(req)
	resp, err := c.HTTP.Post(c.BaseURL+"/remote-agents/register", "application/json", bytes.NewBuffer(body))
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return nil, fmt.Errorf("register failed: %s", resp.Status)
	}

	var res models.RegisterResponse
	if err := json.NewDecoder(resp.Body).Decode(&res); err != nil {
		return nil, err
	}
	return &res, nil
}

func (c *Client) Heartbeat() error {
	req, _ := http.NewRequest("POST", c.BaseURL+"/remote-agents/heartbeat", nil)
	req.Header.Set("Authorization", "Bearer "+c.AgentToken)
	resp, err := c.HTTP.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	if resp.StatusCode != 200 {
		return fmt.Errorf("heartbeat failed: %s", resp.Status)
	}
	return nil
}

func (c *Client) GetPendingTasks(agentUUID string) ([]models.Task, error) {
	url := fmt.Sprintf("%s/remote-agents/%s/tasks/pending", c.BaseURL, agentUUID)
	req, _ := http.NewRequest("GET", url, nil)
	req.Header.Set("Authorization", "Bearer "+c.AgentToken)

	resp, err := c.HTTP.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return nil, fmt.Errorf("get tasks failed: %s", resp.Status)
	}

	var tasks []models.Task
	if err := json.NewDecoder(resp.Body).Decode(&tasks); err != nil {
		return nil, err
	}
	return tasks, nil
}

func (c *Client) SubmitResult(agentUUID, taskID string, res models.TaskResult) error {
	url := fmt.Sprintf("%s/remote-agents/%s/tasks/%s/results", c.BaseURL, agentUUID, taskID)
	body, _ := json.Marshal(res)

	req, _ := http.NewRequest("POST", url, bytes.NewBuffer(body))
	req.Header.Set("Authorization", "Bearer "+c.AgentToken)
	req.Header.Set("Content-Type", "application/json")

	resp, err := c.HTTP.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		b, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("submit failed: %s - %s", resp.Status, string(b))
	}
	return nil
}
