namespace PipingQCPlugin
{
    partial class MainForm
    {
        private System.ComponentModel.IContainer components = null;

        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
                components.Dispose();
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        private void InitializeComponent()
        {
            this.tabControl            = new System.Windows.Forms.TabControl();
            this.tabDashboard          = new System.Windows.Forms.TabPage();
            this.tabISO                = new System.Windows.Forms.TabPage();
            this.tabValidate           = new System.Windows.Forms.TabPage();

            // Settings panel controls
            this.grpSettings           = new System.Windows.Forms.GroupBox();
            this.lblApiUrl             = new System.Windows.Forms.Label();
            this.txtApiUrl             = new System.Windows.Forms.TextBox();
            this.lblUsername           = new System.Windows.Forms.Label();
            this.txtUsername           = new System.Windows.Forms.TextBox();
            this.lblPassword           = new System.Windows.Forms.Label();
            this.txtPassword           = new System.Windows.Forms.TextBox();
            this.btnConnect            = new System.Windows.Forms.Button();

            // Dashboard tab controls
            this.btnRefreshDashboard   = new System.Windows.Forms.Button();
            this.lblTotalIsos          = new System.Windows.Forms.Label();
            this.lblTotalLines         = new System.Windows.Forms.Label();
            this.lblTotalValidations   = new System.Windows.Forms.Label();
            this.lblTotalErrors        = new System.Windows.Forms.Label();
            this.lblPassRate           = new System.Windows.Forms.Label();

            // ISO Drawings tab controls
            this.dgvISOList            = new System.Windows.Forms.DataGridView();
            this.colFileName           = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.colLineNumber         = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.colPipeSize           = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.colSpec               = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.colStatus             = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.btnLoadISOs           = new System.Windows.Forms.Button();
            this.btnPrevPage           = new System.Windows.Forms.Button();
            this.btnNextPage           = new System.Windows.Forms.Button();
            this.lblPageInfo           = new System.Windows.Forms.Label();

            // Validate tab controls
            this.lblIsoId              = new System.Windows.Forms.Label();
            this.txtIsoId              = new System.Windows.Forms.TextBox();
            this.btnValidate           = new System.Windows.Forms.Button();
            this.rtbValidationResults  = new System.Windows.Forms.RichTextBox();

            // Status strip
            this.statusStrip           = new System.Windows.Forms.StatusStrip();
            this.statusLabel           = new System.Windows.Forms.ToolStripStatusLabel();

            // ── Suspend layout ────────────────────────────────────────────────
            this.SuspendLayout();
            this.tabControl.SuspendLayout();
            this.tabDashboard.SuspendLayout();
            this.tabISO.SuspendLayout();
            this.tabValidate.SuspendLayout();
            this.grpSettings.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dgvISOList)).BeginInit();

            // ── Form ──────────────────────────────────────────────────────────
            this.Text            = "Piping QC System";
            this.Size            = new System.Drawing.Size(900, 680);
            this.MinimumSize     = new System.Drawing.Size(800, 600);
            this.StartPosition   = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Font            = new System.Drawing.Font("Segoe UI", 9F);

            // ── Settings GroupBox ─────────────────────────────────────────────
            this.grpSettings.Text     = "Connection Settings";
            this.grpSettings.Location = new System.Drawing.Point(12, 12);
            this.grpSettings.Size     = new System.Drawing.Size(860, 80);
            this.grpSettings.Anchor   = System.Windows.Forms.AnchorStyles.Top
                                      | System.Windows.Forms.AnchorStyles.Left
                                      | System.Windows.Forms.AnchorStyles.Right;

            this.lblApiUrl.Text     = "API URL:";
            this.lblApiUrl.Location = new System.Drawing.Point(10, 28);
            this.lblApiUrl.AutoSize = true;

            this.txtApiUrl.Text     = "http://localhost:8000";
            this.txtApiUrl.Location = new System.Drawing.Point(68, 25);
            this.txtApiUrl.Size     = new System.Drawing.Size(240, 23);

            this.lblUsername.Text     = "Username:";
            this.lblUsername.Location = new System.Drawing.Point(320, 28);
            this.lblUsername.AutoSize = true;

            this.txtUsername.Location = new System.Drawing.Point(390, 25);
            this.txtUsername.Size     = new System.Drawing.Size(130, 23);

