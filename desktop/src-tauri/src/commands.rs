use serde::{Deserialize, Serialize};
use std::io::{BufRead, BufReader, Write};
use std::process::{Child, Command, Stdio};
use std::sync::Mutex;
use tauri::State;

pub struct AgentState {
    pub process: Mutex<Option<Child>>,
}

#[derive(Serialize, Deserialize)]
struct AgentRequest {
    id: String,
    prompt: String,
}

#[derive(Serialize, Deserialize)]
struct AgentResponse {
    #[serde(rename = "type")]
    msg_type: String,
    id: Option<String>,
    content: String,
}

#[tauri::command]
pub async fn start_agent(state: State<'_, AgentState>) -> Result<String, String> {
    let mut process_lock = state.process.lock().unwrap();
    
    if process_lock.is_some() {
        return Ok("Agent already running".to_string());
    }

    let child = Command::new("python3")
        .arg("../../src/agent_core/adk/bridge.py")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::inherit()) // Let python errors show up in the terminal
        .spawn()
        .map_err(|e| format!("Failed to start agent: {}", e))?;

    *process_lock = Some(child);
    Ok("Agent started successfully".to_string())
}

#[tauri::command]
pub async fn send_message(
    state: State<'_, AgentState>,
    message: String,
    msg_id: String,
) -> Result<String, String> {
    let mut process_lock = state.process.lock().unwrap();
    
    let process = process_lock.as_mut()
        .ok_or("Agent not running. Call start_agent first.")?;

    let stdin = process.stdin.as_mut()
        .ok_or("Failed to access agent stdin")?;

    let request = AgentRequest {
        id: msg_id.clone(),
        prompt: message,
    };
    let json_line = serde_json::to_string(&request)
        .map_err(|e| format!("JSON serialization error: {}", e))?;
    
    writeln!(stdin, "{}", json_line)
        .map_err(|e| format!("Failed to write to agent: {}", e))?;
    
    stdin.flush()
        .map_err(|e| format!("Failed to flush stdin: {}", e))?;

    // Read response
    let stdout = process.stdout.as_mut()
        .ok_or("Failed to access agent stdout")?;
    
    let mut reader = BufReader::new(stdout);
    let mut response_line = String::new();
    
    // Skip trace events and find the JSON response
    loop {
        response_line.clear();
        reader.read_line(&mut response_line)
            .map_err(|e| format!("Failed to read response: {}", e))?;

        if response_line.is_empty() {
            return Err("Agent process produced no output".to_string());
        }

        let trimmed = response_line.trim();
        if trimmed.is_empty() {
            continue;
        }

        // If it's not a trace event, try to parse it as our response
        if !trimmed.starts_with("ADK_EVENT:") {
            break;
        }
    }

    if response_line.is_empty() {
        return Err("Agent process produced no output".to_string());
    }

    let response: AgentResponse = serde_json::from_str(&response_line)
        .map_err(|e| format!("Failed to parse response: {}, line: {}", e, response_line))?;

    Ok(response.content)
}

#[tauri::command]
pub async fn get_agent_status(state: State<'_, AgentState>) -> Result<bool, String> {
    let process_lock = state.process.lock().unwrap();
    Ok(process_lock.is_some())
}
