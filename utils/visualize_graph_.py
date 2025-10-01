from colorama import Fore, Style
import plotext as plt


def visualize_graph(graph_data: dict):
    """
    Terminal visualization of financial charts
    """

    if not graph_data or not isinstance(graph_data, dict):
        print(f"{Fore.RED}No chart data received{Style.RESET_ALL}")
        return

    try:
        _render_graph(graph_data)
    except Exception as e:
        print(f"{Fore.RED}Error rendering graph: {str(e)}{Style.RESET_ALL}")


def _render_graph(graph_spec: dict):
    """Render different types of financial charts"""

    if not graph_spec or not isinstance(graph_spec, dict):
        return

    chart_type = graph_spec.get("type", "line").lower()
    title = graph_spec.get("title", "Financial Chart")
    subtitle = graph_spec.get("subtitle", "")
    x_label = graph_spec.get("x_label", "")
    y_label = graph_spec.get("y_label", "")
    data = graph_spec.get("data", {})
    insights = graph_spec.get("insights", "")

    if not data:
        print(f"{Fore.RED}No chart data provided{Style.RESET_ALL}")
        return

    # Setup plot with black background
    plt.clear_data()
    plt.plotsize(100, 25)

    # Set black background instead of white
    try:
        plt.canvas_color("black")
    except:
        pass

    try:
        plt.theme("dark")
    except:
        pass

    # Handle different chart types
    if chart_type == "line":
        _render_line_chart(data, title, subtitle, x_label, y_label)
    elif chart_type == "bar":
        _render_bar_chart(data, title, subtitle, x_label, y_label)
    elif chart_type == "scatter":
        _render_scatter_chart(data, title, subtitle, x_label, y_label)
    elif chart_type == "multi_line":
        _render_multi_line_chart(data, title, subtitle, x_label, y_label)
    elif chart_type == "grouped_bar":
        _render_grouped_bar_chart(data, title, subtitle, x_label, y_label)
    else:
        _render_line_chart(data, title, subtitle, x_label, y_label)

    # Show chart
    plt.show()

    # Display insights if available
    if insights:
        print(f"\n{Fore.GREEN}{Style.BRIGHT}Chart Insights:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{insights}{Style.RESET_ALL}")


def _render_line_chart(
    data: dict, title: str, subtitle: str, x_label: str, y_label: str
):
    """Render line chart"""
    x_data = data.get("x", [])
    y_data = data.get("y", [])

    if x_data and y_data:
        # Convert string labels to numeric indices for plotting
        x_numeric = list(range(len(x_data)))
        plt.plot(x_numeric, y_data, marker="braille", color="green")
        # Set custom x-axis labels
        plt.xticks(x_numeric, x_data)

    _set_chart_labels(title, subtitle, x_label, y_label)


def _render_bar_chart(
    data: dict, title: str, subtitle: str, x_label: str, y_label: str
):
    """Render bar chart"""
    x_data = data.get("x", [])
    y_data = data.get("y", [])

    if x_data and y_data:
        # Convert string labels to numeric indices for plotting
        x_numeric = list(range(len(x_data)))
        plt.bar(x_numeric, y_data, color="blue")
        # Set custom x-axis labels
        plt.xticks(x_numeric, x_data)

    _set_chart_labels(title, subtitle, x_label, y_label)


def _render_scatter_chart(
    data: dict, title: str, subtitle: str, x_label: str, y_label: str
):
    """Render scatter chart"""
    x_data = data.get("x", [])
    y_data = data.get("y", [])

    if x_data and y_data:
        # Convert string labels to numeric indices for plotting
        x_numeric = list(range(len(x_data)))
        plt.scatter(x_numeric, y_data, marker="braille", color="red")
        # Set custom x-axis labels
        plt.xticks(x_numeric, x_data)

    _set_chart_labels(title, subtitle, x_label, y_label)


def _render_multi_line_chart(
    data: dict, title: str, subtitle: str, x_label: str, y_label: str
):
    """Render multiple line series"""
    x_data = data.get("x", [])
    series = data.get("series", [])

    colors = ["green", "red", "blue", "yellow", "magenta", "cyan"]

    if x_data:
        # Convert string labels to numeric indices for plotting
        x_numeric = list(range(len(x_data)))

    for i, series_data in enumerate(series):
        if isinstance(series_data, dict):
            name = series_data.get("name", f"Series {i+1}")
            values = series_data.get("values", [])
            color = series_data.get("color", colors[i % len(colors)])

            if x_data and values and len(x_data) == len(values):
                plt.plot(x_numeric, values, label=name, marker="braille", color=color)

    if x_data:
        # Set custom x-axis labels
        plt.xticks(x_numeric, x_data)

    _set_chart_labels(title, subtitle, x_label, y_label)


def _render_grouped_bar_chart(
    data: dict, title: str, subtitle: str, x_label: str, y_label: str
):
    """Render grouped bar chart"""
    x_data = data.get("x", [])
    series = data.get("series", [])

    colors = ["green", "red", "blue", "yellow", "magenta", "cyan"]

    for i, series_data in enumerate(series):
        if isinstance(series_data, dict):
            name = series_data.get("name", f"Series {i+1}")
            values = series_data.get("values", [])
            color = series_data.get("color", colors[i % len(colors)])

            if x_data and values and len(x_data) == len(values):
                # Offset x positions for grouped bars
                x_numeric = list(range(len(x_data)))
                x_offset = [x + i * 0.3 for x in x_numeric]
                plt.bar(x_offset, values, label=name, color=color)

    if x_data:
        # Set custom x-axis labels at the center of grouped bars
        x_numeric = list(range(len(x_data)))
        center_offset = [x + (len(series) - 1) * 0.15 for x in x_numeric]
        plt.xticks(center_offset, x_data)

    _set_chart_labels(title, subtitle, x_label, y_label)


def _set_chart_labels(title: str, subtitle: str, x_label: str, y_label: str):
    """Set chart titles and labels"""
    full_title = title
    if subtitle:
        full_title += f"\n{subtitle}"

    plt.title(full_title)
    if x_label:
        plt.xlabel(x_label)
    if y_label:
        plt.ylabel(y_label)
