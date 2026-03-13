#!/bin/bash

# ============================================
# 🚀 Vivo X300U 舆论监测网站 - 自动化部署脚本
# ============================================
# 
# 用途: 自动配置 GitHub、Vercel、Railway 部署
# 支持: macOS, Linux (不支持 Windows 直接运行，需要 Git Bash 或 WSL)
# 权限: 需要 git 命令行工具

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的信息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 检查必要工具
check_tools() {
    print_info "检查必要工具..."
    
    if ! command -v git &> /dev/null; then
        print_error "Git 未安装，请访问 https://git-scm.com/download 安装"
        exit 1
    fi
    print_success "Git 已安装"
    
    if ! command -v node &> /dev/null; then
        print_warning "Node.js 未安装，请访问 https://nodejs.org/ 安装"
    else
        print_success "Node.js 已安装: $(node --version)"
    fi
}

# 初始化 git 仓库
setup_git() {
    print_info "初始化 Git 仓库..."
    
    if [ -d ".git" ]; then
        print_warning "Git 仓库已存在，跳过初始化"
    else
        git init
        git config user.email "admin@example.com"
        git config user.name "Sentiment Monitor Admin"
        print_success "Git 仓库初始化完成"
    fi
}

# 添加文件到 git
add_files() {
    print_info "添加文件到 Git..."
    
    git add .
    git commit -m "Initial commit: Vivo X300U sentiment monitor" || true
    print_success "文件已提交"
}

# 配置 Vercel
setup_vercel() {
    print_info "配置 Vercel..."
    
    # 检查 Vercel CLI
    if ! command -v vercel &> /dev/null; then
        print_warning "Vercel CLI 未安装，自动安装中..."
        npm install -g vercel
    fi
    
    print_info "请按照以下步骤操作:"
    echo "  1. 访问 https://vercel.com"
    echo "  2. 点击 'Sign Up' 并用 GitHub 登录"
    echo "  3. 授权 Vercel 访问您的 GitHub"
    echo "  4. 返回此窗口，按 Enter 继续"
    read -p "按 Enter 继续..."
    
    # 创建 vercel.json
    cat > vercel.json << 'EOF'
{
  "version": 2,
  "public": false,
  "env": {
    "REACT_APP_API_URL": "@api_url",
    "REACT_APP_WS_URL": "@ws_url"
  },
  "buildCommand": "npm run build",
  "outputDirectory": "dist"
}
EOF
    
    git add vercel.json
    git commit -m "Add Vercel configuration" || true
    
    print_success "Vercel 配置已创建"
    print_info "现在需要手动连接 GitHub..."
    echo "  1. 访问 https://vercel.com/dashboard"
    echo "  2. 点击 'Import Project'"
    echo "  3. 选择您的 sentiment-monitor 仓库"
    echo "  4. 点击 'Deploy'"
}

# 配置 Railway
setup_railway() {
    print_info "配置 Railway..."
    
    # 创建 railway.json
    cat > railway.json << 'EOF'
{
  "version": 2
}
EOF
    
    # 创建 railway.toml (可选)
    cat > railway.toml << 'EOF'
[env]
# 环境变量在 Railway 仪表板中设置

[build]
builder = "nixpacks"

[deploy]
startCommand = "node backend/src/server.js"
healthcheckPath = "/api/dashboard"
healthcheckInterval = 10
EOF
    
    git add railway.json railway.toml
    git commit -m "Add Railway configuration" || true
    
    print_success "Railway 配置已创建"
    print_info "现在需要手动连接 GitHub..."
    echo "  1. 访问 https://railway.app"
    echo "  2. 点击 'Dashboard'"
    echo "  3. 点击 'New Project' → 'Deploy from GitHub'"
    echo "  4. 授权并选择 sentiment-monitor 仓库"
}

