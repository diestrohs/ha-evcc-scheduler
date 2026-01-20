import { LitElement, html, css } from "https://cdn.jsdelivr.net/gh/lit/lit@2.8.0/+esm";

class RepeatingSchedulerCardEditor extends LitElement {
  static get styles() {
    return css`
      :host {
        --primary-color: #2196f3;
        --bg-primary: #263238;
        --text-primary: #ffffff;
      }

      .editor {
        display: flex;
        flex-direction: column;
        gap: 16px;
        padding: 16px;
        background: var(--bg-primary);
        border-radius: 8px;
      }

      .info-box {
        padding: 12px;
        background: rgba(33, 150, 243, 0.1);
        border-left: 3px solid var(--primary-color);
        border-radius: 4px;
        color: var(--text-primary);
        font-size: 14px;
      }
    `;
  }

  static get properties() {
    return {
      config: { type: Object },
    };
  }

  setConfig(config) {
    this.config = { ...config };
  }

  render() {
    return html`
      <div class="editor">
        <div class="info-box">
          ℹ️ <strong>Automatische Fahrzeugauswahl</strong><br/>
          Diese Card verwendet automatisch das aktuell in EVCC ausgewählte Fahrzeug.
          Eine Konfiguration ist nicht erforderlich!
        </div>
      </div>
    `;
  }
}

customElements.define(
  "repeating-scheduler-card-editor",
  RepeatingSchedulerCardEditor
);
