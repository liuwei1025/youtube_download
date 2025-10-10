#!/bin/bash
# YouTube 下载器测试运行脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ ${1}${NC}"
}

print_success() {
    echo -e "${GREEN}✓ ${1}${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ ${1}${NC}"
}

print_error() {
    echo -e "${RED}✗ ${1}${NC}"
}

# 显示帮助信息
show_help() {
    echo "YouTube 下载器测试运行脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -a, --all           运行所有测试（包括集成测试）"
    echo "  -u, --unit          仅运行单元测试"
    echo "  -i, --integration   仅运行集成测试"
    echo "  -m, --module        仅运行模块测试"
    echo "  -c, --coverage      生成覆盖率报告"
    echo "  -f, --fast          快速测试（单元+模块）"
    echo "  -v, --verbose       详细输出"
    echo "  -h, --help          显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0                  # 运行单元测试和模块测试"
    echo "  $0 --all            # 运行所有测试"
    echo "  $0 --unit           # 仅运行单元测试"
    echo "  $0 --coverage       # 生成覆盖率报告"
    echo ""
}

# 检查依赖
check_dependencies() {
    print_info "检查测试依赖..."
    
    if ! command -v pytest &> /dev/null; then
        print_error "pytest 未安装"
        print_info "正在安装测试依赖..."
        pip install pytest pytest-asyncio pytest-cov httpx pytest-xdist -q
        print_success "测试依赖安装完成"
    else
        print_success "测试依赖已安装"
    fi
}

# 运行单元测试
run_unit_tests() {
    print_info "运行单元测试..."
    if pytest tests/test_unit_api.py -v $VERBOSE_FLAG; then
        print_success "单元测试通过"
        return 0
    else
        print_error "单元测试失败"
        return 1
    fi
}

# 运行模块测试
run_module_tests() {
    print_info "运行模块测试..."
    if pytest tests/test_youtube_downloader.py -v $VERBOSE_FLAG; then
        print_success "模块测试通过"
        return 0
    else
        print_error "模块测试失败"
        return 1
    fi
}

# 运行集成测试
run_integration_tests() {
    print_warning "运行集成测试（需要网络连接，可能需要5-10分钟）..."
    if SKIP_INTEGRATION_TESTS=false pytest tests/test_integration_api.py -v $VERBOSE_FLAG; then
        print_success "集成测试通过"
        return 0
    else
        print_error "集成测试失败"
        return 1
    fi
}

# 运行所有测试
run_all_tests() {
    print_info "运行所有测试..."
    local failed=0
    
    run_unit_tests || ((failed++))
    run_module_tests || ((failed++))
    run_integration_tests || ((failed++))
    
    if [ $failed -eq 0 ]; then
        print_success "所有测试通过！"
        return 0
    else
        print_error "$failed 个测试套件失败"
        return 1
    fi
}

# 运行快速测试
run_fast_tests() {
    print_info "运行快速测试（单元+模块）..."
    local failed=0
    
    run_unit_tests || ((failed++))
    run_module_tests || ((failed++))
    
    if [ $failed -eq 0 ]; then
        print_success "快速测试通过！"
        return 0
    else
        print_error "$failed 个测试套件失败"
        return 1
    fi
}

# 生成覆盖率报告
generate_coverage() {
    print_info "生成覆盖率报告..."
    pytest tests/test_unit_api.py tests/test_youtube_downloader.py \
        --cov=app --cov=src \
        --cov-report=html \
        --cov-report=term-missing \
        $VERBOSE_FLAG
    
    print_success "覆盖率报告已生成: htmlcov/index.html"
    
    # 尝试打开报告（macOS）
    if command -v open &> /dev/null; then
        print_info "打开覆盖率报告..."
        open htmlcov/index.html
    fi
}

# 主函数
main() {
    # 切换到项目根目录
    cd "$(dirname "$0")"
    
    echo ""
    echo "╔═══════════════════════════════════════════╗"
    echo "║   YouTube 下载器 API 测试套件            ║"
    echo "╚═══════════════════════════════════════════╝"
    echo ""
    
    # 解析参数
    VERBOSE_FLAG=""
    TEST_TYPE="fast"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -a|--all)
                TEST_TYPE="all"
                shift
                ;;
            -u|--unit)
                TEST_TYPE="unit"
                shift
                ;;
            -i|--integration)
                TEST_TYPE="integration"
                shift
                ;;
            -m|--module)
                TEST_TYPE="module"
                shift
                ;;
            -c|--coverage)
                TEST_TYPE="coverage"
                shift
                ;;
            -f|--fast)
                TEST_TYPE="fast"
                shift
                ;;
            -v|--verbose)
                VERBOSE_FLAG="-vv"
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                print_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 检查依赖
    check_dependencies
    echo ""
    
    # 运行测试
    case $TEST_TYPE in
        all)
            run_all_tests
            ;;
        unit)
            run_unit_tests
            ;;
        integration)
            run_integration_tests
            ;;
        module)
            run_module_tests
            ;;
        coverage)
            generate_coverage
            ;;
        fast)
            run_fast_tests
            ;;
    esac
    
    exit_code=$?
    echo ""
    
    if [ $exit_code -eq 0 ]; then
        echo "╔═══════════════════════════════════════════╗"
        echo "║          🎉 测试全部通过！               ║"
        echo "╚═══════════════════════════════════════════╝"
    else
        echo "╔═══════════════════════════════════════════╗"
        echo "║          ❌ 测试失败                     ║"
        echo "╚═══════════════════════════════════════════╝"
    fi
    
    exit $exit_code
}

# 运行主函数
main "$@"

