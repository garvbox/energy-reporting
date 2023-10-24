use std::sync::Arc;

use axum::{routing::get, Router, Server};
use dotenv::dotenv;
use envconfig::Envconfig;
use influxdb::Client;
use tracing::info;
use tracing_subscriber;

mod config;
mod handlers;

pub struct Connections {
    client: Client,
    // TODO: Define DB connection state here
}

impl Connections {
    pub fn new() -> Self {
        let config = config::Config::init_from_env().unwrap();
        let client = Client::new(config.influx_url, config.influx_db);
        Self { client }
    }
}

#[tokio::main]
async fn main() {
    dotenv().ok();
    tracing_subscriber::fmt::init();
    // Set up InfluxDB Client and store as shared state
    let state = Arc::new(Connections::new());
    let app = Router::new()
        // Ping DB test
        .route("/ping", get(handlers::ping_db))
        .route("/data", get(handlers::get_data))
        .with_state(state)
        .fallback(handlers::handler_404);
    info!("Starting server...");
    Server::bind(&"0.0.0.0:8000".parse().unwrap())
        .serve(app.into_make_service())
        .await
        .expect("Server failed to start")
}
