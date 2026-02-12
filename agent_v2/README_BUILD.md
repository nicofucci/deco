# How to Build Deco-Security Agent V2 (Windows)

## Prerequisites
*   Windows 10/11 or Server 2016+
*   Python 3.11+
*   Pip

## Build Steps

1.  **Install Dependencies**
    ```powershell
    pip install -r requirements.txt
    pip install pyinstaller
    ```

2.  **Verify Code**
    Run in console mode to test Registration:
    ```powershell
    python src/main.py
    ```
    *Note: Ensure you have a valid `config.json` in `C:\ProgramData\DecoSecurity\` or allow the agent to create default config.*

3.  **Build Executable**
    ```powershell
    pyinstaller --noconsole --onefile --name "DecoAgent" --hidden-import win32timezone src/main.py
    ```

4.  **Install Service**
    Admin PowerShell:
    ```powershell
    dist\DecoAgent.exe --startup=auto install
    dist\DecoAgent.exe start
    ```

## Testing
*   Check `C:\ProgramData\DecoSecurity\logs\agent.log`
*   Verify Agent appears "Online" in Tower Dashboard.
