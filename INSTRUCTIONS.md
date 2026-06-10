# PurpleBerrie Development Protocol

This file outlines the mandatory protocols for maintaining the PurpleBerrie repository. As an AI agent assistant, I MUST adhere to these protocols for all future interactions.

## 1. Versioning Protocol
- Every significant change, new feature, or enhancement MUST increment the version number (e.g., V6 -> V7).
- The version in the `README.md` and the internal application title/header MUST be updated accordingly on every commit.

## 2. README Maintenance Protocol
- The `README.md` MUST be updated on **every single change**.
- The latest version section in `README.md` should ONLY list the changes specific to that version (do not duplicate the features of previous versions).
- Ensure the version history (V6, V5, V4, etc.) is preserved as an archive in the documentation.

## 3. Build & Compilation Workflow
Before every compilation, the following steps MUST be executed in order:
1.  **Dependency Check:** Check `requirements.txt` and ensure all dependencies are installed using `pip install -r requirements.txt`.
2.  **Clean Workspace:** 
    - Stop any running instances of the application.
    - Remove `dist/` and `build/` directories.
3.  **Compilation:** Run `pyinstaller` with `--clean` and all necessary flags (`--onefile`, `--windowed`, `--icon=PurpleBerrie.ico`, `--add-data "PurpleBerrie.ico;."`, `--hidden-import pynput`).
4.  **Executable Deployment:** Move the newly compiled executable from `dist/` to the project root directory and rename it to `PurpleBerrie.exe`.
5.  **Repository Sync:** Commit the updated code, the updated `README.md`, and the newly compiled `.exe` to the repository.

## 4. Archival Protocol
- The `Versions/` folder is reserved for archiving previous releases.
- While I only have the latest version (V6) in the repository currently, any future major changes should archive the previous executable here before pushing the new one.
