**Changelog – RDR2 LML Conflict Checker**

**Version 3.0**

**New Features**

* Added a built-in Help system to guide users through all tool features

  * Accessible via a Help tab or tooltip popup
  * Explains scanning, conflict levels, exclusions, backups, and more

* Implemented a version checker

  * On startup, the tool checks for updates from NexusMods or RDR2Mods
  * Notifies the user if a newer version is available and provides a download link

**Improvements**

* Updated the interface with a modern dark theme inspired by Windows 11 design
* Refactored the entire application into modular, class-based architecture using PyQt5
* Improved performance and memory efficiency during mod conflict scans

**Fixes**

* Resolved UI freezing during large scans by offloading work to background threads
* Improved handling of large or binary files in the comparison window

---

Let me know the version/date if you’d like this finalized.


# RDR2 Mod Conflict Checker — Changelog (July 21, 2025)

### New Features

* **Backup System Enhancements**
  • Added the ability to name backups during creation
  • Implemented a backup selection dialog for restoring backups
  • Included metadata in backups such as creation date and file count
  • Added an option to create an automatic backup before restoring

* **Mod File Comparison Tool**
  • Added side-by-side comparison of mod files with left and right panels showing differences
  • Enabled editing of files directly within the comparison tool with save functionality
  • Improved search highlight visibility in the compare window for easier navigation
  • Updated compare window colors to a plain white background with yellow highlights to reduce lag and enhance readability

* **Ko-fi Support Button**
  • Added a “Support me on Ko-fi” button fixed at the bottom-right corner
  • Direct link to the Ko-fi page for users who want to support development
  • Button styling adapts automatically to light and dark application themes

* **GXT2 File Warning**
  • Added a user warning that GXT2 files typically do not cause conflicts and may produce false positives
  • Users are advised to only modify GXT2 files if they understand the risks

### Build Improvements

* **Executable Creation**
  • Optimized PyInstaller build for a cleaner, more reliable executable
  • Added application icon properly embedded in the executable
  • Reduced false positive detections by antivirus software
  • Improved resource handling within the packaged app

### Technical Improvements

* **Resource Management**
  • Improved handling of application resources when running as an executable
  • Fixed path resolution issues for icons and other resource files
  • Ensured resources load correctly regardless of execution context

### Bug Fixes

* Fixed issues with the backup restoration process
* Corrected resource path handling for the application icon
* Resolved UI layout problems in the backup selection dialog
* Fixed bug where selecting "All file types" did not clear the search bar properly
* Resolved UI cutoff issues with file type toggles, ensuring all toggles fit within a visible area

### Other Changes

* Optimized code for better performance and reduced UI lag
* Enhanced error handling throughout the app
* Improved tooltips for clearer user guidance

---

Thank you for supporting RDR2 Mod Manager! If you find this tool useful, please consider supporting development via the Ko-fi button.
