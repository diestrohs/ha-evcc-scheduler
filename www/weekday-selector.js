import { LitElement, html, css } from "https://cdn.jsdelivr.net/gh/lit/lit@2.8.0/+esm";

class WeekdaySelector extends LitElement {
  static properties = {
    weekdays: { type: Array },
    _open: { state: true },
    _direction: { state: true }, // up | down
  };

  constructor() {
    super();
    this.weekdays = [];
    this._open = false;
    this._direction = "down";
    this._outsideHandler = this._handleOutside.bind(this);
  }

  connectedCallback() {
    super.connectedCallback();
    document.addEventListener("click", this._outsideHandler);
  }

  disconnectedCallback() {
    document.removeEventListener("click", this._outsideHandler);
    super.disconnectedCallback();
  }

  static styles = css`
    :host {
      display: block;
    }

    .value-container {
      position: relative;
      width: 100%;
    }

    .value {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 8px 12px;
      gap: 8px;
      background: #37474f;
      border: 1px solid #555;
      border-radius: 8px;
      cursor: pointer;
      user-select: none;
      color: #ffffff;
    }

    .value:hover {
      border-color: #2196f3;
    }

    .value-text {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      flex: 1;
    }

    .arrow {
      opacity: 0.6;
      transform: rotate(0deg);
      transition: transform 0.25s cubic-bezier(0.4, 0.0, 0.2, 1);
      flex-shrink: 0;
    }

    .arrow.open {
      color: #2196f3;
      opacity: 0.8;
      transform: rotate(180deg);
    }

    .overlay {
      position: absolute;
      left: 0;
      right: 0;
      z-index: 100;
      background: #37474f;
      border: 1px solid #555;
      border-radius: 8px;
      padding: 8px 0;
      max-height: 300px;
      overflow-y: auto;
      animation: open 120ms ease-out;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }

    .overlay.down {
      top: calc(100% + 6px);
    }

    .overlay.up {
      bottom: calc(100% + 6px);
    }

    @keyframes open {
      from {
        opacity: 0;
        transform: scale(0.97);
      }
      to {
        opacity: 1;
        transform: scale(1);
      }
    }

    .item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 10px 12px;
      white-space: nowrap;
      color: #ffffff;
      cursor: pointer;
      user-select: none;
    }

    .item:hover {
      background: rgba(33, 150, 243, 0.1);
    }

    .checkbox {
      width: 18px;
      height: 18px;
      border: 2px solid #555;
      border-radius: 3px;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      cursor: pointer;
    }

    .checkbox.checked {
      background: #2196f3;
      border-color: #2196f3;
    }

    .checkbox.checked::after {
      content: "✓";
      color: white;
      font-size: 12px;
      font-weight: bold;
    }

    .item-name {
      flex: 1;
    }
  `;

  weekdayNames = {
    1: { name: "Montag", short: "Mo" },
    2: { name: "Dienstag", short: "Di" },
    3: { name: "Mittwoch", short: "Mi" },
    4: { name: "Donnerstag", short: "Do" },
    5: { name: "Freitag", short: "Fr" },
    6: { name: "Samstag", short: "Sa" },
    7: { name: "Sonntag", short: "So" },
  };

  _handleOutside(e) {
    if (this._open && !this.shadowRoot.contains(e.target)) {
      this._open = false;
    }
  }

  _toggleMenu(e) {
    e.stopPropagation();

    const anchor = this.shadowRoot.querySelector(".value");
    const rect = anchor.getBoundingClientRect();

    const spaceBelow = window.innerHeight - rect.bottom;
    const spaceAbove = rect.top;

    this._direction =
      spaceBelow < 250 && spaceAbove > spaceBelow ? "up" : "down";

    this._open = !this._open;
  }

  _toggleWeekday(weekday) {
    const index = this.weekdays.indexOf(weekday);
    if (index > -1) {
      this.weekdays.splice(index, 1);
    } else {
      this.weekdays.push(weekday);
    }
    this.weekdays.sort((a, b) => a - b);
    this.dispatchEvent(
      new CustomEvent("weekdays-changed", {
        detail: { weekdays: this.weekdays },
        bubbles: true,
        composed: true,
      })
    );
  }

  _summary() {
    if (!this.weekdays || this.weekdays.length === 0) return "Keine Tage ausgewählt";

    const sorted = [...this.weekdays].sort((a, b) => a - b);

    // Check if all weekdays
    if (sorted.length === 7) {
      return "Täglich";
    }

    // Check if workdays only
    if (sorted.length === 5 && sorted.every((d) => d >= 1 && d <= 5)) {
      return "Mo – Fr";
    }

    // Check if weekend only
    if (sorted.length === 2 && sorted[0] === 6 && sorted[1] === 7) {
      return "Sa – So";
    }

    // Otherwise, show individual days
    return sorted.map((d) => this.weekdayNames[d].short).join(", ");
  }

  render() {
    return html`
      <div class="value-container">
        <div class="value" @click=${this._toggleMenu}>
          <span class="value-text">${this._summary()}</span>
          <span class="arrow ${this._open ? "open" : ""}">▼</span>
        </div>

        ${this._open
          ? html`
              <div class="overlay ${this._direction}">
                ${[1, 2, 3, 4, 5, 6, 7].map(
                  (day) => html`
                    <div
                      class="item"
                      @click=${() => {
                        this._toggleWeekday(day);
                      }}
                    >
                      <div
                        class="checkbox ${this.weekdays.includes(day)
                          ? "checked"
                          : ""}"
                      ></div>
                      <span class="item-name">${this.weekdayNames[day].name}</span>
                    </div>
                  `
                )}
              </div>
            `
          : ""}
      </div>
    `;
  }
}

customElements.define("weekday-selector", WeekdaySelector);
