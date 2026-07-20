from pathlib import Path

import pandas as pd


def answer_question(base_dir: Path, question: str) -> str:
    data_dir = base_dir / "data"
    metrics_df = pd.read_csv(data_dir / "overall_metrics.csv", encoding="utf-8-sig")
    metrics = dict(zip(metrics_df["指标"], metrics_df["数值"]))
    category_df = pd.read_csv(data_dir / "category_analysis.csv", encoding="utf-8-sig")
    segment_df = pd.read_csv(data_dir / "segment_analysis.csv", encoding="utf-8-sig")
    normalized = question.replace(" ", "").lower()

    if any(word in normalized for word in ["多少用户", "用户数", "总用户"]):
        return f"数据集中共有{int(metrics['用户数']):,}名用户。"

    elif any(word in normalized for word in ["流失率", "流失情况", "总体流失率", "流失人数"]):
        loss_rate = metrics["流失率"]
        loss_user_count = int(metrics["流失人数"])
        return f"当前总体流失率为{loss_rate:.2%}，累计流失用户{loss_user_count:,}人。"

    elif any(word in normalized for word in ["偏好品类", "哪个品类用户最多", "品类用户", "品类偏好"]):
        # 找到用户数最高的品类行
        max_user_row = category_df.loc[category_df["用户数"].idxmax()]
        category_name = max_user_row["PreferedOrderCat"]
        user_count = int(max_user_row["用户数"])
        return f"用户数最多的偏好品类是「{category_name}」，该品类共有{user_count:,}名用户。"

    elif any(word in normalized for word in ["生命周期", "阶段风险", "哪个阶段风险最高", "流失风险最高"]):
        # 找到流失率最高的生命周期阶段
        max_loss_row = segment_df.loc[segment_df["流失率"].idxmax()]
        stage_name = max_loss_row["TenureGroup"]
        loss_rate = max_loss_row["流失率"]
        return f"流失风险最高的生命周期阶段是「{stage_name}」，该阶段流失率达到{loss_rate:.2%}。"

    elif any(word in normalized for word in ["平均订单数", "订单情况", "人均订单", "订单均值"]):
        avg_order = metrics["平均订单数"]
        # 兼容中位数字段，无中位数时仅返回均值
        median_order = metrics.get("订单中位数", None)
        if median_order is not None:
            return f"当前用户平均订单数为{avg_order:.2f}单/人，订单数中位数为{median_order:.2f}单/人。"
        else:
            return f"当前用户平均订单数为{avg_order:.2f}单/人。"

    return (
        "暂无分析该问题的能力，请换一个问题。"
    )
