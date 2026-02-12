; Script de Inno Setup para Deco-Security Agent (Windows)
; Compilar con Inno Setup 6+
; Requiere binario generado previamente en: ..\dist\DecoAgent.exe

#define AppName "Deco Security Agent"
#define AppVersion "2.0.0"
#define AppPublisher "Deco Security"
#define AppURL "https://deco-security.com"
#define AppExeName "DecoAgent.exe"
#define ServiceName "DecoSecurityAgent"

[Setup]
; Identificador unico para el desinstalador
AppId={{DECO-SEC-AGENT-V2-WIN-001}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}

; Directorio por defecto: %ProgramFiles%\DecoSecurityAgent
DefaultDirName={commonpf}\DecoSecurityAgent
; Directorio de datos: %ProgramData%\DecoSecurity
DefaultGroupName={#AppName}

; Opciones de instalacion
DisableProgramGroupPage=yes
OutputBaseFilename=DecoSecurityAgentSetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

; Privilegios administrativos requeridos para instalar servicio y escribir en ProgramFiles
PrivilegesRequired=admin

; Nombre del archivo de salida
OutputDir=..\dist

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Files]
; Copia del ejecutable principal
Source: "..\dist\windows\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
; Crear directorio de datos/logs con permisos
Name: "{commonappdata}\DecoSecurity"; Permissions: users-modify
Name: "{commonappdata}\DecoSecurity\logs"; Permissions: users-modify

[Run]
; 1. Instalar el servicio (usando el propio ejecutable python/pywin32)
; --startup=auto configura el servicio para inicio automatico
Filename: "{app}\{#AppExeName}"; Parameters: "--startup=auto install"; Flags: runhidden waituntilterminated; StatusMsg: "Installing service..."

; 2. Arrancar el servicio
Filename: "net"; Parameters: "start {#ServiceName}"; Flags: runhidden waituntilterminated; StatusMsg: "Starting service..."

[UninstallRun]
; 1. Detener servicio
Filename: "net"; Parameters: "stop {#ServiceName}"; Flags: runhidden waituntilterminated; RunOnceId: "StopService"

; 2. Eliminar servicio
Filename: "{app}\{#AppExeName}"; Parameters: "remove"; Flags: runhidden waituntilterminated; RunOnceId: "RemoveService"

[Code]
var
  UserPage: TInputQueryWizardPage;

// Init Wizard: Add the configuration page
procedure InitializeWizard;
begin
  UserPage := CreateInputQueryPage(wpWelcome,
    'Agent Configuration', 'Server Connection Details',
    'Please enter the Orchestrator settings provided by your administrator.');
  
  // Add items (Index 0: URL, Index 1: Key)
  UserPage.Add('Orchestrator URL:', False);
  UserPage.Add('Agent API Key:', False);
  
  // Set defaults
  UserPage.Values[0] := 'https://api.deco-security.com';
  UserPage.Values[1] := ''; 
end;

// Validation: Enforce API Key in interactive mode
function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  
  if CurPageID = UserPage.ID then
  begin
    if Trim(UserPage.Values[1]) = '' then
    begin
      MsgBox('An API Key is required to register the agent.', mbError, MB_OK);
      Result := False;
    end;
  end;
end;

// Helper function to escape JSON strings
function JsonEscape(Value: String): String;
var
  I: Integer;
begin
  Result := '';
  for I := 1 to Length(Value) do
  begin
    if Value[I] = '\' then Result := Result + '\\'
    else if Value[I] = '"' then Result := Result + '\"'
    else Result := Result + Value[I];
  end;
end;

// Event: Write config after install
procedure CurStepChanged(CurStep: TSetupStep);
var
  ApiUrl, ApiKey, ConfigContent, ConfigPath: String;
begin
  if CurStep = ssPostInstall then
  begin
    // 1. Try Command Line Params first (Silent Mode priority)
    ApiUrl := ExpandConstant('{param:URL}');
    ApiKey := ExpandConstant('{param:KEY}');

    // 2. Fallback to Wizard values if params are empty
    // Note: In silent mode, Wizard values remain as defaults (Key empty), 
    // unless defaults were set. But silent mode implies params should be provided.
    // However, we handle the case where user runs UI but passes params too.
    
    if ApiUrl = '' then ApiUrl := UserPage.Values[0];
    if ApiKey = '' then ApiKey := UserPage.Values[1];

    // 3. Final Fallback for URL
    if ApiUrl = '' then ApiUrl := 'https://api.deco-security.com';

    ConfigPath := ExpandConstant('{commonappdata}\DecoSecurity\config.json');

    // Build JSON (Matching src/config.py expectation)
    ConfigContent := '{' + #13#10 +
      '  "api_url": "' + JsonEscape(ApiUrl) + '",' + #13#10 +
      '  "api_key": "' + JsonEscape(ApiKey) + '",' + #13#10 +
      '  "log_level": "INFO"' + #13#10 +
      '}';

    try
      SaveStringToFile(ConfigPath, ConfigContent, False);
      Log('Config written to: ' + ConfigPath);
      Log('Orchestrator URL: ' + ApiUrl);
      // Don't log the API key for security
    except
      MsgBox('Failed to write configuration file ' + ConfigPath, mbError, MB_OK);
    end;
  end;
end;
