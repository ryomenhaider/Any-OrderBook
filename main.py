from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import time
import sys
import io

from orderbook_data import fetch_orderboook, clean_orderbook, feature_engineer

console = Console()


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

    def fetch_data(self):
        try:
            symbol, data = fetch_orderboook(self.symbol, self.limit)
            self.bids, self.asks = clean_orderbook(data)
            self.features = feature_engineer(self.bids, self.asks)
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
        console.print(orderbook_table)

        features_panel = self.create_features_panel()
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
    symbol = "BTCUSDT"

    tui = OrderBookTUI(symbol=symbol)
    try:
        tui.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopped by user[/yellow]")


if __name__ == "__main__":
    main()
