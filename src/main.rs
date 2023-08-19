use axum::{response::Json, routing::get, Router};
use influxdb::Client;
use serde_json::{json, Value};
use std::env;
use tracing::{error, info};
use tracing_subscriber;

#[tokio::main]
async fn main() {
    // build our application with a route
    tracing_subscriber::fmt::init();
    let app = Router::new()
        // Ping DB test
        .route("/ping", get(ping_db));

    axum::Server::bind(&"0.0.0.0:3000".parse().unwrap())
        .serve(app.into_make_service())
        .await
        .unwrap();
}

async fn ping_db() -> Json<Value> {
    info!("Pinging InfluxDB");
    let influx_host = env::var("INFLUX_HOST").unwrap();
    let influx_db = env::var("INFLUX_DB").unwrap();
    let influx_url = "http://".to_string() + &influx_host + ":8086";
    let client: Client = Client::new(influx_url, influx_db);

    let ping_res = match client.ping().await {
        Ok(result) => {
            info!("Ping OK");
            result
        }
        Err(error) => {
            error!("Ping Error {:?}", error);
            return Json(json!({"error": error.to_string()}));
        }
    };
    let (server_type, res) = ping_res;
    // res
    Json(json!({ "server_type": server_type, "version": res }))
}
