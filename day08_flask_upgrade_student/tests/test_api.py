import json
import pytest
from app import app

# 测试前置：创建测试客户端，模拟登录会话
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        # 先登录，接口需要 @login_required
        c.post("/login", data={"username": "student", "password": "day07"})
        yield c

# 测试1：GET /api/metrics 正常返回指标JSON
def test_api_metrics_ok(client):
    resp = client.get("/api/metrics")
    data = json.loads(resp.data)
    # 校验状态码、结构
    assert resp.status_code == 200
    assert data["ok"] is True
    assert isinstance(data["metrics"], list)
    # 保证4个指标卡片都存在
    assert len(data["metrics"]) == 4
    # 校验单条字段
    item = data["metrics"][0]
    assert "label" in item and "value" in item and "note" in item

# 测试2：GET /api/categories 不带参数，默认全部品类
def test_api_categories_all(client):
    resp = client.get("/api/categories")
    data = json.loads(resp.data)
    assert resp.status_code == 200
    assert data["ok"] is True
    assert data["category"] == "全部"
    assert isinstance(data["rows"], list)

# 测试3：GET /api/categories 带分类筛选参数
def test_api_categories_filter(client):
    resp = client.get("/api/categories?category=Fashion")
    data = json.loads(resp.data)
    assert resp.status_code == 200
    assert data["category"] == "Fashion"
    # 返回的每一行品类都匹配筛选值
    for row in data["rows"]:
        assert row["偏好品类"] == "Fashion"

# 测试4：未登录访问 /api/metrics 会跳登录页（鉴权拦截）
def test_api_metrics_no_login():
    with app.test_client() as c:
        resp = c.get("/api/metrics")
        # 302重定向到/login
        assert resp.status_code == 302
        assert "/login" in resp.location