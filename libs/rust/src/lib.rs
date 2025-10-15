// Antler Rust Common Library
// Shared utilities, error handling, and telemetry

pub mod error;
pub mod logging;
pub mod metrics;
pub mod telemetry;

// Re-export commonly used items
pub use error::{Error, Result};
pub use logging::init_logging;
pub use metrics::MetricsRegistry; 
pub use telemetry::init_telemetry; 