import sys
import tkinter as tk
import tkinter.font as tkfont
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tkinter import ttk, messagebox

import numpy as np
import matplotlib
from matplotlib import font_manager
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

# katalog projektu na sciezce importu, zeby dzialalo tez `python ui/app.py`
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data.stock_data import get_stock_data
from estimation.ckf import run_ckf, combine_forecasts
from control.cost_function import plan_from_ckf
from helpers.config import SIGMA_V, KAPPA, NUM_OF_FILTERS


PRICE_MODES = {"Close": "Close", "Open": "Open", "High": "High", "Low": "Low"}
PERIODS = ["6mo", "1y", "2y", "5y", "10y"]
HISTORY_ON_PLOT = 60  # ile ostatnich dni historii pokazac na wykresie

# paleta kolorow (ciemny motyw)
BG = "#0e1117"
SURFACE = "#161b26"
SURFACE_2 = "#1e2433"
FIELD = "#0f141e"
BORDER = "#2a3142"
TEXT = "#e6e9f0"
MUTED = "#8a93a8"
ACCENT = "#7c6cf6"
ACCENT_HOVER = "#9286ff"
BLUE = "#5b9dff"
AMBER = "#f5a524"
GREEN = "#2fd27a"
RED = "#ff5d6c"

FONT_CANDIDATES = ["Inter", "Cantarell", "Noto Sans", "DejaVu Sans"]


def pick_font(available: set[str]) -> str:
    return next((name for name in FONT_CANDIDATES if name in available), "TkDefaultFont")


def run_analysis(params: dict) -> dict:
    """
        Pobiera dane, liczy wagi CKF, prognoze i plan MPC.
        Wywolywane w osobnym watku, nie dotyka GUI.

        przyjmuje: slownik parametrow z formularza
        zwraca: slownik z wynikami do wyswietlenia
    """
    price_history = [float(price) for price in
                     get_stock_data(params["ticker"], params["period"], "1d", params["mode"])]
    days = params["days"]
    if len(price_history) <= 2 * days:
        raise ValueError("Za malo danych historycznych dla wybranego horyzontu")

    filter_orders = list(range(1, params["num_filters"] + 1))
    weights, forecasts_on_window, window_prices = run_ckf(
        price_history, filter_orders, params["sigma_v2"], params["kappa"], days)
    window_combined = combine_forecasts(weights, forecasts_on_window, days)

    plan = plan_from_ckf(price_history, params["cash"], params["stocks"], filter_orders,
                         params["sigma_v2"], params["kappa"], weights, days,
                         params["spend_fraction"])

    return {"params": params, "price_history": price_history, "weights": weights,
            "forecasts_on_window": forecasts_on_window, "window_prices": window_prices,
            "window_combined": window_combined, "plan": plan}


