use std::sync::Arc;

use crate::Connections;
use axum::{extract::State, http::StatusCode, response::Json};
use serde_json::{json, Value};
use tracing;
type JsonWithResponseCode = (StatusCode, Json<Value>);

pub async fn handler_404() -> JsonWithResponseCode {
    (StatusCode::NOT_FOUND, Json(json!({"error": "Not Found"})))
}

pub async fn ping_db(State(state): State<Arc<Connections>>) -> Json<Value> {
    tracing::info!("Pinging InfluxDB");
    let ping_res = match state.client.ping().await {
        Ok(result) => {
            tracing::info!("Ping OK");
            result
        }
        Err(error) => {
            tracing::error!("Ping Error {:?}", error);
            return Json(json!({"error": error.to_string()}));
        }
    };
    Json(json!({ "server_type": ping_res.0, "version": ping_res.1 }))
}
