package scanner

import (
	"context"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"time"
)

// RunNmap ejecuta nmap con los argumentos dados y devuelve el XML raw.
// Asume que nmap.exe está en el PATH o en una ruta relativa conocida.
func RunNmap(ctx context.Context, args []string) (string, error) {
	// En Windows producción: C:\Program Files\DecoAgent\nmap\nmap.exe
	// Para MVP: buscamos en PATH o local
	cmdName := "nmap"

	// Argumentos base obligatorios para output XML
	// Usamos archivo temporal para output
	tmpXML := filepath.Join(os.TempDir(), fmt.Sprintf("scan_%d.xml", time.Now().UnixNano()))
	defer os.Remove(tmpXML)

	finalArgs := append(args, "-oX", tmpXML)

	cmd := exec.CommandContext(ctx, cmdName, finalArgs...)
	output, err := cmd.CombinedOutput()
	if err != nil {
		return "", fmt.Errorf("nmap execution failed: %v, output: %s", err, string(output))
	}

	// Leer XML generado
	xmlBytes, err := os.ReadFile(tmpXML)
	if err != nil {
		return "", fmt.Errorf("failed to read nmap xml output: %v", err)
	}

	return string(xmlBytes), nil
}

func BuildArgs(profile, target string) []string {
	args := []string{}
	switch profile {
	case "fast":
		args = append(args, "-T4", "-F")
	case "full":
		args = append(args, "-T4", "-sV", "-O")
	default:
		args = append(args, "-T4", "-F") // Default fast
	}
	args = append(args, target)
	return args
}
