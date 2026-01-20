import { LitElement, html, css } from "https://cdn.jsdelivr.net/gh/lit/lit@2.8.0/+esm";
import "/local/evcc-scheduler-card/weekday-selector.js";
import "/local/evcc-scheduler-card/time-spinner.js";

class RepeatingSchedulerCard extends LitElement {
  static getConfigElement() {
    return document.createElement("repeating-scheduler-card-editor");
  }

  static getStubConfig() {
    return { type: "custom:repeating-scheduler-card", vehicle_id: "" };
  }

  static get styles() {
    return css`
      :host {
        --primary-color: #2196f3;
        --danger-color: #f44336;
        --success-color: #4caf50;
        --warning-color: #ff9800;
        --text-primary: #ffffff;
        --text-secondary: #b0bec5;
        --bg-primary: #263238;
        --bg-secondary: #37474f;
      }

      .card {
        background: var(--bg-primary);
        border-radius: 12px;
        padding: 16px;
        color: var(--text-primary);
      }

      .card-title {
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 16px;
        color: var(--text-primary);
      }

      .plans-list {
        display: flex;
        flex-direction: column;
        gap: 16px;
      }

      .plan-item {
        background: var(--bg-secondary);
        border-radius: 8px;
        padding: 16px;
        border-left: 4px solid var(--primary-color);
      }

      .plan-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      }

      .plan-title {
        font-size: 16px;
        font-weight: bold;
        color: var(--text-primary);
      }

      .plan-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
        margin-bottom: 16px;
      }

      .plan-field {
        display: flex;
        flex-direction: column;
        gap: 8px;
      }

      .field-label {
        font-size: 11px;
        color: var(--text-secondary);
        text-transform: uppercase;
        font-weight: bold;
        letter-spacing: 0.5px;
      }

      .field-value {
        font-size: 14px;
        color: var(--text-primary);
      }

      .field-input {
        background: var(--bg-primary);
        border: 1px solid #555;
        border-radius: 6px;
        padding: 8px;
        color: var(--text-primary);
        font-size: 14px;
      }

      .field-input:focus {
        outline: none;
        border-color: var(--primary-color);
        box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
      }

      .plan-actions {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: 12px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
      }

      .actions-left {
        display: flex;
        align-items: center;
        gap: 8px;
      }

      .actions-right {
        display: flex;
        align-items: center;
        gap: 4px;
      }

      .btn {
        background: transparent;
        border: none;
        color: var(--text-primary);
        cursor: pointer;
        padding: 6px;
        font-size: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s;
      }

      .btn ha-icon {
        --mdc-icon-size: 20px;
      }

      .btn:hover {
        opacity: 0.8;
        transform: scale(1.1);
      }

      .btn-save {
        color: var(--success-color);
      }

      .btn-delete {
        color: var(--danger-color);
      }

      .btn-disabled {
        opacity: 0.4;
        cursor: not-allowed;
      }

      .btn-disabled:hover {
        opacity: 0.4;
        transform: none;
      }

      .add-plan-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 50px;
        height: 50px;
        margin: 20px auto 0;
        background: rgba(76, 175, 80, 0.1);
        border: 2px dashed var(--success-color);
        border-radius: 12px;
        color: var(--success-color);
        font-size: 28px;
        cursor: pointer;
        transition: all 0.3s;
      }

      .add-plan-btn ha-icon {
        --mdc-icon-size: 28px;
      }

      .add-plan-btn:hover {
        background: rgba(76, 175, 80, 0.2);
        transform: scale(1.1);
      }

      .error {
        background: rgba(244, 67, 54, 0.1);
        border-left: 4px solid var(--danger-color);
        color: var(--danger-color);
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 16px;
      }

      .loading {
        text-align: center;
        padding: 20px;
        color: var(--text-secondary);
      }

      time-spinner {
        width: 100%;
      }

      weekday-selector {
        width: 100%;
      }
    `;
  }

  static get properties() {
    return {
      hass: { type: Object },
      config: { type: Object },
      vehicles: { type: Array },
      loading: { type: Boolean },
      error: { type: String },
      editingIndex: { type: Number }, // -1 für kein Edit, sonst Index
      editData: { type: Object },
      originalData: { type: Object },
    };
  }

  constructor() {
    super();
    this.vehicles = [];
    this.loading = false;
    this.error = null;
    this.editingIndex = -1;
    this.editData = {};
    this.originalData = {};
  }

  setConfig(config) {
    if (!config) {
      throw new Error("Config erforderlich");
    }
    this.config = config;
  }

  async connectedCallback() {
    super.connectedCallback();
    await this.fetchPlans();
  }

