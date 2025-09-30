// Prevents additional console window on Windows in release,
//  DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]


// In src-tauri/src/main.rs
mod model; // Import the model module
// In src-tauri/src/main.rs
//... (imports and struct definitions as before)
use tauri::{Manager, api::dialog::FileDialogBuilder, api::fs};
use std::fs::File;
use std::io::Write;
// In src-tauri/src/main.rs
//... (imports and struct definitions as befor


#[tauri::command]
async fn save_kinetic_model(model: KineticModel, window: tauri::Window) -> Result<(), String> {
    // Serialize the model to a JSON string first.
    let json_string = serde_json::to_string_pretty(&model)
      .map_err(|e| format!("Failed to serialize model: {}", e))?;

    // Use the asynchronous file dialog builder.
    let file_path = FileDialogBuilder::new()
      .set_parent(&window) // Attach dialog to the main window
      .add_filter("JSON", &["json"])
      .set_file_name("untitled_model.json")
      .save_file()
      .await;

    if let Some(path) = file_path {
        // The path is a PathBuf. We can now write to it.
        // Using std::fs for blocking I/O is fine within a tauri::command,
        // as Tauri runs them on a separate thread pool.
        let mut file = File::create(&path)
          .map_err(|e| format!("Failed to create file: {}", e))?;
        
        file.write_all(json_string.as_bytes())
          .map_err(|e| format!("Failed to write to file: {}", e))?;
        
        Ok(())
    } else {
        // User cancelled the dialog, which is not an error.
        Ok(())
    }
}
fn main() {
    tauri::Builder::default()
      .invoke_handler(tauri::generate_handler![save_kinetic_model])
      .run(tauri::generate_context!())
      .expect("error while running tauri application");
}