            this.lblPassword.Text     = "Password:";
            this.lblPassword.Location = new System.Drawing.Point(530, 28);
            this.lblPassword.AutoSize = true;

            this.txtPassword.Location     = new System.Drawing.Point(598, 25);
            this.txtPassword.Size         = new System.Drawing.Size(130, 23);
            this.txtPassword.PasswordChar = '*';

            this.btnConnect.Text     = "Connect";
            this.btnConnect.Location = new System.Drawing.Point(740, 23);
            this.btnConnect.Size     = new System.Drawing.Size(100, 27);
            this.btnConnect.Click   += new System.EventHandler(this.btnConnect_Click);

            this.grpSettings.Controls.AddRange(new System.Windows.Forms.Control[] {
                this.lblApiUrl, this.txtApiUrl,
                this.lblUsername, this.txtUsername,
                this.lblPassword, this.txtPassword,
                this.btnConnect
            });

            // ── TabControl ────────────────────────────────────────────────────
            this.tabControl.Location = new System.Drawing.Point(12, 100);
            this.tabControl.Size     = new System.Drawing.Size(860, 520);
            this.tabControl.Anchor   = System.Windows.Forms.AnchorStyles.Top
                                     | System.Windows.Forms.AnchorStyles.Bottom
                                     | System.Windows.Forms.AnchorStyles.Left
                                     | System.Windows.Forms.AnchorStyles.Right;
            this.tabControl.Enabled  = false;
            this.tabControl.TabPages.AddRange(new System.Windows.Forms.TabPage[] {
                this.tabDashboard, this.tabISO, this.tabValidate
            });

            // ── Dashboard Tab ─────────────────────────────────────────────────
            this.tabDashboard.Text    = "Dashboard";
            this.tabDashboard.Padding = new System.Windows.Forms.Padding(10);

            this.btnRefreshDashboard.Text     = "Refresh";
            this.btnRefreshDashboard.Location = new System.Drawing.Point(16, 16);
            this.btnRefreshDashboard.Size     = new System.Drawing.Size(100, 30);
            this.btnRefreshDashboard.Click   += new System.EventHandler(this.btnRefreshDashboard_Click);

