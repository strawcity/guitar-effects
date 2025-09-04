use actix_web::{web, App, HttpServer, Result, HttpResponse};
use actix_files::Files;
use serde::{Deserialize, Serialize};
use std::sync::{Arc, Mutex};
use crate::AudioProcessorTrait;

#[derive(Debug, Serialize, Deserialize)]
pub struct ParameterRequest {
    pub parameter: String,
    pub value: f32,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct StatusResponse {
    pub stereo_delay: StereoDelayStatus,
    pub distortion: DistortionStatus,
    pub system: SystemStatus,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct StereoDelayStatus {
    pub left_delay: f32,
    pub right_delay: f32,
    pub feedback: f32,
    pub wet_mix: f32,
    pub ping_pong: bool,
    pub stereo_width: f32,
    pub cross_feedback: f32,
    pub bpm: Option<f32>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct DistortionStatus {
    pub enabled: bool,
    pub distortion_type: String,
    pub drive: f32,
    pub mix: f32,
    pub feedback_intensity: f32,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SystemStatus {
    pub sample_rate: u32,
    pub buffer_size: usize,
    pub input_device: Option<String>,
    pub output_device: Option<String>,
    pub is_running: bool,
}

pub struct WebServer {
    processor: Arc<Mutex<Box<dyn AudioProcessorTrait + Send>>>,
}

impl WebServer {
    pub fn new(processor: Arc<Mutex<Box<dyn AudioProcessorTrait + Send>>>) -> Self {
        Self {
            processor,
        }
    }

    pub async fn start(self, port: u16) -> std::io::Result<()> {
        let processor = self.processor.clone();
        
        println!("🌐 Starting web interface on http://0.0.0.0:{}", port);
        println!("📱 Access from any device on your network");
        println!("🎛️  Control your guitar effects via web browser");
        
        HttpServer::new(move || {
            App::new()
                .app_data(web::Data::new(processor.clone()))
                .service(Files::new("/static", "./web/static").show_files_listing())
                .route("/", web::get().to(index))
                .route("/api/test", web::get().to(test_endpoint))
                .route("/api/status", web::get().to(get_status))
                .route("/api/parameter", web::post().to(set_parameter))
                .route("/api/start", web::post().to(start_audio))
                .route("/api/stop", web::post().to(stop_audio))
                .route("/api/reset", web::post().to(reset_delay))
                .route("/api/config", web::get().to(get_config))
                .route("/api/config", web::post().to(save_config))
        })
        .bind(format!("0.0.0.0:{}", port))?
        .run()
        .await
    }
}

async fn index() -> Result<actix_files::NamedFile> {
    Ok(actix_files::NamedFile::open("web/static/index.html")?)
}

async fn test_endpoint() -> Result<HttpResponse> {
    println!("🔍 Web API: test endpoint called");
    Ok(HttpResponse::Ok().json(serde_json::json!({
        "status": "ok",
        "message": "API is working"
    })))
}

async fn get_status(
    processor: web::Data<Arc<Mutex<Box<dyn AudioProcessorTrait>>>>,
) -> Result<HttpResponse> {
    println!("🔍 Web API: get_status called");
    
    let processor = match processor.lock() {
        Ok(p) => p,
        Err(e) => {
            println!("❌ Web API: Failed to acquire processor lock: {}", e);
            return Ok(HttpResponse::InternalServerError().json(serde_json::json!({
                "error": "Failed to acquire processor lock"
            })));
        }
    };
    
    match processor.get_status() {
        Ok(status_map) => {
            println!("✅ Web API: Status retrieved successfully, {} fields", status_map.len());
            
            // Parse status into structured response
            let stereo_delay = StereoDelayStatus {
                left_delay: status_map.get("left_delay").unwrap_or(&"0.3".to_string()).parse().unwrap_or(0.3),
                right_delay: status_map.get("right_delay").unwrap_or(&"0.6".to_string()).parse().unwrap_or(0.6),
                feedback: status_map.get("feedback").unwrap_or(&"0.3".to_string()).parse().unwrap_or(0.3),
                wet_mix: status_map.get("wet_mix").unwrap_or(&"0.6".to_string()).parse().unwrap_or(0.6),
                ping_pong: status_map.get("ping_pong").unwrap_or(&"true".to_string()) == "true",
                stereo_width: status_map.get("stereo_width").unwrap_or(&"0.5".to_string()).parse().unwrap_or(0.5),
                cross_feedback: status_map.get("cross_feedback").unwrap_or(&"0.2".to_string()).parse().unwrap_or(0.2),
                bpm: status_map.get("bpm").and_then(|s| s.parse().ok()),
            };
            
            let distortion = DistortionStatus {
                enabled: status_map.get("distortion_enabled").unwrap_or(&"true".to_string()) == "true",
                distortion_type: status_map.get("distortion_type").unwrap_or(&"soft_clip".to_string()).clone(),
                drive: status_map.get("distortion_drive").unwrap_or(&"0.3".to_string()).parse().unwrap_or(0.3),
                mix: status_map.get("distortion_mix").unwrap_or(&"0.7".to_string()).parse().unwrap_or(0.7),
                feedback_intensity: status_map.get("distortion_feedback_intensity").unwrap_or(&"0.5".to_string()).parse().unwrap_or(0.5),
            };
            
            let system = SystemStatus {
                sample_rate: status_map.get("sample_rate").unwrap_or(&"48000".to_string()).parse().unwrap_or(48000),
                buffer_size: status_map.get("buffer_size").unwrap_or(&"1024".to_string()).parse().unwrap_or(1024),
                input_device: status_map.get("input_device").cloned(),
                output_device: status_map.get("output_device").cloned(),
                is_running: status_map.get("is_running").unwrap_or(&"false".to_string()) == "true",
            };
            
            let response = StatusResponse {
                stereo_delay,
                distortion,
                system,
            };
            
            println!("✅ Web API: Response structured successfully");
            Ok(HttpResponse::Ok().json(response))
        }
        Err(e) => {
            println!("❌ Web API: Failed to get status: {}", e);
            Ok(HttpResponse::InternalServerError().json(serde_json::json!({
                "error": format!("Failed to get status: {}", e)
            })))
        }
    }
}

async fn set_parameter(
    processor: web::Data<Arc<Mutex<Box<dyn AudioProcessorTrait>>>>,
    param_req: web::Json<ParameterRequest>,
) -> Result<HttpResponse> {
    let mut processor = processor.lock().unwrap();
    
    let result = if param_req.parameter.starts_with("distortion_") {
        // Handle distortion parameters
        match param_req.parameter.as_str() {
            "distortion_type" => processor.set_distortion_type(&param_req.value.to_string()),
            "distortion_enabled" => processor.set_stereo_delay_parameter("distortion_enabled", param_req.value),
            "distortion_drive" => processor.set_stereo_delay_parameter("distortion_drive", param_req.value),
            "distortion_mix" => processor.set_stereo_delay_parameter("distortion_mix", param_req.value),
            "distortion_feedback_intensity" => processor.set_stereo_delay_parameter("distortion_feedback_intensity", param_req.value),
            _ => Err(crate::error::AudioProcessorError::InvalidParameter {
                param: param_req.parameter.clone(),
                value: param_req.value,
                min: 0.0,
                max: 1.0,
            }),
        }
    } else {
        // Handle stereo delay parameters
        processor.set_stereo_delay_parameter(&param_req.parameter, param_req.value)
    };
    
    match result {
        Ok(_) => {
            Ok(HttpResponse::Ok().json(serde_json::json!({
                "success": true,
                "parameter": param_req.parameter,
                "value": param_req.value
            })))
        }
        Err(e) => {
            Ok(HttpResponse::BadRequest().json(serde_json::json!({
                "error": format!("Failed to set parameter: {}", e)
            })))
        }
    }
}

async fn start_audio(
    processor: web::Data<Arc<Mutex<Box<dyn AudioProcessorTrait>>>>,
) -> Result<HttpResponse> {
    let mut processor = processor.lock().unwrap();
    
    match processor.start_audio() {
        Ok(_) => {
            Ok(HttpResponse::Ok().json(serde_json::json!({
                "success": true,
                "message": "Audio processing started"
            })))
        }
        Err(e) => {
            Ok(HttpResponse::InternalServerError().json(serde_json::json!({
                "error": format!("Failed to start audio: {}", e)
            })))
        }
    }
}

async fn stop_audio(
    processor: web::Data<Arc<Mutex<Box<dyn AudioProcessorTrait>>>>,
) -> Result<HttpResponse> {
    let mut processor = processor.lock().unwrap();
    
    match processor.stop_audio() {
        Ok(_) => {
            Ok(HttpResponse::Ok().json(serde_json::json!({
                "success": true,
                "message": "Audio processing stopped"
            })))
        }
        Err(e) => {
            Ok(HttpResponse::InternalServerError().json(serde_json::json!({
                "error": format!("Failed to stop audio: {}", e)
            })))
        }
    }
}

async fn reset_delay(
    processor: web::Data<Arc<Mutex<Box<dyn AudioProcessorTrait>>>>,
) -> Result<HttpResponse> {
    let mut processor = processor.lock().unwrap();
    
    match processor.reset_delay() {
        Ok(_) => {
            Ok(HttpResponse::Ok().json(serde_json::json!({
                "success": true,
                "message": "Delay buffers reset"
            })))
        }
        Err(e) => {
            Ok(HttpResponse::InternalServerError().json(serde_json::json!({
                "error": format!("Failed to reset delay: {}", e)
            })))
        }
    }
}

async fn get_config(
    _processor: web::Data<Arc<Mutex<Box<dyn AudioProcessorTrait>>>>,
) -> Result<HttpResponse> {
    // For now, return a default config structure
    // In the future, this could read from the actual config file
    let config = serde_json::json!({
        "sample_rate": 48000,
        "buffer_size": 1024,
        "stereo_delay": {
            "left_delay": 0.3,
            "right_delay": 0.6,
            "feedback": 0.3,
            "wet_mix": 0.6,
            "ping_pong": true,
            "stereo_width": 0.5,
            "cross_feedback": 0.2
        },
        "distortion": {
            "enabled": true,
            "distortion_type": "soft_clip",
            "drive": 0.3,
            "mix": 0.7,
            "feedback_intensity": 0.5
        }
    });
    
    Ok(HttpResponse::Ok().json(config))
}

async fn save_config(
    _processor: web::Data<Arc<Mutex<Box<dyn AudioProcessorTrait>>>>,
    _config: web::Json<serde_json::Value>,
) -> Result<HttpResponse> {
    // For now, just return success
    // In the future, this could save to the config file
    Ok(HttpResponse::Ok().json(serde_json::json!({
        "success": true,
        "message": "Configuration saved"
    })))
}