# 配置环境变量模板
setup_env_vars() {
    print_info "创建环境变量模板..."
    
    cat > .env.local.example << 'EOF'
# ==========================================
# Vercel 前端环境变量 (.env.local)
# ==========================================
REACT_APP_API_URL=https://your-railway-url.up.railway.app
REACT_APP_WS_URL=wss://your-railway-url.up.railway.app

# ==========================================
# Railway 后端环境变量
# ==========================================
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/sentiment-monitor
REDIS_HOST=redis
REDIS_PORT=6379
NODE_ENV=production
PORT=3000
FRONTEND_URL=https://your-vercel-url.vercel.app
CORS_ORIGIN=https://your-vercel-url.vercel.app
EOF
    
    print_success "环境变量模板已创建: .env.local.example"
}

# 生成部署检查清单
create_checklist() {
    print_info "生成部署检查清单..."
    
    cat > DEPLOYMENT_CHECKLIST.md << 'EOF'
# 🚀 部署检查清单

## 第一步：GitHub 仓库
- [ ] GitHub 账号已创建
- [ ] 仓库已创建: sentiment-monitor
- [ ] 代码已推送到 main 分支
- [ ] GitHub 访问令牌已生成 (Settings → Developer settings → Personal access tokens)

## 第二步：MongoDB 数据库
- [ ] MongoDB Atlas 账号已创建
- [ ] 集群已创建 (M0 免费层)
- [ ] 数据库用户已创建
- [ ] IP 白名单已添加 (0.0.0.0/0)
- [ ] 连接字符串已获取
- [ ] MONGODB_URI 已设置到 Railway 环境变量

## 第三步：Vercel 前端部署
- [ ] Vercel 账号已创建
- [ ] 项目已导入自 GitHub
- [ ] 构建配置已完成
- [ ] 环境变量已设置:
  - [ ] REACT_APP_API_URL
  - [ ] REACT_APP_WS_URL
- [ ] 部署成功
- [ ] 前端 URL: https://your-vercel-url.vercel.app

## 第四步：Railway 后端部署
- [ ] Railway 账号已创建
- [ ] 项目已导入自 GitHub
- [ ] 后端构建成功
- [ ] 环境变量已设置:
  - [ ] MONGODB_URI
  - [ ] REDIS_HOST
  - [ ] REDIS_PORT
  - [ ] NODE_ENV
  - [ ] PORT
  - [ ] FRONTEND_URL
  - [ ] CORS_ORIGIN
- [ ] 后端 URL: https://your-railway-url.up.railway.app
- [ ] 数据库连接正常

## 第五步：测试验证
- [ ] 访问前端 URL，页面加载正常
- [ ] 浏览器控制台无 CORS 错误
- [ ] WebSocket 连接成功
- [ ] 能获取到实时数据
- [ ] 爬虫功能正常

## 第六步：配置域名 (可选)
- [ ] 域名已注册
- [ ] DNS 记录已配置
- [ ] HTTPS 已启用
- [ ] 自定义域名可访问

## 第七步：监控和维护
- [ ] 已设置 Railway 告警
- [ ] 已配置自动备份
- [ ] 已启用日志收集
- [ ] 已添加监控告警

## 完成标志
当以下条件都满足时，部署完成：
✅ 前端能访问且加载正常
✅ 后端 API 可调用
✅ 数据库连接成功
✅ WebSocket 实时推送工作
✅ 没有错误日志

---

**部署时间:** 约 30 分钟
**技术难度:** ⭐ 简单
**成本:** ✅ 完全免费
EOF
    
    print_success "部署检查清单已创建: DEPLOYMENT_CHECKLIST.md"
}