  async fetchPlans() {
    this.loading = true;
    this.error = null;

    try {
      const result = await this.hass.callWS({
        type: "scheduler/get",
      });

      const vehicles = result.vehicles || {};
      const vehicleList = Object.values(vehicles);
      
      // Setze vehicles auf leer wenn kein Fahrzeug ausgewählt
      this.vehicles = vehicleList.length > 0 ? vehicleList : [];
    } catch (err) {
      this.error = `Fehler beim Abrufen der Pläne: ${err.message}`;
      this.vehicles = [];
    } finally {
      this.loading = false;
    }
  }

  formatWeekdays(weekdays) {
    if (!weekdays || weekdays.length === 0) return "Täglich";

    const weekdayNames = {
      1: "Mo",
      2: "Di",
      3: "Mi",
      4: "Do",
      5: "Fr",
      6: "Sa",
      7: "So",
    };

    const sorted = [...weekdays].sort((a, b) => a - b);

    // Check if all weekdays
    if (sorted.length === 7) {
      return "Täglich";
    }

    // Check if workdays only
    if (sorted.length === 5 && sorted.every((d) => d >= 1 && d <= 5)) {
      return "Mo – Fr";
    }

    // Check if weekend only
    if (
      sorted.length === 2 &&
      sorted[0] === 6 &&
      sorted[1] === 7
    ) {
      return "Sa – So";
    }

    // Otherwise, show individual days
    return sorted.map((d) => weekdayNames[d]).join(", ");
  }

  async togglePlan(vehicleId, planIndex) {
    try {
      const vehicle = this.vehicles[0];
      if (!vehicle) return;

      const plan = vehicle.repeatingPlans[planIndex];
      if (!plan) return;

      const newActive = !plan.active;

      await this.hass.callWS({
        type: "scheduler/edit",
        plan_index: planIndex + 1, // 1-based
        active: newActive,
      });

      await this.fetchPlans();
    } catch (err) {
      this.error = `Fehler beim Togglen: ${err.message}`;
    }
  }

  startEdit(index) {
    const plan = this.vehicles[0]?.repeatingPlans[index];
    if (!plan) return;

    this.editingIndex = index;
    this.editData = { ...plan };
    this.originalData = { ...plan };
  }

  cancelEdit() {
    this.editingIndex = -1;
    this.editData = {};
    this.originalData = {};
  }

  hasChanges() {
    if (this.editingIndex === -1) return false;
    return JSON.stringify(this.editData) !== JSON.stringify(this.originalData);
  }

  async saveEdit() {
    if (this.editingIndex === -1) return;

    try {
      await this.hass.callWS({
        type: "scheduler/edit",
        plan_index: this.editingIndex + 1,
        time: this.editData.time,
        soc: parseInt(this.editData.soc),
        weekdays: this.editData.weekdays,
        active: this.editData.active,
      });

      this.editingIndex = -1;
      this.editData = {};
      this.originalData = {};
      await this.fetchPlans();
    } catch (err) {
      this.error = `Fehler beim Speichern: ${err.message}`;
    }
  }

  async deletePlan(index) {
    if (!confirm("Plan wirklich löschen?")) return;

    try {
      await this.hass.callWS({
        type: "scheduler/deleate",
        plan_index: index + 1,
      });

      await this.fetchPlans();
    } catch (err) {
      this.error = `Fehler beim Löschen: ${err.message}`;
    }
  }

  async addNewPlan() {
    try {
      await this.hass.callWS({
        type: "scheduler/add",
        time: "07:00",
        soc: 80,
        weekdays: [1, 2, 3, 4, 5],
        active: true,
      });

      await this.fetchPlans();
    } catch (err) {
      this.error = `Fehler beim Hinzufügen: ${err.message}`;
    }
  }

  render() {
    if (this.loading) {
      return html`
        <div class="card">
          <div class="loading">Lade Pläne...</div>
        </div>
      `;
    }

    const vehicle = this.vehicles[0];
    
    // Kein Fahrzeug ausgewählt - nichts anzeigen
    if (!vehicle) {
      return html``;
    }

    const plans = vehicle.repeatingPlans || [];

    return html`
      <div class="card">
        <div class="card-title">${vehicle.title} - Wiederholende Pläne</div>

        ${this.error ? html`<div class="error">${this.error}</div>` : ""}

        <div class="plans-list">
          ${plans.map((plan, index) => this.renderPlan(plan, index))}
        </div>

        <button class="add-plan-btn" @click=${this.addNewPlan} title="Neuen Plan hinzufügen">
          <ha-icon icon="mdi:plus"></ha-icon>
        </button>
      </div>
    `;
  }

