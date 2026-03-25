# Piping QC System — Navisworks Plugin

A Navisworks Manage 2024 add-in that provides a Windows Forms UI for interacting
with the Piping QA/QC backend API directly from inside Navisworks.

---

## Prerequisites

| Requirement | Details |
|---|---|
| Navisworks Manage | 2024 (x64) |
| .NET Framework | 4.8 |
| Windows | 10 or 11 (64-bit) |
| Piping QC Backend | Running and reachable (default: `http://localhost:8000`) |

---

## Building the Plugin

1. Open a Visual Studio 2022 (or later) Developer Command Prompt.
2. Navigate to the `navisworks_plugin/` directory.
3. Restore NuGet packages and build:

   ```
   dotnet restore PipingQCPlugin.csproj
   dotnet build   PipingQCPlugin.csproj -c Release
   ```

4. The output DLL is written to `bin\Release\net48\PipingQCPlugin.dll`.

> **Note:** The build references Autodesk Navisworks 2024 DLLs from their default
> installation path (`C:\Program Files\Autodesk\Navisworks Manage 2024\`).
> If Navisworks is installed to a different location, update the `<HintPath>`
> entries in `PipingQCPlugin.csproj` before building.

---

## Installing into Navisworks

Navisworks loads add-ins from `.addin` manifest files placed in one of two locations:

### All-users (requires admin rights)

```
%PROGRAMDATA%\Autodesk\Navisworks Manage 2024\Plugins\PipingQCPlugin\
```

### Current user only

```
%APPDATA%\Autodesk\Navisworks Manage 2024\Plugins\PipingQCPlugin\
```

**Steps:**

1. Create the `PipingQCPlugin` folder inside whichever Plugins directory you choose.
2. Copy these files into that folder:
   - `PipingQCPlugin.dll`
   - `PipingQCPlugin.addin`
   - `Newtonsoft.Json.dll` (from `bin\Release\net48\`)
3. Launch Navisworks Manage 2024.
4. The plugin appears under **Add-Ins** ribbon tab as **Piping QC System**.
   Click the button to open the main window.

---

## Configuring the API Connection

When the plugin window opens you will see a **Connection Settings** panel at the top.

| Field | Description |
|---|---|
| API URL | Base URL of the backend service, e.g. `http://localhost:8000` or `https://piping-qc.example.com` |
| Username | Your Piping QC system username |
| Password | Your Piping QC system password |

Press **Connect**. On success the status bar at the bottom shows
`Connected as <username>` and the tabs become active.

---

## Using the Plugin

### Dashboard Tab

Shows live KPI data fetched from `GET /api/v1/dashboard/summary`:

- Total ISOs
- Total Lines
- Total Validations
- Total Errors
- Pass Rate (%)

Click **Refresh** to reload the figures.

### ISO Drawings Tab

Lists all ISO drawings stored in the system (`GET /api/v1/iso`).

- Click **Load ISOs** to fetch the first page.
- Use **< Previous** and **Next >** to paginate (20 records per page).
- The grid shows: File Name, Line Number, Pipe Size, Spec, Status.

### Validate Tab

Triggers the rule-engine validation for a single ISO:

1. Paste or type the ISO UUID into the **ISO ID** field.
2. Click **Validate** (`POST /api/v1/iso/{id}/validate`).
3. Each validation rule result appears colour-coded:
   - **[PASS]** — green
   - **[FAIL]** — red
   - **[WARN]** — orange

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| Add-in does not appear in Navisworks | `.addin` file not found or wrong folder | Verify the Plugins folder path and that both `.dll` and `.addin` are present |
| "Network error connecting to …" | Backend not running or wrong URL | Start the backend (`docker compose up`) and confirm the URL in the settings panel |
| "Invalid username or password" | Wrong credentials | Use the web UI or admin API to verify your account |
| Validation returns 400 "ISO must be in processed state" | ISO was uploaded but OCR has not completed | Wait for processing or check backend logs |

---

## Development Notes

- **ApiClient.cs** — thin `HttpClient` wrapper; all methods are `async` and
  throw `HttpRequestException` on non-success HTTP status codes.
- **MainForm.cs / MainForm.Designer.cs** — standard WinForms; UI updates from
  background threads are marshalled via `Control.Invoke`.
- The plugin targets `net48` to match the runtime embedded in Navisworks 2024.
  Do not change the target framework.
