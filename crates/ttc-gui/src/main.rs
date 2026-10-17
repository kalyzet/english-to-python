//! ttc-gui: native GUI shell for the English-to-Python translator.
//!
//! The GUI only renders state and manages a Python worker process
//! (`python -m ttc.worker`); all translation/execution logic lives in Python.

#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod app;
mod protocol;
mod worker;

use eframe::egui;

fn main() -> eframe::Result {
    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default()
            .with_inner_size([920.0, 720.0])
            .with_min_inner_size([640.0, 520.0])
            .with_title("Text to Code — English to Python Translator"),
        ..Default::default()
    };
    eframe::run_native(
        "ttc-gui",
        options,
        Box::new(|cc| Ok(Box::new(app::TtcApp::new(cc)))),
    )
}