def style_axes(ax):
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(BORDER)
    ax.tick_params(colors=MUTED, labelsize=9, length=0, pad=6)
    ax.grid(color=BORDER, linewidth=0.6, alpha=0.6)
    ax.set_axisbelow(True)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CKF · MPC — planowanie transakcji")
        self.geometry("1360x860")
        self.minsize(1100, 700)
        self.configure(background=BG)

        self.executor = ThreadPoolExecutor(max_workers=1)
        self.future = None

        self.vars = {
            "ticker": tk.StringVar(value="AAPL"),
            "period": tk.StringVar(value="2y"),
            "mode": tk.StringVar(value="Close"),
            "days": tk.StringVar(value="5"),
            "cash": tk.StringVar(value="5000"),
            "stocks": tk.StringVar(value="10"),
            "kappa": tk.StringVar(value=str(KAPPA)),
            "num_filters": tk.StringVar(value=str(NUM_OF_FILTERS)),
            "sigma_v2": tk.StringVar(value=f"{SIGMA_V:.4f}"),
            "spend_fraction": tk.StringVar(value="0.10"),
        }
        self.status = tk.StringVar(value="Gotowy")

        self._setup_theme()
        self._build_layout()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ---------- motyw ----------

    def _setup_theme(self):
        family = pick_font(set(tkfont.families(self)))
        self.fonts = {
            "base": (family, 10),
            "small": (family, 9),
            "section": (family, 8, "bold"),
            "title": (family, 17, "bold"),
            "heading": (family, 22, "bold"),
            "kpi": (family, 18, "bold"),
            "button": (family, 11, "bold"),
        }
        for name in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont"):
            tkfont.nametofont(name).configure(family=family, size=10)

        mpl_family = pick_font({font.name for font in font_manager.fontManager.ttflist})
        matplotlib.rcParams.update({"font.family": mpl_family, "text.color": TEXT,
                                    "axes.labelcolor": MUTED, "axes.titlecolor": TEXT})

        # zwykle widgety tk (toolbar matplotlib, lista comboboxa)
        for pattern, value in [("*Background", SURFACE), ("*Foreground", TEXT),
                               ("*activeBackground", SURFACE_2), ("*activeForeground", TEXT),
                               ("*highlightThickness", 0), ("*borderWidth", 0),
                               ("*TCombobox*Listbox.background", SURFACE_2),
                               ("*TCombobox*Listbox.foreground", TEXT),
                               ("*TCombobox*Listbox.selectBackground", ACCENT),
                               ("*TCombobox*Listbox.selectForeground", "#ffffff")]:
            self.option_add(pattern, value)

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", background=BG, foreground=TEXT, fieldbackground=FIELD,
                        bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER,
                        troughcolor=SURFACE_2, focuscolor=ACCENT, selectbackground=ACCENT,
                        selectforeground="#ffffff", insertcolor=TEXT, font=self.fonts["base"])

        style.configure("TFrame", background=BG)
        style.configure("Sidebar.TFrame", background=SURFACE)
        style.configure("Card.TFrame", background=SURFACE)

        style.configure("TLabel", background=BG, foreground=TEXT)
        style.configure("Muted.TLabel", background=BG, foreground=MUTED)
        style.configure("Heading.TLabel", background=BG, font=self.fonts["heading"])
        style.configure("Sidebar.TLabel", background=SURFACE, foreground=MUTED)
        style.configure("Title.TLabel", background=SURFACE, foreground=TEXT, font=self.fonts["title"])
        style.configure("Subtitle.TLabel", background=SURFACE, foreground=MUTED, font=self.fonts["small"])
        style.configure("Section.TLabel", background=SURFACE, foreground=ACCENT_HOVER, font=self.fonts["section"])
        style.configure("Hint.TLabel", background=SURFACE_2, foreground=MUTED, font=self.fonts["small"])
        style.configure("CardTitle.TLabel", background=SURFACE, foreground=MUTED, font=self.fonts["small"])
        style.configure("CardValue.TLabel", background=SURFACE, foreground=TEXT, font=self.fonts["kpi"])
        style.configure("CardSub.TLabel", background=SURFACE, foreground=MUTED, font=self.fonts["small"])
        style.configure("Pill.TLabel", background=SURFACE_2, foreground=MUTED, padding=(12, 5),
                        font=self.fonts["small"])

        field_options = dict(fieldbackground=FIELD, foreground=TEXT, bordercolor=BORDER,
                             lightcolor=FIELD, darkcolor=FIELD, padding=(8, 5),
                             arrowcolor=MUTED, background=SURFACE_2)
        field_map = dict(bordercolor=[("focus", ACCENT), ("hover", "#3a4258")],
                         lightcolor=[("focus", ACCENT)], arrowcolor=[("hover", TEXT)])
        for widget in ("TEntry", "TSpinbox", "TCombobox"):
            style.configure(widget, **field_options)
            style.map(widget, **field_map)
        style.map("TCombobox", fieldbackground=[("readonly", FIELD)], foreground=[("readonly", TEXT)],
                  selectbackground=[("readonly", FIELD)], selectforeground=[("readonly", TEXT)],
                  bordercolor=[("focus", ACCENT), ("hover", "#3a4258")])

        style.configure("Accent.TButton", background=ACCENT, foreground="#ffffff", bordercolor=ACCENT,
                        lightcolor=ACCENT, darkcolor=ACCENT, padding=(12, 11), font=self.fonts["button"],
                        focuscolor=ACCENT)
        style.map("Accent.TButton",
                  background=[("disabled", SURFACE_2), ("pressed", "#6a5ae0"), ("active", ACCENT_HOVER)],
                  bordercolor=[("disabled", SURFACE_2), ("active", ACCENT_HOVER)],
                  lightcolor=[("disabled", SURFACE_2), ("active", ACCENT_HOVER)],
                  darkcolor=[("disabled", SURFACE_2), ("active", ACCENT_HOVER)],
                  foreground=[("disabled", MUTED)])

        style.configure("Accent.Horizontal.TProgressbar", background=ACCENT, troughcolor=SURFACE,
                        bordercolor=SURFACE, lightcolor=ACCENT, darkcolor=ACCENT, thickness=3)

        style.configure("TNotebook", background=BG, borderwidth=0, tabmargins=(0, 0, 0, 0))
        style.configure("TNotebook.Tab", background=BG, foreground=MUTED, padding=(16, 8),
                        bordercolor=BG, lightcolor=BG, darkcolor=BG, font=self.fonts["base"])
        style.map("TNotebook.Tab",
                  background=[("selected", SURFACE), ("active", SURFACE_2)],
                  foreground=[("selected", TEXT), ("active", TEXT)],
                  bordercolor=[("selected", SURFACE)], lightcolor=[("selected", ACCENT)])

        style.configure("Treeview", background=SURFACE, fieldbackground=SURFACE, foreground=TEXT,
                        rowheight=34, bordercolor=SURFACE, lightcolor=SURFACE, darkcolor=SURFACE)
        style.map("Treeview", background=[("selected", SURFACE_2)], foreground=[("selected", TEXT)])
        style.configure("Treeview.Heading", background=SURFACE_2, foreground=MUTED, relief="flat",
                        padding=(10, 8), bordercolor=SURFACE_2, lightcolor=SURFACE_2,
                        darkcolor=SURFACE_2, font=self.fonts["section"])
        style.map("Treeview.Heading", background=[("active", SURFACE_2)])
        style.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

    # ---------- uklad okna ----------

    def _build_layout(self):
        sidebar = ttk.Frame(self, style="Sidebar.TFrame", padding=(22, 22, 22, 18), width=300)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        main_area = ttk.Frame(self, padding=(24, 20, 24, 20))
        main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._build_form(sidebar)
        self._build_results(main_area)

    def _build_form(self, parent):
        ttk.Label(parent, text="MPC", style="Title.TLabel").pack(anchor=tk.W)
        ttk.Label(parent, text="Filtry Kalmana + planowanie transakcji",
                  style="Subtitle.TLabel").pack(anchor=tk.W, pady=(2, 14))

        def section(title):
            ttk.Label(parent, text=title.upper(), style="Section.TLabel").pack(anchor=tk.W, pady=(10, 6))
            frame = ttk.Frame(parent, style="Sidebar.TFrame")
            frame.pack(fill=tk.X)
            frame.columnconfigure(1, weight=1)
            return frame

        def row(frame, r, label, widget):
            ttk.Label(frame, text=label, style="Sidebar.TLabel").grid(
                row=r, column=0, sticky=tk.W, pady=3, padx=(0, 10))
            widget.grid(row=r, column=1, sticky=tk.EW, pady=3)

        data = section("Dane")
        row(data, 0, "Ticker", ttk.Entry(data, textvariable=self.vars["ticker"], width=10))
        row(data, 1, "Okres", ttk.Combobox(data, textvariable=self.vars["period"],
                                           values=PERIODS, state="readonly", width=8))
        row(data, 2, "Cena", ttk.Combobox(data, textvariable=self.vars["mode"],
                                          values=list(PRICE_MODES), state="readonly", width=8))

        portfolio = section("Portfel")
        row(portfolio, 0, "Gotówka [$]", ttk.Entry(portfolio, textvariable=self.vars["cash"], width=10))
        row(portfolio, 1, "Liczba akcji", ttk.Entry(portfolio, textvariable=self.vars["stocks"], width=10))
        row(portfolio, 2, "Limit / dzień",
            ttk.Spinbox(portfolio, textvariable=self.vars["spend_fraction"],
                        from_=0.01, to=1.0, increment=0.01, width=8))

        model = section("Model")
        row(model, 0, "Horyzont L",
            ttk.Spinbox(model, textvariable=self.vars["days"], from_=1, to=60, width=8))
        row(model, 1, "Liczba filtrów",
            ttk.Spinbox(model, textvariable=self.vars["num_filters"], from_=1, to=10, width=8))
        row(model, 2, "Kappa (> 0)",
            ttk.Spinbox(model, textvariable=self.vars["kappa"], from_=0.1, to=1000,
                        increment=0.5, width=8))
        row(model, 3, "σ²ᵥ", ttk.Entry(model, textvariable=self.vars["sigma_v2"], width=10))

        hint = ttk.Label(parent, style="Hint.TLabel", padding=(10, 8), wraplength=240, justify=tk.LEFT, anchor=tk.W,
                         text="Kappę warto dobierać do liczby filtrów (rzędu modelu).")
        hint.pack(fill=tk.X, pady=(14, 0))

        self.progress = ttk.Progressbar(parent, mode="determinate", style="Accent.Horizontal.TProgressbar")
        self.progress.pack(side=tk.BOTTOM, fill=tk.X, pady=(6, 0))
        self.run_button = ttk.Button(parent, text="Oblicz plan  →", style="Accent.TButton",
                                     command=self._on_run, cursor="hand2")
        self.run_button.pack(side=tk.BOTTOM, fill=tk.X)

        self.bind("<Return>", lambda _: self._on_run())

    def _build_results(self, parent):
        header = ttk.Frame(parent)
        header.pack(fill=tk.X, pady=(0, 16))
        self.heading = ttk.Label(header, text="Brak wyników", style="Heading.TLabel")
        self.heading.pack(side=tk.LEFT, anchor=tk.S)
        self.subheading = ttk.Label(header, text="", style="Muted.TLabel")
        self.subheading.pack(side=tk.LEFT, anchor=tk.S, padx=(12, 0), pady=(0, 5))
        ttk.Label(header, textvariable=self.status, style="Pill.TLabel").pack(side=tk.RIGHT, anchor=tk.CENTER)

        cards = ttk.Frame(parent)
        cards.pack(fill=tk.X, pady=(0, 16))
        self.cards = {}
        for column, (key, title, color) in enumerate([
                ("price", "Cena dziś", BLUE),
                ("value_now", "Wartość portfela", ACCENT),
                ("value_after", "Wartość po L dniach", ACCENT_HOVER),
                ("profit", "Przewidywany zysk", GREEN),
                ("mae", "Błąd prognozy (MAE)", AMBER)]):
            cards.columnconfigure(column, weight=1, uniform="cards")
            card = ttk.Frame(cards, style="Card.TFrame")
            card.grid(row=0, column=column, sticky=tk.NSEW, padx=(0 if column == 0 else 12, 0))
            tk.Frame(card, background=color, height=3).pack(fill=tk.X)
            body = ttk.Frame(card, style="Card.TFrame", padding=(16, 12, 16, 14))
            body.pack(fill=tk.BOTH, expand=True)
            ttk.Label(body, text=title, style="CardTitle.TLabel").pack(anchor=tk.W)
            value = ttk.Label(body, text="—", style="CardValue.TLabel")
            value.pack(anchor=tk.W, pady=(4, 0))
            sub = ttk.Label(body, text=" ", style="CardSub.TLabel")
            sub.pack(anchor=tk.W)
            self.cards[key] = (value, sub)

        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)

        # zakladka: wykres
        chart_tab = ttk.Frame(notebook, style="Card.TFrame", padding=8)
        notebook.add(chart_tab, text="  Wykres  ")
        self.figure = Figure(figsize=(8, 5), dpi=100, layout="constrained", facecolor=SURFACE)
        self.canvas = FigureCanvasTkAgg(self.figure, master=chart_tab)
        toolbar = NavigationToolbar2Tk(self.canvas, chart_tab, pack_toolbar=False)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # zakladka: plan transakcji
        plan_tab = ttk.Frame(notebook, style="Card.TFrame", padding=12)
        notebook.add(plan_tab, text="  Plan transakcji  ")
        self.plan_table = self._make_table(plan_tab, [
            ("day", "DZIEŃ", 80), ("price", "CENA", 140), ("action", "AKCJA", 120),
            ("trade", "KUP / SPRZEDAJ", 150), ("stocks_after", "AKCJE PO TRANSAKCJI", 180),
            ("spending", "WYDATEK", 150)])
        self.plan_table.pack(fill=tk.BOTH, expand=True)

        # zakladka: wagi modeli
        weights_tab = ttk.Frame(notebook, style="Card.TFrame", padding=12)
        notebook.add(weights_tab, text="  Wagi modeli  ")
        self.weights_table = self._make_table(weights_tab, [
            ("order", "RZĄD FILTRA", 120), ("weight", "WAGA μ", 140), ("mae", "MAE NA OKNIE", 140)])
        self.weights_table.pack(side=tk.LEFT, fill=tk.Y)
        self.weights_figure = Figure(figsize=(5, 4), dpi=100, layout="constrained", facecolor=SURFACE)
        self.weights_canvas = FigureCanvasTkAgg(self.weights_figure, master=weights_tab)
        self.weights_canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(16, 0))

        self._draw_placeholder(self.figure, self.canvas,
                               "Ustaw parametry i kliknij „Oblicz plan”")
        self._draw_placeholder(self.weights_figure, self.weights_canvas, "")

    def _make_table(self, parent, columns):
        table = ttk.Treeview(parent, columns=[key for key, _, _ in columns], show="headings",
                             selectmode="browse")
        for key, heading, width in columns:
            table.heading(key, text=heading, anchor=tk.E)
            table.column(key, anchor=tk.E, width=width, stretch=True)
        table.tag_configure("odd", background=SURFACE)
        table.tag_configure("even", background="#1a2030")
        table.tag_configure("buy", foreground=GREEN)
        table.tag_configure("sell", foreground=RED)
        table.tag_configure("hold", foreground=MUTED)
        return table

    # ---------- obsluga zdarzen ----------

    def _read_params(self) -> dict:
        v = {key: var.get().strip() for key, var in self.vars.items()}
        if not v["ticker"]:
            raise ValueError("Podaj ticker")
        params = {
            "ticker": v["ticker"].upper(),
            "period": v["period"],
            "mode": PRICE_MODES[v["mode"]],
            "days": int(v["days"]),
            "cash": float(v["cash"].replace(",", ".")),
            "stocks": float(v["stocks"].replace(",", ".")),
            "kappa": float(v["kappa"].replace(",", ".")),
            "num_filters": int(v["num_filters"]),
            "sigma_v2": float(v["sigma_v2"].replace(",", ".")),
            "spend_fraction": float(v["spend_fraction"].replace(",", ".")),
        }
        if params["kappa"] <= 0:
            raise ValueError("Kappa musi byc wieksza od 0")
        if params["days"] < 1:
            raise ValueError("Horyzont musi byc >= 1")
        if params["num_filters"] < 1:
            raise ValueError("Liczba filtrow musi byc >= 1")
        if params["sigma_v2"] <= 0:
            raise ValueError("sigma_v2 musi byc wieksze od 0")
        if params["cash"] < 0 or params["stocks"] < 0:
            raise ValueError("Gotowka i liczba akcji nie moga byc ujemne")
        if not 0 < params["spend_fraction"] <= 1:
            raise ValueError("Limit wydatku musi byc w przedziale (0, 1]")
        return params

    def _on_run(self):
        if self.future is not None and not self.future.done():
            return
        try:
            params = self._read_params()
        except ValueError as error:
            messagebox.showerror("Bledne parametry", str(error))
            return

        self.run_button.state(["disabled"])
        self.run_button.configure(text="Obliczanie…")
        self.progress.configure(mode="indeterminate")
        self.progress.start(10)
        self.status.set(f"⏳  Pobieranie danych {params['ticker']}…")
        self.future = self.executor.submit(run_analysis, params)
        self.after(100, self._poll_result)

    def _poll_result(self):
        if not self.future.done():
            self.after(100, self._poll_result)
            return

        self.progress.stop()
        self.progress.configure(mode="determinate", value=0)
        self.run_button.state(["!disabled"])
        self.run_button.configure(text="Oblicz plan  →")
        try:
            result = self.future.result()
        except Exception as error:
            self.status.set("✕  Błąd obliczeń")
            messagebox.showerror("Blad", f"{type(error).__name__}: {error}")
            return

        if result["plan"]["status"] != "ok":
            self.status.set("✕  Solver LP nie znalazł rozwiązania")
            messagebox.showerror("Solver LP", str(result["plan"]["status"]))
            return

        self._show_result(result)

    def _on_close(self):
        self.executor.shutdown(wait=False, cancel_futures=True)
        self.destroy()

    # ---------- wyswietlanie wynikow ----------

    def _set_card(self, key, value, sub=" ", color=TEXT):
        value_label, sub_label = self.cards[key]
        value_label.configure(text=value, foreground=color)
        sub_label.configure(text=sub)

    def _show_result(self, result: dict):
        params, plan = result["params"], result["plan"]
        prices = plan["prices"]
        value_now = params["cash"] + params["stocks"] * prices[0]
        profit = plan["V_after"] - value_now
        mae = float(np.mean(np.abs(np.subtract(result["window_combined"], result["window_prices"]))))
        forecast_change = prices[-1] - prices[0]

        self.heading.configure(text=params["ticker"])
        self.subheading.configure(text=f"{params['mode']} · {params['period']} · "
                                       f"{params['num_filters']} filtrów · κ = {params['kappa']:g}")

        self._set_card("price", f"${prices[0]:,.2f}",
                       f"prognoza za {params['days']} dni: {forecast_change:+.2f}")
        self._set_card("value_now", f"${value_now:,.2f}",
                       f"{params['cash']:,.0f} $ + {params['stocks']:g} akcji")
        self._set_card("value_after", f"${plan['V_after']:,.2f}", f"po {params['days']} dniach")
        self._set_card("profit", f"{profit:+,.2f} $", f"{100 * profit / value_now:+.2f}% wartości portfela",
                       GREEN if profit >= 0 else RED)
        self._set_card("mae", f"{mae:.3f}", f"{100 * mae / prices[0]:.2f}% ceny · okno {params['days']} dni")

        self.plan_table.delete(*self.plan_table.get_children())
        for day, (price, trade, stocks_before) in enumerate(zip(prices, plan["u_sequence"], plan["N_sequence"])):
            action, tag = ("▲ KUP", "buy") if trade > 1e-9 else ("▼ SPRZEDAJ", "sell") if trade < -1e-9 \
                else ("● TRZYMAJ", "hold")
            self.plan_table.insert("", tk.END, tags=(tag, "even" if day % 2 else "odd"), values=(
                day, f"{price:,.2f}", action, f"{trade:+.2f}", f"{stocks_before + trade:.2f}",
                f"{trade * price:+,.2f} $"))

        self.weights_table.delete(*self.weights_table.get_children())
        for index, (order, weight) in enumerate(result["weights"].items()):
            model_mae = float(np.mean(np.abs(np.subtract(result["forecasts_on_window"][order],
                                                         result["window_prices"]))))
            self.weights_table.insert("", tk.END, tags=("even" if index % 2 else "odd",),
                                      values=(order, f"{weight:.4f}", f"{model_mae:.3f}"))

        self._draw_chart(result)
        self._draw_weights(result["weights"])
        self.status.set("✓  Gotowe")

    def _draw_placeholder(self, figure, canvas, text):
        figure.clear()
        ax = figure.add_subplot()
        ax.set_facecolor(SURFACE)
        ax.text(0.5, 0.5, text, ha="center", va="center", color=MUTED, fontsize=13)
        ax.set_axis_off()
        canvas.draw_idle()

    def _draw_chart(self, result: dict):
        """
            Gorny wykres: historia, prognoza na oknie oceny (test wsteczny) i prognoza w przyszlosc.
            Dolny wykres: plan transakcji (ile akcji kupic/sprzedac w kazdym dniu).
        """
        params, plan = result["params"], result["plan"]
        history = result["price_history"]
        days = params["days"]
        n = len(history)

        self.figure.clear()
        ax_price, ax_trade = self.figure.subplots(2, 1, sharex=True, height_ratios=[3, 1])
        style_axes(ax_price)
        style_axes(ax_trade)

        start = max(0, n - HISTORY_ON_PLOT)
        history_x = np.arange(start, n) - (n - 1)  # 0 = dzisiaj
        history_y = history[start:]
        window_x = np.arange(n - days, n) - (n - 1)
        future_x = np.arange(0, days + 1)

        visible = list(history_y) + list(result["window_combined"]) + list(plan["prices"])
        low, high = min(visible), max(visible)
        margin = 0.08 * (high - low or 1)
        ax_price.set_ylim(low - margin, high + margin)

        # historia z wypelnieniem w stylu "area chart"
        ax_price.plot(history_x, history_y, color=TEXT, linewidth=1.6, label="Historia", zorder=3)
        ax_price.fill_between(history_x, history_y, low - margin, color=BLUE, alpha=0.12,
                              linewidth=0, zorder=1)

        ax_price.axvspan(window_x[0] - 0.5, 0, color=AMBER, alpha=0.06, zorder=0)
        ax_price.axvspan(0, days + 0.5, color=ACCENT, alpha=0.07, zorder=0)
        ax_price.plot(window_x, result["window_combined"], color=AMBER, linestyle="--", linewidth=1.6,
                      marker="o", markersize=4, label="Prognoza CKF na oknie oceny", zorder=4)

        # prognoza z efektem "poswiaty"
        for width, alpha in ((9, 0.08), (5, 0.15)):
            ax_price.plot(future_x, plan["prices"], color=ACCENT, linewidth=width, alpha=alpha,
                          solid_capstyle="round", zorder=4)
        ax_price.plot(future_x, plan["prices"], color=ACCENT_HOVER, linewidth=2.2, marker="o",
                      markersize=5, markerfacecolor=SURFACE, markeredgewidth=1.8,
                      label="Prognoza CKF", zorder=5)

        ax_price.axvline(0, color=MUTED, linewidth=0.8, linestyle=":", zorder=2)
        ax_price.annotate(f"${history[-1]:,.2f}", xy=(0, history[-1]), xytext=(-12, 14),
                          textcoords="offset points", ha="right", color=TEXT, fontsize=9,
                          bbox=dict(boxstyle="round,pad=0.35", fc=SURFACE_2, ec=BORDER), zorder=6)
        ax_price.annotate(f"${plan['prices'][-1]:,.2f}", xy=(days, plan["prices"][-1]), xytext=(0, 14),
                          textcoords="offset points", ha="center", color="#ffffff", fontsize=9,
                          bbox=dict(boxstyle="round,pad=0.35", fc=ACCENT, ec=ACCENT), zorder=6)

        ax_price.set_ylabel("Cena [$]")
        ax_price.legend(loc="upper left", fontsize=9, frameon=True, facecolor=SURFACE_2,
                        edgecolor=BORDER, labelcolor=TEXT)

        trades = plan["u_sequence"]
        colors = [GREEN if trade >= 0 else RED for trade in trades]
        ax_trade.bar(np.arange(len(trades)), trades, color=colors, width=0.55, zorder=3)
        ax_trade.axhline(0, color=BORDER, linewidth=1)
        ax_trade.margins(y=0.35)
        ax_trade.set_ylabel("Kup / sprzedaj")
        ax_trade.set_xlabel("Dzień (0 = dziś)")

        self.canvas.draw_idle()

    def _draw_weights(self, weights: dict):
        self.weights_figure.clear()
        ax = self.weights_figure.add_subplot()
        style_axes(ax)
        ax.grid(axis="y", visible=False)

        orders = list(weights)
        values = [weights[order] for order in orders]
        best = int(np.argmax(values))
        colors = [ACCENT if index == best else "#3b4360" for index in range(len(orders))]
        y = np.arange(len(orders))
        ax.barh(y, [1] * len(orders), color=SURFACE_2, height=0.6, zorder=1)
        ax.barh(y, values, color=colors, height=0.6, zorder=2)
        for row, value in zip(y, values):
            ax.text(1.02, row, f"{100 * value:.2f}%", va="center", color=TEXT, fontsize=9)
        ax.set_yticks(y, [f"rząd {order}" for order in orders])
        ax.invert_yaxis()
        ax.set_xlim(0, 1.15)
        ax.set_xticks([0, 0.25, 0.5, 0.75, 1], ["0%", "25%", "50%", "75%", "100%"])
        ax.set_title("Udział modeli w prognozie", loc="left", fontsize=11, pad=10)
        self.weights_canvas.draw_idle()


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
