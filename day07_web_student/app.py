from functools import wraps
from pathlib import Path

from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for

from services.data_service import load_dashboard_data
from services.qa_service import answer_question
from pathlib import Path
import pandas as pd

app = Flask(__name__)
base_dir = Path(__file__).parent

def read_csv(path: Path):
    return pd.read_csv(path, encoding="utf-8-sig")


BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)
app.config["SECRET_KEY"] = "day07-classroom-demo-key"


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "username" not in session:
            flash("请先登录后再访问数据看板。", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


@app.route("/")
def index():
    return redirect(url_for("dashboard") if "username" in session else url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if username == "student" and password == "day07":
            session["username"] = username
            flash("登录成功，欢迎进入电商用户分析系统。", "success")
            return redirect(url_for("dashboard"))
        flash("账号或密码错误。演示账号：student / day07", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("你已安全退出。", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    category = request.args.get("category", "全部")
    dashboard_data = load_dashboard_data(BASE_DIR, category)
    return render_template(
        "dashboard.html",
        username=session["username"],
        selected_category=category,
        **dashboard_data,
    )


@app.route("/assistant")
@login_required
def assistant():
    return render_template("assistant.html", username=session["username"])


@app.route("/api/ask", methods=["POST"])
@login_required
def ask():
    payload = request.get_json(silent=True) or {}
    question = str(payload.get("question", "")).strip()
    if not question:
        return jsonify({"ok": False, "answer": "请输入一个与项目数据有关的问题。"}), 400
    return jsonify({"ok": True, "answer": answer_question(BASE_DIR, question)})


@app.errorhandler(404)
def page_not_found(_error):
    return render_template("404.html"), 404


@app.route("/segments")
def segments_page():
    data_dir = base_dir / "data"
    seg_df = read_csv(data_dir / "segment_analysis.csv")

    # 重命名英文列，方便前端渲染
    seg_df = seg_df.rename(columns={
        "TenureGroup": "生命周期阶段",
        "用户数": "用户数",
        "流失人数": "流失人数",
        "流失率": "流失率"
    })
    # 格式化流失率为百分比
    seg_df["流失率"] = seg_df["流失率"].map(lambda x: f"{x:.1%}")

    # 生成数据观察：找出流失率最高阶段作为数值证据
    raw_seg = read_csv(data_dir / "segment_analysis.csv")
    max_loss_row = raw_seg.loc[raw_seg["流失率"].idxmax()]
    stage_name = max_loss_row["TenureGroup"]
    max_rate = max_loss_row["流失率"]
    max_user = max_loss_row["用户数"]
    insight_text = f"数据观察：「{stage_name}」阶段流失风险最高，该阶段用户共{max_user:,}人，流失率高达{max_rate:.1%}，远高于其他生命周期分段，需优先做新用户留存运营。"

    # 传给模板
    return render_template(
        "segments.html",
        segment_rows=seg_df.to_dict("records"),
        insight=insight_text
    )


if __name__ == "__main__":
    app.run(debug=False, port=5000)
