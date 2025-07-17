#!/bin/bash
# 물품 관리 시스템 실행 스크립트 (레거시 호환)
# ============================================

# 이 스크립트는 기존 호환성을 위해 유지됩니다.
# 새로운 기능을 사용하려면 start_all.sh를 사용하세요.

echo "⚠️  이 스크립트는 레거시 호환성을 위해 유지됩니다."
echo "💡 새로운 기능을 사용하려면 다음 스크립트를 사용하세요:"
echo "   • 전체 시스템: ./scripts/start_all.sh"
echo "   • 시스템 설정: ./scripts/setup_system.sh"
echo "   • 개발 모드: ./scripts/start_dev.sh"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 새로운 시작 스크립트 실행
"$SCRIPT_DIR/start_all.sh"
