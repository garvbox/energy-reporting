use axum;
use tracing::info;
use tracing_subscriber;

mod handlers;

#[tokio::main]
async fn main() {
    // build our application with a route
    tracing_subscriber::fmt::init();
    let app = axum::Router::new()
        // Ping DB test
        .route("/ping", axum::routing::get(handlers::handler_ping_db))
        .fallback(handlers::handler_404);
    info!("Starting server...");
    axum::Server::bind(&"0.0.0.0:8000".parse().unwrap())
        .serve(app.into_make_service())
        .await
        .unwrap();
}
