package scheduler

import (
	"context"
	"deco-agent/internal/api"
	"deco-agent/internal/config"
	"deco-agent/internal/scanner"
	"deco-agent/pkg/models"
	"fmt"
	"log"
	"time"
)

type Scheduler struct {
	Config *config.Config
	Client *api.Client
}

func NewScheduler(cfg *config.Config, client *api.Client) *Scheduler {
	return &Scheduler{
		Config: cfg,
		Client: client,
	}
}

func (s *Scheduler) Start(ctx context.Context) {
	log.Printf("Starting scheduler loop (interval: %d sec)", s.Config.PollInterval)
	ticker := time.NewTicker(time.Duration(s.Config.PollInterval) * time.Second)
	defer ticker.Stop()

	// Primer ciclo inmediato
	s.runCycle(ctx)

	for {
		select {
		case <-ctx.Done():
			log.Println("Stopping scheduler...")
			return
		case <-ticker.C:
			s.runCycle(ctx)
		}
	}
}

func (s *Scheduler) runCycle(ctx context.Context) {
	// 1. Heartbeat
	if err := s.Client.Heartbeat(); err != nil {
		log.Printf("Heartbeat failed: %v", err)
		// Si falla heartbeat, quizás no deberíamos pedir tareas, pero intentamos igual por resiliencia
	} else {
		log.Println("Heartbeat OK")
	}

	// 2. Get Tasks
	tasks, err := s.Client.GetPendingTasks(s.Config.AgentUUID)
	if err != nil {
		log.Printf("Failed to get tasks: %v", err)
		return
	}

	if len(tasks) == 0 {
		return
	}

	log.Printf("Received %d tasks", len(tasks))

	// 3. Execute Tasks
	for _, task := range tasks {
		s.executeTask(ctx, task)
	}
}

func (s *Scheduler) executeTask(ctx context.Context, task models.Task) {
	log.Printf("Executing task %s (type: %s)", task.TaskID, task.Type)

	result := models.TaskResult{
		StartedAt: time.Now().Format(time.RFC3339),
		Status:    "running",
	}

	var err error
	var rawXML string

	switch task.Type {
	case "nmap_basic_scan", "nmap_full_scan":
		target := task.Params["target_cidr"]
		profile := task.Params["profile"]
		if profile == "" {
			if task.Type == "nmap_full_scan" {
				profile = "full"
			} else {
				profile = "fast"
			}
		}

		args := scanner.BuildArgs(profile, target)
		rawXML, err = scanner.RunNmap(ctx, args)
	default:
		err = fmt.Errorf("unknown task type: %s", task.Type)
	}

	result.FinishedAt = time.Now().Format(time.RFC3339)
	if err != nil {
		log.Printf("Task %s failed: %v", task.TaskID, err)
		result.Status = "error"
		result.ErrorMsg = err.Error()
	} else {
		log.Printf("Task %s completed", task.TaskID)
		result.Status = "completed"
		result.RawNmapXML = rawXML
		result.Summary = map[string]string{"msg": "Scan completed successfully"}
	}

	// 4. Submit Result
	if err := s.Client.SubmitResult(s.Config.AgentUUID, task.TaskID, result); err != nil {
		log.Printf("Failed to submit result for task %s: %v", task.TaskID, err)
	} else {
		log.Printf("Result submitted for task %s", task.TaskID)
	}
}