  renderPlan(plan, index) {
    const isEditing = this.editingIndex === index;

    if (isEditing) {
      return html`
        <div class="plan-item">
          <div class="plan-header">
            <span class="plan-title">PLAN #${index + 1}</span>
          </div>

          <div class="plan-grid">
            <div class="plan-field">
              <div class="field-label">Wochentage</div>
              <weekday-selector
                .weekdays=${this.editData.weekdays || []}
                @weekdays-changed=${(e) => {
                  this.editData = { ...this.editData, weekdays: e.detail.weekdays };
                }}
              ></weekday-selector>
            </div>

            <div class="plan-field">
              <div class="field-label">Uhrzeit</div>
              <time-spinner
                .value=${this.editData.time || "07:00"}
                @time-changed=${(e) => {
                  this.editData = { ...this.editData, time: e.detail.time };
                }}
              ></time-spinner>
            </div>

            <div class="plan-field">
              <div class="field-label">Ladeziel (%)</div>
              <input
                type="number"
                class="field-input"
                min="10"
                max="100"
                step="5"
                .value=${this.editData.soc || 80}
                @input=${(e) => {
                  this.editData = { ...this.editData, soc: parseInt(e.target.value) };
                }}
              />
            </div>

            <div class="plan-field">
              <div class="field-label">Status</div>
              <div class="toggle-switch">
                <input
                  type="checkbox"
                  class="switch-input"
                  .checked=${this.editData.active || true}
                  @change=${(e) => {
                    this.editData = { ...this.editData, active: e.target.checked };
                  }}
                />
                <span>${this.editData.active ? "aktiv" : "inaktiv"}</span>
              </div>
            </div>
          </div>

          <div class="plan-actions">
            <div class="actions-left">
              <button
                class="btn btn-save"
                @click=${this.saveEdit}
                title="Speichern"
              >
                <ha-icon icon="mdi:content-save"></ha-icon>
              </button>
              <button
                class="btn ${this.hasChanges() ? "" : "btn-disabled"}"
                @click=${this.cancelEdit}
                title="Abbrechen"
              >
                <ha-icon icon="mdi:close"></ha-icon>
              </button>
            </div>
            <button
              class="btn btn-delete"
              @click=${() => this.deletePlan(index)}
              title="Löschen"
            >
              <ha-icon icon="mdi:delete"></ha-icon>
            </button>
          </div>
        </div>
      `;
    } else {
      return html`
        <div class="plan-item">
          <div class="plan-header">
            <span class="plan-title">PLAN #${index + 1}</span>
            <span class="plan-status">${plan.active ? "aktiv" : "inaktiv"}</span>
          </div>

          <div class="plan-grid">
            <div class="plan-field">
              <div class="field-label">Wochentage</div>
              <div class="field-value">${this.formatWeekdays(plan.weekdays)}</div>
            </div>

            <div class="plan-field">
              <div class="field-label">Uhrzeit</div>
              <div class="field-value">${plan.time}</div>
            </div>

            <div class="plan-field">
              <div class="field-label">Ladeziel</div>
              <div class="field-value">${plan.soc}%</div>
            </div>
          </div>

          <div class="plan-actions">
            <div class="actions-left">
              <div class="toggle-switch">
                <input
                  type="checkbox"
                  class="switch-input"
                  .checked=${plan.active}
                  @change=${async () => {
                    try {
                      await this.hass.callWS({
                        type: "scheduler/edit",
                        plan_index: index + 1,
                        active: !plan.active,
                      });
                      await this.fetchPlans();
                    } catch (err) {
                      this.error = `Fehler: ${err.message}`;
                    }
                  }}
                />
              </div>
            </div>

            <div class="actions-right">
              <button
                class="btn"
                @click=${() => this.startEdit(index)}
                title="Bearbeiten"
                style="color: #2196f3;"
              >
                <ha-icon icon="mdi:pencil"></ha-icon>
              </button>
              <button
                class="btn btn-delete"
                @click=${() => this.deletePlan(index)}
                title="Löschen"
              >
                <ha-icon icon="mdi:delete"></ha-icon>
              </button>
            </div>
          </div>
        </div>
      `;
    }
  }
}

customElements.define("repeating-scheduler-card", RepeatingSchedulerCard);

// Register card
window.customCards = window.customCards || [];
window.customCards.push({
  type: "repeating-scheduler-card",
  name: "EVCC Repeating Scheduler",
  description: "Verwaltung wiederholender Ladepläne für EVCC",
});
