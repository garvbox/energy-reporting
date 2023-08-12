use axum::{response::Json, routing::get, Router};
use influxdb::Client;
use serde_json::{json, Value};
use std::env;

#[tokio::main]
async fn main() {
    // build our application with a route
    let app = Router::new()
        // Ping DB test
        .route("/ping", get(ping_db));

    axum::Server::bind(&"0.0.0.0:3000".parse().unwrap())
        .serve(app.into_make_service())
        .await
        .unwrap();
}

async fn ping_db() -> Json<Value> {
    let influx_url = env::var("INFLUX_URL").unwrap();
    let influx_db = env::var("INFLUX_DB").unwrap();
    let client: Client = Client::new(influx_url, influx_db);

    let ping_res = client.ping().await.unwrap();
    let (server_type, res) = ping_res;
    // res
    Json(json!({ "server_type": server_type, "version": res }))
}
