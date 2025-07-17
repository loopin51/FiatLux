import React, { useState, useEffect } from 'react';
import { Item, Category } from '@/types';
import { XMarkIcon, CheckIcon, TrashIcon, PencilIcon } from '@heroicons/react/24/outline';
import InteractiveGrid from './InteractiveGrid';
import { motion, AnimatePresence } from 'framer-motion';

interface ItemEditModalProps {
  item: Item | null;
  existingItems: Item[];
  categories: Category[];
  onSave: (item: Item) => Promise<void>;
  onCancel: () => void;
  isNewItem?: boolean;
}

interface FormData {
  name: string;
  description: string;
  category: string;
  grid_position: string;
}

const ItemEditModal: React.FC<ItemEditModalProps> = ({
  item,
  existingItems,
  categories,
  onSave,
  onCancel,
  isNewItem = false
}) => {
  const [formData, setFormData] = useState<FormData>({
    name: '',
    description: '',
    category: '',
    grid_position: ''
  });
  const [selectedPositions, setSelectedPositions] = useState<string[]>([]);
  const [showPositionSelector, setShowPositionSelector] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  // 폼 데이터 초기화
  useEffect(() => {
    if (item) {
      setFormData({
        name: item.name,
        description: item.description || '',
        category: item.category,
        grid_position: item.grid_position
      });
      setSelectedPositions(parseGridPosition(item.grid_position));
    } else {
      setFormData({
        name: '',
        description: '',
        category: categories[0]?.name || '',
        grid_position: ''
      });
      setSelectedPositions([]);
    }
    setError(null);
    setShowDeleteConfirm(false);
  }, [item, categories]);

  // 그리드 위치 파싱
  const parseGridPosition = (gridPosition: string): string[] => {
    if (!gridPosition) return [];
    
    if (!gridPosition.includes('-')) {
      return [gridPosition];
    }

    const [start, end] = gridPosition.split('-');
    const startMatch = start.match(/^([A-E])(\d+)$/);
    const endMatch = end.match(/^([A-E])(\d+)$/);
    
    if (!startMatch || !endMatch) return [gridPosition];
    
    const startRow = startMatch[1].charCodeAt(0) - 65;
    const startCol = parseInt(startMatch[2]) - 1;
    const endRow = endMatch[1].charCodeAt(0) - 65;
    const endCol = parseInt(endMatch[2]) - 1;
    
    const positions: string[] = [];
    
    if (startRow === endRow) {
      // 같은 행
      for (let col = startCol; col <= endCol; col++) {
        positions.push(`${String.fromCharCode(65 + startRow)}${col + 1}`);
      }
    } else if (startCol === endCol) {
      // 같은 열
      for (let row = startRow; row <= endRow; row++) {
        positions.push(`${String.fromCharCode(65 + row)}${startCol + 1}`);
      }
    } else {
      // 복잡한 경우
      positions.push(start, end);
    }
    
    return positions;
  };

  // 선택된 위치들을 그리드 위치 문자열로 변환
  const formatGridPosition = (positions: string[]): string => {
    if (positions.length === 0) return '';
    if (positions.length === 1) return positions[0];
    
    // 정렬
    const sorted = positions.sort((a, b) => {
      const aRow = a.charCodeAt(0);
      const aCol = parseInt(a.slice(1));
      const bRow = b.charCodeAt(0);
      const bCol = parseInt(b.slice(1));
      
      if (aRow === bRow) return aCol - bCol;
      return aRow - bRow;
    });
    
    // 연속된 위치 찾기
    const first = sorted[0];
    const last = sorted[sorted.length - 1];
    
    const firstRow = first.charCodeAt(0) - 65;
    const firstCol = parseInt(first.slice(1)) - 1;
    const lastRow = last.charCodeAt(0) - 65;
    const lastCol = parseInt(last.slice(1)) - 1;
    
    // 같은 행 또는 같은 열에서 연속된 경우
    if (firstRow === lastRow || firstCol === lastCol) {
      let isConsecutive = true;
      for (let i = 1; i < sorted.length; i++) {
        const curr = sorted[i];
        const prev = sorted[i - 1];
        const currRow = curr.charCodeAt(0) - 65;
        const currCol = parseInt(curr.slice(1)) - 1;
        const prevRow = prev.charCodeAt(0) - 65;
        const prevCol = parseInt(prev.slice(1)) - 1;
        
        if (firstRow === lastRow) {
          // 같은 행
          if (currRow !== prevRow || currCol !== prevCol + 1) {
            isConsecutive = false;
            break;
          }
        } else {
          // 같은 열
          if (currCol !== prevCol || currRow !== prevRow + 1) {
            isConsecutive = false;
            break;
          }
        }
      }
      
      if (isConsecutive) {
        return `${first}-${last}`;
      }
    }
    
    return sorted.join(',');
  };

  // 위치 선택 핸들러
  const handlePositionSelect = (positions: string[]) => {
    setSelectedPositions(positions);
    const gridPosition = formatGridPosition(positions);
    setFormData(prev => ({ ...prev, grid_position: gridPosition }));
  };

  // 유효성 검사
  const validateForm = (): boolean => {
    if (!formData.name.trim()) {
      setError('물품 이름을 입력해주세요.');
      return false;
    }
    if (!formData.category) {
      setError('카테고리를 선택해주세요.');
      return false;
    }
    if (!formData.grid_position.trim()) {
      setError('그리드 위치를 선택해주세요.');
      return false;
    }

    // 위치 중복 확인 (편집 중인 아이템 제외)
    const conflictingItem = existingItems.find((existingItem: Item) => 
      existingItem.id !== item?.id && 
      hasPositionConflict(existingItem.grid_position, formData.grid_position)
    );
    
    if (conflictingItem) {
      setError(`해당 위치는 이미 "${conflictingItem.name}"에서 사용 중입니다.`);
      return false;
    }

    return true;
  };

  // 위치 충돌 확인
  const hasPositionConflict = (pos1: string, pos2: string): boolean => {
    const positions1 = parseGridPosition(pos1);
    const positions2 = parseGridPosition(pos2);
    
    return positions1.some(p => positions2.includes(p));
  };

  // 저장 핸들러
  const handleSave = async () => {
    if (!validateForm()) return;

    setLoading(true);
    setError(null);

    try {
      const itemData: Item = {
        id: item?.id || 0,
        name: formData.name.trim(),
        description: formData.description.trim(),
        category: formData.category,
        grid_position: formData.grid_position,
        created_at: item?.created_at,
        updated_at: new Date().toISOString()
      };

      await onSave(itemData);
      onCancel();
    } catch (error) {
      setError(error instanceof Error ? error.message : '저장 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 삭제 핸들러 (필요시 구현)
  const handleDelete = async () => {
    if (!item) return;

    setLoading(true);
    setError(null);

    try {
      // 삭제 로직은 부모에서 처리하도록 수정
      onCancel();
    } catch (error) {
      setError(error instanceof Error ? error.message : '삭제 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 모달이 항상 표시되도록 수정
  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
        onClick={onCancel}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden mx-4"
          onClick={(e) => e.stopPropagation()}
        >
          {/* 헤더 */}
          <div className="flex items-center justify-between p-6 border-b">
            <h2 className="text-2xl font-bold text-gray-900">
              {isNewItem ? '새 물품 추가' : '물품 정보 수정'}
            </h2>
            <button
              onClick={onCancel}
              className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
            >
              <XMarkIcon className="w-6 h-6" />
            </button>
          </div>

          {/* 내용 */}
          <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
            {error && (
              <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-800">{error}</p>
              </div>
            )}

            <div className="space-y-6">
              {/* 기본 정보 */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    물품 이름 *
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="물품 이름을 입력하세요"
                    disabled={loading}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    카테고리 *
                  </label>
                  <select
                    value={formData.category}
                    onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    disabled={loading}
                  >
                    {categories.map(category => (
                      <option key={category.id} value={category.name}>
                        {category.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* 설명 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  설명
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="물품에 대한 설명을 입력하세요"
                  disabled={loading}
                />
              </div>

              {/* 위치 선택 */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <label className="block text-sm font-medium text-gray-700">
                    그리드 위치 *
                  </label>
                  <button
                    type="button"
                    onClick={() => setShowPositionSelector(!showPositionSelector)}
                    className="px-4 py-2 text-sm bg-blue-100 text-blue-800 rounded-lg hover:bg-blue-200 transition-colors"
                  >
                    {showPositionSelector ? '위치 선택 닫기' : '위치 선택 열기'}
                  </button>
                </div>

                <div className="flex items-center space-x-4 mb-4">
                  <input
                    type="text"
                    value={formData.grid_position}
                    onChange={(e) => {
                      setFormData(prev => ({ ...prev, grid_position: e.target.value }));
                      setSelectedPositions(parseGridPosition(e.target.value));
                    }}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="예: A1, A1-A3"
                    disabled={loading}
                  />
                  <span className="text-sm text-gray-500">
                    선택된 위치: {selectedPositions.length}개
                  </span>
                </div>

                {showPositionSelector && (
                  <div className="border border-gray-200 rounded-lg p-4">
                    <InteractiveGrid
                      items={existingItems.filter((i: Item) => i.id !== item?.id)}
                      selectedPositions={selectedPositions}
                      onPositionSelect={handlePositionSelect}
                      selectionMode="range"
                      disabled={loading}
                    />
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* 하단 버튼 */}
          <div className="flex items-center justify-between p-6 border-t bg-gray-50">
            <div>
              {!isNewItem && (
                <button
                  onClick={() => setShowDeleteConfirm(true)}
                  disabled={loading}
                  className="px-4 py-2 text-red-600 hover:text-red-800 transition-colors disabled:opacity-50"
                >
                  <TrashIcon className="w-5 h-5 inline mr-2" />
                  삭제
                </button>
              )}
            </div>

            <div className="flex space-x-3">
              <button
                onClick={onCancel}
                disabled={loading}
                className="px-6 py-2 text-gray-600 hover:text-gray-800 transition-colors disabled:opacity-50"
              >
                취소
              </button>
              <button
                onClick={handleSave}
                disabled={loading}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white inline-block mr-2"></div>
                    저장 중...
                  </>
                ) : (
                  <>
                    <CheckIcon className="w-5 h-5 inline mr-2" />
                    저장
                  </>
                )}
              </button>
            </div>
          </div>
        </motion.div>

        {/* 삭제 확인 모달 */}
        {showDeleteConfirm && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-60 flex items-center justify-center bg-black bg-opacity-50"
            onClick={() => setShowDeleteConfirm(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  물품 삭제 확인
                </h3>
                <p className="text-gray-600 mb-6">
                  "{item?.name}"을(를) 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.
                </p>
                <div className="flex justify-end space-x-3">
                  <button
                    onClick={() => setShowDeleteConfirm(false)}
                    disabled={loading}
                    className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors disabled:opacity-50"
                  >
                    취소
                  </button>
                  <button
                    onClick={handleDelete}
                    disabled={loading}
                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50"
                  >
                    {loading ? '삭제 중...' : '삭제'}
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </motion.div>
    </AnimatePresence>
  );
};

export default ItemEditModal;
