"""
MathModelAgent 测试套件

这个包包含了 MathModelAgent 后端项目的完整测试套件。

测试结构:
    - routers/: API 路由测试
    - core/: 核心业务逻辑测试
    - services/: 服务层测试
    - utils/: 工具函数测试
    - tools/: 工具类测试
    - schemas/: 数据模式测试
    - config/: 配置测试

使用方法:
    # 运行所有测试
    pytest

    # 运行特定目录
    pytest tests/routers/

    # 生成覆盖率报告
    pytest --cov=app --cov-report=html

更多信息请参考:
    - tests/README.md: 测试套件说明
    - TESTING.md: 完整测试指南
    - TEST_SUITE_SUMMARY.md: 测试总结
"""

__version__ = "1.0.0"
__author__ = "MathModelAgent Team"
