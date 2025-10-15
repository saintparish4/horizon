use prometheus::{Registry, Counter, Histogram, Gauge};
use std::sync::Arc;

/// Central metrics registry for Prometheus
pub struct MetricsRegistry {
    registry: Arc<Registry>, 
}

impl MetricsRegistry {
    /// Create a new metrics registry
    pub fn new() -> Self {
        Self {
            registry: Arc::new(Registry::new()), 
        }
    }

    /// Get the underlying Prometheus Registry
    pub fn registry(&self) -> Arc<Registry> {
        self.registry.clone() 
    }

    /// Register a counter metric
    pub fn register_counter(&self, name: &str, help: &str) -> prometheus::Result<Counter> {
        let counter = Counter::new(name, help)?;
        self.registry.register(Box::new(counter.clone()))?;
        Ok(counter) 
    }

    /// Register a histogram metric
    pub fn register_histogram(&self, name: &str, help: &str) -> prometheus::Result<Histogram> {
        let histogram = Histogram::new(name, help)?;
        self.registry.register(Box::new(histogram.clone()))?;
        Ok(histogram)  
    }

    /// Register a gauge metric
    pub fn register_gauge(&self, name: &str, help: &str) -> prometheus::Result<Gauge> {
        let gauge = Gauge::new(name, help)?;
        self.registry.register(Box::new(gauge.clone()))?;
        Ok(gauge)  
    }

    /// Gather all metrics for Prometheus scraping
    pub fn gather(&self) -> prometheus::Result<Vec<prometheus::MetricFamily>> {
        self.registry.gather()  
    }
}

impl Default for MetricsRegistry {
    fn default() -> Self {
        Self::new()   
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_metrics_registry() {
        let registry = MetricsRegistry::new();

        // Test counter registration
        let counter = registry.register_counter("test_counter", "Test counter").unwrap();
        counter.inc();
        assert_eq!(counter.get(), 1.0);

        // Test histogram registration
        let histogram = registry.register_histogram("test_histogram", "Test histogram").unwrap();
        histogram.observe(1.5);

        // Test gauge registration
        let gauge = registry.register_gauge("test_gauge", "Test gauge").unwrap();
        gauge.set(42.0);
        assert_eq!(gauge.get(), 42.0);

        // Test gathering metrics
        let metrics = registry.gather();
        assert!(metrics.is_ok()); 
    }
}