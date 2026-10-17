//! Main egui application: translates English instructions to Python and
//! runs them through the Python worker process.

use eframe::egui;

use crate::protocol::{Message, Request, RequestId};
use crate::worker::{WorkerEvent, WorkerHandle};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum Kind {
    Translate,
    Execute,
}

#[derive(Debug, Clone, Copy)]
struct Pending {
    id: RequestId,
    kind: Kind,
}

#[derive(Debug)]
struct InputDialog {
    prompt: String,
    answer: String,
    focus: bool,
}

pub struct TtcApp {
    input: String,
    code: String,
    output: String,
    warnings: Vec<String>,
    status: String,
    pending: Option<Pending>,
    next_id: RequestId,
    dialog: Option<InputDialog>,
    worker: Option<WorkerHandle>,
    worker_error: Option<String>,
    engine_version: Option<String>,
    last_exec_time: Option<f64>,
}

impl TtcApp {
    pub fn new(_cc: &eframe::CreationContext<'_>) -> Self {
        let (worker, worker_error) = match WorkerHandle::spawn() {
            Ok(handle) => (Some(handle), None),
            Err(reason) => (None, Some(reason)),
        };
        let mut app = Self {
            input: "set x to 5".to_string(),
            code: String::new(),
            output: String::new(),
            warnings: Vec::new(),
            status: "Ready".to_string(),
            pending: None,
            next_id: 1,
            dialog: None,
            worker,
            worker_error,
            engine_version: None,
            last_exec_time: None,
        };
        app.ping_engine();
        app
    }

    /// Ask the worker for its version (request id 0, outside normal flow).
    fn ping_engine(&mut self) {
        if let Some(worker) = &self.worker {
            let _ = worker.send(&Request::Ping { id: 0 });
        }
    }

    fn next_request_id(&mut self) -> RequestId {
        let id = self.next_id;
        self.next_id += 1;
        id
    }

    fn send_request(&mut self, kind: Kind, request: Request) {
        let id = request.request_id().unwrap_or(0);
        match &self.worker {
            Some(worker) => match worker.send(&request) {
                Ok(()) => {
                    self.pending = Some(Pending { id, kind });
                    self.status = match kind {
                        Kind::Translate => "Translating…".to_string(),
                        Kind::Execute => "Running…".to_string(),
                    };
                }
                Err(reason) => self.status = format!("Cannot reach worker: {reason}"),
            },
            None => self.status = "Python worker is not running".to_string(),
        }
    }

    fn start_translate(&mut self) {
        if self.pending.is_some() {
            return;
        }
        let text = self.input.trim().to_string();
        if text.is_empty() {
            self.status = "Type an English instruction first".to_string();
            return;
        }
        let id = self.next_request_id();
        self.send_request(Kind::Translate, Request::Translate { id, text });
    }

    fn start_execute(&mut self) {
        if self.pending.is_some() {
            return;
        }
        let code = self.code.clone();
        if code.trim().is_empty() {
            self.status = "Nothing to run — translate something first".to_string();
            return;
        }
        let id = self.next_request_id();
        self.send_request(
            Kind::Execute,
            Request::Execute {
                id,
                code,
                timeout: None,
                allow_imports: None,
            },
        );
    }

    fn submit_answer(&mut self, answer: String) {
        self.dialog = None;
        match &self.worker {
            Some(worker) => {
                if let Err(reason) = worker.send(&Request::InputAnswer { answer }) {
                    self.status = format!("Cannot reach worker: {reason}");
                }
            }
            None => self.status = "Python worker is not running".to_string(),
        }
    }

    fn restart_worker(&mut self) {
        if self.worker.is_some() {
            return;
        }
        match WorkerHandle::spawn() {
            Ok(handle) => {
                self.worker = Some(handle);
                self.worker_error = None;
                self.engine_version = None;
                self.status = "Worker restarted".to_string();
                self.ping_engine();
            }
            Err(reason) => {
                self.worker_error = Some(reason.clone());
                self.status = format!("Worker failed: {reason}");
            }
        }
    }

    // ------------------------------------------------------------- events
    fn drain_worker_events(&mut self) {
        let mut events = Vec::new();
        if let Some(worker) = &self.worker {
            while let Ok(event) = worker.events().try_recv() {
                events.push(event);
            }
        }
        for event in events {
            self.handle_worker_event(event);
        }
    }

