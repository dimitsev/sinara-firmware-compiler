import pandas as pd


def style(
    df           : pd.DataFrame,
    col_width_px : int = 100,
):
    return df.map(lambda x: x if isinstance(x, (int, float, str)) else str(x)).style.set_table_styles(
        table_styles = [
            {"selector": "td", "props": [
                ("white-space"  , "nowrap"),
                ("overflow"     , "hidden"),
                ("text-overflow", "ellipsis"),
                ("max-width"    , f"{col_width_px}px")
            ]},
            {"selector": "th", "props": [("max-width", f"{col_width_px}px")]},
            #{"selector": "tr", "props": [("height", "20px")]},
            {"selector": ".index_name, .row_heading", "props": [("max-width", None)]},
        ],
        overwrite = False,
    ).format(escape="html")