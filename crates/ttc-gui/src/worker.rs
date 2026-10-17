//! Manages the Python worker subprocess (`python -m ttc.worker`).
//!
//! - a writer thread owns the child's stdin and receives JSON lines over an
//!   mpsc channel from the GUI thread,
//! - a reader thread parses stdout JSON lines into [`WorkerEvent`]s,
//! - a drain thread forwards stderr lines as log events,
//! - the GUI drains events each frame.

use std::env;
use std::io::{BufRead, BufReader, Write};
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Stdio};
use std::sync::mpsc::{self, Receiver, Sender};
use std::thread;
use std::time::{Duration, Instant};

use crate::protocol::{Message, Request};

/// Events flowing from the worker threads to the GUI thread.
#[derive(Debug)]
pub enum WorkerEvent {
    /// A parsed JSON line (responses and `input_request`s alike).
    Message(Message),
    /// Worker stderr line (logging — stdout is the JSON stream only).
    Log(String),
    /// The worker's stdout reached EOF; the process is finishing/exited.
    StdoutClosed,
}

pub struct WorkerHandle {
    child: Child,
    tx: Option<Sender<String>>,
    events: Receiver<WorkerEvent>,
}

impl WorkerHandle {
    pub fn spawn() -> Result<Self, String> {
        let python = find_python()?;
        let engine_root = find_engine_root();

        let mut command = Command::new(&python);
        command
            .arg("-u")
            .arg("-m")
            .arg("ttc.worker")
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .env("PYTHONUNBUFFERED", "1");
        if let Some(root) = &engine_root {
            command.env("PYTHONPATH", build_python_path(root));
        }

        let mut child = command
            .spawn()
            .map_err(|e| format!("failed to spawn {}: {e}", python.display()))?;

        let stdin = child.stdin.take().ok_or("worker stdin unavailable")?;
        let stdout = child.stdout.take().ok_or("worker stdout unavailable")?;
        let stderr = child.stderr.take().ok_or("worker stderr unavailable")?;

        let (event_tx, event_rx) = mpsc::channel::<WorkerEvent>();
        let (line_tx, line_rx) = mpsc::channel::<String>();

        spawn_writer(stdin, line_rx);
        spawn_stdout_reader(stdout, event_tx.clone());
        spawn_stderr_drain(stderr, event_tx);

        Ok(Self {
            child,
            tx: Some(line_tx),
            events: event_rx,
        })
    }

    /// Queue a request line for the worker (never blocks the UI thread).
    pub fn send(&self, request: &Request) -> Result<(), String> {
        let line = request.to_json();
        match &self.tx {
            Some(tx) => tx
                .send(line)
                .map_err(|_| "worker is not accepting requests".to_string()),
            None => Err("worker is shut down".to_string()),
        }
    }

    pub fn events(&self) -> &Receiver<WorkerEvent> {
        &self.events
    }

    /// Non-blocking exit check.
    pub fn try_reap(&mut self) -> Option<i32> {
        match self.child.try_wait() {
            Ok(Some(status)) => status.code(),
            _ => None,
        }
    }
}

impl Drop for WorkerHandle {
    fn drop(&mut self) {
        // Best-effort graceful shutdown, then make sure no orphan survives.
        if let Some(tx) = self.tx.take() {
            let _ = tx.send(Request::Shutdown { id: 0 }.to_json());
        }
        let deadline = Instant::now() + Duration::from_millis(400);
        loop {
            if matches!(self.child.try_wait(), Ok(Some(_))) {
                return;
            }
            if Instant::now() >= deadline {
                break;
            }
            thread::sleep(Duration::from_millis(20));
        }
        let _ = self.child.kill();
        let _ = self.child.wait();
    }
}

fn spawn_writer(mut stdin: std::process::ChildStdin, lines: Receiver<String>) {
    thread::Builder::new()
        .name("worker-writer".into())
        .spawn(move || {
            for line in lines {
                if writeln!(stdin, "{line}").is_err() {
                    break;
                }
                if stdin.flush().is_err() {
                    break;
                }
            }
        })
        .expect("spawn worker writer thread");
}