# 生成快速参考指南
create_quick_reference() {
    print_info "生成快速参考指南..."
    
    cat > QUICK_START.md << 'EOF'
# 🚀 快速开始指南

## 部署流程 (简化版)

### 1️⃣ 准备 GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/sentiment-monitor.git
git push -u origin main
```

### 2️⃣ 创建 MongoDB
1. 访问 https://www.mongodb.com/cloud/atlas
2. 创建免费集群 (M0)
3. 获取连接字符串

### 3️⃣ 部署前端到 Vercel
1. 访问 https://vercel.com
2. 点击 "Import Project"
3. 选择 GitHub 仓库
4. 设置环境变量
5. 点击 "Deploy"

### 4️⃣ 部署后端到 Railway  
1. 访问 https://railway.app
2. 创建新项目
3. 连接 GitHub 仓库
4. 设置环境变量 (包括 MONGODB_URI)
5. 部署

### 5️⃣ 连接前后端
在 Vercel 环境变量中设置：
```
REACT_APP_API_URL=https://your-railway-url.up.railway.app
REACT_APP_WS_URL=wss://your-railway-url.up.railway.app
```

### 6️⃣ 测试
访问 https://your-vercel-url.vercel.app 查看是否能加载数据

## 常用 URLs

| 服务 | 网址 |
|------|------|
| GitHub | https://github.com |
| Vercel | https://vercel.com |
| Railway | https://railway.app |
| MongoDB | https://www.mongodb.com/cloud/atlas |
| Freenom | https://www.freenom.com |

## 环境变量速查表

### Vercel (前端)
```
REACT_APP_API_URL=https://your-railway-url.up.railway.app
REACT_APP_WS_URL=wss://your-railway-url.up.railway.app
```

### Railway (后端)
```
MONGODB_URI=mongodb+srv://username:password@...
REDIS_HOST=redis
REDIS_PORT=6379
NODE_ENV=production
PORT=3000
FRONTEND_URL=https://your-vercel-url.vercel.app
CORS_ORIGIN=https://your-vercel-url.vercel.app
```

## 故障排查

| 问题 | 解决方案 |
|------|---------|
| Vercel 构建失败 | 检查日志 → 确保 package.json 正确 |
| Railway 连接超时 | 检查 MONGODB_URI 和 IP 白名单 |
| CORS 错误 | 检查 FRONTEND_URL 和 CORS_ORIGIN |
| WebSocket 失败 | 使用 WSS (Secure WebSocket) |

## 帮助资源

- Vercel 文档: https://vercel.com/docs
- Railway 文档: https://docs.railway.app
- MongoDB 文档: https://docs.mongodb.com
EOF
    
    print_success "快速参考指南已创建: QUICK_START.md"
}

# 主函数
main() {
    clear
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════╗"
    echo "║  🚀 Vivo X300U 舆论监测网站                       ║"
    echo "║     自动化部署脚本                                 ║"
    echo "║     Vercel + Railway 完全免费部署                 ║"
    echo "╚════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    print_info "开始部署配置过程..."
    echo ""
    
    # 执行步骤
    check_tools
    echo ""
    
    setup_git
    echo ""
    
    add_files
    echo ""
    
    setup_env_vars
    echo ""
    
    create_checklist
    echo ""
    
    create_quick_reference
    echo ""
    
    setup_vercel
    echo ""
    
    setup_railway
    echo ""
    
    # 最后的总结
    echo -e "${GREEN}"
    echo "╔════════════════════════════════════════════════════╗"
    echo "║            ✅ 配置完成！                           ║"
    echo "╚════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo ""
    print_success "已创建的文件:"
    echo "  • vercel.json - Vercel 配置"
    echo "  • railway.json - Railway 配置"
    echo "  • railway.toml - Railway 部署配置"
    echo "  • .env.local.example - 环境变量模板"
    echo "  • DEPLOYMENT_CHECKLIST.md - 部署检查清单"
    echo "  • QUICK_START.md - 快速开始指南"
    echo ""
    
    print_info "后续步骤:"
    echo "  1. 将代码推送到 GitHub"
    echo "  2. 访问 Vercel 连接 GitHub 仓库"
    echo "  3. 访问 Railway 连接 GitHub 仓库"
    echo "  4. 设置环境变量"
    echo "  5. 等待自动部署完成"
    echo ""
    
    print_info "推荐阅读文档:"
    echo "  • DEPLOYMENT_CHECKLIST.md - 完整检查清单"
    echo "  • QUICK_START.md - 快速参考"
    echo "  • 部署方案_Vercel+Railway_完全免费.md - 详细指南"
    echo ""
    
    print_success "祝您部署顺利！🚀"
}

# 运行主函数
main
