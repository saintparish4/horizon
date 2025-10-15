use std::fmt;

/// Common result type for Antler Services
pub type Result<T> = std::result::Result<T, Error>;

/// Common error types across Antler Services
#[derive(Debug)]
pub enum Error {
    /// Database operation failed
    Database(String),

    /// Network or HTTP error
    Network(String),

    /// Serialization/Deserialization error
    Serialization(String),

    /// Authentication or authorization error
    Auth(String),

    /// Resource not found
    NotFound(String),

    /// Invalid Input or Validation error
    Validation(String),

    /// Internal server error
    Internal(String),

    /// External Service error
    ExternalService(String),

    /// Configuration error
    Config(String), 
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Error::Database(msg) => write!(f, "Database error: {}", msg),
            Error::Network(msg) => write!(f, "Network error: {}", msg),
            Error::Serialization(msg) => write!(f, "Serialization error: {}", msg),
            Error::Auth(msg) => write!(f, "Authentication error: {}", msg),
            Error::NotFound(msg) => write!(f, "Resource not found: {}", msg),
            Error::Validation(msg) => write!(f, "Validation error: {}", msg),
            Error::Internal(msg) => write!(f, "Internal server error: {}", msg),
            Error::ExternalService(msg) => write!(f, "External service error: {}", msg),
            Error::Config(msg) => write!(f, "Configuration error: {}", msg), 
        }
    }
}

impl std::error::Error for Error {}

// Conversions from common error types
impl From<sqlx::Error> for Error {
    fn from(err: sqlx::Error) -> Self {
        Error::Database(err.to_string()) 
    }
}

impl From<redis::RedisError> for Error {
    fn from(err: redis::RedisError) -> Self {
        Error::Database(format!("Redis error: {}", err)) 
    }
}

impl From<serde_json::Error> for Error {
    fn from(err: serde_json::Error) -> Self {
        Error::Serialization(err.to_string()) 
    }
}

impl From<reqwest::Error> for Error {
    fn from(err: reqwest::Error) -> Self {
        Error::Network(err.to_string()) 
    }
}

impl From<config::ConfigError> for Error {
    fn from(err: config::ConfigError) -> Self {
        Error::Config(err.to_string())  
    }
}

/// HTTP status code mapping for error types
impl Error {
    pub fn status_code(&self) -> u16 {
        match self {
            Error::NotFound(_) => 404,
            Error::Auth(_) => 401,
            Error::Validation(_) => 400,
            Error::Internal(_) | Error::Database(_) | Error::ExternalService(_) => 500,
            Error::Network(_) => 503,
            Error::Serialization(_) => 400,
            Error::Config(_) => 500,
        }
    }

    pub fn error_code(&self) -> &str {
        match self {
            Error::Database(_) => "DATABASE_ERROR",
            Error::Network(_) => "NETWORK_ERROR",
            Error::Serialization(_) => "SERIALIZATION_ERROR",
            Error::Auth(_) => "AUTHENTICATION_ERROR",
            Error::NotFound(_) => "RESOURCE_NOT_FOUND",
            Error::Validation(_) => "VALIDATION_ERROR",
            Error::Internal(_) => "INTERNAL_ERROR",
            Error::ExternalService(_) => "EXTERNAL_SERVICE_ERROR",
            Error::Config(_) => "CONFIGURATION_ERROR",
        }
    }
}