Here is a concise log of the setup. You can copy and paste this directly into one of your Obsidian vaults for future reference.

> [!tip] Edit C:\Users\CaseyM\AppData\Roaming\espanso\match\base.yml

```
c C:\Users\CaseyM\AppData\Roaming\espanso\match\base.yml
```
---
> [!claude] Whassup?
## **Log: Espanso Installation & Configuration**

**Date:** 2026-04-11

**Purpose:** Global text expansion for Obsidian callouts across multiple vaults without per-vault plugins.

### **1. Installation Details**

- **Method:** installed via `winget`.
    
- **Command:** `winget install --id=Espanso.Espanso -e`
    
- **Install Location:** `C:\Users\CaseyM\AppData\Local\Programs\Espanso\`
    
- **Executable:** `espansod.exe`
    

### **2. Service & Runtime Setup**

Because the installation was user-level (not system-wide), we manually registered the service and used the `launcher` mode to ensure it interacts correctly with the Windows user session.

- **Registration:**
    
    PowerShell
    
    ```
    & "C:\Users\CaseyM\AppData\Local\Programs\Espanso\espansod.exe" service register
    ```
    
- **Start Command:**
    
    PowerShell
    
    ```
    & "C:\Users\CaseyM\AppData\Local\Programs\Espanso\espansod.exe" launcher
    ```
    
- **Persistence:** Added a shortcut to `shell:startup` pointing to the launcher command to ensure it runs on boot.
    

### **3. Configuration Locations**

Espanso uses a split-directory structure. The configuration (where snippets live) is separate from the application.

- **Config Root:** `%AppData%\espanso\`
    
- **Snippets File (Main):** `%AppData%\espanso\match\base.yml`
    
- **Global Settings:** `%AppData%\espanso\config\default.yml`
    

### **4. Active Snippets**

Current snippets added to `base.yml`:

YAML

```
matches:
  - trigger: ":claude"
    replace: "> [!Claude] "
```

### **5. Useful Commands**

- **Edit Config:** `espanso edit` (Opens the snippet file in the default editor).
    
- **Check Paths:** `espanso path` (Displays all active directory locations).
    
- **Restart Service:** `espanso restart` (Required after manual YAML edits if they aren't auto-detected).
    

---