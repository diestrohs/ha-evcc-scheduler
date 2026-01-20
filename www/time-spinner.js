class TimeSpinner extends HTMLElement {
  constructor() {
    super();
    this.itemHeight = 48;
    this.visibleItems = 5;
    this.repeat = 3;
    this.selectedHour = 0;
    this.selectedMinute = 0;
    this._value = "00:00";
  }

  set value(timeString) {
    this._value = timeString;
    const [h, m] = timeString.split(":").map(Number);
    this.selectedHour = h;
    this.selectedMinute = m;
    this.updateDisplay();
  }

  get value() {
    return `${String(this.selectedHour).padStart(2, "0")}:${String(this.selectedMinute).padStart(2, "0")}`;
  }

  connectedCallback() {
    this.render();
  }

  render() {
    this.innerHTML = `
      <div class="time-spinner-wrapper">
        <button class="time-btn">--:--</button>
      </div>
    `;

    this.style.cssText = `
      display: block;
    `;

    const style = document.createElement("style");
    style.textContent = `
      .time-spinner-wrapper {
        display: flex;
        justify-content: center;
      }

      .time-btn {
        width: 100%;
        height: 40px;
        border: 1px solid #555;
        border-radius: 8px;
        background: #37474f;
        color: #ffffff;
        font-size: 16px;
        cursor: pointer;
        transition: all 0.2s;
      }

      .time-btn:hover {
        border-color: #2196f3;
        box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
      }

      .overlay {
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
      }

      .overlay-content {
        background: #37474f;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
      }

      .wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        height: ${this.visibleItems * this.itemHeight}px;
        position: relative;
        overflow: hidden;
        margin-bottom: 20px;
      }

      .wheel {
        width: 80px;
        height: 100%;
        overflow-y: scroll;
        scrollbar-width: none;
        -webkit-overflow-scrolling: touch;
      }

      .wheel::-webkit-scrollbar {
        display: none;
      }

      .item {
        height: ${this.itemHeight}px;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 18px;
        opacity: 0.35;
        user-select: none;
        color: #ffffff;
      }

      .item.active {
        opacity: 1;
        font-weight: bold;
      }

      .colon {
        font-size: 32px;
        padding: 0 12px;
        font-weight: bold;
        color: #ffffff;
      }

      .indicator {
        position: absolute;
        top: 50%;
        left: 0;
        right: 0;
        height: ${this.itemHeight}px;
        margin-top: -${this.itemHeight / 2}px;
        border-top: 2px solid #2196f3;
        border-bottom: 2px solid #2196f3;
        pointer-events: none;
      }

      .buttons {
        display: flex;
        justify-content: flex-end;
        gap: 8px;
      }

      .buttons button {
        height: 40px;
        padding: 8px 20px;
        border-radius: 8px;
        border: none;
        background: transparent;
        border: 1px solid #555;
        color: #ffffff;
        cursor: pointer;
        font-size: 14px;
        font-weight: bold;
        transition: all 0.2s;
      }

      .buttons button:hover {
        border-color: #2196f3;
        background: rgba(33, 150, 243, 0.1);
      }

      .buttons button.ok {
        background: #2196f3;
        border-color: #2196f3;
        color: #ffffff;
      }

      .buttons button.ok:hover {
        background: #1976d2;
      }
    `;

    this.appendChild(style);

    const timeBtn = this.querySelector(".time-btn");
    timeBtn.textContent = this._value;
    timeBtn.onclick = (e) => {
      e.stopPropagation();
      this.openOverlay();
    };

    this.updateDisplay();
  }

  updateDisplay() {
    const timeBtn = this.querySelector(".time-btn");
    if (timeBtn) {
      timeBtn.textContent = this.value;
    }
  }

  openOverlay() {
    const overlay = document.createElement("div");
    overlay.className = "overlay";

    const content = document.createElement("div");
    content.className = "overlay-content";

    const wrapper = document.createElement("div");
    wrapper.className = "wrapper";

    this.hoursEl = document.createElement("div");
    this.hoursEl.className = "wheel";

    const colon = document.createElement("div");
    colon.className = "colon";
    colon.textContent = ":";

    this.minutesEl = document.createElement("div");
    this.minutesEl.className = "wheel";

    const indicator = document.createElement("div");
    indicator.className = "indicator";

    wrapper.append(this.hoursEl, colon, this.minutesEl, indicator);
    content.append(wrapper);

    const buttons = document.createElement("div");
    buttons.className = "buttons";

    const cancel = document.createElement("button");
    cancel.textContent = "Abbrechen";
    cancel.onclick = () => {
      overlay.remove();
    };

    const ok = document.createElement("button");
    ok.className = "ok";
    ok.textContent = "OK";
    ok.onclick = () => {
      overlay.remove();
      this.dispatchEvent(
        new CustomEvent("time-changed", {
          detail: { time: this.value },
          bubbles: true,
          composed: true,
        })
      );
    };

    buttons.append(cancel, ok);
    content.append(buttons);

    overlay.append(content);
    document.body.append(overlay);

    this.buildWheel(this.hoursEl, 24, (v) => (this.selectedHour = v));
    this.buildWheel(this.minutesEl, 60, (v) => (this.selectedMinute = v));

    const [h, m] = this._value.split(":").map(Number);
    this.selectedHour = h;
    this.selectedMinute = m;

    this.setInitial(this.hoursEl, 24, this.selectedHour);
    this.setInitial(this.minutesEl, 60, this.selectedMinute);

    // Close on outside click
    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) {
        overlay.remove();
      }
    });
  }

  buildWheel(container, count, onChange) {
    container.innerHTML = "";
    const pad = Math.floor(this.visibleItems / 2);
    container.items = [];

    const list = document.createElement("div");
    list.append(
      Object.assign(document.createElement("div"), {
        style: `height:${pad * this.itemHeight}px`,
      })
    );

    for (let r = 0; r < this.repeat; r++) {
      for (let i = 0; i < count; i++) {
        const d = document.createElement("div");
        d.className = "item";
        d.textContent = String(i).padStart(2, "0");
        list.append(d);
        container.items.push(d);
      }
    }

    list.append(
      Object.assign(document.createElement("div"), {
        style: `height:${pad * this.itemHeight}px`,
      })
    );

    container.append(list);

    let t;
    container.addEventListener("scroll", () => {
      clearTimeout(t);
      t = setTimeout(() => this.snap(container, count, onChange), 80);
    });
  }

  snap(container, count, onChange) {
    const idx = Math.round(container.scrollTop / this.itemHeight);
    container.scrollTo({ top: idx * this.itemHeight, behavior: "smooth" });

    const logical = ((idx % count) + count) % count;
    onChange(logical);

    container.items.forEach((e, i) =>
      e.classList.toggle("active", i === idx)
    );
  }

  setInitial(container, count, idx) {
    requestAnimationFrame(() => {
      const mid = Math.floor(this.repeat / 2) * count;
      container.scrollTop = (mid + idx) * this.itemHeight;
      this.snap(container, count, () => {});
    });
  }
}

customElements.define("time-spinner", TimeSpinner);
