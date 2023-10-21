use crate::config::Config;
use axum::{http::StatusCode, response::Json};
use influxdb::Client;
use serde_json::{json, Value};
use tracing;
type JsonWithResponseCode = (StatusCode, Json<Value>);

use envconfig::Envconfig;

pub async fn handler_404() -> JsonWithResponseCode {
    (StatusCode::NOT_FOUND, Json(json!({"error": "Not Found"})))
}

pub async fn handler_ping_db() -> Json<Value> {
    tracing::info!("Pinging InfluxDB");
    let config = Config::init_from_env().unwrap();
    // TODO: Influx client should probably be cached
    let client: Client = Client::new(config.influx_url, config.influx_db);

    let ping_res = match client.ping().await {
        Ok(result) => {
            tracing::info!("Ping OK");
            result
        }
        Err(error) => {
            tracing::error!("Ping Error {:?}", error);
            return Json(json!({"error": error.to_string()}));
        }
    };
    let (server_type, res) = ping_res;
    // res
    Json(json!({ "server_type": server_type, "version": res }))
}