    fn handle_worker_event(&mut self, event: WorkerEvent) {
        match event {
            WorkerEvent::Message(message) => self.handle_message(message),
            WorkerEvent::Log(line) => {
                if !line.trim().is_empty() {
                    if !self.output.is_empty() {
                        self.output.push('\n');
                    }
                    self.output.push_str(&format!("[worker] {line}"));
                }
            }
            WorkerEvent::StdoutClosed => {
                let code = self.worker.as_mut().and_then(WorkerHandle::try_reap);
                self.worker = None;
                self.pending = None;
                self.dialog = None;
                self.engine_version = None;
                self.status = match code {
                    Some(code) => format!("Worker exited (code {code})"),
                    None => "Worker exited".to_string(),
                };
            }
        }
    }

    fn handle_message(&mut self, message: Message) {
        // Response to the startup version ping (id 0), outside normal flow.
        if message.id == Some(0) {
            self.engine_version = message.version;
            return;
        }

        if message.is_input_request() {
            self.dialog = Some(InputDialog {
                prompt: message.prompt_text(),
                answer: String::new(),
                focus: true,
            });
            return;
        }

        let Some(pending) = self.pending else {
            if let Some(error) = message.error {
                self.status = error;
            }
            return;
        };
        if message.id != Some(pending.id) {
            return;
        }
        self.pending = None;

        if message.ok == Some(false) {
            self.status = message
                .error
                .unwrap_or_else(|| "Request failed".to_string());
            return;
        }

        match pending.kind {
            Kind::Translate => self.finish_translate(&message),
            Kind::Execute => self.finish_execute(&message),
        }
    }

    fn finish_translate(&mut self, message: &Message) {
        match message.decode_translation() {
            Ok(payload) if payload.success => {
                self.code = payload.python_code;
                self.warnings = payload.warnings;
                let suffix = if self.warnings.is_empty() {
                    String::new()
                } else {
                    format!(
                        " ({} warning{})",
                        self.warnings.len(),
                        if self.warnings.len() == 1 { "" } else { "s" }
                    )
                };
                self.status = format!("Translated ✓{suffix}");
            }
            Ok(payload) => {
                self.status = if payload.error_message.trim().is_empty() {
                    "Translation failed".to_string()
                } else {
                    payload.error_message
                };
            }
            Err(reason) => self.status = reason,
        }
    }

    fn finish_execute(&mut self, message: &Message) {
        match message.decode_execution() {
            Ok(payload) => {
                let mut text = payload.stdout.clone();
                if !payload.success {
                    let error = if payload.error_message.trim().is_empty() {
                        payload.stderr.clone()
                    } else {
                        payload.error_message.clone()
                    };
                    if !text.is_empty() && !text.ends_with('\n') {
                        text.push('\n');
                    }
                    text.push_str(&error);
                }
                self.output = text;
                self.last_exec_time = Some(payload.execution_time);
                self.status = if payload.success {
                    format!("Executed in {:.2}s", payload.execution_time)
                } else {
                    format!("Execution failed ({:.2}s)", payload.execution_time)
                };
            }
            Err(reason) => self.status = reason,
        }
    }

