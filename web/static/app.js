// Guitar Effects Web Controller
class GuitarEffectsController {
  constructor() {
    this.apiBase = "/api";
    this.statusInterval = null;
    this.isConnected = false;
    this.currentStatus = {};

    this.init();
  }

  async init() {
    this.setupEventListeners();
    await this.connect();
    this.startStatusPolling();
  }

  setupEventListeners() {
    // System controls
    document
      .getElementById("start-btn")
      .addEventListener("click", () => this.startAudio());
    document
      .getElementById("stop-btn")
      .addEventListener("click", () => this.stopAudio());
    document
      .getElementById("reset-btn")
      .addEventListener("click", () => this.resetDelay());

    // Stereo delay controls
    this.setupKnobControl("feedback", "feedback", (value) => value.toFixed(2));
    this.setupKnobControl("wet-mix", "wet_mix", (value) => value.toFixed(2));
    this.setupKnobControl("stereo-width", "stereo_width", (value) =>
      value.toFixed(2)
    );
    this.setupKnobControl("cross-feedback", "cross_feedback", (value) =>
      value.toFixed(2)
    );
    this.setupKnobControl("bpm", "bpm", (value) => `${value} BPM`);

    // Toggle controls
    this.setupToggleControl("ping-pong", "ping_pong");

    // Distortion controls
    this.setupToggleControl("distortion-enabled", "distortion_enabled");
    this.setupSelectControl("distortion-type", "distortion_type");
    this.setupKnobControl("distortion-drive", "distortion_drive", (value) =>
      value.toFixed(2)
    );
    this.setupKnobControl("distortion-mix", "distortion_mix", (value) =>
      value.toFixed(2)
    );
    this.setupKnobControl(
      "distortion-feedback-intensity",
      "distortion_feedback_intensity",
      (value) => value.toFixed(2)
    );
  }

  setupKnobControl(elementId, parameterName, valueFormatter) {
    const element = document.getElementById(elementId);
    const valueElement = document.getElementById(`${elementId}-value`);

    element.addEventListener("input", async (e) => {
      const value = parseFloat(e.target.value);
      valueElement.textContent = valueFormatter(value);

      try {
        await this.setParameter(parameterName, value);
      } catch (error) {
        console.error(`Failed to set ${parameterName}:`, error);
        this.showError(`Failed to set ${parameterName}`);
      }
    });
  }

  setupToggleControl(elementId, parameterName) {
    const element = document.getElementById(elementId);

    element.addEventListener("change", async (e) => {
      const value = e.target.checked ? 1 : 0;

      try {
        await this.setParameter(parameterName, value);
      } catch (error) {
        console.error(`Failed to set ${parameterName}:`, error);
        this.showError(`Failed to set ${parameterName}`);
        // Revert the toggle
        e.target.checked = !e.target.checked;
      }
    });
  }

  setupSelectControl(elementId, parameterName) {
    const element = document.getElementById(elementId);

    element.addEventListener("change", async (e) => {
      const value = e.target.value;

      try {
        await this.setParameter(parameterName, value);
      } catch (error) {
        console.error(`Failed to set ${parameterName}:`, error);
        this.showError(`Failed to set ${parameterName}`);
      }
    });
  }

