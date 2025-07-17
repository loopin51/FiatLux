import React, { useState, useEffect } from 'react';
import { Item, GridCell, GRID_DIMENSIONS, formatGridPosition, parseGridPosition, CATEGORY_COLORS } from '@/types';
import { motion, AnimatePresence } from 'framer-motion';

interface InteractiveGridProps {
  items: Item[];
  selectedPositions: string[];
  onPositionSelect: (positions: string[]) => void;
  onItemSelect?: (item: Item) => void;
  selectionMode?: 'single' | 'range' | 'multiple';
  disabled?: boolean;
  className?: string;
}

const InteractiveGrid: React.FC<InteractiveGridProps> = ({
  items,
  selectedPositions,
  onPositionSelect,
  onItemSelect,
  selectionMode = 'single',
  disabled = false,
  className = ''
}) => {
  const [grid, setGrid] = useState<GridCell[][]>([]);
  const [dragStart, setDragStart] = useState<{row: number, col: number} | null>(null);
  const [dragEnd, setDragEnd] = useState<{row: number, col: number} | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  // 그리드 초기화
  useEffect(() => {
    const newGrid: GridCell[][] = [];
    
    // 빈 그리드 생성
    for (let row = 0; row < GRID_DIMENSIONS.ROWS; row++) {
      const gridRow: GridCell[] = [];
      for (let col = 0; col < GRID_DIMENSIONS.COLS; col++) {
        const position = formatGridPosition(row, col);
        gridRow.push({
          position,
          isEmpty: true
        });
      }
      newGrid.push(gridRow);
    }

    // 물품으로 그리드 채우기
    items.forEach(item => {
      const positions = parseItemPosition(item.grid_position);
      positions.forEach(pos => {
        const { row, col } = parseGridPosition(pos);
        if (row >= 0 && row < GRID_DIMENSIONS.ROWS && col >= 0 && col < GRID_DIMENSIONS.COLS) {
          newGrid[row][col] = {
            position: pos,
            item,
            isEmpty: false,
            category: item.category
          };
        }
      });
    });

    setGrid(newGrid);
  }, [items]);

  // 물품 위치 파싱 (예: "A1-A3" -> ["A1", "A2", "A3"])
  const parseItemPosition = (gridPosition: string): string[] => {
    if (!gridPosition.includes('-')) {
      return [gridPosition];
    }

    const [start, end] = gridPosition.split('-');
    const startPos = parseGridPosition(start);
    const endPos = parseGridPosition(end);
    const positions: string[] = [];

    if (startPos.row === endPos.row) {
      // 같은 행에서 연속
      for (let col = startPos.col; col <= endPos.col; col++) {
        positions.push(formatGridPosition(startPos.row, col));
      }
    } else if (startPos.col === endPos.col) {
      // 같은 열에서 연속
      for (let row = startPos.row; row <= endPos.row; row++) {
        positions.push(formatGridPosition(row, startPos.col));
      }
    } else {
      // 복잡한 경우는 시작과 끝만
      positions.push(start, end);
    }

    return positions;
  };

  // 범위 선택 계산
  const getRangePositions = (start: {row: number, col: number}, end: {row: number, col: number}): string[] => {
    const positions: string[] = [];
    const minRow = Math.min(start.row, end.row);
    const maxRow = Math.max(start.row, end.row);
    const minCol = Math.min(start.col, end.col);
    const maxCol = Math.max(start.col, end.col);

    for (let row = minRow; row <= maxRow; row++) {
      for (let col = minCol; col <= maxCol; col++) {
        positions.push(formatGridPosition(row, col));
      }
    }

    return positions;
  };

  // 마우스 다운 핸들러
  const handleMouseDown = (row: number, col: number, e: React.MouseEvent) => {
    if (disabled) return;

    e.preventDefault();
    const position = formatGridPosition(row, col);
    const cell = grid[row][col];

    // 기존 아이템이 있는 셀을 클릭한 경우 아이템 선택
    if (!cell.isEmpty && cell.item && onItemSelect) {
      onItemSelect(cell.item);
      return;
    }

    if (selectionMode === 'range') {
      setDragStart({row, col});
      setIsDragging(true);
    } else if (selectionMode === 'multiple') {
      // 다중 선택 모드
      const newPositions = selectedPositions.includes(position)
        ? selectedPositions.filter(p => p !== position)
        : [...selectedPositions, position];
      onPositionSelect(newPositions);
    } else {
      // 단일 선택 모드
      onPositionSelect([position]);
    }
  };

  // 마우스 이동 핸들러
  const handleMouseMove = (row: number, col: number) => {
    if (!isDragging || !dragStart || disabled) return;
    setDragEnd({row, col});
  };

  // 마우스 업 핸들러
  const handleMouseUp = () => {
    if (!isDragging || !dragStart || disabled) return;

    if (dragEnd) {
      const rangePositions = getRangePositions(dragStart, dragEnd);
      onPositionSelect(rangePositions);
    } else {
      const position = formatGridPosition(dragStart.row, dragStart.col);
      onPositionSelect([position]);
    }

    setDragStart(null);
    setDragEnd(null);
    setIsDragging(false);
  };

  // 셀 스타일 결정
  const getCellClassName = (cell: GridCell, row: number, col: number): string => {
    const baseClasses = 'grid-cell relative cursor-pointer transition-all duration-200';
    
    let cellClasses = baseClasses;

    // 선택된 위치인지 확인
    const isSelected = selectedPositions.includes(cell.position);
    
    // 드래그 중인 범위에 포함되는지 확인
    const isDragRange = isDragging && dragStart && dragEnd && 
      getRangePositions(dragStart, dragEnd).includes(cell.position);

    if (cell.isEmpty) {
      cellClasses += ' grid-cell-empty border-2 border-gray-200';
      
      if (isSelected) {
        cellClasses += ' bg-blue-200 border-blue-400';
      } else if (isDragRange) {
        cellClasses += ' bg-blue-100 border-blue-300';
      } else {
        cellClasses += ' hover:bg-gray-50 hover:border-gray-300';
      }
    } else {
      const categoryColor = CATEGORY_COLORS[cell.category || '기타'] || 'miscellaneous';
      cellClasses += ` grid-cell-${categoryColor}`;
      
      if (isSelected) {
        cellClasses += ' ring-4 ring-blue-400 ring-opacity-75';
      } else if (isDragRange) {
        cellClasses += ' ring-2 ring-blue-300 ring-opacity-50';
      } else {
        cellClasses += ' hover:ring-2 hover:ring-gray-300';
      }
    }

    if (disabled) {
      cellClasses += ' opacity-50 cursor-not-allowed';
    }

    return cellClasses;
  };

  // 행 레이블 (A, B, C, D, E)
  const rowLabels = Array.from({ length: GRID_DIMENSIONS.ROWS }, (_, i) => 
    String.fromCharCode(65 + i)
  );

  // 열 레이블 (1, 2, 3, ..., 8)
  const colLabels = Array.from({ length: GRID_DIMENSIONS.COLS }, (_, i) => i + 1);

  return (
    <div className={`interactive-grid ${className}`}>
      {/* 선택 모드 안내 */}
      <div className="mb-4 p-3 bg-blue-50 rounded-lg">
        <div className="flex items-center justify-between">
          <div className="text-sm text-blue-800">
            {selectionMode === 'single' && '단일 위치를 클릭하세요'}
            {selectionMode === 'range' && '드래그하여 범위를 선택하세요'}
            {selectionMode === 'multiple' && '여러 위치를 클릭하여 선택하세요'}
          </div>
          {selectedPositions.length > 0 && (
            <div className="text-sm text-blue-600">
              선택된 위치: {selectedPositions.join(', ')}
            </div>
          )}
        </div>
      </div>

      {/* 그리드 컨테이너 */}
      <div className="grid-container bg-white rounded-xl shadow-lg p-6 overflow-x-auto">
        <div className="min-w-max">
          {/* 열 헤더 */}
          <div className="grid grid-cols-9 gap-1 mb-2">
            <div className="grid-header"></div>
            {colLabels.map(col => (
              <div key={col} className="grid-header">
                {col}
              </div>
            ))}
          </div>

          {/* 그리드 행들 */}
          {grid.map((row, rowIndex) => (
            <div key={rowIndex} className="grid grid-cols-9 gap-1 mb-1">
              {/* 행 헤더 */}
              <div className="grid-header">
                {rowLabels[rowIndex]}
              </div>

              {/* 셀들 */}
              {row.map((cell, colIndex) => (
                <motion.div
                  key={cell.position}
                  className={getCellClassName(cell, rowIndex, colIndex)}
                  onMouseDown={(e) => handleMouseDown(rowIndex, colIndex, e)}
                  onMouseMove={() => handleMouseMove(rowIndex, colIndex)}
                  onMouseUp={handleMouseUp}
                  whileHover={{ scale: disabled ? 1 : 1.05 }}
                  whileTap={{ scale: disabled ? 1 : 0.95 }}
                >
                  {/* 셀 내용 */}
                  <div className="cell-content">
                    {!cell.isEmpty && cell.item && (
                      <>
                        <div className="item-name">{cell.item.name}</div>
                        <div className="item-category">{cell.item.category}</div>
                      </>
                    )}
                    
                    {/* 위치 표시 */}
                    <div className="cell-position">
                      {cell.position}
                    </div>
                    
                    {/* 선택 표시 */}
                    {selectedPositions.includes(cell.position) && (
                      <div className="absolute inset-0 bg-blue-400 bg-opacity-20 rounded">
                        <div className="absolute top-1 right-1 w-3 h-3 bg-blue-500 rounded-full"></div>
                      </div>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          ))}
        </div>
      </div>

      {/* 선택 정보 */}
      {selectedPositions.length > 0 && (
        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
          <h4 className="font-medium text-gray-900 mb-2">선택된 위치</h4>
          <div className="flex flex-wrap gap-2">
            {selectedPositions.map(position => (
              <span
                key={position}
                className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
              >
                {position}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default InteractiveGrid;