            this.lblTotalIsos.Text      = "Total ISOs: —";
            this.lblTotalIsos.Location  = new System.Drawing.Point(16, 65);
            this.lblTotalIsos.AutoSize  = true;
            this.lblTotalIsos.Font      = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Regular);

            this.lblTotalLines.Text     = "Total Lines: —";
            this.lblTotalLines.Location = new System.Drawing.Point(16, 100);
            this.lblTotalLines.AutoSize = true;
            this.lblTotalLines.Font     = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Regular);

            this.lblTotalValidations.Text     = "Total Validations: —";
            this.lblTotalValidations.Location = new System.Drawing.Point(16, 135);
            this.lblTotalValidations.AutoSize = true;
            this.lblTotalValidations.Font     = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Regular);

            this.lblTotalErrors.Text     = "Total Errors: —";
            this.lblTotalErrors.Location = new System.Drawing.Point(16, 170);
            this.lblTotalErrors.AutoSize = true;
            this.lblTotalErrors.Font     = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Regular);

            this.lblPassRate.Text     = "Pass Rate: —";
            this.lblPassRate.Location = new System.Drawing.Point(16, 205);
            this.lblPassRate.AutoSize = true;
            this.lblPassRate.Font     = new System.Drawing.Font("Segoe UI", 14F, System.Drawing.FontStyle.Bold);

            this.tabDashboard.Controls.AddRange(new System.Windows.Forms.Control[] {
                this.btnRefreshDashboard,
                this.lblTotalIsos,
                this.lblTotalLines,
                this.lblTotalValidations,
                this.lblTotalErrors,
                this.lblPassRate
            });

            // ── ISO Drawings Tab ──────────────────────────────────────────────
            this.tabISO.Text    = "ISO Drawings";
            this.tabISO.Padding = new System.Windows.Forms.Padding(10);

            // DataGridView columns
            this.colFileName.HeaderText = "File Name";
            this.colFileName.Width      = 200;
            this.colFileName.ReadOnly   = true;

            this.colLineNumber.HeaderText = "Line Number";
            this.colLineNumber.Width      = 130;
            this.colLineNumber.ReadOnly   = true;

            this.colPipeSize.HeaderText = "Pipe Size";
            this.colPipeSize.Width      = 100;
            this.colPipeSize.ReadOnly   = true;

            this.colSpec.HeaderText = "Spec";
            this.colSpec.Width      = 100;
            this.colSpec.ReadOnly   = true;

            this.colStatus.HeaderText = "Status";
            this.colStatus.Width      = 100;
            this.colStatus.ReadOnly   = true;

            this.dgvISOList.Location              = new System.Drawing.Point(10, 50);
            this.dgvISOList.Size                  = new System.Drawing.Size(820, 370);
            this.dgvISOList.Anchor                = System.Windows.Forms.AnchorStyles.Top
                                                  | System.Windows.Forms.AnchorStyles.Bottom
                                                  | System.Windows.Forms.AnchorStyles.Left
                                                  | System.Windows.Forms.AnchorStyles.Right;
            this.dgvISOList.AutoSizeColumnsMode   = System.Windows.Forms.DataGridViewAutoSizeColumnsMode.Fill;
            this.dgvISOList.AllowUserToAddRows    = false;
            this.dgvISOList.AllowUserToDeleteRows = false;
            this.dgvISOList.ReadOnly              = true;
            this.dgvISOList.SelectionMode         = System.Windows.Forms.DataGridViewSelectionMode.FullRowSelect;
            this.dgvISOList.RowHeadersVisible     = false;
            this.dgvISOList.BackgroundColor       = System.Drawing.SystemColors.Window;
            this.dgvISOList.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
                this.colFileName, this.colLineNumber, this.colPipeSize, this.colSpec, this.colStatus
            });

            this.btnLoadISOs.Text     = "Load ISOs";
            this.btnLoadISOs.Location = new System.Drawing.Point(10, 14);
            this.btnLoadISOs.Size     = new System.Drawing.Size(100, 30);
            this.btnLoadISOs.Click   += new System.EventHandler(this.btnLoadISOs_Click);

            this.btnPrevPage.Text     = "< Previous";
            this.btnPrevPage.Location = new System.Drawing.Point(10, 430);
            this.btnPrevPage.Size     = new System.Drawing.Size(100, 30);
            this.btnPrevPage.Enabled  = false;
            this.btnPrevPage.Anchor   = System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left;
            this.btnPrevPage.Click   += new System.EventHandler(this.btnPrevPage_Click);

            this.lblPageInfo.Text      = "Page 1 of 1";
            this.lblPageInfo.Location  = new System.Drawing.Point(120, 436);
            this.lblPageInfo.AutoSize  = true;
            this.lblPageInfo.Anchor    = System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left;

            this.btnNextPage.Text     = "Next >";
            this.btnNextPage.Location = new System.Drawing.Point(300, 430);
            this.btnNextPage.Size     = new System.Drawing.Size(100, 30);
            this.btnNextPage.Enabled  = false;
            this.btnNextPage.Anchor   = System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left;
            this.btnNextPage.Click   += new System.EventHandler(this.btnNextPage_Click);

            this.tabISO.Controls.AddRange(new System.Windows.Forms.Control[] {
                this.btnLoadISOs,
                this.dgvISOList,
                this.btnPrevPage,
                this.lblPageInfo,
                this.btnNextPage
            });

            // ── Validate Tab ──────────────────────────────────────────────────
            this.tabValidate.Text    = "Validate";
            this.tabValidate.Padding = new System.Windows.Forms.Padding(10);

            this.lblIsoId.Text     = "ISO ID:";
            this.lblIsoId.Location = new System.Drawing.Point(10, 20);
            this.lblIsoId.AutoSize = true;

            this.txtIsoId.Location    = new System.Drawing.Point(70, 17);
            this.txtIsoId.Size        = new System.Drawing.Size(380, 23);
            this.txtIsoId.PlaceholderText = "Enter ISO UUID…";

            this.btnValidate.Text     = "Validate";
            this.btnValidate.Location = new System.Drawing.Point(462, 15);
            this.btnValidate.Size     = new System.Drawing.Size(100, 27);
            this.btnValidate.Click   += new System.EventHandler(this.btnValidate_Click);

            this.rtbValidationResults.Location  = new System.Drawing.Point(10, 55);
            this.rtbValidationResults.Size      = new System.Drawing.Size(820, 400);
            this.rtbValidationResults.Anchor    = System.Windows.Forms.AnchorStyles.Top
                                                | System.Windows.Forms.AnchorStyles.Bottom
                                                | System.Windows.Forms.AnchorStyles.Left
                                                | System.Windows.Forms.AnchorStyles.Right;
            this.rtbValidationResults.ReadOnly  = true;
            this.rtbValidationResults.BackColor = System.Drawing.Color.White;
            this.rtbValidationResults.Font      = new System.Drawing.Font("Consolas", 9.5F);
            this.rtbValidationResults.ScrollBars = System.Windows.Forms.RichTextBoxScrollBars.Vertical;

            this.tabValidate.Controls.AddRange(new System.Windows.Forms.Control[] {
                this.lblIsoId,
                this.txtIsoId,
                this.btnValidate,
                this.rtbValidationResults
            });

            // ── Status Strip ──────────────────────────────────────────────────
            this.statusLabel.Spring = true;
            this.statusLabel.TextAlign = System.Drawing.ContentAlignment.MiddleLeft;
            this.statusLabel.Text   = "Not connected";

            this.statusStrip.Items.Add(this.statusLabel);
            this.statusStrip.SizingGrip = false;

            // ── Add top-level controls to Form ────────────────────────────────
            this.Controls.AddRange(new System.Windows.Forms.Control[] {
                this.grpSettings,
                this.tabControl,
                this.statusStrip
            });

            // ── Resume layout ─────────────────────────────────────────────────
            ((System.ComponentModel.ISupportInitialize)(this.dgvISOList)).EndInit();
            this.grpSettings.ResumeLayout(false);
            this.grpSettings.PerformLayout();
            this.tabDashboard.ResumeLayout(false);
            this.tabDashboard.PerformLayout();
            this.tabISO.ResumeLayout(false);
            this.tabValidate.ResumeLayout(false);
            this.tabValidate.PerformLayout();
            this.tabControl.ResumeLayout(false);
            this.ResumeLayout(false);
            this.PerformLayout();
        }

        #endregion

        // ── Control declarations ───────────────────────────────────────────

        private System.Windows.Forms.TabControl tabControl;
        private System.Windows.Forms.TabPage tabDashboard;
        private System.Windows.Forms.TabPage tabISO;
        private System.Windows.Forms.TabPage tabValidate;

        private System.Windows.Forms.GroupBox grpSettings;
        private System.Windows.Forms.Label lblApiUrl;
        private System.Windows.Forms.TextBox txtApiUrl;
        private System.Windows.Forms.Label lblUsername;
        private System.Windows.Forms.TextBox txtUsername;
        private System.Windows.Forms.Label lblPassword;
        private System.Windows.Forms.TextBox txtPassword;
        private System.Windows.Forms.Button btnConnect;

        private System.Windows.Forms.Button btnRefreshDashboard;
        private System.Windows.Forms.Label lblTotalIsos;
        private System.Windows.Forms.Label lblTotalLines;
        private System.Windows.Forms.Label lblTotalValidations;
        private System.Windows.Forms.Label lblTotalErrors;
        private System.Windows.Forms.Label lblPassRate;

        private System.Windows.Forms.DataGridView dgvISOList;
        private System.Windows.Forms.DataGridViewTextBoxColumn colFileName;
        private System.Windows.Forms.DataGridViewTextBoxColumn colLineNumber;
        private System.Windows.Forms.DataGridViewTextBoxColumn colPipeSize;
        private System.Windows.Forms.DataGridViewTextBoxColumn colSpec;
        private System.Windows.Forms.DataGridViewTextBoxColumn colStatus;
        private System.Windows.Forms.Button btnLoadISOs;
        private System.Windows.Forms.Button btnPrevPage;
        private System.Windows.Forms.Button btnNextPage;
        private System.Windows.Forms.Label lblPageInfo;

        private System.Windows.Forms.Label lblIsoId;
        private System.Windows.Forms.TextBox txtIsoId;
        private System.Windows.Forms.Button btnValidate;
        private System.Windows.Forms.RichTextBox rtbValidationResults;

        private System.Windows.Forms.StatusStrip statusStrip;
        private System.Windows.Forms.ToolStripStatusLabel statusLabel;
    }
}
