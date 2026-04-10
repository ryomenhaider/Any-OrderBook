from rich.console import Console
from rich.table import Table
import time

from orderbook_data import (
    fetch_orderboook,
    clean_orderbook,
    feature_engineer,
)

console = Console()


def get_input(prompt: str, default: str) -> str:
    console.print(prompt, end="")
    return input().strip() or default


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
        table = Table(show_header=False)

        table.add_column(style="green", justify="right")
        table.add_column(style="green", justify="right")
        table.add_column(style="red", justify="left")
        table.add_column(style="red", justify="left")

        sorted_bids = sorted(self.bids, key=lambda x: x["price"], reverse=True)
        sorted_asks = sorted(self.asks, key=lambda x: x["price"])

        max_rows = max(len(sorted_bids), len(sorted_asks))

        for i in range(max_rows):
            bid_price = f"{sorted_bids[i]['price']:.2f}" if i < len(sorted_bids) else ""
            bid_qty = (
                f"{sorted_bids[i]['quantity']:.4f}" if i < len(sorted_bids) else ""
            )
            ask_qty = (
                f"{sorted_asks[i]['quantity']:.4f}" if i < len(sorted_asks) else ""
            )
            ask_price = f"{sorted_asks[i]['price']:.2f}" if i < len(sorted_asks) else ""

            table.add_row(bid_price, bid_qty, ask_qty, ask_price)

        return table

    def create_features_content(self) -> str:
        spread, spread_pct, mid_price = self.features.get("spread", (0, 0, 0))
        bid_depth, ask_depth = self.features.get("depth", (0, 0))
        imbalance = self.features.get("imbalance_ratio", 0)
        bid_vwap, ask_vwap = self.features.get("vwap", (0, 0))

        content = f"""Spread:       {spread:.2f} ({spread_pct:.3f}%)
Mid Price:    {mid_price:.2f}

Bid Depth:    {bid_depth:.4f}
Ask Depth:    {ask_depth:.4f}

Imbalance:    {imbalance:.4f}

Bid VWAP:     {bid_vwap:.2f}
Ask VWAP:     {ask_vwap:.2f}"""
        return content

    def render(self):
        console.clear()

        orderbook_table = self.create_orderbook_table()
        console.print(orderbook_table)

        console.print()
        console.print(self.create_features_content())

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
