package models

type RegisterRequest struct {
	ClientID  string   `json:"client_id"`
	AgentUUID string   `json:"agent_uuid"`
	AgentName string   `json:"agent_name"`
	Hostname  string   `json:"hostname"`
	OS        string   `json:"os"`
	LocalIPs  []string `json:"local_ips"`
	AuthToken string   `json:"auth_token"`
}

type RegisterResponse struct {
	Status          string `json:"status"`
	AgentToken      string `json:"agent_token"`
	PollIntervalSec int    `json:"poll_interval_sec"`
}

type Task struct {
	TaskID string            `json:"task_id"`
	Type   string            `json:"type"`
	Params map[string]string `json:"params"`
}

type TaskResult struct {
	Status     string `json:"status"`
	StartedAt  string `json:"started_at"`
	FinishedAt string `json:"finished_at"`
	RawNmapXML string `json:"raw_nmap_xml"`
	Summary    any    `json:"summary"`
	ErrorMsg   string `json:"error_message,omitempty"`
}
