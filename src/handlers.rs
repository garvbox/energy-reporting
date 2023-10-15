use axum::{http::StatusCode, response::Json};
use influxdb::Client;
use serde_json::{json, Value};
use std::env;
use tracing;
type JsonWithResponseCode = (StatusCode, Json<Value>);

pub async fn handler_404() -> JsonWithResponseCode {
    (StatusCode::NOT_FOUND, Json(json!({"error": "Not Found"})))
}

pub async fn handler_ping_db() -> Json<Value> {
    tracing::info!("Pinging InfluxDB");
    // TODO: Influx client should probably be cached
    let influx_url = env::var("INFLUX_URL").unwrap();
    let influx_db = env::var("INFLUX_DB").unwrap();
    let client: Client = Client::new(influx_url, influx_db);

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
