from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import time
import sys

from orderbook_data import (
    fetch_orderboook,
    fetch_kline,
    clean_orderbook,
    feature_engineer,
)

console = Console()


def get_input(prompt: str, default: str) -> str:
    console.print(prompt, end="")
    try:
        return input().strip() or default
    except EOFError:
        return default


class OrderBookTUI:
    def __init__(
        self, symbol: str = "BTCUSDT", limit: int = 20, refresh_rate: float = 2.0
    ):
        self.symbol = symbol
        self.limit = limit
        self.refresh_rate = refresh_rate
        self.running = False
        self.bids = []
        self.asks = []
        self.features = {}
        self.price_history = []
        self.price_times = []

    def fetch_data(self):
        try:
            symbol, data = fetch_orderboook(self.symbol, self.limit)
            self.bids, self.asks = clean_orderbook(data)
            self.features = feature_engineer(self.bids, self.asks)

            symbol, kline_data, timestamps, closes, times = fetch_kline(self.symbol)
            self.price_history = closes
            self.price_times = times
        except Exception as e:
            console.print(f"[red]Error fetching data: {e}[/red]")

    def create_orderbook_table(self) -> Table:
        table = Table(
            show_header=True,
            header_style="bold magenta",
            title=f"Order Book - {self.symbol}",
        )

        table.add_column("Bid Price", style="green", justify="right")
        table.add_column("Quantity", style="green", justify="right")
        table.add_column("Quantity", style="red", justify="left")
        table.add_column("Ask Price", style="red", justify="left")

        max_rows = max(len(self.bids), len(self.asks))

        for i in range(max_rows):
            bid_price = f"{self.bids[i]['price']:.2f}" if i < len(self.bids) else ""
            bid_qty = f"{self.bids[i]['quantity']:.4f}" if i < len(self.bids) else ""
            ask_qty = f"{self.asks[i]['quantity']:.4f}" if i < len(self.asks) else ""
            ask_price = f"{self.asks[i]['price']:.2f}" if i < len(self.asks) else ""

            table.add_row(bid_price, bid_qty, ask_qty, ask_price)

        return table

    def create_features_panel(self) -> Panel:
        spread, spread_pct, mid_price = self.features.get("spread", (0, 0, 0))
        bid_depth, ask_depth = self.features.get("depth", (0, 0))
        imbalance = self.features.get("imbalance_ratio", 0)
        bid_vwap, ask_vwap = self.features.get("vwap", (0, 0))

        content = f"""
[bold]Spread:[/bold]       {spread:.2f} ({spread_pct:.3f}%)
[bold]Mid Price:[/bold]    {mid_price:.2f}

[bold green]Bid Depth:[/bold green]   {bid_depth:.4f}
[bold red]Ask Depth:[/bold red]   {ask_depth:.4f}

[bold]Imbalance:[/bold]    {imbalance:.4f} ({"Bid Pressure" if imbalance > 0.5 else "Ask Pressure"})

[bold]Bid VWAP:[/bold]     {bid_vwap:.2f}
[bold]Ask VWAP:[/bold]     {ask_vwap:.2f}
        """
        return Panel(content, title="Features", border_style="blue")

    def render_kline_chart(self) -> str:
        import plotext as plt

        plt.clear_data()
        plt.clf()

        if self.price_history:
            plt.plot(self.price_history, marker="dot", color="cyan")
            plt.title(f"Price Chart - {self.symbol}")
            plt.xlabel("Time")
            plt.ylabel("Price")
            plt.xticks([])
            plt.yticks([])

        plt.plotsize(80, 20)
        return plt.build()

    def render(self):
        console.clear()

        console.print(
            Panel.fit(
                f"[bold cyan]ANYORDERBOOK TUI - {self.symbol}[/bold cyan]",
                border_style="cyan",
            )
        )
        console.print()

        orderbook_table = self.create_orderbook_table()
        kline_chart = self.render_kline_chart()

        features_panel = self.create_features_panel()

        console.print(Panel("[bold]Order Book[/bold]", style="on black"))
        console.print(orderbook_table)
        console.print()
        console.print(Panel("[bold]Price Chart[/bold]", style="on black"))
        sys.stdout.write(kline_chart + "\n")
        console.print()
        console.print(Panel("[bold]Features[/bold]", style="on black"))
        console.print(features_panel)

    def run(self):
        self.running = True
        self.fetch_data()
        self.render()

        while self.running:
            time.sleep(self.refresh_rate)
            self.fetch_data()
            self.render()


def main():
    console.print("[bold cyan]Welcome to AnyOrderBook TUI![/bold cyan]")

    console.print("\n[bold]Configure Order Book:[/bold]")
    symbol = get_input("  Symbol (e.g., BTCUSDT, ETHUSDT): ", "BTCUSDT")
    limit_input = get_input("  Limit (number of orders, default 20): ", "20")
    limit = int(limit_input) if limit_input.isdigit() else 20
    refresh_input = get_input("  Refresh rate in seconds (default 2): ", "2")
    refresh_rate = (
        float(refresh_input) if refresh_input.replace(".", "", 1).isdigit() else 2.0
    )

    console.print(
        f"\n[green]Starting with {symbol} (limit: {limit}, refresh: {refresh_rate}s)[/green]\n"
    )
    console.print("[dim]Press Ctrl+C to exit[/dim]\n")

    tui = OrderBookTUI(symbol=symbol, limit=limit, refresh_rate=refresh_rate)
    try:
        tui.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopped by user[/yellow]")


if __name__ == "__main__":
    main()
