//! Wire protocol shared with the Python worker (`python -m ttc.worker`).
//!
//! Transport: one JSON object per line over stdin/stdout.
//! Requests are internally tagged by `cmd`; responses are loosely typed
//! (`Message`) because the worker replies with flat objects that either
//! carry `ok`/`result` (responses) or `cmd`/`prompt` (`input_request`).

use serde::{Deserialize, Serialize};
use serde_json::Value;

pub type RequestId = u64;

/// Requests sent from the GUI to the worker.
#[derive(Debug, Clone, PartialEq, Serialize)]
#[serde(tag = "cmd")]
pub enum Request {
    #[serde(rename = "translate")]
    Translate { id: RequestId, text: String },
    #[serde(rename = "execute")]
    Execute {
        id: RequestId,
        code: String,
        #[serde(skip_serializing_if = "Option::is_none")]
        timeout: Option<f64>,
        #[serde(skip_serializing_if = "Option::is_none")]
        allow_imports: Option<bool>,
    },
    #[serde(rename = "ping")]
    Ping { id: RequestId },
    #[serde(rename = "shutdown")]
    Shutdown { id: RequestId },
    /// Reply to an `input_request` raised while executing code.
    #[serde(rename = "input_answer")]
    InputAnswer { answer: String },
}

impl Request {
    pub fn to_json(&self) -> String {
        serde_json::to_string(self).expect("request serialization cannot fail")
    }

    pub fn request_id(&self) -> Option<RequestId> {
        match self {
            Request::Translate { id, .. }
            | Request::Execute { id, .. }
            | Request::Ping { id }
            | Request::Shutdown { id } => Some(*id),
            Request::InputAnswer { .. } => None,
        }
    }
}

/// Any JSON line coming from the worker.
#[derive(Debug, Clone, Default, Deserialize)]
pub struct Message {
    pub id: Option<RequestId>,
    pub ok: Option<bool>,
    pub error: Option<String>,
    pub result: Option<Value>,
    pub version: Option<String>,
    pub cmd: Option<String>,
    pub prompt: Option<String>,
}

impl Message {
    pub fn is_input_request(&self) -> bool {
        self.cmd.as_deref() == Some("input_request")
    }

    pub fn prompt_text(&self) -> String {
        self.prompt.clone().unwrap_or_default()
    }

    pub fn decode_translation(&self) -> Result<TranslationPayload, String> {
        self.decode_result()
    }

    pub fn decode_execution(&self) -> Result<ExecutionPayload, String> {
        self.decode_result()
    }

    fn decode_result<T: for<'de> Deserialize<'de>>(&self) -> Result<T, String> {
        let value = self.result.as_ref().ok_or_else(|| {
            self.error
                .clone()
                .unwrap_or_else(|| "missing result in worker response".to_string())
        })?;
        serde_json::from_value(value.clone()).map_err(|e| format!("bad result payload: {e}"))
    }
}

/// `TranslationResult.to_dict()` fields the GUI needs.
#[derive(Debug, Clone, Deserialize)]
pub struct TranslationPayload {
    pub success: bool,
    #[serde(default)]
    pub python_code: String,
    #[serde(default)]
    pub error_message: String,
    #[serde(default)]
    pub warnings: Vec<String>,
}

/// `ExecutionResult.to_dict()` fields the GUI needs.
#[derive(Debug, Clone, Deserialize)]
pub struct ExecutionPayload {
    pub success: bool,
    #[serde(default)]
    pub stdout: String,
    #[serde(default)]
    pub stderr: String,
    #[serde(default)]
    pub error_message: String,
    pub execution_time: f64,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn request_translate_serializes_with_cmd_tag() {
        let request = Request::Translate {
            id: 7,
            text: "set x to 5".to_string(),
        };
        let json: Value = serde_json::from_str(&request.to_json()).unwrap();
        assert_eq!(json["cmd"], "translate");
        assert_eq!(json["id"], 7);
        assert_eq!(json["text"], "set x to 5");
    }

    #[test]
    fn request_execute_serializes_optional_fields() {
        let request = Request::Execute {
            id: 2,
            code: "print(1)".to_string(),
            timeout: Some(1.5),
            allow_imports: None,
        };
        let json: Value = serde_json::from_str(&request.to_json()).unwrap();
        assert_eq!(json["cmd"], "execute");
        assert_eq!(json["timeout"], 1.5);
        assert!(json.get("allow_imports").is_none());
    }

    #[test]
    fn request_input_answer_has_no_id() {
        let request = Request::InputAnswer {
            answer: "Budi".to_string(),
        };
        let json: Value = serde_json::from_str(&request.to_json()).unwrap();
        assert_eq!(json["cmd"], "input_answer");
        assert_eq!(json["answer"], "Budi");
        assert!(json.get("id").is_none());
        assert!(request.request_id().is_none());
    }

    #[test]
    fn parse_worker_success_response() {
        let line = r#"{"id": 1, "ok": true, "result": {
            "success": true, "python_code": "x = 5",
            "error_message": "", "warnings": ["w1"]}}"#;
        let message: Message = serde_json::from_str(line).unwrap();
        assert!(!message.is_input_request());
        assert_eq!(message.id, Some(1));
        assert_eq!(message.ok, Some(true));
        let payload = message.decode_translation().unwrap();
        assert!(payload.success);
        assert_eq!(payload.python_code, "x = 5");
        assert_eq!(payload.warnings, vec!["w1"]);
    }

    #[test]
    fn parse_worker_input_request() {
        let line = r#"{"id": 8, "cmd": "input_request", "prompt": "name? "}"#;
        let message: Message = serde_json::from_str(line).unwrap();
        assert!(message.is_input_request());
        assert_eq!(message.id, Some(8));
        assert_eq!(message.prompt_text(), "name? ");
    }

    #[test]
    fn parse_worker_error_response() {
        let line = r#"{"id": null, "ok": false, "error": "invalid request: nope"}"#;
        let message: Message = serde_json::from_str(line).unwrap();
        assert_eq!(message.id, None);
        assert_eq!(message.ok, Some(false));
        assert!(message
            .error
            .as_deref()
            .unwrap()
            .contains("invalid request"));
        assert!(message.decode_translation().is_err());
    }

    #[test]
    fn parse_execution_payload() {
        let line = r#"{"id": 9, "ok": true, "result": {
            "success": false, "stdout": "", "stderr": "boom",
            "error_message": "ZeroDivisionError: division by zero",
            "execution_time": 0.05}}"#;
        let message: Message = serde_json::from_str(line).unwrap();
        let payload = message.decode_execution().unwrap();
        assert!(!payload.success);
        assert!(payload.error_message.contains("ZeroDivisionError"));
    }
}
