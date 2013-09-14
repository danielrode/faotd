// Author: Daniel Rode
// Made: February 20 2013
// Version: 1.2
// Last Updated: June 8 2013

// Windows launcher for faotd program

using System;
using System.IO;
using System.Diagnostics;
using System.Windows.Forms;
using Microsoft.Win32;


namespace OZ {
	class Vars {
			public static string @cacheFile;
		}
		
	class Starter {
		// Exit function
		static public void ErrorExit(string errorMessage) {
			MessageBox.Show(errorMessage,
			"Failed to launch FAOTD",
			MessageBoxButtons.OK,
			MessageBoxIcon.Error);
			Environment.Exit(1);
		}
		
		// Make cache file function
		static public void MakeCache() {
			// Get Python exe path
			string InstallPath = (string)Registry.GetValue(@"HKEY_LOCAL_MACHINE\SOFTWARE\Python\PythonCore\3.3\InstallPath", "", null);
			if (InstallPath == null) {
				ErrorExit("It doesn't look like Python 3.3 is installed.");
			}
			
			// Write path to cache file
			System.IO.File.WriteAllText(Vars.cacheFile, InstallPath);
		}
			
		// Main
		static void Main() {
			Vars.cacheFile = System.Environment.GetEnvironmentVariable("TEMP") + @"\py33path";
			
			// Check if cache file exists
			if (!File.Exists(Vars.cacheFile)) {
				MakeCache();
			}
			
			// Read cache
			string InstallPath = System.IO.File.ReadAllText(Vars.cacheFile);

			// Check that python exe exists
			if (!File.Exists(InstallPath + "pythonw.exe")) {
				ErrorExit("Could not find Python executable.");
			}

			//CD to program drectory
			// try {
				// Directory.SetCurrentDirectory("program");
			// }
			// catch {
				// ErrorExit("Directory 'program' does not exist.");
			// }

			// Check that faotd.py exists
			if (!File.Exists("faotd.py")) {
				ErrorExit("File 'faotd.py' does not exist.");
			}

			// Start FAOTDI
			Process proc = new Process();
			proc.StartInfo.FileName = InstallPath + "pythonw.exe";
			proc.StartInfo.Arguments = "faotd.py";
			//proc.StartInfo.WindowStyle = ProcessWindowStyle.Hidden; // prevents process from creating any windows
			proc.StartInfo.CreateNoWindow = true;
			proc.Start();
		}
	}
}
