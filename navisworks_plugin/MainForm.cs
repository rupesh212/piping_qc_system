using System;
using System.Drawing;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace PipingQCPlugin
{
    public partial class MainForm : Form
    {
        private ApiClient _apiClient;
        private int _currentPage = 0;
        private const int PageSize = 20;
        private int _totalIsos = 0;

        public MainForm()
        {
            InitializeComponent();
            UpdateConnectionStatus("Not connected");
            UpdatePaginationLabel();
        }

        // ── Connection / Settings ────────────────────────────────────────────

        private async void btnConnect_Click(object sender, EventArgs e)
        {
            var baseUrl  = txtApiUrl.Text.Trim();
            var username = txtUsername.Text.Trim();
            var password = txtPassword.Text;

            if (string.IsNullOrEmpty(baseUrl))
            {
                MessageBox.Show("Please enter an API URL.", "Validation", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }
            if (string.IsNullOrEmpty(username) || string.IsNullOrEmpty(password))
            {
                MessageBox.Show("Please enter a username and password.", "Validation", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            btnConnect.Enabled = false;
            UpdateConnectionStatus("Connecting…");

            try
            {
                _apiClient = new ApiClient(baseUrl);
                bool ok = await Task.Run(() => _apiClient.LoginAsync(username, password));

                if (ok)
                {
                    UpdateConnectionStatus($"Connected as {username}");
                    tabControl.Enabled = true;
                }
                else
                {
                    _apiClient = null;
                    UpdateConnectionStatus("Not connected");
                    MessageBox.Show("Invalid username or password.", "Authentication Failed",
                        MessageBoxButtons.OK, MessageBoxIcon.Error);
                }
            }
            catch (Exception ex)
            {
                _apiClient = null;
                UpdateConnectionStatus("Not connected");
                MessageBox.Show($"Connection error:\n{ex.Message}", "Error",
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            finally
            {
                btnConnect.Enabled = true;
            }
        }

        // ── Dashboard ────────────────────────────────────────────────────────

        private async void btnRefreshDashboard_Click(object sender, EventArgs e)
        {
            if (!EnsureConnected()) return;

            btnRefreshDashboard.Enabled = false;
            try
            {
                DashboardSummary summary = await Task.Run(() => _apiClient.GetDashboardSummaryAsync());
                UpdateDashboardLabels(summary);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Failed to load dashboard:\n{ex.Message}", "Error",
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            finally
            {
                btnRefreshDashboard.Enabled = true;
            }
        }

        private void UpdateDashboardLabels(DashboardSummary s)
        {
            if (InvokeRequired)
            {
                Invoke(new Action(() => UpdateDashboardLabels(s)));
                return;
            }
            lblTotalIsos.Text        = $"Total ISOs: {s.TotalIsos}";
            lblTotalLines.Text       = $"Total Lines: {s.TotalLines}";
            lblTotalValidations.Text = $"Total Validations: {s.TotalValidations}";
            lblTotalErrors.Text      = $"Total Errors: {s.TotalErrors}";
            lblPassRate.Text         = $"Pass Rate: {s.PassRate:F1}%";
        }

        // ── ISO Drawings ─────────────────────────────────────────────────────

        private async void btnLoadISOs_Click(object sender, EventArgs e)
        {
            if (!EnsureConnected()) return;
            await LoadISOPage(_currentPage);
        }

        private async void btnPrevPage_Click(object sender, EventArgs e)
        {
            if (_currentPage > 0)
            {
                _currentPage--;
                await LoadISOPage(_currentPage);
            }
        }

        private async void btnNextPage_Click(object sender, EventArgs e)
        {
            int maxPage = Math.Max(0, (int)Math.Ceiling((double)_totalIsos / PageSize) - 1);
            if (_currentPage < maxPage)
            {
                _currentPage++;
                await LoadISOPage(_currentPage);
            }
        }

        private async Task LoadISOPage(int page)
        {
            btnLoadISOs.Enabled  = false;
            btnPrevPage.Enabled  = false;
            btnNextPage.Enabled  = false;

            try
            {
                int skip = page * PageSize;
                ISOListResponse result = await Task.Run(() => _apiClient.GetISOListAsync(skip, PageSize));

                _totalIsos = result.Total;

                if (InvokeRequired)
                    Invoke(new Action(() => PopulateISOGrid(result)));
                else
                    PopulateISOGrid(result);

                UpdatePaginationLabel();
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Failed to load ISOs:\n{ex.Message}", "Error",
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            finally
            {
                btnLoadISOs.Enabled = true;
                UpdatePaginationButtons();
            }
        }

        private void PopulateISOGrid(ISOListResponse result)
        {
            dgvISOList.Rows.Clear();
            if (result.Items == null) return;

            foreach (var iso in result.Items)
            {
                dgvISOList.Rows.Add(
                    iso.FileName,
                    iso.LineNumber,
                    iso.PipeSize,
                    iso.Spec,
                    iso.Status
                );
            }
        }

        private void UpdatePaginationLabel()
        {
            if (InvokeRequired)
            {
                Invoke(new Action(UpdatePaginationLabel));
                return;
            }
            int totalPages = _totalIsos == 0 ? 1 : (int)Math.Ceiling((double)_totalIsos / PageSize);
            lblPageInfo.Text = $"Page {_currentPage + 1} of {totalPages}  ({_totalIsos} total)";
        }

        private void UpdatePaginationButtons()
        {
            if (InvokeRequired)
            {
                Invoke(new Action(UpdatePaginationButtons));
                return;
            }
            int totalPages = Math.Max(1, (int)Math.Ceiling((double)_totalIsos / PageSize));
            btnPrevPage.Enabled = _currentPage > 0;
            btnNextPage.Enabled = _currentPage < totalPages - 1;
        }

        // ── Validate ─────────────────────────────────────────────────────────

        private async void btnValidate_Click(object sender, EventArgs e)
        {
            if (!EnsureConnected()) return;

            string isoId = txtIsoId.Text.Trim();
            if (string.IsNullOrEmpty(isoId))
            {
                MessageBox.Show("Please enter an ISO ID.", "Validation", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            btnValidate.Enabled = false;
            rtbValidationResults.Clear();
            rtbValidationResults.AppendText("Running validation…\n");

            try
            {
                ValidationResponse resp = await Task.Run(() => _apiClient.ValidateISOAsync(isoId));

                if (InvokeRequired)
                    Invoke(new Action(() => DisplayValidationResults(resp)));
                else
                    DisplayValidationResults(resp);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Validation failed:\n{ex.Message}", "Error",
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
                rtbValidationResults.Clear();
            }
            finally
            {
                btnValidate.Enabled = true;
            }
        }

        private void DisplayValidationResults(ValidationResponse resp)
        {
            rtbValidationResults.Clear();

            if (resp.Results == null || resp.Results.Length == 0)
            {
                rtbValidationResults.AppendText("No validation results returned.\n");
                return;
            }

            foreach (var r in resp.Results)
            {
                string indicator = r.Result?.ToLowerInvariant() switch
                {
                    "pass"    => "[PASS]",
                    "fail"    => "[FAIL]",
                    "warning" => "[WARN]",
                    _         => $"[{r.Result?.ToUpper() ?? "?"}]"
                };

                int start = rtbValidationResults.TextLength;
                rtbValidationResults.AppendText($"{indicator} {r.RuleName}: {r.Message}\n");

                // Colour the indicator
                Color indicatorColour = r.Result?.ToLowerInvariant() switch
                {
                    "pass"    => Color.Green,
                    "fail"    => Color.Red,
                    "warning" => Color.DarkOrange,
                    _         => Color.Gray
                };

                rtbValidationResults.Select(start, indicator.Length);
                rtbValidationResults.SelectionColor = indicatorColour;
                rtbValidationResults.SelectionLength = 0;
            }

            // Reset selection so subsequent appends use default colour
            rtbValidationResults.SelectionStart  = rtbValidationResults.TextLength;
            rtbValidationResults.SelectionLength  = 0;
            rtbValidationResults.SelectionColor   = rtbValidationResults.ForeColor;
        }

        // ── Helpers ──────────────────────────────────────────────────────────

        private bool EnsureConnected()
        {
            if (_apiClient != null) return true;
            MessageBox.Show("Please connect to the API first (Settings panel).", "Not Connected",
                MessageBoxButtons.OK, MessageBoxIcon.Information);
            return false;
        }

        private void UpdateConnectionStatus(string message)
        {
            if (InvokeRequired)
            {
                Invoke(new Action(() => UpdateConnectionStatus(message)));
                return;
            }
            statusLabel.Text = message;
        }
    }
}