fn spawn_stdout_reader(stdout: std::process::ChildStdout, events: Sender<WorkerEvent>) {
    thread::Builder::new()
        .name("worker-reader".into())
        .spawn(move || {
            let reader = BufReader::new(stdout);
            for line in reader.lines() {
                match line {
                    Ok(line) => {
                        let trimmed = line.trim();
                        if trimmed.is_empty() {
                            continue;
                        }
                        match serde_json::from_str::<Message>(trimmed) {
                            Ok(message) => {
                                if events.send(WorkerEvent::Message(message)).is_err() {
                                    return;
                                }
                            }
                            Err(_) => {
                                if events.send(WorkerEvent::Log(line)).is_err() {
                                    return;
                                }
                            }
                        }
                    }
                    Err(_) => break,
                }
            }
            let _ = events.send(WorkerEvent::StdoutClosed);
        })
        .expect("spawn worker reader thread");
}

fn spawn_stderr_drain(stderr: std::process::ChildStderr, events: Sender<WorkerEvent>) {
    thread::Builder::new()
        .name("worker-stderr".into())
        .spawn(move || {
            let reader = BufReader::new(stderr);
            for line in reader.lines().map_while(Result::ok) {
                if events.send(WorkerEvent::Log(line)).is_err() {
                    return;
                }
            }
        })
        .expect("spawn worker stderr thread");
}

/// Locate a Python 3 interpreter: `$TTC_PYTHON`, then `python3`, then `python`.
pub fn find_python() -> Result<PathBuf, String> {
    if let Ok(path) = env::var("TTC_PYTHON") {
        if !path.trim().is_empty() {
            return Ok(PathBuf::from(path));
        }
    }
    for candidate in ["python3", "python"] {
        if python_responds(candidate) {
            return Ok(PathBuf::from(candidate));
        }
    }
    Err("No Python 3 interpreter found; set the TTC_PYTHON environment variable".to_string())
}

fn python_responds(candidate: &str) -> bool {
    Command::new(candidate)
        .arg("--version")
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status()
        .map(|status| status.success())
        .unwrap_or(false)
}

/// Walk up from the executable and the working directory looking for the
/// directory that contains the `ttc` package (`ttc/__init__.py`).
pub fn find_engine_root() -> Option<PathBuf> {
    let mut starts = Vec::new();
    if let Ok(exe) = env::current_exe() {
        if let Some(dir) = exe.parent() {
            starts.push(dir.to_path_buf());
        }
    }
    if let Ok(cwd) = env::current_dir() {
        starts.push(cwd);
    }
    let relative = Path::new("ttc").join("__init__.py");
    starts
        .into_iter()
        .find_map(|start| find_up(&start, &relative))
}

fn find_up(start: &Path, relative: &Path) -> Option<PathBuf> {
    let mut current = Some(start);
    while let Some(dir) = current {
        if dir.join(relative).is_file() {
            return Some(dir.to_path_buf());
        }
        current = dir.parent();
    }
    None
}

