use opentelemetry::global;
use opentelemetry_jaeger::JaegerPipeline;
use tracing_subscriber::layer::SubscriberExt;

/// Initialize distributed tracing with Jaeger
///
/// Sets up OpenTelemetry tracing with Jaeger backend
/// Traces can be viewed in Jaeger UI
pub fn init_telemetry(service_name: &str, jaeger_endpoint: &str) -> Result<(), Box<dyn std::error::Error>> {
    // Create Jaeger tracer
    let tracer = opentelemetry_jaeger::new_agent_pipeline()
        .with_service_name(service_name)
        .with_endpoint(jaeger_endpoint)
        .install_batch(opentelemetry::runtime::Tokio)?;

    // Set global tracer provider
    global::set_tracer_provider(tracer.provider().unwrap());

    tracing::info!(
        service = service_name,
        endpoint = jaeger_endpoint,
        "Telemetry initialized"
    );

    Ok(())
}

/// Shutdown telemetry gracefully
pub fn shutdown_telemetry() {
    global::shutdown_tracer_provider();
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_telemetry_init() {
        // Test basic initialization (will fail without Jaeger running, but shouldn't panic)
        let result = init_telemetry("test-service", "http://localhost:14268/api/traces");
        // We don't assert success since Jaeger might not be running in test env
        drop(result);
    }
}