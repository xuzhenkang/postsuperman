# 贡献指南

感谢您对PostSuperman项目的关注！我们欢迎所有形式的贡献，包括但不限于：

- 🐛 报告Bug
- 💡 提出新功能建议
- 📝 改进文档
- 🔧 提交代码修复
- 🎨 改进用户界面

## 开发环境设置

### 1. 克隆项目
```bash
git clone https://github.com/xuzhenkang/postsuperman.git
cd postsuperman
```

### 2. 创建虚拟环境
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 运行开发版本
```bash
python main.py
```

## 代码规范

### Python代码风格
- 遵循PEP 8规范
- 使用4个空格缩进
- 行长度不超过120字符
- 使用有意义的变量和函数名

### 代码注释
- 为所有公共函数和类添加文档字符串
- 使用中文注释说明复杂逻辑
- 保持注释与代码同步更新

### 提交规范
使用[约定式提交](https://www.conventionalcommits.org/zh-hans/)格式：

```
<类型>[可选的作用域]: <描述>

[可选的正文]

[可选的脚注]
```

类型包括：
- `feat`: 新功能
- `fix`: 修复Bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

示例：
```
feat: 添加环境变量支持

- 新增环境变量管理界面
- 支持环境变量在请求中的使用
- 添加环境变量导入导出功能

Closes #123
```

## 提交流程

### 1. Fork项目
在GitHub上Fork本项目到您的账户。

### 2. 创建功能分支
```bash
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/your-bug-fix
```

### 3. 进行修改
- 编写代码
- 添加测试（如果适用）
- 更新文档
- 确保代码通过所有检查

### 4. 提交更改
```bash
git add .
git commit -m "feat: 添加新功能描述"
```

### 5. 推送分支
```bash
git push origin feature/your-feature-name
```

### 6. 创建Pull Request
- 在GitHub上创建Pull Request
- 填写详细的描述
- 关联相关Issue（如果有）

## 测试指南

### 运行测试
```bash
# 运行所有测试
python -m pytest

# 运行特定测试
python -m pytest tests/test_main_window.py

# 生成覆盖率报告
python -m pytest --cov=ui
```

### 手动测试清单
在提交代码前，请确保：

- [ ] 应用能正常启动
- [ ] 所有主要功能正常工作
- [ ] 界面在不同分辨率下正常显示
- [ ] 数据保存和加载功能正常
- [ ] 打包后的exe文件能正常运行

## 报告Bug

### Bug报告模板
请在GitHub Issues中使用以下模板：

```markdown
## Bug描述
简要描述Bug的内容。

## 重现步骤
1. 打开应用
2. 执行操作A
3. 执行操作B
4. 观察错误

## 预期行为
描述您期望看到的行为。

## 实际行为
描述实际发生的行为。

## 环境信息
- 操作系统：Windows 10
- Python版本：3.6.6
- 应用版本：1.0.0
- 是否使用打包版本：是/否

## 附加信息
任何其他相关信息，如错误截图、日志文件等。
```

## 功能建议

### 功能建议模板
```markdown
## 功能描述
详细描述您希望添加的功能。

## 使用场景
描述这个功能的使用场景和用户价值。

## 实现建议
如果有的话，提供实现建议或参考。

## 优先级
- [ ] 高优先级
- [ ] 中优先级  
- [ ] 低优先级
```

## 文档贡献

### 文档类型
- README.md：项目介绍和使用指南
- CHANGELOG.md：版本更新日志
- API文档：代码API说明
- 用户手册：详细使用教程

### 文档规范
- 使用清晰的标题结构
- 包含代码示例
- 添加截图说明（如需要）
- 保持文档与代码同步

## 代码审查

### 审查要点
- 代码质量和可读性
- 功能正确性
- 性能影响
- 安全性考虑
- 向后兼容性

### 审查流程
1. 自动检查（CI/CD）
2. 代码审查者审查
3. 测试验证
4. 合并到主分支

## 发布流程

### 版本号规范
遵循[语义化版本](https://semver.org/lang/zh-CN/)：

- 主版本号：不兼容的API修改
- 次版本号：向下兼容的功能性新增
- 修订号：向下兼容的问题修正

### 发布步骤
1. 更新版本号
2. 更新CHANGELOG.md
3. 创建Release标签
4. 生成发布说明
5. 上传打包文件

## 联系方式

如有问题或需要帮助，请通过以下方式联系：

- 📧 邮箱：xuzhenkang@hotmail.com
- 💬 GitHub Issues：https://github.com/xuzhenkang/postsuperman/issues
- 📖 文档：https://github.com/xuzhenkang/postsuperman/wiki

## 致谢

感谢所有为PostSuperman项目做出贡献的开发者！

---

**让我们一起让API调试变得更简单！** 🚀 