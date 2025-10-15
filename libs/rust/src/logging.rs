use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt, EnvFilter};

/// Initialize logging with environment based configuration
///
/// Sets up structured logging with tracing-subscriber
/// Log level can be controlled via RUST_LOG environment variable
/// Default level: info
pub fn init_logging(service_name: &str) {
    let env_filter = EnvFilter::try_from_default_env()
        .unwrap_or_else(|_| EnvFilter::new("info"));

    let format_layer = tracing_subscriber::fmt::layer()
        .with_target(true)
        .with_thread_ids(true)
        .with_line_number(true)
        .json();

    tracing_subscriber::registry()
        .with(env_filter)
        .with(format_layer)
        .init();

    tracing::info!(
        service = service_name,
        "logging initialized"
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_init_logging() {
        // Test that logging can be initialized without panicking
        init_logging("test_service"); 
    }
}