fn build_python_path(root: &Path) -> String {
    let mut value = root.to_string_lossy().into_owned();
    if let Some(existing) = env::var_os("PYTHONPATH") {
        if let Ok(joined) =
            env::join_paths(std::iter::once(root.to_path_buf()).chain(env::split_paths(&existing)))
        {
            value = joined.to_string_lossy().into_owned();
        }
    }
    value
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::protocol::Request;
    use serde_json::Value;
    use std::time::Duration;

    /// A live worker for integration-style protocol tests (requires Python).
    struct LiveWorker {
        handle: WorkerHandle,
        next_id: u64,
    }

    impl LiveWorker {
        fn new() -> Self {
            let handle =
                WorkerHandle::spawn().expect("python worker should spawn in the dev environment");
            Self { handle, next_id: 1 }
        }

        fn next_id(&mut self) -> u64 {
            self.next_id += 1;
            self.next_id - 1
        }

        fn recv(&self) -> WorkerEvent {
            self.handle
                .events()
                .recv_timeout(Duration::from_secs(30))
                .expect("worker event within timeout")
        }

        /// Request/response round trip, answering input prompts on the way.
        fn request(&mut self, request: Request) -> Message {
            let expect_input = matches!(request, Request::Execute { .. });
            self.handle.send(&request).expect("send request");
            loop {
                match self.recv() {
                    WorkerEvent::Message(message) => {
                        if message.is_input_request() {
                            assert!(expect_input, "unexpected input_request for {request:?}");
                            self.handle
                                .send(&Request::InputAnswer {
                                    answer: "42".to_string(),
                                })
                                .expect("send input answer");
                            continue;
                        }
                        if message.cmd.is_none() {
                            return message;
                        }
                    }
                    WorkerEvent::Log(_) => continue,
                    WorkerEvent::StdoutClosed => panic!("worker exited during {request:?}"),
                }
            }
        }
    }

    #[test]
    fn engine_root_is_discoverable() {
        let root = find_engine_root().expect("engine root should be found from cargo test cwd");
        assert!(root.join("ttc").join("__init__.py").is_file());
    }

    #[test]
    fn ping_pong_round_trip() {
        let mut worker = LiveWorker::new();
        let id = worker.next_id();
        let reply = worker.request(Request::Ping { id });
        assert_eq!(reply.id, Some(id));
        assert_eq!(reply.ok, Some(true));
        assert_eq!(reply.result, Some(Value::String("pong".to_string())));
        assert!(reply.version.is_some());
    }

    #[test]
    fn translate_round_trip() {
        let mut worker = LiveWorker::new();
        let id = worker.next_id();
        let reply = worker.request(Request::Translate {
            id,
            text: "set x to 5".to_string(),
        });
        let payload = reply.decode_translation().expect("translation payload");
        assert!(payload.success);
        assert!(payload.python_code.contains("x = 5"));
    }

    #[test]
    fn execute_with_interactive_input() {
        let mut worker = LiveWorker::new();
        let id = worker.next_id();
        let reply = worker.request(Request::Execute {
            id,
            code: "name = input('name? ')\nprint('hi ' + name)".to_string(),
            timeout: None,
            allow_imports: None,
        });
        let payload = reply.decode_execution().expect("execution payload");
        assert!(payload.success, "stderr: {}", payload.stderr);
        assert!(payload.stdout.contains("hi 42"));
    }

    #[test]
    fn execute_reports_runtime_error() {
        let mut worker = LiveWorker::new();
        let id = worker.next_id();
        let reply = worker.request(Request::Execute {
            id,
            code: "result = 1 / 0".to_string(),
            timeout: None,
            allow_imports: None,
        });
        let payload = reply.decode_execution().expect("execution payload");
        assert!(!payload.success);
        assert!(payload.error_message.contains("ZeroDivisionError"));
    }

    #[test]
    fn unknown_command_is_reported_without_killing_worker() {
        let mut worker = LiveWorker::new();
        // Hand-craft an unknown command to bypass the typed Request enum.
        worker
            .handle
            .tx
            .as_ref()
            .expect("writer channel")
            .send(r#"{"id": 999, "cmd": "explode"}"#.to_string())
            .expect("send raw");
        loop {
            match worker.recv() {
                WorkerEvent::Message(message) => {
                    if message.id == Some(999) {
                        assert_eq!(message.ok, Some(false));
                        assert!(message.error.unwrap().contains("explode"));
                        break;
                    }
                }
                _ => continue,
            }
        }
        let id = worker.next_id();
        let reply = worker.request(Request::Ping { id });
        assert_eq!(reply.ok, Some(true));
    }

    #[test]
    fn shutdown_exits_cleanly() {
        let mut worker = LiveWorker::new();
        let id = worker.next_id();
        worker
            .handle
            .send(&Request::Shutdown { id })
            .expect("send shutdown");
        let deadline = Instant::now() + Duration::from_secs(10);
        loop {
            if let Some(code) = worker.handle.try_reap() {
                assert_eq!(code, 0);
                break;
            }
            assert!(
                Instant::now() < deadline,
                "worker did not exit after shutdown"
            );
            thread::sleep(Duration::from_millis(25));
        }
    }
}
