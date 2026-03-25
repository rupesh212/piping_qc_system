using Autodesk.Navisworks.Api.Plugins;
using System.Windows.Forms;

namespace PipingQCPlugin
{
    [Plugin("PipingQCPlugin", "ACME", DisplayName = "Piping QC/QC System")]
    [AddInPlugin(AddInLocation.AddIn)]
    public class PipingQCAddIn : AddInPlugin
    {
        public override int Execute(params string[] parameters)
        {
            var form = new MainForm();
            form.ShowDialog();
            return 0;
        }
    }
}