    // --------------------------------------------------------------- views
    fn header_panel(&mut self, ui: &mut egui::Ui) {
        let mut restart = false;
        egui::Panel::top("header").show(ui, |ui| {
            ui.add_space(6.0);
            ui.horizontal(|ui| {
                ui.heading("English → Python Translator");
                ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                    if self.worker.is_some() {
                        let version = self
                            .engine_version
                            .as_deref()
                            .map(|v| format!(" · engine {v}"))
                            .unwrap_or_default();
                        ui.colored_label(
                            egui::Color32::from_rgb(90, 200, 120),
                            format!("● worker online{version}"),
                        );
                    } else {
                        let reason = self
                            .worker_error
                            .clone()
                            .unwrap_or_else(|| "not running".to_string());
                        ui.colored_label(
                            egui::Color32::from_rgb(230, 100, 100),
                            format!("● offline — {reason}"),
                        );
                        if ui
                            .button("Retry")
                            .on_hover_text("Try starting the Python worker again")
                            .clicked()
                        {
                            restart = true;
                        }
                    }
                });
            });
            ui.add_space(4.0);
        });
        if restart {
            self.restart_worker();
        }
    }

    fn status_panel(&self, ui: &mut egui::Ui) {
        egui::Panel::bottom("status").show(ui, |ui| {
            ui.horizontal(|ui| {
                if self.pending.is_some() {
                    ui.spinner();
                }
                ui.label(&self.status);
                ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                    if let Some(seconds) = self.last_exec_time {
                        ui.weak(format!("last run {seconds:.2}s"));
                    }
                    ui.weak("ttc-gui");
                });
            });
        });
    }

    fn central_panel(&mut self, ui: &mut egui::Ui) {
        egui::CentralPanel::default().show(ui, |ui| {
            ui.add_space(8.0);

            ui.label(egui::RichText::new("English instruction").strong());
            ui.add(
                egui::TextEdit::multiline(&mut self.input)
                    .desired_rows(3)
                    .desired_width(f32::INFINITY)
                    .hint_text("e.g. set x to 5"),
            );

            let can_interact = self.pending.is_none();
            ui.horizontal(|ui| {
                let translate = ui.add_enabled(
                    can_interact,
                    egui::Button::new("Translate").shortcut_text("Ctrl+Enter"),
                );
                if translate.clicked() {
                    self.start_translate();
                }
                if ui.button("Clear input").clicked() {
                    self.input.clear();
                }
                if ui
                    .button("Example")
                    .on_hover_text("Load the demo instruction")
                    .clicked()
                {
                    self.input = "set x to 5".to_string();
                }
            });

            ui.add_space(10.0);
            ui.separator();

            ui.horizontal(|ui| {
                ui.label(egui::RichText::new("Generated Python").strong());
                let has_code = !self.code.trim().is_empty();
                let run = ui.add_enabled(can_interact, egui::Button::new("▶ Run"));
                if has_code && run.clicked() {
                    self.start_execute();
                }
                if ui
                    .button("Copy")
                    .on_hover_text("Copy the generated code")
                    .clicked()
                    && has_code
                {
                    ui.ctx().copy_text(self.code.clone());
                }
                if self.pending.is_some() {
                    ui.spinner();
                }
            });
            ui.add(
                egui::TextEdit::multiline(&mut self.code)
                    .code_editor()
                    .desired_rows(7)
                    .desired_width(f32::INFINITY)
                    .hint_text("generated code appears here (editable before running)"),
            );

            for warning in &self.warnings {
                ui.colored_label(
                    egui::Color32::from_rgb(230, 180, 60),
                    format!("⚠ {warning}"),
                );
            }

            ui.add_space(8.0);
            ui.separator();

            ui.horizontal(|ui| {
                ui.label(egui::RichText::new("Output").strong());
                if ui.button("Clear").clicked() {
                    self.output.clear();
                }
            });
            egui::ScrollArea::vertical()
                .id_salt("output_scroll")
                .auto_shrink([false, false])
                .max_height(220.0)
                .show(ui, |ui| {
                    ui.add(
                        egui::TextEdit::multiline(&mut self.output)
                            .code_editor()
                            .interactive(false)
                            .desired_rows(9)
                            .desired_width(f32::INFINITY),
                    );
                });
        });
    }

    fn input_dialog(&mut self, ui: &mut egui::Ui) {
        let ctx = ui.ctx().clone();
        let mut submit: Option<String> = None;
        if let Some(dialog) = &mut self.dialog {
            let mut open = true;
            egui::Window::new("Program input")
                .collapsible(false)
                .resizable(false)
                .anchor(egui::Align2::CENTER_CENTER, egui::Vec2::ZERO)
                .open(&mut open)
                .show(&ctx, |ui| {
                    ui.label("The program asks:");
                    ui.label(egui::RichText::new(&dialog.prompt).monospace().strong());
                    ui.add_space(4.0);
                    let answer = ui.add(
                        egui::TextEdit::singleline(&mut dialog.answer)
                            .desired_width(320.0)
                            .hint_text("type your answer"),
                    );
                    if dialog.focus {
                        answer.request_focus();
                        dialog.focus = false;
                    }
                    let enter = ui.input(|i| i.key_pressed(egui::Key::Enter));
                    ui.add_space(6.0);
                    ui.horizontal(|ui| {
                        if ui
                            .add_enabled(!enter || answer.has_focus(), egui::Button::new("Submit"))
                            .clicked()
                            || (enter && answer.has_focus())
                        {
                            submit = Some(dialog.answer.clone());
                        }
                        if ui
                            .button("Skip")
                            .on_hover_text("Answer with an empty string")
                            .clicked()
                        {
                            submit = Some(String::new());
                        }
                    });
                });
            if !open {
                // Window closed via X: answer with empty string so the program
                // does not hang forever waiting for input.
                submit = Some(String::new());
            }
        }
        if let Some(answer) = submit {
            self.submit_answer(answer);
        }
    }
}

impl eframe::App for TtcApp {
    fn logic(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        self.drain_worker_events();

        // Ctrl+Enter translates from anywhere.
        let ctrl_enter = ctx.input(|i| i.key_pressed(egui::Key::Enter) && i.modifiers.command);
        if ctrl_enter && self.pending.is_none() {
            self.start_translate();
        }

        // Keep polling the worker while a request is in flight.
        if self.pending.is_some() || self.dialog.is_some() {
            ctx.request_repaint();
        }
    }

    fn ui(&mut self, ui: &mut egui::Ui, _frame: &mut eframe::Frame) {
        self.header_panel(ui);
        self.status_panel(ui);
        self.central_panel(ui);
        self.input_dialog(ui);
    }
}