  async connect() {
    try {
      const response = await fetch(`${this.apiBase}/status`);
      if (response.ok) {
        this.updateConnectionStatus(true);
        const status = await response.json();
        this.updateInterface(status);
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      console.error("Failed to connect:", error);
      this.updateConnectionStatus(false);
      this.showError("Failed to connect to server");
    }
  }

  updateConnectionStatus(connected) {
    this.isConnected = connected;
    const statusText = document.getElementById("status-text");
    const statusDot = document.getElementById("status-dot");

    if (connected) {
      statusText.textContent = "Connected";
      statusDot.className = "status-dot connected";
    } else {
      statusText.textContent = "Disconnected";
      statusDot.className = "status-dot error";
    }
  }

  startStatusPolling() {
    this.statusInterval = setInterval(async () => {
      if (this.isConnected) {
        try {
          const response = await fetch(`${this.apiBase}/status`);
          if (response.ok) {
            const status = await response.json();
            this.updateInterface(status);
          } else {
            this.updateConnectionStatus(false);
          }
        } catch (error) {
          this.updateConnectionStatus(false);
        }
      } else {
        // Try to reconnect
        await this.connect();
      }
    }, 1000); // Poll every second
  }

  updateInterface(status) {
    this.currentStatus = status;

    // Update stereo delay controls
    this.updateKnobValue("feedback", status.stereo_delay.feedback, (value) =>
      value.toFixed(2)
    );
    this.updateKnobValue("wet-mix", status.stereo_delay.wet_mix, (value) =>
      value.toFixed(2)
    );
    this.updateKnobValue(
      "stereo-width",
      status.stereo_delay.stereo_width,
      (value) => value.toFixed(2)
    );
    this.updateKnobValue(
      "cross-feedback",
      status.stereo_delay.cross_feedback,
      (value) => value.toFixed(2)
    );
    this.updateKnobValue(
      "bpm",
      status.stereo_delay.bpm || 120,
      (value) => `${value} BPM`
    );

    // Update toggles
    this.updateToggleValue("ping-pong", status.stereo_delay.ping_pong);

    // Update distortion controls
    this.updateToggleValue("distortion-enabled", status.distortion.enabled);
    this.updateSelectValue(
      "distortion-type",
      status.distortion.distortion_type
    );
    this.updateKnobValue("distortion-drive", status.distortion.drive, (value) =>
      value.toFixed(2)
    );
    this.updateKnobValue("distortion-mix", status.distortion.mix, (value) =>
      value.toFixed(2)
    );
    this.updateKnobValue(
      "distortion-feedback-intensity",
      status.distortion.feedback_intensity,
      (value) => value.toFixed(2)
    );

    // Update system info
    document.getElementById(
      "sample-rate"
    ).textContent = `${status.system.sample_rate} Hz`;
    document.getElementById("buffer-size").textContent =
      status.system.buffer_size;
    document.getElementById("input-device").textContent =
      status.system.input_device || "Default";
    document.getElementById("output-device").textContent =
      status.system.output_device || "Default";
  }

  updateKnobValue(elementId, value, formatter) {
    const element = document.getElementById(elementId);
    const valueElement = document.getElementById(`${elementId}-value`);

    if (element && valueElement) {
      element.value = value;
      valueElement.textContent = formatter(value);
    }
  }

  updateToggleValue(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
      element.checked = value;
    }
  }

  updateSelectValue(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
      element.value = value;
    }
  }

  async setParameter(parameter, value) {
    const response = await fetch(`${this.apiBase}/parameter`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        parameter: parameter,
        value: value,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || "Failed to set parameter");
    }

    return await response.json();
  }

  async startAudio() {
    try {
      const response = await fetch(`${this.apiBase}/start`, {
        method: "POST",
      });

      if (response.ok) {
        this.showSuccess("Audio processing started");
      } else {
        const error = await response.json();
        throw new Error(error.error || "Failed to start audio");
      }
    } catch (error) {
      console.error("Failed to start audio:", error);
      this.showError("Failed to start audio processing");
    }
  }

  async stopAudio() {
    try {
      const response = await fetch(`${this.apiBase}/stop`, {
        method: "POST",
      });

      if (response.ok) {
        this.showSuccess("Audio processing stopped");
      } else {
        const error = await response.json();
        throw new Error(error.error || "Failed to stop audio");
      }
    } catch (error) {
      console.error("Failed to stop audio:", error);
      this.showError("Failed to stop audio processing");
    }
  }

  async resetDelay() {
    try {
      const response = await fetch(`${this.apiBase}/reset`, {
        method: "POST",
      });

      if (response.ok) {
        this.showSuccess("Delay buffers reset");
      } else {
        const error = await response.json();
        throw new Error(error.error || "Failed to reset delay");
      }
    } catch (error) {
      console.error("Failed to reset delay:", error);
      this.showError("Failed to reset delay buffers");
    }
  }

  showSuccess(message) {
    this.showNotification(message, "success");
  }

  showError(message) {
    this.showNotification(message, "error");
  }

  showNotification(message, type = "info") {
    // Create notification element
    const notification = document.createElement("div");
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    // Add styles
    notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 1000;
            animation: slideIn 0.3s ease;
            max-width: 300px;
        `;

    if (type === "success") {
      notification.style.background =
        "linear-gradient(45deg, #66bb6a, #4caf50)";
    } else if (type === "error") {
      notification.style.background =
        "linear-gradient(45deg, #ef5350, #f44336)";
    } else {
      notification.style.background =
        "linear-gradient(45deg, #4ecdc4, #45b7d1)";
    }

    // Add to page
    document.body.appendChild(notification);

    // Remove after 3 seconds
    setTimeout(() => {
      notification.style.animation = "slideOut 0.3s ease";
      setTimeout(() => {
        if (notification.parentNode) {
          notification.parentNode.removeChild(notification);
        }
      }, 300);
    }, 3000);
  }
}

// Add CSS animations for notifications
const style = document.createElement("style");
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Initialize the controller when the page loads
document.addEventListener("DOMContentLoaded", () => {
  new GuitarEffectsController();
});
